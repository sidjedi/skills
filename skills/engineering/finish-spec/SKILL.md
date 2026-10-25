---
name: finish-spec
description: "Close a finished spec's branch: run the structural checks, the full test suite once, the visual checks, then write the PR body with real evidence and open the PR. Does not review code."
disable-model-invocation: true
---

Closes the branch of a spec whose tickets are implemented. `/implement-spec` calls it after `code-review` and its fixes; call it by hand after implementing tickets with `/implement` in layers.

It does **not** review the code: `code-review` already did, and running it twice is waste. This skill only checks what no review checks (record, proofs, the full suite, the screen) and opens the PR.

The issue tracker should have been provided to you. If not, tell the user to run `/setup-matt-pocock-skills`.

## Steps

1. **Locate** the spec folder (`.scratch/<feature>/` on a local tracker) and the fixed point (the commit where the integration branch left main). Ask only if you cannot tell.

2. **Structural checks** (they exit 1 on a gap):
   - `python <skill-dir>/scripts/check_spec.py <feature-dir>`: every AC has a proof and a ticket.
   - `python <skill-dir>/scripts/check_tickets.py <feature-dir> --stale-visual`: every `done` ticket cites a commit that exists, and every AC it delivers has a proof line. It also lists the visual ACs that need a fresh look.

   Fix **mechanical** gaps yourself (a missing proof line, a status left as `ready-for-agent`) and commit the fix. A gap that needs code or a decision is not yours to fix: go to step 6 and report it.

3. **Full suite, once.** Start the project's full test command in the background (use its parallel mode; the command is in `AGENTS.md`). Do not wait for it idly: do step 4 meanwhile.

4. **Visual checks, in one batch.** Call the Skill tool with `browser-harness` and, in a single browser session, check the visual ACs that step 2 listed (`visual: <screen>` in the spec). One capture per AC. Visual ACs not listed reuse the evidence already in their ticket's record. If a check fails, say which AC and what you saw; do not edit code.

   If the `## Agent skills` block lists a quality doc (`docs/agents/quality.md`), run the checks it names too. Their output goes into the PR Evidence; warnings do not stop the PR.

5. **Result of the suite.** Read it when it finishes. Green is the only pass. Red or flaky: report the failing tests, do not "fix" tests to pass.

6. **If anything failed** (structural gap needing code, a failed visual check, a red suite): stop here. Report each item with its AC, and do not open a PR. The user decides.

7. **If everything passed:** call the Skill tool with `pr` to write the body. Use the checks above as its **Evidence** (script output, suite result with counts, capture paths for visual ACs), not an invented before/after. Then open the PR the way the issue tracker closes work, marked as closing the spec and its tickets. If the tracker does not use PRs, report the branch instead.

8. If `docs/roadmap.md` has a stage for this spec, set its row to `done`.

9. Reply with: what passed, what you overrode (a script you judged wrong and why, noted in the ticket's `## Comments`), and the PR or branch.

## Scripts can be overridden, with a reason

If a script blocks and you are sure it is wrong, go on and write `Script override: <what and why>` in the ticket's `## Comments`, and say so in the final reply. Never override silently.

`<skill-dir>` is the directory that contains this SKILL.md; its `scripts/` folder ships with the skill.
