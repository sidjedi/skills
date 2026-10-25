---
name: setup-jedi
description: "Initialize a project for the Jedi workflow: stack, AGENTS.md, glossary, test runner, machine checks, then setup-matt-pocock-skills. Safe to re-run."
disable-model-invocation: true
---

Prepares a repo (new or existing) so the Jedi skills work from the first ticket. It scaffolds with the stack's official CLI, writes a short `AGENTS.md`, wires the test runner, checks the machine, and ends by running `setup-matt-pocock-skills`.

Nothing is overwritten. What exists stays; what differs from the template is shown as a diff for the user to decide.

## Steps

1. **Detect.** Read what exists: `AGENTS.md`, `CLAUDE.md`, the glossary (`CONTEXT.md` or `GLOSSARY.md`), `docs/agents/`, the manifest (`pyproject.toml`, `package.json`), `git`. Done when you can say which pieces below are present, which are missing, and whether the repo is new (no code) or existing.

2. **Brief and stack.** New repo: ask what the project is, for whom, and what ships first, in one round. From the answer, suggest 2 or 3 stacks from `stacks/` with a one-line trade-off each, plus "other" (`stacks/generic.md`). Existing repo: take the stack from its manifest and ask nothing. Done when the stack is chosen.

3. **Overview, one confirmation.** Read `stacks/<stack>.md` and show everything you will do: the scaffold command, the files, the test runner, which quality checks to enable (the fast ones in lint, the slow ones for the PR), each with its limit, and the machine changes (step 5). The user can change any item, limits included; apply what they say. Write nothing before this is confirmed.

4. **Scaffold and write.**
   - New repo: run the stack's create command.
   - Test runner and a passing smoke test, from the stack file.
   - `AGENTS.md` from `templates/agents-core.md` plus the stack's `Camadas` block. Keep a block a tool already wrote (for example the one `create-next-app` adds). If `CLAUDE.md` has content, show it and move it into `AGENTS.md`, then leave `CLAUDE.md` as a symlink to `AGENTS.md`, or a one-line `@AGENTS.md` if the symlink fails.
   - Glossary: keep the existing file and its name. If none, create `GLOSSARY.md` from `templates/glossary-seed.md`, seeded with the brief. Offer the rename only when asked.
   - `docs/agents/testing.md` from `templates/testing.md`, and `docs/agents/quality.md` (slow checks and how to run them) only when the user accepted slow checks.
   - `.gitignore` and `.env.example` per stack.

   Template sections carry `<!-- setup-jedi: <name> v<N> -->`. On a re-run, compare the version and show a diff for the sections that changed.

5. **Machine.** Check, and for each gap ask once before acting:
   - **Statusline:** `~/.claude/settings.json` has a `statusLine` that writes `~/.claude/state/context-latest.json` (the `implement` gate reads it). If missing, back up the file as `<name>.bak-antes-setup-jedi` and add `templates/statusline-context-snippet.txt` to the user's statusline, keeping what is there. With no statusline, use the user's choice.
   - **Browser Harness:** installed and responding. If not, follow its `install.md`.
   - **Other tools** (`uv`, `pnpm`, `node`, `git`, `gh`, `rtk`): offer only the ones this project's stack uses and the machine lacks.

   Hooks are left alone unless a skill requires one.

6. **Git.** If the folder is not a repo, `git init` and one initial commit, after showing what enters it. Create no remote and push nothing.

7. **Skills docs.** Call the Skill tool with `setup-matt-pocock-skills`. It edits `AGENTS.md`; tell it which glossary file the repo uses, and have it list `docs/agents/testing.md` and `docs/agents/quality.md` in the `## Agent skills` block, the only pointer in `AGENTS.md`.

8. **Reply** with what was created, what already existed and was kept, and any step the user declined.
