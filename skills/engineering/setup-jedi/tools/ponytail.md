# Ponytail

Rules injected at session start (and into subagents) that push the model to the smallest complete change. Repo and research: `docs/jedi/research/token-tools-ponytail-headroom-caveman.md`.

**Status: no command here has been run yet.** They come from Ponytail's README. Before the first real offer, run Install and Verify once in a scratch folder and fix this file with what actually happened.

## Offer when
- The `ponytail` plugin is not installed. If it is, only add the Testes snippet below when the project lacks it.

## Inform and ask (not a blocker)
- Caveman is installed or accepted in this run. Both inject style rules at session start; a past issue reports them contradicting each other. Ask which one the user wants.

## Requirements
- Claude Code with plugin support. Nothing else: no daemon, no proxy, no `ANTHROPIC_BASE_URL`.

## Install
Plugin commands (the `/plugin` form works inside a session).

```bash
claude plugin marketplace add DietrichGebert/ponytail
claude plugin install ponytail@ponytail
```

Keep the default level `full`. `lite` and `ultra` ask the user to choose or push back on the request, which breaks the "no babysitting" goal.

## AGENTS.md snippet
Its test rule is looser than the Jedi proof rule, so add this under `## Testes` of `AGENTS.md`, and only when the user accepted Ponytail. The skills already defer to `AGENTS.md` for test limits.

```
<!-- setup-jedi: ponytail v1 -->
- Lógica trivial (ligação, texto, config, repasse) não ganha teste: a Prova é `cmd:` com a checagem mais barata. Teste é para ramo, laço, parser, dinheiro, segurança ou fronteira de IO.
- Sempre teste: permissão, dinheiro, deduplicação, importação, transição de estado, webhook. Na dúvida, teste.
<!-- /setup-jedi -->
```

## Confirm
Show this to the user and ask for an explicit yes or no:

> **Ponytail (opcional).** Faz o agente escolher a menor mudança completa e terminar cada resposta dizendo o que pulou.
> - Plugin do Claude Code: 3 hooks, sem processo em segundo plano e sem tocar na API. Modo `full`.
> - Vou acrescentar duas linhas na seção Testes do `AGENTS.md`: lógica trivial usa Prova `cmd:`; permissão, dinheiro, deduplicação, importação, transição de estado e webhook sempre têm teste; na dúvida, teste.
> - O ganho declarado (menos código e menos tokens de saída) vem do fabricante e não foi medido no fluxo do Jedi.
> Instalar? (sim / não)

## Verify
- `claude plugin list` shows `ponytail`.
- After the first ticket, `check_spec.py` and `check_tickets.py` still pass.

## Undo
```bash
claude plugin uninstall ponytail@ponytail
```
Remove the snippet between the `setup-jedi: ponytail` markers from `AGENTS.md`, and run the plugin's `scripts/uninstall.js` to clear the flags it left in `~/.claude`.
