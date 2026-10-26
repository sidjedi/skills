# Ferramentas de economia de tokens: Ponytail, Headroom e Caveman

Pesquisa feita em 2026-10-25, a partir de fontes primárias: código e instaladores dos repositórios, issues do GitHub e docs oficiais do Claude Code e da API. Nada foi instalado nem executado. Itens sem fonte primária estão marcados como "não verificado".

## Atualização (2026-10-25, após revisão do dono)

Correções e decisões posteriores ao texto abaixo, que continua como foi escrito:

- **Gate:** o `usage` pós-proxy refletir o corpo comprimido é uma diferença de semântica, não um erro comprovado. É o que o modelo de fato recebe. Não medido.
- **Teste do Ponytail:** o conflito é menor que o descrito. A Prova aceita `cmd:` e `visual:`, e o `check_tickets.py` acusa AC sem linha de prova.
- **Tool search (#4313):** o Claude Code 2.1.310 já defere ferramentas por padrão atrás de gateway (docs de MCP), e o Headroom grava `ENABLE_TOOL_SEARCH=true`. Desligar carregaria todas as definições de MCP. A issue segue não reproduzida.
- **Peso das issues:** parte do veredito contra Headroom e Caveman veio de issues abertas, que são relatos não reproduzidos.
- **Decisão:** o que foi decidido sobre cada ferramenta fica registrado nos commits do repositório, não neste texto.

## Resumo

| Ferramenta | Camada | Footprint de instalação | Conflito com RTK | Conflito com context gate | Risco principal | Veredito |
|---|---|---|---|---|---|---|
| Ponytail | Comportamento do modelo: regras de código injetadas no início da sessão e em subagentes | Plugin do Claude Code: 3 hooks, módulo band que grava um CSV por turno (ligado por padrão), flags em `~/.claude`. Reversível | Nenhum (não toca Bash) | Nenhum direto | Regra de teste mais frouxa que as Provas do Jedi; modos lite e ultra pedem decisão ao usuário | Trial opcional, isolado, só modo full |
| Headroom | Proxy de API local: comprime tool results e histórico no corpo da requisição | Python `headroom-ai`; proxy local; `wrap` por sessão, ou `init` durável que grava `ANTHROPIC_BASE_URL` e hooks em `settings.json`. Beacon ligado por padrão | Duas compressões sobre a mesma saída | Alto: o gate lê o `usage` da API, que reflete o corpo já comprimido | Bugs de cache abertos; tool search pode esconder o Agent tool (#4313); exatidão não medida no Jedi | Não instalar agora. Trial com `wrap` |
| Caveman | Três camadas: voz curta (regras), rota nativa opcional (troca saída de ferramenta e roteia a API), Auto e telemetria na nuvem | Plugin: 4 hooks. CLI npm: `ANTHROPIC_BASE_URL` e `ENABLE_TOOL_SEARCH=auto` em `settings.json` quando habilitada. Telemetria ligada por padrão | Rota nativa pode duplicar a compressão; `updatedToolOutput` em Bash provavelmente é ignorado | Rota nativa: sim, lê `usage` pós-proxy. Voz: efeito pequeno | Voz em pt-BR não verificada; subagentes recebem a voz; privacidade | Não instalar. Se quiser a voz: só o plugin, só no chat |

**Recomendação em uma linha:** nenhuma das três entra no passo 5 (Machine) do `setup-jedi` por padrão. Ponytail é o único candidato a trial opcional, fora do setup automático.

---

## Ponytail

Repositório: https://github.com/DietrichGebert/ponytail (MIT)

### 1. Mecanismo

- **Camada:** comportamento do modelo. Não comprime entrada, não comprime saída de ferramenta e não é proxy.
- **Ruleset:** o conteúdo é o `skills/ponytail/SKILL.md`. O hook de início de sessão, `hooks/ponytail-activate.js` (linha 61), injeta esse texto filtrado pelo nível (`hooks/ponytail-instructions.js` linhas 77-92). Também anexa um mapa do repositório gerado por `git ls-files`, com timeout de 3 s e orçamento padrão de 2000 caracteres (`ponytail-activate.js` linhas 66-71; `hooks/ponytail-map.js` linha 16).
- **Subagentes:** `hooks/ponytail-subagent.js` injeta o mesmo ruleset em todo `SubagentStart`. Um filtro opcional, `PONYTAIL_SUBAGENT_MATCHER`, restringe a injeção (linhas 8-11).
- **Por prompt:** `hooks/ponytail-mode-tracker.js` só age em comandos `/ponytail` e em "stop ponytail". No Claude Code não reinjeta a regra a cada turno (linhas 51-157).
- **Regras que importam para o Jedi:**
  - Teste só para lógica não trivial: "Trivial changes need none" (`skills/ponytail/SKILL.md` linha 41).
  - "Be lazy about the solution, never about the change itself" (linha 34).
  - Toda resposta termina com "what you skipped or did not check" (linha 15).
  - Os modos lite e ultra pedem que o agente nomeie uma opção menor e deixe o usuário escolher, ou questione o pedido (linhas 50-52).

### 2. Instalação

- Comandos oficiais: `/plugin marketplace add DietrichGebert/ponytail` e `/plugin install ponytail@ponytail` (README, seção Install).
- Hooks do plugin: `SessionStart`, `SubagentStart` e `UserPromptSubmit`, com timeout de 15 s (`hooks/claude-codex-hooks.json`).
- **Módulo band** (`hooks/claude-band.json`, `hooks/band/register.tsx`): com `userConfig.ledger = true` (`.claude-plugin/plugin.json`), grava uma linha por turno em `~/.config/ponytail/band/<projeto>.csv` e reconstrói `board.html` (`register.tsx` linhas 139-149). O webhook só existe se for configurado e exige https (`hooks/band/metrics.ts` linha 313).
- **Arquivos tocados:** `~/.claude/.ponytail-active` e `~/.claude/ponytail-modes/<hash>` (`hooks/ponytail-runtime.js` linhas 54-66); cópia de `ponytail-statusline.sh` e `.ps1` para `~/.claude` quando há nudge (`ponytail-activate.js` linhas 118-131); flag `~/.claude/.ponytail-statusline-nudged` (linhas 113-134).
- **Não escreve `settings.json`.** Se não houver `statusLine`, só instrui o agente a sugerir a linha (`ponytail-activate.js` linhas 133-153).
- **Daemon:** não. Não altera `ANTHROPIC_BASE_URL`.
- **Reversão:** `/plugin uninstall` mais `scripts/uninstall.js`, que remove flags, config e a linha `statusLine` apenas quando ela é do ponytail (linhas 26-92).

### 3. Economia: claim e evidência

- **Claim do README:** -53% de linhas, -41% de tempo, -26% de custo e -45% de tokens de saída contra sem skill (Opus 5.5, 39 tarefas, 5 runs).
- **Evidência no repo:** `benchmarks/results/2026-10-07-agentic.md`. Mede código entregue e tokens de saída de tarefas em `claude -p` headless. Em 18 tarefas com hidden checks, o ponytail 5 passou 87/90 contra 86/90 sem skill.
- **Limites declarados pelo próprio arquivo:**
  - Bash desligado em todos os braços: mede o que o agente escreve, não a depuração.
  - Carregamento de CLAUDE.md desligado.
  - Execução em pasta temporária, fora de repo.
  - 21 das 39 tarefas medem tamanho de código; "pass" nelas só significa "entregue".
  - Juiz de completude é um LLM.
- O benchmark rodável pelo usuário ainda é issue aberta (#1036). Reprodução independente não está pronta.
- **Não verificado:** economia num fluxo com AGENTS.md, em lanes de subagentes, e em sessões em pt-BR.

### 4. Riscos

- **Cobertura de teste (principal):** o ruleset exige teste só para lógica não trivial (`SKILL.md` linha 41). O `check_spec.py` exige um comando ou teste por AC (`skills/scripts/jedi/check_spec.py` linhas 10, 22). Um AC tratado como trivial pelo agente pode perder o teste de Prova. Não testado.
- **Formatos exatos:** o Ponytail não toca saída de ferramenta nem escrita de arquivo. Os riscos estão no texto que o modelo escreve: comentários "só o porquê" e `shortcut:` (`SKILL.md` linhas 37, 42). Impacto em specs e tickets não verificado. Pt-BR não verificado.
- **Quebra do "sem babysitting":** lite e ultra pedem decisão do usuário (`SKILL.md` linhas 50-52). Nas lanes, usar só full.
- **Cache:** a documentação oficial diz que o SessionStart adiciona contexto "at the start of the conversation, before the first prompt" (code.claude.com/docs/en/hooks). A regra fica em mensagens, não em `tools` ou `system`. Pelas regras de cache da documentação, isso não invalida o prefixo. Injeção de novo no compact. Em regime estacionário a inferência é neutra. Não medido.
- **Contexto:** o SKILL.md tem cerca de 3,5 KB, mais até 2000 caracteres de mapa. Em subagente entra de novo. Isso é em bytes, não em tokens. Não medido.
- **Issues relevantes:**
  - #332 (fechada em 2026-10-03): Ponytail não detectava Caveman e os dois injetavam regras contraditórias. O hook baixado não tem nenhuma referência a Caveman, então a detecção não existe no código atual.
  - #1162 (aberta): sessão com default off apaga o badge de outras sessões.
  - #1283 (aberta): mapa descartado em silêncio se `PONYTAIL_MAP_CHARS` passar de 64 KiB.
  - #1150 (aberta): CRLF no Windows, sem `.gitattributes`.
  - #1229 (aberta): cache do OpenCode. Não se aplica ao Claude Code.
- **Windows:** há `ponytail-statusline.ps1` e testes de hooks (`tests/hooks-windows.test.js`; #774 fechada). A band chama `grep` via `process.run` (`register.tsx` linha 126). Sem `grep` no PATH, o modelo some do board. Inferência, não testada.

### 5. Saúde

- **Licença:** MIT (`LICENSE`; API do repo).
- **Stars:** 175.997 (API, 2026-10-25). Criado em 2026-06-12. Último push em 2026-10-18.
- **Releases:** v5.3.2 (2026-10-16), v5.3.1 e v5.3.0 (2026-10-16), v5.2.0 (2026-10-13), v5.1.1 (2026-10-12). Cadência alta, mas concentrada em duas semanas de outubro.
- **Issues abertas:** 135 (contagem da API, que inclui pull requests).
- **Plataforma:** Windows com statusline em PowerShell; band depende de Node.

---

## Headroom

Repositório: https://github.com/headroomlabs-ai/headroom (Apache-2.0)

### 1. Mecanismo

- **Camada:** proxy de API local. Com `ANTHROPIC_BASE_URL` apontando para ele, comprime tool results, logs, RAG e histórico no corpo da requisição antes de chegar ao provedor (README, "What it does" e "How it works"). A "live zone" comprime só os bytes novos e preserva o prefixo (README, "What's inside"). Os originais ficam em CCR e voltam via `headroom_retrieve`.
- **Saída:** steering opcional de verbosidade, desligado por padrão (`HEADROOM_OUTPUT_SHAPER=1`). Em modo cache ele fica desligado, exceto quando o nível é fixado por variável de ambiente antes do start (`headroom/proxy/output_shaper.py` linhas 177-192 e 262-286).
- **Hook PreToolUse em `Bash|PowerShell`:** não reescreve comando. Só roda `headroom init hook ensure` para garantir que o proxy está de pé (`plugins/headroom-agent-hooks/hooks/hooks.json`; `bin/headroom-hook.sh`).
- **RTK:** `REALIGNMENT/09-phase-G-rtk-observability.md` (cabeçalho, marcado SUPERSEDED) diz que RTK foi removido do Headroom. A justificativa é o "cache hot zone risk on tool_result content compression".

### 2. Instalação

- **Pacote:** `uv tool install --python 3.13 "headroom-ai[all]"` ou `pip install "headroom-ai[all]"`. Requer Python 3.10+ (README, "Get started").
- **Por sessão:** `headroom wrap claude` sobe o proxy, instala o Serena MCP (escopo local em `~/.claude.json`) e lança o Claude com o ambiente. `headroom unwrap claude` reverte (README, "Agent compatibility").
- **Durável:** `headroom init -g claude` (ou `deploy`) grava em `~/.claude/settings.json`:
  - `env.ANTHROPIC_BASE_URL = http://127.0.0.1:<porta>`;
  - `env.ENABLE_TOOL_SEARCH`, respeitando valor do usuário;
  - dois hooks, `SessionStart` (startup|resume) e `PreToolUse` (Bash|PowerShell), com marcador próprio (`headroom/cli/init.py` linhas 206-262; `headroom/providers/claude/install.py` linhas 14-27).
- **Risco de ordem:** se o CLI ou o proxy faltar, `ANTHROPIC_BASE_URL` continua apontando para a porta local. O hook só imprime aviso e sai com 0 (`bin/headroom-hook.sh`, último bloco). Inferência a partir do código; não testada.
- **Telemetria:** o beacon é ligado por padrão e faz POST de contadores e identificadores para `headroom-beacon.headroom-beacon.workers.dev`, sem conteúdo (`docs/content/docs/security-model.mdx`, "The beacon is on by default"). Desligar: `HEADROOM_BEACON=off`, `HEADROOM_TELEMETRY=off` ou `DO_NOT_TRACK=1`.
- **Reversão:** `headroom unwrap claude` e remoção manual das chaves. Não há desinstalação consolidada (issue #748, aberta).
- **Divergência de documentação:** `docs/content/docs/agent-hooks.mdx` diz "15s timeout each", e `plugins/headroom-agent-hooks/hooks/hooks.json` define timeout 60 nos dois hooks.
- **`headroom learn`:** escreve `CLAUDE.local.md` por padrão e `CLAUDE.md` ou `AGENTS.md` por opção (README). No Jedi, `AGENTS.md` é a fonte única; essa opção deve ficar desligada.

### 3. Economia: claim e evidência

- **README, "Proof":** 21%, 57%, 42% e 30% em quatro cenários sintéticos com seed (`benchmarks/index_proof_table.py`). Medido com o tokenizer do provedor. Não são sessões reais.
- **README, "Accuracy":** GSM8K 0,870 para 0,870; TruthfulQA +0,03, dentro do intervalo de confiança com N=100; SQuAD v2 97% com 19% de compressão; BFCL 97% com 32%.
- **Economia de saída:** `headroom output-savings` é estimativa com intervalo, rotulada "estimated" (README). O comentário em `output_shaper.py` linhas 278-280 cita cerca de 700 tokens de saída economizados por turno. Não há benchmark publicado para isso.
- **Medição de terceiro (issue #4260, aberta, 2026-10-18, rotulada como preliminar):** Claude Code headless, `claude-haiku-5-5`, 12 tarefas com 3 runs por braço. Custo -12% (intervalo de 90% de -17% a -7%), pass 32/36 contra 32/36. O contador `/stats` do proxy reportava cerca de $10,61 economizados. Sobre o custo medido nas 36 execuções, a economia real ficou entre $0,05 e $0,08. O autor atribui a maior parte do efeito ao tool search, que adia definições de ferramentas, e não à compressão.

### 4. Riscos

- **Cache (README afirma prefixo byte-idêntico; issues mostram exceções):**
  - #4156 (aberta): a requisição de "away recap" do próprio Claude Code, após cerca de 3 min ociosos, substitui o lineage e reescreve o cache. Relevante para lanes e pausas do Jedi.
  - #4213 (aberta): o modo cache perde o lineage quando a requisição anterior termina em mensagem `user` one-shot, e reescreve o cache a cada prompt (reproduzido com pi).
  - #4275 (aberta): hooks `pre_compress` in-place fazem requisições idênticas perderem o response cache.
  - Regra oficial: "Changes at each level invalidate that level and all subsequent levels" (platform.claude.com/docs/en/build-with-claude/prompt-caching). O steering de verbosidade entra no `system` (`output_shaper.py` linhas 268-276).
- **Context gate (principal):**
  - A documentação do statusline diz que `context_window` vem "from the most recent API response" e que `current_usage` são "Token counts from the last API call" (code.claude.com/docs/en/statusline).
  - O snippet do Jedi soma `input_tokens + cache_creation_input_tokens + cache_read_input_tokens` (`setup-jedi/templates/statusline-context-snippet.txt` linhas 4-7).
  - Com um proxy que reduz o corpo, esses números refletem o corpo enviado, não a transcrição completa. Consequência inferida: o gate dispara mais tarde do que o tamanho real da conversa. Não medido.
  - #4249 (aberta): sessões roteadas recebem respostas com `usage.iterations` de 2 a 3. Efeito no `usage` não verificado.
- **Tool search (bloqueante até verificar):**
  - #4313 (aberta): o tool search server-side esconde as ferramentas Agent, Workflow e AskUserQuestion. O `/implement-spec` depende do Agent tool. Relatado na issue; não reproduzido aqui.
  - #3954 (aberta): ferramentas de Claude in Chrome não são encontradas pelo ToolSearch sob `wrap`. Não verificado para o Browser Harness do Jedi.
  - #2584 (aberta): `mode=token` trava com `ENABLE_TOOL_SEARCH`.
- **Compressão de saída de ferramenta:** pode comprimir logs que o agente precisa ler. O README diz que a linha FATAL sobrevive, e o CCR permite recuperar o original. Efeito em saídas de `check_spec.py` e `check_tickets.py` não verificado.
- **RTK (informado pelo usuário; não verifiquei o repo do RTK):** RTK reduz a saída do comando; o Headroom comprime o mesmo resultado de novo. Não encontrei mecanismo de coordenação no código. Os documentos REALIGNMENT tratam a compressão no proxy como risco de cache.
- **Estabilidade:** #2722 (aberta; `wrap claude` não repara comando desatualizado), #3561 (aberta; sem compressor de conteúdo no path `/v1/messages` nas versões 0.30 a 0.37; status atual não verificado).

### 5. Saúde

- **Licença:** Apache-2.0 (API do repo).
- **Stars:** 77.793. Criado em 2026-01-07. Último push em 2026-10-24.
- **Releases:** v0.41.0 (2026-10-14), v0.40.0 (2026-10-06), v0.39.1 (2026-09-26), v0.39.0 (2026-09-25), v0.38.0 (2026-09-21). Cadência de uma a duas semanas.
- **Issues abertas:** 548 (API, inclui pull requests).
- **Plataforma:** `scripts/install.ps1` existe e `hooks.json` tem entrada `powershell`. O `wrap claude` no Windows não foi verificado; o README cita Windows para o Copilot CLI.

---

## Caveman

Repositório: https://github.com/JuliusBrussee/caveman (Apache-2.0)

### 1. Mecanismo

- **Camada 1, voz:** regras de resposta curta injetadas no início da sessão e nos subagentes (`.claude-plugin/plugin.json` linhas 9-57; `src/hooks/caveman-activate.js` linhas 306-307 e 442). As regras dizem "Payload verbatim: Code blocks unchanged", "Floor: code, commands, paths, numbers and error strings verbatim", "Boundaries: code, comments, commits, PRs, docs written normal" e "Compress the style, not the language" (`src/rules/caveman-activate.md`). A fronteira de docs é instrução ao modelo. Nenhum hook confere.
- **Camada 2, rota nativa** (só com a CLI npm e `caveman enable claude`): para Claude, o `PostToolUse` responde com `hookSpecificOutput.updatedToolOutput = output_replacement` (`packages/cli/src/native-hook-fast.ts` linhas 496-497). O `PreToolUse` só devolve `additionalContext` (linhas 493-495). A rota aponta `ANTHROPIC_BASE_URL` para um gateway local, por padrão `127.0.0.1:8787` (`agents/profiles/claude.json`, bloco `injection`; função `localGatewayEndpoint` no mesmo arquivo).
- **Camada 3, sob demanda:** `caveman-compress` reescreve arquivos de memória (como CLAUDE.md), mantém backup e envia o arquivo ao provedor (README, Privacy).
- **Camada 4, nuvem:** Auto envia o último pedido, CLAUDE.md, memória e @-mentions quando logado (README, Privacy).
- **Telemetria:** a CLI envia estatísticas de uso por padrão. Desligar com `caveman telemetry off` ou `DO_NOT_TRACK=1` (README, Privacy).

### 2. Instalação

- **Plugin:** `claude plugin marketplace add JuliusBrussee/caveman && claude plugin install caveman@caveman` (README). Hooks: `SessionStart`, `SubagentStart`, `UserPromptSubmit` e `SessionEnd`. Escreve `~/.claude/.caveman-active` (`caveman-activate.js` linha 162). Não grava `settings.json`; sem `statusLine`, só sugere (linhas 544-607).
- **CLI:** `npx @caveman-ai/cli@latest` (Node 22.13+). O instalador grava hooks em `settings.json` e só adiciona `statusLine` se não existir. Se existir, imprime NOTE e não sobrescreve (`installer/install.js` linhas 1938-1955).
- **Rota nativa:** `caveman enable claude` grava `ANTHROPIC_BASE_URL` e `_CLAUDE_CODE_ASSUME_FIRST_PARTY_BASE_URL` em `~/.claude/settings.json` (`docs/technical/install-and-update.md` linhas 175-176). A issue #1361 (fechada em 2026-10-25) relata `ENABLE_TOOL_SEARCH=auto` gravado por esse caminho. Não verifiquei em qual release a correção saiu.
- **Reversão:** `npx -y github:JuliusBrussee/caveman -- --uninstall` seguido de `npm uninstall -g @caveman-ai/cli` (`install-and-update.md` linhas 155-178). A própria doc avisa que a rota pode sobrar e cita Remote Control quebrado (`docs/technical/agent-wrapping.md` linhas 218-227). Issue #1040 (fechada): o uninstall deixava `ANTHROPIC_BASE_URL`.
- **Daemon:** sim, para a rota nativa (gateway local e `native.sock`). Não para o plugin de voz.

### 3. Economia: claim e evidência

- **README, "Say less":** 63 para 20 tokens num exemplo único. `/ultracave` 14 e `/megacave` 13, no mesmo exemplo.
- **`docs/HONEST-NUMBERS.md`, medição direta:** `/caveman` corta 3% a mais no mediano contra o controle "Answer concisely."; `/ultracave` corta 35%. Amostra de 10, uma rodada, versão 3.1.0, não reexecutada. O número de 63 para 20 compara com verbosidade sem instrução.
- **Custo das regras:** o README diz cerca de 1.160 tokens de entrada. O HONEST-NUMBERS diz "Not measured yet".
- **README, "Read less":** 33,2% menos tokens de entrada por sessão, em 3 runs por tipo de arquivo, com sessão de agosto em engine antiga. HTML teve 9,9% pior. É medição de compressão de arquivo e rota, não do plugin de voz.
- **README, "Auto":** 54% mais barato, status interim, metade da execução, margem de ±7. `docs/AUTO-BENCHMARK.md` não lido.
- **Adobe Research (arXiv 2606.24083), Elastic e JetBrains:** citados pelo README. Não li as fontes. Não verificado.
- **Blocks:** 397 para 76 tokens em um teste; versão pré-lançamento (rc.5).
- **Warm cache:** "Not yet" (README). Mecanismo não lido.

### 4. Riscos

- **Formatos e pt-BR:** a voz diz "payload verbatim", mas as regras são em inglês e a prosa em pt-BR não foi testada. Não verificado se a voz abrevia prosa em pt-BR de forma aceitável.
- **Subagentes:** o `SubagentStart` injeta a voz em todas as lanes (`caveman-activate.js` linhas 306-307). Relatórios de lane ficariam curtos. Risco baixo para `**Entrega:**` se o formato for explícito, mas não testado.
- **Saída de ferramenta via `PostToolUse`:** a documentação oficial diz que, para ferramentas built-in, o valor de `updatedToolOutput` deve casar com o schema de saída. Bash retorna um objeto com `stdout`, `stderr`, `interrupted` e `isImage`. Se não casar, "a value that doesn't match the tool's output schema is ignored and the original output is used" (code.claude.com/docs/en/hooks, PostToolUse decision control). A rota envia `output_replacement` como string (`native-hook-fast.ts` linha 497). Pela documentação, a substituição em Bash seria ignorada. Não testado. Mesmo quando aplicada, altera só o que o Claude vê; a telemetria captura o original.
- **Cache:**
  - #1361 (fechada): `ENABLE_TOOL_SEARCH=auto` gerou cache miss e custo cerca de 2,5x maior em hosts SDK, segundo a evidência da própria issue.
  - #1364 (aberta, pi): contexto de runtime anexado ao system prompt reescreve o cache a cada prompt. Não é Claude Code, mas é o mesmo tipo de risco de #4213 do Headroom.
- **Context gate:** a voz reduz a saída, que vira entrada nas rodadas seguintes. Efeito pequeno, não medido. A rota nativa lê `usage` pós-proxy, pela mesma inferência do Headroom.
- **Privacidade:** telemetria por padrão; Auto envia conteúdo à nuvem quando logado; `caveman-compress` envia o arquivo ao provedor. Para projeto com dados de cliente, é ponto decisivo.
- **Issues abertas com impacto:** #1020 (`claude -p` por assinatura não comprime), #1279 (upgrade de 2.0.1 para 4.0.1 deixa o shrink desligado), #1366 (CLI instala runtime antigo), #1371 (stats lento). 103 issues abertas no total (API, inclui PRs).

### 5. Saúde

- **Licença:** Apache-2.0 (`LICENSE`, README).
- **Stars:** 114.973. Criado em 2026-04-04. Último push em 2026-10-25 (hoje).
- **Releases:** plugin v4.0.1 (2026-10-13, latest) e v4.0.0 (2026-10-13); CLI `bin-v4.0.2` (2026-10-23) e `bin-v4.0.1` (2026-10-13).
- **Issues abertas:** 103 (API, inclui PRs).
- **Plataforma:** `install.ps1`, `docs/install-windows.md`, `caveman-statusline.ps1` e `src/hooks/install.ps1` existem.

---

## Como se combinam (matriz)

| Camada | Ponytail | Caveman | Headroom | RTK (informado) |
|---|---|---|---|---|
| Regra no início da sessão | Sim (SessionStart) | Sim (SessionStart) | Não | Não |
| Regra em subagentes | Sim (SubagentStart, filtrável) | Sim (SubagentStart) | Herda o ambiente (inferido) | Não verificado |
| Estilo de resposta | Termina com "o que não verifiquei" | Voz curta | Steering opcional (desligado) | Não |
| Código escrito | Mínimo; teste só se lógica | Não | Não | Não |
| Saída de ferramenta | Não | Substitui via PostToolUse na rota nativa (provável no-op em Bash) | Comprime o corpo da requisição | Reescreve o comando |
| `ANTHROPIC_BASE_URL` | Não | Só na rota nativa | Sim (`wrap` ou `init`) | Não |
| Grava `settings.json` | Não | Só com `enable` ou instalador | Só com `init` | Não verificado |

**Sobreposições e incompatibilidades:**

- **Ponytail x Caveman:** duas regras de estilo no mesmo início de sessão e nos mesmos subagentes. A issue #332 relatou contradição; a detecção não existe no código baixado. Não empilham de forma limpa.
- **Caveman nativo x Headroom:** os dois apontam `ANTHROPIC_BASE_URL` e gravam em `settings.json` (`headroom/cli/init.py` linha 210; `installer/install.js` linha 2187). Quem gravar por último vence. Escolher um.
- **Headroom x RTK:** duas compressões sobre a mesma saída. Efeito líquido não medido.
- **Ponytail x RTK, Ponytail x Headroom:** sem sobreposição direta. O Ponytail não toca Bash nem a API.
- **Statusline:** o Jedi exige uma linha que grave `context-latest.json`. Ponytail e Caveman só sugerem `statusLine` quando ela não existe. Se houver mais de uma, a linha precisa encadear os comandos com `&&`, como o próprio uninstall do Ponytail espera (`scripts/uninstall.js` linhas 67-81).

---

## Recomendação para o setup-jedi

**Escolha:** não instalar nenhuma das três no passo 5 (Machine) por padrão. Ponytail como trial opcional, fora do setup automático. Caveman não. Headroom não agora.

**Razões:**

1. O `setup-jedi` diz que hooks só entram quando uma skill exige (`skills/skills/engineering/setup-jedi/SKILL.md` linha 34). Nenhuma das três é exigida.
2. **Gate:** Headroom e a rota nativa do Caveman mudam o `usage` que o statusline lê. O gate passa a medir o corpo enviado, não a conversa (statusline docs; `skills/skills/engineering/implement/scripts/context_gate.py` linhas 45-48).
3. **Formatos:** `check_spec.py` e `check_tickets.py` dependem de linhas exatas (`check_spec.py` linhas 22 e 47). A voz e o Headroom atuam sobre texto e saída de ferramenta. Não testado.
4. **Subagentes:** o Jedi usa lanes. O tool search do Headroom (#4313) pode esconder o Agent tool. Bloqueante até verificar.
5. **Privacidade:** telemetria e Auto do Caveman. Relevante para projetos com dados de cliente.

**Pergunta única para o passo 5, se houver trial:** "Quer testar o modo de código enxuto do ponytail neste projeto? Padrão: não." Se sim: instalar o plugin, `/ponytail default full`, `/ponytail band off`, desligar `ledger` no `userConfig` (caminho exato não verificado), e opcionalmente `PONYTAIL_SUBAGENT_MATCHER` para excluir as lanes.

**Reversão:**

- Ponytail: `/plugin uninstall ponytail@ponytail`; rodar `scripts/uninstall.js`; apagar `~/.config/ponytail/band` se quiser remover o histórico; conferir que a linha `statusLine` não ficou.
- Headroom (se trial): `headroom unwrap claude`; conferir `ANTHROPIC_BASE_URL` e os hooks marcados em `settings.json`.
- Caveman (se alguém instalar): `--uninstall`, `npm uninstall -g @caveman-ai/cli`; conferir `ANTHROPIC_BASE_URL` e `_CLAUDE_CODE_ASSUME_FIRST_PARTY_BASE_URL`.

**Plano de trial mínimo do Ponytail** (num repo descartável, não num Jedi real):

1. Duas specs pequenas, cada uma com 4 ACs, e Prova do tipo `test` ou `cmd`.
2. Rodar `/implement` duas vezes na mesma spec e no mesmo modelo: uma com Ponytail em full, outra sem.
3. Rodar `check_spec.py` e `check_tickets.py` nos dois resultados. Contar testes por AC e ler a última linha de cada resposta. Anotar `context_tokens` do statusline por ticket.
4. Adotar só se: os scripts passam nos dois; nenhum AC ficou sem teste que existiria sem o Ponytail; nenhuma lane pediu escolha ao usuário. Caso contrário, não instalar.

**Plano de trial do Headroom** (se quiser testar depois): `headroom wrap claude` (não `init`), `HEADROOM_BEACON=off`, sem `--learn`, sem `HEADROOM_OUTPUT_SHAPER`, modo cache. Comparar `context_tokens` do statusline com o tamanho real da transcrição. Verificar se o Agent tool aparece (#4313). Abortar se sumir.

---

## Não verificado

- Voz do Caveman em pt-BR.
- `updatedToolOutput` com string em Bash (provável no-op pela documentação; não testado).
- Ordem de combinação de `updatedInput` entre hooks paralelos. A documentação diz que hooks do mesmo evento rodam em paralelo; a regra de merge de `updatedInput` não foi encontrada.
- Efeito real do proxy sobre o statusline e sobre o gate.
- RTK: o repo não foi lido; os fatos sobre RTK vêm do usuário.
- Browser Harness sob proxy.
- Caminho exato para desligar o `ledger` do Ponytail.
- Números do Adobe, Elastic, JetBrains e do Auto.
- Mecanismo do "warm cache" do Caveman.

---

## Fontes

**Ponytail** (https://github.com/DietrichGebert/ponytail, branch main): README.md; INSTALL.md; after-install.md; .claude-plugin/plugin.json; .claude-plugin/marketplace.json; hooks/claude-codex-hooks.json; hooks/claude-band.json; hooks/ponytail-activate.js; hooks/ponytail-mode-tracker.js; hooks/ponytail-subagent.js; hooks/ponytail-runtime.js; hooks/ponytail-config.js; hooks/ponytail-instructions.js; hooks/ponytail-map.js; hooks/ponytail-statusline.sh; hooks/band/register.tsx; hooks/band/metrics.ts; scripts/uninstall.js; skills/ponytail/SKILL.md; benchmarks/results/2026-10-07-agentic.md; package.json.

**Headroom** (https://github.com/headroomlabs-ai/headroom, branch main): README.md; .claude-plugin/marketplace.json; plugins/headroom-agent-hooks/hooks/hooks.json; plugins/headroom-agent-hooks/bin/headroom-hook.sh; plugins/headroom-agent-hooks/README.md; headroom/cli/init.py; headroom/providers/claude/install.py; headroom/proxy/output_shaper.py; headroom/telemetry/beacon.py; docs/content/docs/agent-hooks.mdx; docs/content/docs/security-model.mdx; REALIGNMENT/09-phase-G-rtk-observability.md.

**Caveman** (https://github.com/JuliusBrussee/caveman, branch main): README.md; INSTALL.md; install.sh; install.ps1; installer/install.js; installer/lib/settings.js; installer/lib/host-hooks.js; .claude-plugin/plugin.json; src/hooks/caveman-activate.js; src/hooks/README.md; src/rules/caveman-activate.md; packages/cli/src/native-hook-fast.ts; agents/profiles/claude.json; docs/HONEST-NUMBERS.md; docs/technical/install-and-update.md; docs/technical/agent-wrapping.md.

**Issues do GitHub** (consultadas em 2026-10-25):
- Ponytail: #332, #1036, #1150, #1162, #1229, #1283, #774.
- Headroom: #748, #2584, #2722, #3561, #3954, #4156, #4213, #4249, #4260, #4275, #4313.
- Caveman: #947, #1020, #1040, #1279, #1361, #1364, #1366.

**Documentação oficial:**
- https://code.claude.com/docs/en/statusline (campos `context_window` e `current_usage`).
- https://code.claude.com/docs/en/hooks (eventos; `updatedToolOutput` em PostToolUse; precedência `deny > defer > ask > allow` em PreToolUse; execução paralela; `additionalContext` no SessionStart).
- https://platform.claude.com/docs/en/build-with-claude/prompt-caching (hierarquia tools, system, messages; campos de `usage`).

**Jedi (repositório local, G:\Antigravity\matt-jedi-skills\skills):**
- skills/skills/engineering/setup-jedi/SKILL.md (passo 5, linhas 29-34).
- skills/skills/engineering/setup-jedi/templates/statusline-context-snippet.txt.
- skills/skills/engineering/implement/scripts/context_gate.py.
- skills/skills/engineering/implement/SKILL.md (linha 18).
- skills/scripts/jedi/check_spec.py (linhas 10, 22, 47).
- skills/docs/jedi/README.md (linhas 54-58, 78).
- skills/CLAUDE.md (linha 26, regra de travessão).

**Secundárias** (apenas citadas pelo README do Caveman; não lidas): Adobe arXiv 2606.24083; Elastic Search Labs; blog da JetBrains.
