# skills_v2

Ajustes nas skills de implementação (base: Matt Pocock) com ideias do `tlc-spec-lean`.
Mesmos nomes das originais: ao copiar para o seu repositório, elas **substituem** as originais.

## Skills

| Skill | Mudança em relação à original |
|---|---|
| `to-roadmap` (nova) | grilling -> `docs/roadmap.md`, etapas verticais com status `todo/specced/done` |
| `to-spec` | `US-n`, tabela `AC-n.n` com coluna Prova, lê etapa do roadmap |
| `to-tickets` | `Entrega:` (US/AC), `Tamanho:` P/M/G, não une fatias |
| `implement` | vários tickets por janela, ciclo completo por ticket, gate de 200k tokens |
| `implement-spec` | lanes sequenciais por subagente, merge sem squash, termina em `finish-spec` |
| `code-review` | igual; só acrescenta PASS/FAIL por AC e checagens de registro quando existem ids |
| `finish-spec` (nova) | scripts, suíte uma vez, Browser Harness em lote, `pr` com evidência |

## Scripts (`scripts/`, Python 3, só biblioteca padrão)

Copie a pasta `scripts/` ao lado das skills. As skills a chamam como `<skills-root>/scripts/...`.

- `check_spec.py <feature-dir> [--spec-only]`: todo AC tem prova e ticket.
- `check_tickets.py <feature-dir> [--ticket NN] [--stale-visual]`: ticket `done` com `Entrega:` cita commit existente e prova por AC (tickets antigos só geram aviso).
- `context_gate.py`: lê o tamanho do contexto gravado pela statusline (exit 0 pode seguir, 1 parar, 2 sem leitura).

Os scripts bloqueiam, mas o agente pode passar por cima registrando `Script override: <motivo>` no `## Comments` do ticket.

## Statusline

`~/.claude/statusline.sh` foi alterado para gravar `~/.claude/state/context-latest.json`
(`context_tokens`, usado pelo gate). Backup: `statusline.sh.bak-antes-context-gate`.
O arquivo também guarda `raw_context_window`, para conferir qual campo representa o contexto atual.

## O que o AGENTS.md do projeto precisa dizer (a skill de init, ainda por fazer)

Comando da suíte completa (com paralelismo); limite de testes por AC e só no seam declarado;
verificação visual pelo Browser Harness em vez de teste; simplicidade do código.

## Fora desta rodada

Skill de init do projeto (`AGENTS.md`, symlink `CLAUDE.md`, Browser Harness, `setup-matt-pocock-skills`).
