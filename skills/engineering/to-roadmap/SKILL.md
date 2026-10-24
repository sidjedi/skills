---
name: to-roadmap
description: "Turn a big, greenfield or multi-spec project into a short living roadmap of vertical stages, by interview. Each stage later becomes one spec."
disable-model-invocation: true
---

Create `docs/roadmap.md` for a project too big for one spec. The roadmap fixes the **order** of the work; each stage is later detailed by `/to-spec`, one stage at a time.

The issue tracker and triage label vocabulary should have been provided to you. If not, tell the user to run `/setup-matt-pocock-skills`.

## Process

1. Explore the repo (`CONTEXT.md`, ADRs, existing specs) so the stages use the project's vocabulary and respect decisions already made. If there is no repo yet, skip this.

2. Call the Skill tool with `grilling` to interview the user about the project: who it is for, what the first usable version must do, what can wait, what is risky or unknown. Ask about **outcomes the user will see**, not layers.

3. Draft the stages and check them against the **vertical rule**:
   - every stage cuts through all layers (data, logic, UI) and ends with something the user can **use or see**;
   - never a stage that only does back-end, only a schema, or only "setup" with nothing to show. Foundations ride inside the first stage that needs them;
   - stage 1 is the thinnest end-to-end path (a tracer bullet);
   - later stages may stay vague. Only the next one or two need a clear "user can now" line.

4. Show the stages to the user and iterate until they approve the order and size. A stage that would not fit in one spec is too big: split it.

5. Write `docs/roadmap.md` with the template below. Decisions that are hard to reverse go to ADRs; link them, do not copy them.

<roadmap-template>

# Roadmap: <project>

One paragraph: what the project is and what "first release" means.

## Stages

| # | Stage | The user can now… | Blocked by | Status | Spec |
|---|-------|-------------------|------------|--------|------|
| 1 | <short name> | <one sentence, from the user's view> | None | todo | |
| 2 | … | … | 1 | todo | |

Status is one of `todo`, `specced` (a spec exists), `done` (spec fully implemented and PR closed).

## Not now

Ideas deliberately left out of the first release.

## Open questions

Only those that block a stage. Remove them as they are answered.

</roadmap-template>

## Using the roadmap later

When the user asks for "the spec of the next stage", `/to-spec` reads the stage row, writes the spec for that stage only, and sets the row to `specced` with the spec path. `/implement-spec` (through `/finish-spec`) sets it to `done`. Keep the file short; if it grows past one screen of table, stages are being over-planned.
