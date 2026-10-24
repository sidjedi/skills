#!/usr/bin/env python3
"""Context gate: may the agent start another ticket in this window?

Usage:
    context_gate.py [--limit 200000] [--max-age 900]

Reads ~/.claude/state/context-latest.json, written by the statusline (see skills_v2/README.md).

Exit 0 = below the limit, may start the next ticket.
Exit 1 = at or above the limit, do not start a new ticket (finish, commit, ask for /compact).
Exit 2 = no usable reading (missing, stale, or from another project): fall back to the
         file-size estimate described in the implement skill.

Prints one line so the agent can quote it.
"""
import json
import os
import sys
import time
from pathlib import Path


def arg(name, default):
    return type(default)(sys.argv[sys.argv.index(name) + 1]) if name in sys.argv else default


def main():
    limit = arg("--limit", 200000)
    max_age = arg("--max-age", 900)
    f = Path.home() / ".claude" / "state" / "context-latest.json"
    try:
        d = json.loads(f.read_text(encoding="utf-8"))
    except Exception:
        print("unknown: no context reading (statusline not writing context-latest.json)")
        return 2
    age = time.time() - d.get("written_at", 0)
    if age > max_age:
        print(f"unknown: reading is {int(age)}s old")
        return 2
    here = os.path.basename(os.getcwd().rstrip("/\\")).lower()
    theirs = os.path.basename(str(d.get("cwd", "")).rstrip("/\\")).lower()
    if here != theirs:
        print(f"unknown: reading belongs to another project ({theirs})")
        return 2
    tokens = d.get("context_tokens")
    if not isinstance(tokens, (int, float)):
        print("unknown: reading has no context_tokens")
        return 2
    if tokens >= limit:
        print(f"STOP: context at {int(tokens)} tokens (limit {limit}); do not start a new ticket")
        return 1
    print(f"OK: context at {int(tokens)} tokens (limit {limit}); may start the next ticket")
    return 0


if __name__ == "__main__":
    sys.exit(main())
