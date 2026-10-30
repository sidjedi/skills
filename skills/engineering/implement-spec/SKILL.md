---
name: implement-spec
description: "Implement the result of /to-spec and /to-tickets in code, running small tickets in sequential lanes, then reviewing and closing the branch."
disable-model-invocation: true
---

You have been provided a spec. This spec should have tickets associated with it, describing how to implement the spec.

The issue tracker should have been provided to you. If not, tell the user to run `/setup-matt-pocock-skills`.

The goal is the entire spec implemented on a single **integration branch**, with every ticket resolved the way the issue tracker closes work.

The tickets are not a list of steps. They are a **task graph** with blocking relationships between them. This means there is always a **frontier** of tickets which are ready to be grabbed.

Communication to and from subagents should be sparse. Communicate primarily through **context pointers**: to the spec, tickets, research notes, and previous commits. Don't duplicate information already available via pointers.

**Implementer subagents** should be run in the background where possible. Prefer fewer, fuller lanes over many small ones: parallelism only pays when lanes are truly independent.

## Lanes

A **lane** is a chain of tickets that one implementer subagent builds **in sequence**, in one worktree on one branch. It exists so several small tickets share one context instead of paying one subagent each.

Plan lanes from the frontier and the ticket sizes (`P` ≈ 30k, `M` ≈ 60k, `G` ≈ 110k tokens):

- tickets in a lane follow their blocking order;
- a lane holds at most **four `P`, three `M` or two `G`** tickets; for mixed sizes keep the estimated total near that ceiling, and start a new lane when the next ticket would pass it;
- tickets with no dependency between them go in different lanes and run in parallel;

## Steps

1. Read the spec and tickets to understand the task graph.

2. (optional) Use an **exploration subagent** to conduct any exploration required by the tickets - relevant codebase files or external documentation. Run it on Sonnet. Ensure the exploration subagent can save files - it should save its markdown notes in a directory outside the repo, accessible by all future subagents. This lets **implementer subagents** focus on implementation rather than exploration.

3. Create the integration branch. If the issue tracker closes work through PRs, or the user asks for one, a draft PR may be opened after the first merge in step 5 (a branch with no commits ahead of main can't open one), marked as closing the spec and tickets.

4. Plan the lanes (above), then start one **implementer subagent** per lane, each in its own worktree on its own branch. Each implementer subagent:
   - confirms its worktree is based on the integration branch before starting, and resets onto it if not;
   - goes through its tickets in order. For **each** ticket it calls the Skill tool with `tdd` to build it, runs the new tests plus the related test files, commits, then records the ticket and runs the check as `implement` steps 7 and 8 describe. It does not run `code-review` or the context gate: the lane size is the budget;
   - waits for tests in the foreground, never with short-timeout `Monitor` calls used as a sleep;
   - never runs the full suite and has no user to ask about it: `finish-spec` runs it once at the end;
   - merges the integration branch tip into its own branch before reporting done.

5. Once an **implementer subagent** completes a lane, merge its work to the integration branch with a **merger subagent** (a Haiku model is enough). Merge **without squashing** (merge commit or fast-forward) so the commit hashes recorded in the tickets stay valid.

6. If this changes the **frontier** of available tickets, plan and start more lanes. This allows for maximum concurrency.

7. Once all tickets are complete, call the Skill tool with `code-review` on the integration branch, from the orchestrator and never inside an implementer's context. Fix all issues raised by the code review in a single **implementer subagent**.

8. Call the Skill tool with `finish-spec`. It runs the structural checks, the full suite once, the visual checks and opens the PR (or reports how the tracker closes the work). If a roadmap stage exists for this spec, `finish-spec` sets it to `done`.

9. Clean up all **implementer subagent** worktrees.
