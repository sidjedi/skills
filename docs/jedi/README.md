# Jedi: o framework de skills (fork do Matt Pocock)

Leitura obrigatória para um agente que vá usar, manter ou atualizar estas skills.
Este fork mantém o método do Matt (fatias verticais, grilling, TDD, review em dois eixos) e
acrescenta **rastreabilidade por critério, verificação por script, lotes de tickets e um fechamento de branch**.
Foco: MVPs lançados rápido, **sem microgerenciamento nem babysitting**.

## Rotina: ver se o Matt publicou novidades

Rode de vez em quando, no clone `G:\Antigravity\matt-jedi-skills\skills`:

```bash
git fetch upstream
git rev-list --count jedi..upstream/main        # quantos commits novos o Matt tem
git log --oneline jedi..upstream/main           # quais são
git diff --stat jedi...upstream/main            # que arquivos mudaram
```

Se houver novidade, veja antes o que ele mudou nas skills que nós também alteramos
(`to-spec`, `to-tickets`, `implement`, `implement-spec`, `code-review`, `setup-matt-pocock-skills`):

```bash
git diff jedi...upstream/main -- skills/engineering/<skill>
```

Para trazer, com as suas mudanças já commitadas na `jedi`:

```bash
git checkout jedi
git merge upstream/main     # conflito só onde ele e nós mudamos a mesma linha
git push origin jedi        # depois: npx skills@latest update
```

Manter a `main` do fork como espelho do Matt:

```bash
git checkout main && git merge --ff-only upstream/main && git push origin main && git checkout jedi
```

## 1. O processo, de ponta a ponta

```
projeto grande?  --sim-->  /to-roadmap  ---> docs/roadmap.md (etapas verticais)
                                  |
                                  v  (uma etapa por vez)
ideia / feature  ---> /grill-with-docs ---> /to-spec ---> /to-tickets ---> implementar ---> /finish-spec
                      (afia a ideia)        (US + AC       (fatias          /implement        (fecha a branch,
                                             + Prova)       verticais        ou                 abre o PR)
                                                            P/M/G)           /implement-spec
```

1. **Projeto grande ou novo:** `/to-roadmap` (usa o grilling) grava `docs/roadmap.md`: etapas **verticais**, ordenadas, com status `todo/specced/done`. Projeto pequeno pula esta etapa.
2. **Afinar a ideia:** `/grill-with-docs` (ou `/grill-me` fora de um repo). Para neblina grande demais para uma sessão, `/wayfinder` antes do spec.
3. **Spec:** `/to-spec` (sem entrevista). Cada user story tem id `US-n`; a tabela **Acceptance Criteria** tem `AC-n.n` com uma coluna **Prova** (`test`, `cmd: <comando>` ou `visual: <tela>`).
4. **Tickets:** `/to-tickets` quebra em fatias verticais **pequenas**, cada uma com `**Entrega:** US-…, AC-…` e `**Tamanho:** P|M|G`. Não une fatias para ter menos tickets.
5. **Implementar** (um dos dois):
   - `/implement <tickets…>`: um ou vários tickets pequenos, em sequência, na mesma janela de contexto. Para quando o contexto passa de 200k tokens (pedir `/compact` e chamar de novo).
   - `/implement-spec`: spec inteiro. Agrupa tickets em **lanes** (cadeias sequenciais de ~150k estimados, um subagente por lane), lanes independentes em paralelo, integração sem squash. Termina chamando `code-review` e depois `finish-spec`.
6. **Fechar:** `/finish-spec` roda os scripts, a suíte completa **uma vez**, as checagens visuais em lote, escreve o PR com evidência real e abre o PR.

## 2. Convenções que as skills e os scripts esperam

- Spec: `.scratch/<feature>/spec.md` (tracker local). Tickets: `.scratch/<feature>/issues/NN-<slug>.md`.
- Ticket: linhas `**Blocked by:**`, `**Entrega:**`, `**Tamanho:**`, `**Status:**` e um checkbox por AC (`- [ ] AC-1.1 …`).
- Ao concluir um ticket: `Status: done`, checkboxes marcados e, em `## Registro`/`## Comments`, o commit e **uma linha de prova por AC**:
  `- AC-1.1 -> tests/test_x.py::test_name` ou `- AC-1.2 -> visual: <captura>`.
- Critério **visual** nunca vira teste: é verificado no navegador (skill `browser-harness`) e a captura é a evidência.
- Quem manda no comportamento do projeto é o **`AGENTS.md` do projeto** (comando da suíte, limites de teste, regra visual, simplicidade). As skills ficam genéricas.

## 3. Quando duas skills parecem fazer a mesma coisa

| Situação ambígua | Regra |
|---|---|
| `code-review` × `finish-spec` | `code-review` **julga o código** (Standards + Spec). `finish-spec` **não revisa**: confere registro, provas, suíte e tela, e abre o PR. Rodam em sequência, nunca um dentro do outro. |
| `code-review` por ticket × no fim do spec | Mesma skill. No `/implement` roda a cada ticket (diff pequeno). No `/implement-spec` roda **uma vez** na branch de integração. Não repetir no `finish-spec`. |
| `finish-spec` × `pr` | `pr` só **escreve o corpo** do PR. `finish-spec` junta a evidência, chama `pr` e abre o PR. Não chame `pr` sozinho para fechar um spec. |
| `implement` × `implement-spec` | Poucos tickets ou trabalho linear: `/implement`. Spec inteiro com tickets independentes: `/implement-spec`. `implement-spec` roda o ciclo do `implement` dentro de cada lane. |
| Gate de contexto (`context_gate.py`) × lanes | O gate vale só no `/implement` na sessão principal. Dentro de uma lane vale o orçamento estimado (~150k); o gate é ignorado lá. |
| `to-roadmap` × `wayfinder` × `grill-with-docs` | `wayfinder`: neblina grande, produz decisões. `to-roadmap`: já sabe o rumo, ordena etapas verticais. `grill-with-docs`: afia **uma** ideia/etapa. O `to-roadmap` pode usar o grilling por dentro; não chamar os três para o mesmo assunto. |
| `to-spec` × etapa do roadmap | Uma etapa do roadmap = um spec. Nunca spec de várias etapas. |
| Roadmap × tickets | Roadmap ordena **etapas**. Tickets ordenam **fatias** dentro de um spec. Não duplicar um no outro. |
| `tdd` × verificação visual | `tdd` para comportamento no seam declarado. Visual é navegador. Nunca escrever teste para validar aparência. |
| `triage` × `to-tickets` | `triage` é só para issues **de fora**. Tickets do `to-tickets` já nascem prontos; não triar. |
| Script bloqueia × agente discorda | O agente pode seguir, **registrando** `Script override: <o que e por quê>` no `## Comments` do ticket e avisando no fechamento. Nunca em silêncio. |
| `setup-jedi` × `setup-matt-pocock-skills` | `setup-jedi` prepara o projeto (stack, `AGENTS.md`, glossário, testes, máquina, ferramentas opcionais) e chama o `setup-matt-pocock-skills` por último. O setup do Matt segue dono do tracker, dos labels e de `docs/agents/`. |
| Ferramenta opcional × setup do projeto | Cada uma é oferecida no passo 6 do `setup-jedi`, com confirmação própria, separada do resumo do passo 3. Sem "sim" explícito nada é instalado. Uma regra que só existe por causa de uma ferramenta vai no snippet de `AGENTS.md` do arquivo `tools/<ferramenta>.md`, nunca numa skill genérica. Remover uma ferramenta é apagar o arquivo dela. |
| Ticket antigo (sem `Entrega:`) | Os scripts só **avisam** sobre commit ausente; as checagens rígidas valem para tickets novos. |

## 4. A aplicação ideal

0. Projeto novo ou ainda sem `AGENTS.md`: `/setup-jedi` uma vez (stack, `AGENTS.md`, glossário, testes, máquina). Oferece, uma a uma e com confirmação própria, as ferramentas opcionais de `skills/engineering/setup-jedi/tools/`. Termina chamando o `setup-matt-pocock-skills`. Para mudar o que ela instala, leia `skills/engineering/setup-jedi/DESIGN.md`.
1. Projeto novo e grande: `/to-roadmap` uma vez. Depois, para cada etapa: grilling curto → `/to-spec` (da etapa) → `/to-tickets` → `/implement-spec` (ou `/implement` em lotes) → `/finish-spec` → etapa `done` → próxima.
2. Feature num projeto existente: `/grill-with-docs` → `/to-spec` → `/to-tickets` → implementar → `/finish-spec`.
3. Ajuste pequeno e óbvio: `/implement` direto sobre um ticket ou pedido, sem spec.
4. Fatias sempre **verticais** (nunca "só back-end"). Pequenas, porque o `implement` junta várias numa janela.
5. Autonomia: o líder decide e segue. Pergunta ao usuário só o que é decisão dele (ver `grilling`), nunca "posso continuar?".
6. Testes enxutos: suíte inteira rodada **uma vez** no fim; durante o trabalho só os testes relacionados.

## 5. Scripts

Fonte canônica em `scripts/jedi/` (Python 3, só biblioteca padrão). **O instalador só leva a pasta da skill**, então
cada skill carrega a sua cópia em `skills/engineering/<skill>/scripts/`. Edite sempre em `scripts/jedi/` e rode
`bash scripts/jedi/sync.sh` antes de commitar.

| Script | Copiado em | Faz |
|---|---|---|
| `check_spec.py <feature-dir> [--spec-only]` | to-spec, to-tickets, finish-spec | todo AC tem prova e ticket |
| `check_tickets.py <feature-dir> [--ticket NN] [--stale-visual]` | implement, finish-spec | ticket `done` com `Entrega:` cita commit existente e prova por AC; lista ACs visuais a rever |
| `context_gate.py` | implement | lê `~/.claude/state/context-latest.json` (escrito pela statusline); exit 0 segue, 1 para, 2 sem leitura |

O gate depende da statusline gravar o arquivo (ver o `statusline.sh` do usuário). Sem ele, usar a estimativa por tamanho de arquivos.

## 6. Instalar e atualizar

Instalar a partir do fork, **na branch `jedi`** (a `main` do fork espelha o Matt e não tem as nossas skills):

```bash
npx skills@latest add sidjedi/skills#jedi -a claude-code      # inclua setup-matt-pocock-skills
```

Atualizar o que já está instalado: `npx skills@latest update`. Skills novas: repetir o `add`.
Não instalar o plugin do Matt junto, para não duplicar as skills.


Skills alteradas aqui: `to-spec`, `to-tickets`, `implement`, `implement-spec`, `code-review`. Novas: `to-roadmap`, `finish-spec`, `setup-jedi`.
Ao resolver conflito, preserve as nossas adições e aceite as melhorias dele.
