#!/usr/bin/env python3
"""Structural check: every acceptance criterion (AC) has a proof and a ticket.

Usage:
    check_spec.py <feature-dir> [--spec-only]

<feature-dir> is the folder holding spec.md and issues/NN-*.md (e.g. .scratch/painel-leads).

Spec format it reads (see to-spec):
    | AC-1.1 | criterion text | test / cmd: <command> / visual: <screen> |

Ticket format it reads (see to-tickets), a line such as:
    **Entrega:** US-1, US-2, AC-1.1, AC-2.1

Exit 0 = ok. Exit 1 = a structural gap. This checks structure only: whether the proof
actually proves the criterion is the review's job, not this script's.
"""
import re
import sys
from pathlib import Path

AC_ROW = re.compile(r"^\|\s*(AC-\d+\.\d+)\s*\|(.*)\|\s*$")
AC_ID = re.compile(r"AC-\d+\.\d+")
US_ID = re.compile(r"US-\d+")
US_LINE = re.compile(r"^\s*(?:\d+\.|-)?\s*\*{0,2}(US-\d+)\b")


def read_spec(spec: Path):
    acs = {}
    stories = set()
    for line in spec.read_text(encoding="utf-8").splitlines():
        m = AC_ROW.match(line)
        if m:
            cells = [c.strip() for c in m.group(2).split("|")]
            acs[m.group(1)] = cells[-1] if cells else ""
            continue
        m = US_LINE.match(line)
        if m:
            stories.add(m.group(1))
    return acs, stories


def read_tickets(issues: Path):
    delivered = {}
    for f in sorted(issues.glob("*.md")):
        for line in f.read_text(encoding="utf-8").splitlines():
            if re.match(r"^\*\*Entrega:\*\*", line):
                delivered[f.name] = set(AC_ID.findall(line)) | set(US_ID.findall(line))
                break
    return delivered


def main(argv):
    args = [a for a in argv[1:] if not a.startswith("--")]
    spec_only = "--spec-only" in argv
    if len(args) != 1:
        print(__doc__)
        return 2
    root = Path(args[0])
    spec = root / "spec.md"
    if not spec.exists():
        print(f"FAIL: {spec} not found")
        return 1

    acs, stories = read_spec(spec)
    errors = []

    if not acs:
        errors.append("spec has no acceptance criteria table (rows like '| AC-1.1 | ... | ... |')")
    for ac, proof in acs.items():
        if not proof or proof.lower() in {"-", "tbd", "?"}:
            errors.append(f"{ac}: no Proof (use 'test', 'cmd: <command>' or 'visual: <screen>')")

    if not spec_only:
        issues = root / "issues"
        delivered = read_tickets(issues) if issues.exists() else {}
        if not delivered:
            errors.append("no ticket has an '**Entrega:**' line")
        covered = set().union(*delivered.values()) if delivered else set()
        for ac in acs:
            if ac not in covered:
                errors.append(f"{ac}: not delivered by any ticket")
        for name, ids in delivered.items():
            for i in sorted(ids):
                if i.startswith("AC-") and i not in acs:
                    errors.append(f"{name}: cites {i}, which is not in the spec")
                if i.startswith("US-") and stories and i not in stories:
                    errors.append(f"{name}: cites {i}, which is not in the spec")
        for us in sorted(stories - (set().union(*delivered.values()) if delivered else set())):
            print(f"warn: {us} is not cited by any ticket")

    if errors:
        print("FAIL")
        for e in errors:
            print(f"- {e}")
        return 1
    print(f"OK: {len(acs)} acceptance criteria" + ("" if spec_only else ", all delivered by a ticket"))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
