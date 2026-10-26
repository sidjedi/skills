# setup-jedi: why it is built this way

Read this before changing the skill. It records decisions, so a change does not undo one by accident.

## Principles
- **Minimum instruction, at the right place.** Everything in `AGENTS.md` is read on every message, so it holds only what applies to any task. Detail sits one level down and is read when needed.
- **Profile, not rules.** The `Ao implementar` section shapes how the agent works (KISS, complexity, decide and follow). Numbers and limits live in tool config, never in prose.
- **One pointer.** The `## Agent skills` block written by `setup-matt-pocock-skills` is the only index in `AGENTS.md`. Skills find the tracker, labels, glossary and `docs/agents/*` through it. Never add a second pointer, and never repeat a path inside a skill.
- **Nothing hardcoded.** File names (glossary, tracker) are whatever `docs/agents/domain.md` records. The project's existing choice wins over the template's.
- **Visual is validated visually.** `browser-harness` is the default and the only visual tool named.
- **Terminal over copying.** Install and configure with the stack's own commands. `templates/` holds only text with no command equivalent.
- **No duplication across skills.** Each skill owns one job; if two say the same thing, one of them is wrong.
- **Never overwrite.** What exists stays; differences are shown as a diff for the user.
- **Machine config is edited only with permission**, with a backup, keeping what the user already has. Hooks are left alone unless a skill needs one or the user accepts an optional tool.
- **Optional tools are offered, never assumed.** They are the owner's preferences, not requirements of the method. Each one gets its own explicit yes or no, separate from the setup overview, and a no is final for the run. A fact that might conflict (such as an existing `ANTHROPIC_BASE_URL`) is shown and the user decides; it is not an automatic block.

## Why each part is there
- `SKILL.md`: orchestration only, with one confirmation before anything is written, plus one separate confirmation per optional tool.
- `stacks/<stack>.md`: everything that varies by stack, one file per stack, loaded only for the chosen one. Fixed layout: Create, Tests, Fast checks, Slow checks, Camadas, Suggest, Look up. Commands go in code blocks, with a one-line reason above them.
- `templates/agents-core.md`: the always-loaded core, about 15 lines.
- `templates/testing.md` becomes `docs/agents/testing.md`: test models, read when tests are written.
- `quality.md` (generated): slow checks for the PR, read by `finish-spec`. Fast checks run with lint and do not appear in it.
- `templates/statusline-context-snippet.txt`: the `implement` gate reads the context size from the file this writes.
- `tools/<tool>.md`: one optional tool per file, offered in step 6. Fixed layout: Offer when, Inform and ask, Requirements, Install, Run or Configuration, Confirm, Verify, Undo. The Confirm block is the exact text shown to the user. Commands are run once in a scratch folder before the first real offer.

## Changing it
- **A rule that applies to every task** (a way of working, a style): `templates/agents-core.md`, as one profile sentence. Bump the `v<N>` marker so re-runs show a diff.
- **Something for one stack** (a tool, a layer layout, a test setup): that stack's file. Run each command once in a scratch folder before writing it down.
- **A new stack:** copy the layout of `stacks/python.md`, then list it as an option in step 2 of `SKILL.md`.
- **A test model, or when to use which:** `templates/testing.md`.
- **A new optional tool (Caveman, another):** copy the layout of an existing file in `tools/` into `tools/<tool>.md`; step 6 picks it up. Removing a tool is deleting its file. A rule that only makes sense with that tool goes in its `AGENTS.md` snippet there, not in `templates/agents-core.md` and not in a generic skill.
- **A PR-time check:** the stack's `Slow checks` section; it reaches `quality.md` through the user's confirmation.
- **A pattern specific to one repo:** not here. Short and universal goes in that repo's `AGENTS.md` (`Camadas`); a decision with reasons goes in an ADR.
- **Research** (tests, aesthetics, method): run `research`, keep the cited file in the repo, and turn its conclusions into the smallest change above.
