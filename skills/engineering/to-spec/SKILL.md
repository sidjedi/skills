---
name: to-spec
description: "Turn the current conversation into a spec and publish it to the project issue tracker: no interview, just synthesis of what you've already discussed. User stories and acceptance criteria carry ids and proofs so they can be checked later."
disable-model-invocation: true
---

This skill takes the current conversation context and codebase understanding and produces a spec. Do NOT interview the user; just synthesize what you already know.

The issue tracker and triage label vocabulary should have been provided to you. If not, tell the user to run `/setup-matt-pocock-skills`.

## Process

1. Explore the repo to understand the current state of the codebase, if you haven't already. Use the project's domain glossary vocabulary throughout the spec, and respect any ADRs in the area you're touching.

   If the user points at a stage of `docs/roadmap.md` ("spec the next stage"), read that row and scope the spec to **that stage only**.

2. Sketch out the seams at which you're going to test the feature. Existing seams should be preferred to new ones. Use the highest seam possible. If new seams are needed, propose them at the highest point you can. The fewer seams across the codebase, the better - the ideal number is one.

Check with the user that these seams match their expectations.

3. Write the spec using the template below, then publish it to the project issue tracker. Apply the `ready-for-agent` triage label - no need for additional triage.

4. Run `python <skill-dir>/scripts/check_spec.py <feature-dir> --spec-only` (the folder holding `spec.md`). It fails if an acceptance criterion has no Proof. Fix the spec and rerun until it exits 0. If the script is wrong for this spec, you may go on, but say why in `Further Notes`.

5. If the spec came from a roadmap stage, set that row to `specced` and fill its `Spec` column.

<spec-template>

## Problem Statement

The problem that the user is facing, from the user's perspective.

## Solution

The solution to the problem, from the user's perspective.

## User Stories

A LONG, numbered list of user stories, each with a stable id. Each user story should be in the format of:

US-1. As an <actor>, I want a <feature>, so that <benefit>

<user-story-example>
US-1. As a mobile bank customer, I want to see balance on my accounts, so that I can make better informed decisions about my spending
</user-story-example>

This list of user stories should be extremely extensive and cover all aspects of the feature.

## Acceptance Criteria

One row per verifiable behaviour, grouped under the story it serves (`AC-<story>.<n>`). Each row says **how it will be proven**. Keep it to observable behaviour, not implementation.

| ID | Criterion | Proof |
|----|-----------|-------|
| AC-1.1 | The account page shows the balance of every account | test |
| AC-1.2 | The balance card is readable on a phone | visual: account page, 390px |

Proof is one of: `test` (a behaviour test at the seam above), `cmd: <command>` (a command whose exit code settles it), or `visual: <screen/route>` (checked in the browser with Browser Harness, never as a test; see the project's `AGENTS.md`). The exact test id is recorded later, in the ticket.

## Implementation Decisions

A list of implementation decisions that were made. This can include:

- The modules that will be built/modified
- The interfaces of those modules that will be modified
- Technical clarifications from the developer
- Architectural decisions
- Schema changes
- API contracts
- Specific interactions

Do NOT include specific file paths or code snippets. They may end up being outdated very quickly.

Exception: if a prototype produced a snippet that encodes a decision more precisely than prose can (state machine, reducer, schema, type shape), inline it within the relevant decision and note briefly that it came from a prototype. Trim to the decision-rich parts, not a working demo, just the important bits.

## Testing Decisions

A list of testing decisions that were made. Include:

- A description of what makes a good test (only test external behavior, not implementation details)
- Which modules will be tested
- Prior art for the tests (i.e. similar types of tests in the codebase)
- Anything from the project's `AGENTS.md` that applies (test limits, what is verified visually instead of by test)

## Out of Scope

A description of the things that are out of scope for this spec.

## Further Notes

Any further notes about the feature.

</spec-template>

`<skill-dir>` is the directory that contains this SKILL.md; its `scripts/` folder ships with the skill.
