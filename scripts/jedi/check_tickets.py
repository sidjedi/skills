#!/usr/bin/env python3
"""Structural check of finished tickets: record, commit and per-AC proof.

Usage:
    check_tickets.py <feature-dir> [--ticket NN] [--stale-visual] [--repo .]

For every ticket whose Status starts with `done`:
  - its `## Registro` / `## Comments` section cites a commit that exists in git;
  - when the ticket has an `**Entrega:**` line, every AC it lists has a proof line there:
        - AC-1.1 -> tests/test_x.py::test_name        (file exists and holds `test_name`)
        - AC-1.2 -> visual: <capture path or note>
  - an unticked checkbox on a `done` ticket is only a warning (the Registro must say why).

`--stale-visual` prints the visual ACs that need a fresh look: a later commit touched the
same files as the ticket's own commit. Visual ACs not listed can reuse the Registro evidence.

Exit 0 = ok, 1 = a gap. Tickets without `**Entrega:**` (legacy) only get the commit check.
"""
import re
import subprocess
import sys
from pathlib import Path

HEX = re.compile(r"\b(?=[0-9a-f]*\d)[0-9a-f]{7,40}\b")
AC_ID = re.compile(r"AC-\d+\.\d+")
PROOF = re.compile(r"(AC-\d+\.\d+)\s*(?:->|→)\s*(.+)")


def git(repo, *a):
    r = subprocess.run(["git", "-C", str(repo), *a], capture_output=True, text=True)
    return r.returncode, r.stdout.strip()


def field(text, name):
    m = re.search(rf"^\**{name}:?\**:?\**\s*(.*)$", text, re.M | re.I)
    return m.group(1).strip() if m else ""


def record_section(text):
    m = re.search(r"^##\s+(Registro|Comments)\s*$(.*)", text, re.M | re.S)
    return m.group(2) if m else ""


def spec_visual_acs(root):
    spec = root / "spec.md"
    out = set()
    if spec.exists():
        for line in spec.read_text(encoding="utf-8").splitlines():
            m = re.match(r"^\|\s*(AC-\d+\.\d+)\s*\|.*\|\s*visual\b", line, re.I)
            if m:
                out.add(m.group(1))
    return out


def main(argv):
    args = [a for a in argv[1:] if not a.startswith("--")]
    flags = set(a for a in argv[1:] if a.startswith("--"))
    repo = Path(".")
    only = None
    if "--repo" in argv:
        repo = Path(argv[argv.index("--repo") + 1])
        args = [a for a in args if a != str(repo)]
    if "--ticket" in argv:
        only = argv[argv.index("--ticket") + 1]
        args = [a for a in args if a != only]
    if len(args) != 1:
        print(__doc__)
        return 2
    root = Path(args[0])
    issues = sorted((root / "issues").glob("*.md"))
    visual = spec_visual_acs(root)
    errors, stale = [], []

    for f in issues:
        if only and not f.name.startswith(only.zfill(2)):
            continue
        text = f.read_text(encoding="utf-8")
        if not field(text, "Status").lower().startswith("done"):
            continue
        rec = record_section(text)
        commits = [h for h in HEX.findall(rec) if git(repo, "cat-file", "-e", h + "^{commit}")[0] == 0]
        if not commits:
            msg = f"{f.name}: done, but no existing commit cited under Registro/Comments"
            if field(text, "Entrega"):
                errors.append(msg)
            else:
                print(f"warn: {msg} (legacy ticket, no Entrega line)")
        if "[ ]" in text:
            print(f"warn: {f.name}: done with unticked checkboxes (Registro should say why)")

        entrega = field(text, "Entrega")
        acs = AC_ID.findall(entrega)
        proofs = {m.group(1): m.group(2).strip() for m in PROOF.finditer(rec)}
        for ac in acs:
            p = proofs.get(ac)
            if not p:
                errors.append(f"{f.name}: {ac} has no proof line ('- {ac} -> path::test' or '-> visual: ...')")
            elif "::" in p:
                path, name = p.split("::", 1)
                tf = repo / path.strip(" `")
                if not tf.exists():
                    errors.append(f"{f.name}: {ac} cites {path}, which does not exist")
                elif name.strip(" `") not in tf.read_text(encoding="utf-8", errors="ignore"):
                    errors.append(f"{f.name}: {ac} cites {name}, not found in {path}")

        if "--stale-visual" in flags and commits:
            _, files = git(repo, "show", "--name-only", "--format=", commits[0])
            files = [x for x in files.splitlines() if x]
            _, later = git(repo, "log", f"{commits[0]}..HEAD", "--format=%h", "--", *files) if files else (0, "")
            if later:
                stale += [f"{f.name}: {ac}" for ac in acs if ac in visual]

    if "--stale-visual" in flags:
        print("visual ACs to re-check:" if stale else "visual ACs to re-check: none")
        for s in stale:
            print(f"- {s}")
    if errors:
        print("FAIL")
        for e in errors:
            print(f"- {e}")
        return 1
    print("OK")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
