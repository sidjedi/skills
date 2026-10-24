---
name: implement
description: "Implement a piece of work based on a spec or set of tickets. Accepts several small tickets and runs them one after another in the same context window."
disable-model-invocation: true
---

Implement the work described by the user in the spec or tickets.

If the user passes ticket references, fetch each from the issue tracker and state its title before starting it. If a reference is ambiguous, ask. If the user passes several tickets (or "the next N ready tickets"), do them **in dependency order, one after another, in this same context window**.

## One ticket = one full cycle

Every ticket gets the whole cycle below, as if it were its own run. Sharing the window is only about reusing what you already read: **never merge tickets into one pass, one commit or one record.**

1. **Gate.** Before starting each ticket, run `python <skill-dir>/scripts/context_gate.py`.
   - exit 0: go on.
   - exit 1: do **not** start the ticket. Stop, say how many tickets are done and which remain, and tell the user to run `/compact` and call `/implement` again with the remaining ones.
   - exit 2 (no reading): estimate instead. Add up the size of the files the ticket touches, divided by 4, plus the tickets already done in this window; stop if the total passes ~150k tokens.
   The gate applies **between** tickets. Never abandon a ticket half-built because of it.
2. **Understand.** Read the ticket and the code it touches. Read the ticket's `Entrega:` line: those `AC-` ids are what must be proven.
3. **Build.** Call the Skill tool with "tdd" where possible, at pre-agreed seams. Follow the project's `AGENTS.md` for test limits (for example, tests only at the declared seam, a small number per AC, each test tied to an AC). Anything visual is **not** a test: check it in the browser with Browser Harness and keep the capture path as evidence.
4. **Run the right tests.** Run typechecking regularly and single test files regularly. At the end run only the new tests plus the test files related to what you changed (the same module, route, template or helper).
5. **Review.** Call the Skill tool with "code-review" to review this ticket's work.
6. **Commit** to the current branch.
7. **Record.** Update the ticket in the issue tracker: set its `Status:` line to `done` (the repo convention; add a short note in parentheses if something is left out, e.g. `done (falta só a captura)`), tick the checkboxes that were delivered, and make sure the `## Registro` / `## Comments` section lists the commit and what was not done. If the ticket has an `Entrega:` line, add one proof line per AC there: `- AC-1.1 -> tests/test_x.py::test_name` or `- AC-1.2 -> visual: <capture path>`. Commit that update too (a small docs commit is fine). Never leave an implemented ticket as `ready-for-agent`.
8. **Check.** Run `python <skill-dir>/scripts/check_tickets.py <feature-dir> --ticket <NN>`. Fix what it reports and rerun.

Then the next ticket, back to step 1.

## Scripts can be overridden, with a reason

The scripts catch structural gaps; they do not judge. If one blocks you and you are sure it is wrong, go on and write `Script override: <what and why>` in the ticket's `## Comments`. Never override silently.

## The full suite

Do NOT run the full test suite on your own: it can take many minutes. When the work is done, say which tests you ran and ask the user whether to run the full suite now or later (for example once the whole branch of work is finished, which `/finish-spec` does once). Run it only after they confirm. If the project supports parallel runs (for example `pytest -n auto`), use that.

`<skill-dir>` is the directory that contains this SKILL.md; its `scripts/` folder ships with the skill.
