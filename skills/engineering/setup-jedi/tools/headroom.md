# Headroom

Local proxy that compresses what goes into each API request (JSON, logs, code by AST, text by a small local model). Repo and research: `docs/jedi/research/token-tools-ponytail-headroom-caveman.md`.

**Status: no command here has been run yet.** They come from Headroom's README and docs. Before the first real offer, run Install, Run and Verify once in a scratch folder and fix this file with what actually happened.

## Offer when
- `headroom` is not on PATH. If it is, say so and stop: nothing to install.

## Inform and ask (not a blocker)
- `ANTHROPIC_BASE_URL` already set (shell, `~/.claude/settings.json`, project settings). Show the value and say Headroom will sit in front of it. Ask: keep it as Headroom's upstream (`--anthropic-api-url <value>`), replace it, or skip Headroom. Never decide for the user.
- Another tool accepted in this run also sets `ANTHROPIC_BASE_URL` (for example Caveman's native route). Only one can own it: ask which.

## Requirements
Check each one and name the ones that fail; skip the tool if any fails.
- Python 3.10 or newer, or `uv`.
- Internet access to download the packages and the text model from Hugging Face (about 261 MB for the model).
- Free disk for the packages and the model (a few hundred MB with the lean extra below).
- Windows: `wrap claude` has not been verified there yet; the first run is the check.

## Install
Lean extra: no torch, and no cross-agent memory dependencies. The text model still runs locally on CPU through ONNX Runtime.

```bash
uv tool install --python 3.13 "headroom-ai[sandbox]"
```

## Run
Per session, flags verified in the docs. Use this until Persist is validated.

```bash
headroom wrap claude --code-aware --code-graph
```

Persist per repo (to validate): `headroom init claude` without `-g` writes the proxy URL and hooks to `.claude/settings.local.json` of the current folder only, so it applies to this repo and nothing else. `init -g`, `deploy` and `install apply` are machine-wide: not used here. Confirm that `init` can carry the options below before switching the default to it. Make sure `.claude/settings.local.json` is in `.gitignore`.

## Configuration
| Setting | Value | Why |
|---|---|---|
| `--code-aware` | on | AST compression of code; needs the `code` extra (in `sandbox`) |
| `--code-graph` | on | live code-graph watcher; check whether it downloads a separate binary (`codebase-memory-mcp`) and tell the user if so |
| Serena MCP | on (default of `wrap`) | symbol navigation; local scope for this project only |
| `--mode` | `cache` (default) | `token` rewrites old turns and breaks the prompt-cache prefix |
| Tool search | leave the default (on) | Claude Code 2.1.304 and later defer tools behind a gateway by default; off would load every MCP tool definition up front |
| `--memory` | **off** | cross-agent memory, declined by the owner |
| `--1m` | off | only forces the `[1m]` model selector; not needed when the session already has the 1M window, and it edits the user-level `model` setting |
| `HEADROOM_BEACON=off`, `HEADROOM_TELEMETRY=off` | set | the beacon is on by default |
| Output shaper, `headroom learn` into `AGENTS.md` | off | style and file writes the Jedi formats must not inherit |

## Confirm
Show this to the user, filling the brackets, and ask for an explicit yes or no:

> **Headroom (opcional).** Proxy local que comprime o que vai em cada requisição.
> - Usa um **modelo pequeno** (~261 MB, roda na sua CPU, sem GPU) para comprimir texto. A compressão de texto funciona **melhor em inglês**; em português pode comprimir pior, e isso não foi medido.
> - Requisitos: [resultado da checagem].
> - `ANTHROPIC_BASE_URL`: [valor atual / não definido] e o que será feito com ele.
> - Liga: compressão de código por AST, code graph, Serena. Mantém o cache de prefixo (modo `cache`) e a busca de ferramentas padrão.
> - Desliga: memória entre agentes, `--1m`, telemetria.
> - Rodará [por sessão com `headroom wrap claude` / só neste repositório].
> - Desfazer: [comando da seção Undo].
> Instalar? (sim / não)

## Verify
- `headroom doctor` passes.
- Start a session through the proxy and confirm the Agent tool exists by dispatching one trivial subagent (issue #4313 reports it hidden; not reproduced).
- `headroom perf` shows requests going through.

## Undo
```bash
headroom unwrap claude
uv tool uninstall headroom-ai
```
Then check that `ANTHROPIC_BASE_URL` and the Headroom hooks are gone from `.claude/settings.local.json`.
