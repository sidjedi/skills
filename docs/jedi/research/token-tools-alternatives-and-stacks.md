# Alternativas e stacks para reduzir tokens no Claude Code

Data da pesquisa: 2026-10-25. Escopo: ferramentas além de Ponytail, Headroom e Caveman (essas três estão em outro documento, `token-tools-ponytail-headroom-caveman.md`).

Método e convenções:
- Fontes primárias: docs oficiais do Claude Code (code.claude.com), docs da API (platform.claude.com), README e código dos repositórios, e dados da GitHub API consultados em 2026-10-25. Nenhuma fonte secundária (blog, vídeo, Reddit) foi usada.
- Referências entre colchetes (ex.: [S3]) apontam para a seção "Fontes" no fim.
- Número de fornecedor aparece como "claim do fornecedor", sem reprodução. Número medido na sua máquina aparece como "medido localmente". O que não consegui comprovar aparece como "não verificado".
- Saúde do repositório: estrelas, último push e issues abertas vêm da GitHub API em 2026-10-25. Estrelas não são sinal de qualidade; serviram só para descartar projeto morto.

---

## 1. Resumo executivo

A maior parte do ganho disponível hoje está em configuração nativa do Claude Code (escopo de MCP, effort, caps de leitura e de saída) e em medir antes de instalar qualquer coisa. Ferramenta de terceiro só se justifica para exploração de repositório grande. As que mexem no hook de Bash entram em conflito com o RTK.

Top 5, ordenado por (benefício esperado) / (risco para o fluxo Jedi):

1. **Escopo de MCP com recursos nativos.** Benefício: alto potencial, ainda não medido. Risco: baixo. O tool search já vem ligado por padrão, então as definições dos MCP entram sob demanda [S2]. Os 229.8k que aparecem como "deferred" no seu `/context` provavelmente não são custo recorrente, porque a doc diz que na inicialização entram só nomes e instruções do servidor [S2]. Isso precisa ser confirmado. Ação: desligar por projeto os connectors que o projeto não usa (`/mcp` ou `disableClaudeAiConnectors`) e conferir o `/context` em sessão nova.
2. **Medir antes de mudar.** Benefício: pré-requisito para provar qualquer saving. Risco: baixo. Use `/context`, `/usage`, o campo `prompt_cache` do statusline, `rtk gain`, e `claude -p --output-format json` [S10, S16, S17]. Evite `ccusage statusline` porque disputa a única chave `statusLine` com o escritor de `context-latest.json`.
3. **Language server oficial** (plugins `pyright-lsp` ou `typescript-lsp`, marketplace oficial). Benefício: médio a alto, porque o agente navega por símbolo em vez de grep em loop e recebe erros de tipo logo após editar [S15]. Risco: baixo. Exige o binário no PATH. Não roda em cloud sessions [S15].
4. **Config enxuta nativa.** Use `effortLevel` e não `MAX_THINKING_TOKENS` (que não se aplica a Sonnet 5 e posteriores) [S1, S5]. Coloque caps em `CLAUDE_CODE_FILE_READ_MAX_OUTPUT_TOKENS` e `MAX_MCP_OUTPUT_TOKENS`. Avalie `autoMemoryEnabled` e `disable-model-invocation` nas skills manuais. Benefício: médio. Risco: baixo a médio, porque skill que o agente invoca sozinho deixa de ser invocada se você desligar a descoberta automática [S8].
5. **codegraph como trial de exploração** (ou Serena em monorepo), fora das lanes. Benefício incerto: o fornecedor claim 62% menos tokens processados e 44% mais barato em média [T10], mas o próprio README documenta cerca de 80% mais contexto residente ao fim de sessões multi-turn (VS Code: 67k contra 18k) [T10]. Risco: médio, porque esse contexto residual pesa direto no gate de 200k.

Fora do top 5, de propósito:
- **context-mode**: também intercepta Bash via PreToolUse, como o RTK. Conflito provável, não testado. Licença Elastic License 2.0, que é source-available e não open source OSI [T7]. Trial só em projeto descartável.
- **rtk-proxy** (daemon do próprio RTK): altera o payload da API e pode mudar o número que o gate lê. Licença BUSL-1.1 [T2]. Trial só em projeto descartável.
- **claude-mem**: o instalador pede login numa conta do fornecedor e oferece observer hospedado [T12]. Instala hooks em toda tool call. Não recomendado.
- **claude-context**: exige Zilliz Cloud e chave OpenAI, ou seja, o código sai da máquina [T9].
- **LLMLingua** e **claude-code-router**: não se encaixam no Claude Code com Sonnet 5.5 e prompt caching (ver seção 3).

Stack inicial recomendada: **Minimal** (seção 5).

---

## 2. Tabela de todas as opções

Legenda do verdict: adopt (adotar), trial (testar em projeto controlado com medição), skip (não usar agora).
"Conflito RTK" avalia o hook de Bash. "Conflito gate" avalia o número de `context_tokens` que o `context_gate.py` lê.

| Categoria | Ferramenta | Camada | Footprint | Conflito RTK | Conflito gate | Verdict |
|---|---|---|---|---|---|---|
| MCP | Tool search (`ENABLE_TOOL_SEARCH`, default ligado) [S1, S2] | Config nativa | env ou settings | Nenhum | Baixo (reduz definições) | adopt (já ativo, confirmar) |
| MCP | `/mcp` toggle por projeto (`disabledMcpServers`) [S2] | Config nativa | `~/.claude.json` | Nenhum | Baixo | adopt |
| MCP | `disableClaudeAiConnectors` / `ENABLE_CLAUDEAI_MCP_SERVERS=false` [S2, S3] | Config nativa | settings ou env | Nenhum | Baixo | adopt por projeto |
| MCP | `alwaysLoad` por servidor, `_meta.anthropic/alwaysLoad` por tool [S2] | Config nativa | `.mcp.json` | Nenhum | Baixo | trial (só para servidor próprio) |
| Output | `MAX_MCP_OUTPUT_TOKENS` (default 25000) [S1] | Config nativa | env | Nenhum | Reduz picos | adopt se houver MCP com payload grande |
| Input | `CLAUDE_CODE_FILE_READ_MAX_OUTPUT_TOKENS` (default 25000) [S1] | Config nativa | env | RTK não cobre Read, Grep nem Glob [T1] | Reduz picos | trial |
| Output | `bashOutputMaxChars` / `BASH_MAX_OUTPUT_LENGTH` [S1, S3] | Config nativa | settings ou env | Sobrepõe o RTK | Reduz picos | trial (só se o RTK não bastar) |
| Model | `effortLevel` / `CLAUDE_CODE_EFFORT_LEVEL` / `/effort` [S1, S3, S5] | Config nativa | settings ou env | Nenhum | Nenhum direto | trial |
| Model | `MAX_THINKING_TOKENS` [S1, S5] | Config nativa | env | Nenhum | Nenhum | skip para Sonnet 5.5 (modelo adaptativo ignora o budget) |
| Cache | `CLAUDE_CODE_PROMPT_CACHE_TTL`, `ENABLE_PROMPT_CACHING_1H`, `promptCacheTtl` [S1, S3, S4] | Config nativa | env ou settings | Nenhum | Nenhum | decidir pelo billing (ver seção 4) |
| Memory | `autoMemoryEnabled` / `CLAUDE_CODE_DISABLE_AUTO_MEMORY` [S1, S3, S7] | Config nativa | settings ou env | Nenhum | Reduz injeção inicial | trial |
| Memory | `claudeMdExcludes`, CLAUDE.md abaixo de 200 linhas [S3, S7] | Config nativa | settings e arquivo | Nenhum | Reduz base | adopt (higiene) |
| Memory | `/compact` com instruções e seção "Compact instructions" no CLAUDE.md [S5] | Config nativa | CLAUDE.md | Nenhum | Compacta quando você manda | adopt |
| Memory | `autoCompactEnabled`, `idleCompaction`, `CLAUDE_CODE_AUTO_COMPACT_WINDOW` [S3, S11, S12] | Config nativa | settings ou env | Nenhum | Ver nota: o gate usa tokens absolutos | manter padrão, medir |
| Output style | `outputStyle` (Concise, Explanatory, Learning, Proactive) [S6, S3] | Config nativa | settings | Nenhum | Nenhum no número; muda o formato | trial (não em artefatos de formato exato) |
| Skills | `disable-model-invocation: true` e `skillOverrides` [S8] | Frontmatter ou settings | SKILL.md | Nenhum | Tira descrição do contexto | trial (só skills manuais) |
| Skills | `CLAUDE_CODE_DISABLE_BUNDLED_SKILLS` [S1] | Config nativa | env | Nenhum | Reduz base | trial |
| Subagent | `CLAUDE_CODE_SUBAGENT_MODEL` e `_FORCE` [S1, S9] | Config nativa | env | Nenhum | Nenhum | trial sem FORCE (FORCE mudaria as lanes) |
| Hooks | `PostToolUse` com `updatedToolOutput` (hook próprio) [S13] | Hook | settings hooks | Conflito se outro hook editar a mesma saída | Reduz o que entra | trial (Jedi deixa hooks quietos) |
| Measure | OpenTelemetry nativo (`claude_code.token.usage`, `claude_code.cost.usage`) [S14] | Medição | env + exporter | Nenhum | Nenhum | adopt para medir (sem `OTEL_LOG_RAW_API_BODIES`) |
| Measure | `/context`, `/usage`, statusline com `prompt_cache` e `context_window` [S10, S11, S17] | Medição | nativo | Nenhum | Usa a mesma fonte do gate | adopt |
| Measure | `ccusage` (MIT em `apps/ccusage`) [T16] | Medição | `bunx` ou `npx` | Nenhum | Conflito só se usar `statusline` | adopt (só terminal) |
| Measure | `Claude-Code-Usage-Monitor` (MIT) [T17] | Medição | pip ou uv | Nenhum | Nenhum | trial (alternativa ao ccusage) |
| Output | RTK (`rtk` CLI + hook de Bash) [T1, T3] | Output, Bash | binário + hook PreToolUse | n/a | Baixo | adopt (verificar edição e versão, ver seção 3) |
| Output | RTK proxy (`rtk claude`, daemon) [T2] | API | daemon local, BUSL-1.1 | Mesmo dono, porém outra camada | Alto (altera payload e usage) | trial em projeto descartável |
| Output | context-mode (ELv2) [T7] | Output, memória de sessão | plugin: 11 tools MCP, 6 hooks, SQLite | Conflito provável (PreToolUse em Bash) | Reduz ocupação, não testado | trial isolado |
| Output | LLMLingua (MIT) [T13] | Compressão de prompt | lib Python | n/a | Não se integra ao Claude Code | skip |
| Routing | Claude Code Router (MIT) [T14] | Gateway de modelos | processo local | n/a | Altera cache e modelo | skip |
| Retrieval | LSP oficial (`pyright-lsp`, `typescript-lsp`) [S15] | Retrieval por símbolo | plugin + binário no PATH | Nenhum | Baixo | adopt (TS ou Python) |
| Retrieval | Serena (GPL-3.0-or-later na app, MIT no SolidLSP) [T8] | Retrieval por símbolo + memória | `uv tool` + MCP + LSPs | Nenhum | Médio (corpos de símbolo entram) | trial (monorepo) |
| Retrieval | codegraph (MIT) [T10] | Grafo de código pré-indexado | CLI + MCP + SQLite local | Nenhum | Alto (residual documentado) | trial (exploração) |
| Retrieval | ast-grep MCP (MIT) [T15] | Busca e reescrita por AST | `ast-grep` + `uv` + MCP | Nenhum | Baixo | trial (refactor) |
| Retrieval | claude-context (MIT) [T9] | Busca semântica vetorial | MCP + Zilliz Cloud + OpenAI | Nenhum | Baixo, mas dados saem da máquina | skip |
| Retrieval | graphify (Apache-2.0) [T11] | Grafo de conhecimento | pip (`graphifyy`) + hook opcional | Nenhum | Médio | skip para código |
| Retrieval | Aider repo map (conceito) [T19] | Mapa do repo com token budget | conceito, sem integração | n/a | Baixo | concept (gerar mapa curto manualmente) |
| Memory | Auto memory oficial (`MEMORY.md`) [S7] | Memória nativa | arquivo | Nenhum | Carrega 200 linhas ou 25KB por sessão | adopt (configurar) |
| Memory | claude-mem (Apache-2.0) [T12] | Memória entre sessões | plugin, hooks em toda tool, worker Bun, SQLite e Chroma | Nenhum direto | Injeção no SessionStart | skip |
| Memory | planning-with-files (MIT) [T18] | Planejamento em arquivo | skill e hooks por turno | Nenhum | Injeta contexto a cada turno | skip (o Jedi já tem spec e tickets) |
| MCP | Gateways e agregadores de MCP | Roteamento de MCP | variado | n/a | n/a | não verificado: não achei projeto primário que supere o tool search oficial |

---

## 3. Por categoria

### 3.1 Compressão de saída de shell (RTK e alternativas)

- **RTK, o que você já tem.** O hook de Claude Code reescreve o comando de Bash para a versão filtrada [T3]. Medido localmente: `rtk gain` mostra 9423 comandos e 83.4% de tokens economizados (21.0M de 25.2M de entrada), com a ressalva de que essa contagem é estimativa do próprio RTK. A instalação local é a 0.37.2, e a última release oficial é a v1.0.1, de 2026-10-14 [T6]. Vale atualizar e confirmar a edição: o README diz que a edição `rtk` completa tem engine de compressão sob BUSL-1.1, e a `rtk-oss` tem só Apache-2.0 e não tem engine [T1].
- **Limitação documentada:** o hook só dispara em Bash. Read, Grep e Glob não passam por ele. Para leitura grande, use o cap `CLAUDE_CODE_FILE_READ_MAX_OUTPUT_TOKENS` [S1] ou um hook `PostToolUse` com `updatedToolOutput` [S13].
- **Dependência de `jq`:** a doc do hook Claude diz que ele exige `jq` e sai em silêncio se `jq` faltar [T3]. Nesta máquina, `jq` não aparece no PATH do bash, mas o `rtk gain` mostra 9423 comandos filtrados. Então o hook da sua versão funciona por outro caminho (não verificado qual). Confirme com `rtk gain --history` depois de um comando novo, e rode `rtk bypass <cmd>` quando precisar do output bruto [T1].
- **rtk-proxy (mesmo dono, outra camada).** Daemon local que fica entre o Claude Code e a API, comprime payload de tool_result e, opcionalmente, alinha breakpoints de cache [T2]. A doc diz que comprime payload e remove bytes que o modelo não usa [T1]. Riscos que eu não consigo afastar só com a doc: (a) o payload enviado muda, então o prefixo de cache pode mudar; (b) o número de `usage` que o statusline lê passa a refletir o payload comprimido, e não o que o Claude Code montou; isso afeta o gate (inferência, não testado). Licença BUSL-1.1, que converte para Apache-2.0 em 2030-09-09 [T2]. Verdict: trial só em projeto descartável, medido com `rtk gain`.

### 3.2 Compressão de contexto e proxies de API

- **context-mode.** Sandboxa a saída de tools, indexa em SQLite FTS5 e restaura estado após compaction [T7]. Traz 11 tools MCP e hooks PreToolUse, PostToolUse, UserPromptSubmit, PreCompact, SessionStart e Stop [T7]. O README reporta redução de 95% a 100% em payloads de exemplo (claim do fornecedor; a tabela cita BENCHMARK.md, que não abri). Conflito: ele intercepta Bash, como o RTK. A doc do Claude Code diz que hooks de um mesmo evento rodam em paralelo e não descreve como `updatedInput` de dois hooks se combina [S13]. Então o conflito é provável e precisa de teste. Licença: Elastic License 2.0, source-available, e o próprio README diz que não é MIT [T7]. 356 issues abertas [T6]. Verdict: trial isolado, sem RTK no mesmo projeto.
- **rtk-proxy.** Ver 3.1.
- **LLMLingua (Microsoft, MIT).** Comprime prompt com um modelo pequeno que remove tokens não essenciais; o README fala em "up to 20x" (claim do fornecedor, em contexto de prompt compression) [T13]. É biblioteca Python (`pip install llmlingua`) que você integra no próprio pipeline de API [T13]. Não existe ponto de integração no Claude Code que comprima o prompt inteiro antes do envio. Verdict: skip para este setup.
- **Claude Code Router (MIT, 37.8k estrelas, último push 2026-10-10).** Gateway local que roteia para outros provedores e mostra custo estimado [T14]. Não comprime. Ao trocar de modelo, a doc mostra que o cache do Claude Code é invalidado [S4]. Verdict: skip, a não ser que você precise de outro provedor.
- **Caching proxies.** A doc diz que o cache depende do gateway quando há `ANTHROPIC_BASE_URL` [S4]. Um proxy de cache é um risco novo, não um ganho novo, enquanto a API nativa já cacheia. Verdict: skip.
- **Headroom.** Coberto no outro documento.

### 3.3 Controle de verbosidade e output style

- O nativo `outputStyle` tem Default, Proactive, Concise, Explanatory e Learning. Estilo customizado aceita `keep-coding-instructions: true` para manter as instruções de engenharia [S6]. Trocar de estilo no meio da sessão não quebra o cache, porque as instruções entram como mensagem [S4].
- Para o Jedi, o risco é o formato: skills dependem de saída exata (tabela de AC, linhas `AC-1.1 -> test`, PR body) [contexto do usuário]. Estilo que corta palavras pode afetar isso. Verdict: trial só em conversa livre, não em artefato de formato exato.
- Não verificado: se o output style muda o comportamento dos subagents. A doc diz que o subagent carrega CLAUDE.md, a não ser com `omitClaudeMd` [S9], mas não diz nada sobre estilo.

### 3.4 Navegação e recuperação de código

- **LSP oficial (adopt para TypeScript ou Python).** Plugins `pyright-lsp` e `typescript-lsp` no marketplace oficial da Anthropic. Dão "go to definition" e diagnósticos automáticos após edição [S15]. A doc diz que isso substitui um grep seguido de leitura de vários arquivos [S5]. Binário no PATH (no Windows, confira com `Get-Command`) [S15].
- **Serena (trial, monorepo).** Toolkit MCP com ferramentas por símbolo, edição simbólica e memória [T8]. Instalação via `uv tool install -p 3.13 serena-agent` e `serena init`; o README pede para não instalar via marketplace de MCP [T8]. O README diz que as ferramentas são "much more token-efficient" (claim do fornecedor, não medido) [T8]. Não verificado: quais arquivos `serena init` cria no projeto. Licença mista: GPL-3.0-or-later na aplicação e MIT no SolidLSP [T8]. Saúde: 30.7k estrelas, último push 2026-10-20, 122 issues abertas [T6].
- **codegraph (trial, exploração).** Grafo de símbolos pré-indexado, local em SQLite, MCP para Claude Code e outros [T10]. Pelos números do fornecedor: 2 tools contra 28 no VS Code, 77% menos tokens, 71% mais barato (Opus 4.8 headless, sete repositórios) [T10]. Mesmo README: ao fim de sessões multi-turn, o contexto residente é cerca de 80% maior (67k contra 18k no VS Code) [T10]. Como o gate conta esse contexto, o gate dispara antes. Telemetria é anônima, pergunta na instalação, e pode ser desligada com `codegraph telemetry off` ou `DO_NOT_TRACK=1` [T10]. Licença MIT, último push 2026-10-24, 529 issues abertas [T6]. Verdict: trial só fora das lanes, medindo o gate.
- **ast-grep MCP (trial, refactor).** MCP que faz busca e reescrita por padrão de AST, exige o binário `ast-grep` e `uv` [T15]. MIT, 484 estrelas, último push 2026-10-22 [T6]. Útil para renomear em massa com saída pequena.
- **claude-context (skip).** Busca semântica com Milvus/Zilliz Cloud e embeddings da OpenAI [T9]. O README reporta "~40% token reduction" em avaliação própria, sem reprodução (claim do fornecedor) [T9]. Dados de código saem da máquina e há duas chaves para gerenciar.
- **graphify (skip para código).** Grafo de conhecimento; o README traz "71.5x fewer tokens per query" em um corpus misto que inclui papers e imagens (claim do fornecedor, não representa código) [T11]. A extração usa Claude, então tem custo de build [T11]. Atenção: o pacote PyPI é `graphifyy`, com dois y. Confirme no PyPI antes de instalar [T11].
- **Aider repo map (concept).** O mapa do repo tem token budget, default de 1k tokens, controlado por `--map-tokens` [T19]. Não é componente do Claude Code. A ideia útil é gerar um mapa curto do repo e colocá-lo em `AGENTS.md`.

### 3.5 Memória entre sessões e handoff

- **Auto memory oficial (adopt, configurar).** `MEMORY.md` é índice carregado em toda sessão, com as primeiras 200 linhas ou 25KB; os arquivos de tópico são lidos sob demanda [S7]. Desligue com `autoMemoryEnabled: false` ou `CLAUDE_CODE_DISABLE_AUTO_MEMORY=1` se o projeto já tem spec e tickets [S3, S1].
- **Memória do Jedi.** Specs, tickets e AGENTS.md já fazem o papel de handoff. Esses arquivos são a memória canônica, e memória paralela vira fonte de divergência.
- **claude-mem (skip).** Apache-2.0, 103k estrelas, último push hoje, 98 issues abertas [T6, T12]. Problemas para este setup:
  - Instala hooks em SessionStart, UserPromptSubmit, PreToolUse, PostToolUse, Stop e SessionEnd, todos chamando `claude-mem hook claude-code <event>` [T12]. Ou seja, roda em toda tool call.
  - O instalador pede login numa conta do fornecedor e oferece um observer hospedado com trial de 30 dias; o README diz que, depois do trial, a memória cai para o plano Anthropic, a não ser que você assine [T12]. Para evitar, use `--provider` explícito ou `CLAUDE_MEM_ONLINE_OPTIN=false` [T12].
  - O README tem uma seção sobre um token cripto de terceiro, com endereço de contrato [T12]. Não é análise técnica, mas é um sinal de governança que vale checar (não verificado de forma independente).
  - "~10x token savings" para a busca em camadas é claim do fornecedor, não medido [T12].
- **planning-with-files (skip).** Mantém `task_plan.md`, `findings.md` e `progress.md` e injeta contexto por hooks de ciclo de vida [T18]. Os "3 out of 3 blind A/B wins" são autorreportados [T18]. Sobrepõe o Jedi.

### 3.6 Overhead de MCP

- **O que o oficial já faz.** Tool search é o padrão. Só nomes e instruções do servidor entram na inicialização. `ENABLE_TOOL_SEARCH=auto` carrega upfront enquanto as definições somarem menos de 10% da janela, e `false` carrega tudo [S2, S1]. Tool description deferida é cortada em 16.384 caracteres, e instruções de servidor em 4.096 [S2].
- **Controle por projeto.** `/mcp` liga e desliga servidores por projeto, gravando em `disabledMcpServers` no `~/.claude.json` [S2]. Para connectors do claude.ai: `disableClaudeAiConnectors: true` (vale em qualquer escopo de settings), `ENABLE_CLAUDEAI_MCP_SERVERS=false` para a sessão, `deniedMcpServers` (gerenciado) e o toggle por connector em `/mcp` [S2, S3].
- **Mudança de MCP no meio da sessão.** Só invalida cache quando as tools estão carregadas upfront, o que não é o caso com tool search ligado [S4]. Ainda assim, faça a mudança no início da sessão.
- **Gap real.** Não há allowlist oficial por projeto para connectors do claude.ai. Há desligar tudo, desligar um por um pelo `/mcp`, e bloquear por política gerenciada. Para o seu caso (Higgsfield, Figma, Drive e outros), o toggle por projeto cobre a necessidade.
- **Gap de medição.** A doc diz que o `/context` mostra "(deferred)" ou "(loaded on-demand)" [S2], mas não diz se o número de 229.8k entra no custo por turno. Confirmar com teste (seção 6).
- **Gateways de MCP de terceiros.** Não encontrei projeto primário e ativo que resolva isso melhor que o tool search oficial. Verdict: não verificado, não recomendo busca adicional sem um problema concreto.

### 3.7 Ganhos nativos gratuitos

Ver seção 4.

### 3.8 Observabilidade

- **Nativo primeiro.** `/context` dá o breakdown por categoria e sugestões; `/usage` dá custo, limite e cache hit ratio da sessão; o statusline expõe `context_window` e `prompt_cache` [S10, S11, S17].
- **OpenTelemetry (adopt para medir).** Métricas `claude_code.token.usage` e `claude_code.cost.usage`, spans `claude_code.tool` e eventos `claude_code.api_request` [S14]. Exporters `otlp`, `prometheus`, `console` e `none` [S14]. Mantenha `OTEL_LOG_RAW_API_BODIES` desligado: ele grava o histórico inteiro da conversa [S14]. `OTEL_LOG_TOOL_DETAILS` grava comandos e caminhos, então ligue só se precisar [S14].
- **ccusage (adopt, terminal).** MIT no pacote `apps/ccusage` (o repositório raiz está como NOASSERTION por ser monorepo) [T16]. Comandos: `ccusage claude daily`, `ccusage blocks`, `--json`, `--instances` [T16]. O subcomando `statusline` é Beta e disputaria a chave statusLine [T16]. Não instalado no PATH desta máquina (verificado).
- **Claude-Code-Usage-Monitor (trial).** MIT, 8.8k estrelas, último push 2026-07-05 [T17]. Alternativa se o ccusage não servir.

---

## 4. Ganhos gratuitos nativos (só configuração)

Tudo abaixo vem da documentação oficial. "Cuidado com Jedi" indica onde isso pode afetar o fluxo.

| Configuração | Onde se define | Efeito documentado | Cuidado com Jedi | Fonte |
|---|---|---|---|---|
| `ENABLE_TOOL_SEARCH` (unset, `auto`, `auto:N`, `false`) | env ou `settings.json` `env` | Tool search deferido por padrão; `auto` carrega upfront abaixo de 10% da janela | Não force `false` sem medir | https://code.claude.com/docs/en/mcp (Configure tool search) |
| `disabledMcpServers` (via `/mcp`) | `~/.claude.json`, por projeto | Não conecta o servidor | Não afeta outros projetos | https://code.claude.com/docs/en/mcp (Disable a server without removing it) |
| `disableClaudeAiConnectors: true` | settings (qualquer escopo) | Desliga connectors do claude.ai que o Claude Code busca | `true` em qualquer escopo vence um `false` de projeto | https://code.claude.com/docs/en/settings-reference#disableclaudeaiconnectors |
| `ENABLE_CLAUDEAI_MCP_SERVERS=false` | env | Mesmo efeito, para a sessão | Útil em script | https://code.claude.com/docs/en/mcp (Disable claude.ai connectors) |
| `alwaysLoad` (`.mcp.json`) e `_meta["anthropic/alwaysLoad"]` | `.mcp.json` ou tool | Força tools upfront | Só use para servidor seu e poucas tools | https://code.claude.com/docs/en/mcp (Exempt a server from deferral) |
| `MAX_MCP_OUTPUT_TOKENS` (default 25000, aviso acima de 10000) | env | Limita resposta de tool MCP | Pode cortar resposta útil de Figma ou Drive | https://code.claude.com/docs/en/env-vars |
| `CLAUDE_CODE_FILE_READ_MAX_OUTPUT_TOKENS` (default 25000) | env | Limite de leitura de arquivo | `allow_large` pode passar do limite | https://code.claude.com/docs/en/env-vars |
| `bashOutputMaxChars` (4000 a 128000) e `BASH_MAX_OUTPUT_LENGTH` (default 30000 chars, máximo 150000) | settings ou env (settings vence) | Quanto de saída de Bash entra inline; o resto vai para arquivo | Com RTK, quase não muda nada; não baixe sem medir | https://code.claude.com/docs/en/settings-reference#bashoutputmaxchars e https://code.claude.com/docs/en/tools-reference#output-limits |
| `effortLevel`, `CLAUDE_CODE_EFFORT_LEVEL`, `/effort`, `maxEffortLevel` | settings, env ou comando | Controla raciocínio em modelos adaptativos | Sonnet 5.5 não desliga o thinking; use effort | https://code.claude.com/docs/en/model-config#adjust-effort-level |
| `MAX_THINKING_TOKENS` | env | Budget fixo, só em modelos com budget fixo | Não tem efeito em Sonnet 5 e posteriores, nem Haiku 5.5 | https://code.claude.com/docs/en/costs#adjust-extended-thinking |
| `CLAUDE_CODE_PROMPT_CACHE_TTL` (5m ou 1h), `ENABLE_PROMPT_CACHING_1H`, `promptCacheTtl`, `FORCE_PROMPT_CACHING_5M` | env ou settings | TTL do cache da conversa principal | Em plano de assinatura, 1h já é automático dentro do uso incluído; com créditos de uso ou API, o padrão é 5m e a escrita de 1h custa mais | https://code.claude.com/docs/en/prompt-caching#which-ttl-each-request-gets |
| `CLAUDE_CODE_SUBAGENT_MODEL` e `CLAUDE_CODE_SUBAGENT_MODEL_FORCE` | env | Modelo padrão de subagent; FORCE sobrescreve todos | FORCE faria as lanes do `/implement-spec` rodarem no modelo escolhido; use `model:` no frontmatter só dos agentes de exploração | https://code.claude.com/docs/en/sub-agents#choose-a-model |
| `autoCompactEnabled`, `DISABLE_AUTO_COMPACT`, `idleCompaction`, `autoCompactWindow`, `CLAUDE_CODE_AUTO_COMPACT_WINDOW` | settings ou env | Quando compacta | `idleCompaction` pode compactar durante pausa; o gate continua correto porque lê tokens absolutos | https://code.claude.com/docs/en/settings-reference#idlecompaction e https://code.claude.com/docs/en/model-config#set-the-auto-compact-window |
| `autoMemoryEnabled`, `CLAUDE_CODE_DISABLE_AUTO_MEMORY` | settings ou env | Liga ou desliga a auto memory | Com spec e tickets no repo, pode desligar | https://code.claude.com/docs/en/memory#auto-memory |
| `claudeMdExcludes` | settings | Pula CLAUDE.md de outros escopos | Pode esconder regra necessária | https://code.claude.com/docs/en/settings-reference#claudemdexcludes |
| `CLAUDE_CODE_DISABLE_BUNDLED_SKILLS` | env | Remove skills embutidas e esconde do modelo | Não remove as suas skills | https://code.claude.com/docs/en/env-vars |
| `disable-model-invocation: true` (frontmatter) e `skillOverrides` com `user-invocable-only` | SKILL.md ou settings | Tira a descrição da skill do contexto e impede invocação pelo agente | Skill que o `/implement` chama sozinha deixa de ser chamada; aplique só em workflows manuais | https://code.claude.com/docs/en/skills#control-who-invokes-a-skill |
| `outputStyle` | settings ou `/output-style` | Muda tom e formato; troca no meio da sessão não quebra cache | Não use em artefato de formato exato | https://code.claude.com/docs/en/output-styles |
| CLAUDE.md abaixo de 200 linhas; regra por caminho | arquivo | Base menor a cada sessão | Edição no meio da sessão só vale após `/clear`, `/compact` ou reinício | https://code.claude.com/docs/en/memory#write-effective-instructions e https://code.claude.com/docs/en/prompt-caching#editing-claude-md-mid-session |
| `/compact <instruções>` e seção "Compact instructions" no CLAUDE.md | comando ou arquivo | Controla o que o resumo preserva | Compactação invalida o cache da conversa | https://code.claude.com/docs/en/costs#manage-context-proactively |
| Subagents para leitura grande | nativo | Conteúdo fica na janela do subagent e só o resumo volta | Lanes já funcionam assim | https://code.claude.com/docs/en/context-window#check-your-own-session |
| `omitClaudeMd` (frontmatter de subagent) | agente | Inicia subagent sem CLAUDE.md | Pode quebrar regra de pt-BR e sem travessão; teste antes | https://code.claude.com/docs/en/sub-agents#supported-frontmatter-fields |
| `claude -p --output-format json` | CLI | Retorna `usage` e `total_cost_usd` | Medição, não economia | https://code.claude.com/docs/en/headless |
| `CLAUDE_CODE_ENABLE_TELEMETRY=1` com `OTEL_METRICS_EXPORTER=console` | env | Métricas no console, sem collector | Não envie para fora sem decidir | https://code.claude.com/docs/en/monitoring-usage |
| `statusLine` com `context_window.used_percentage` e `prompt_cache` | settings | Mostra e expõe o contexto | É a fonte do gate; não troque sem migrar o gate | https://code.claude.com/docs/en/statusline |

Sobre cache: a doc lista o que invalida o prefixo, com um efeito por ação: trocar de modelo, mudar effort, ligar fast mode, conectar ou remover MCP com tools carregadas upfront, compactar, e mudar o prompt de sistema [S4]. Trocar output style não invalida [S4]. Tool search ligado mantém as definições estáveis, e o prefixo sobrevive [S4]. Preços da API: leitura de cache a 0.1x do preço base; escrita a 1.25x no TTL de 5 minutos e a 2x no de 1 hora [S22]. Modelos específicos podem ter exceções na tabela de preços [S22].

Sobre context editing: a limpeza de tool results e de thinking blocks (`clear_tool_uses_20250919`, `clear_thinking_20251015`) é server-side e fica na API [S21]. A doc consultada não mostra como configurar isso no Claude Code CLI. Não verificado se o Claude Code usa internamente.

---

## 5. Stacks sugeridas

### Minimal (começar aqui)
- **Componentes:** RTK já instalado (atualizar para a release atual e confirmar a edição), seção 4 aplicada por projeto, LSP oficial para a linguagem do projeto, ccusage e `/context` para medir.
- **Mudanças de config:** `disableClaudeAiConnectors` ou `/mcp` por projeto para connectors que o projeto não usa; `effortLevel` decidido por tipo de tarefa; `CLAUDE_CODE_FILE_READ_MAX_OUTPUT_TOKENS` e `MAX_MCP_OUTPUT_TOKENS` como caps; `autoMemoryEnabled: false` se o projeto usa spec e tickets.
- **Não instalar:** nenhum hook novo, nenhum daemon, nenhum MCP novo.
- **Risco:** baixo. Não muda skill nem gate. Único cuidado: settings de projeto (`.claude/settings.json`) entram no git se forem commitados.
- **Quando sair daqui:** quando a medição mostrar que a exploração ainda queima tokens em repo grande.

### Balanced
- **Minimal mais** codegraph (ou Serena, se o repo for monorepo) como trial, só na fase de exploração antes de `/to-tickets` ou `/implement`. Não dentro das lanes do `/implement-spec`.
- **Verificar antes de manter:** se o `context_tokens` final de uma sessão com codegraph fica acima do que o gate permite, o gate dispara antes e você perde capacidade por janela.
- **Risco:** médio. Contexto residual, índice local, mais uma superfície MCP, telemetria opcional (desligar na instalação).

### Aggressive (não recomendada agora)
- **Balanced mais** context-mode para payloads de MCP, Read e WebFetch, mais rtk-proxy em trial.
- **Riscos concretos:** (a) PreToolUse duplo em Bash com o RTK, comportamento não documentado; (b) licenças source-available (ELv2 e BUSL-1.1), que permitem uso interno segundo os textos, mas valem revisão jurídica se o uso for comercial [T2, T7]; (c) o proxy muda o payload e pode distorcer o número do gate e o cache (inferência); (d) três camadas para depurar quando uma lane falhar.
- **Quando faria sentido:** só se a medição do Balanced mostrar que o gargalo é payload de MCP, e não exploração.

### Não adotar em nenhum stack
- claude-mem com o instalador padrão. Se quiser memória entre sessões, use `--provider` explícito e desligue o login, e mesmo assim o ganho não está medido.

---

## 6. Como medir (provar o saving antes e depois)

Regras gerais: mude uma coisa por vez; teste mudanças de config no início da sessão, porque mudanças no meio invalidam cache [S4]; use 3 execuções por braço e compare a mediana.

Protocolo:
1. **Escolha uma tarefa fixa.** Use um ticket real já fechado, ou um ticket de teste. Mesma spec, mesmo commit de partida.
2. **Braço A (atual) e braço B (com a mudança).** Três execuções cada. Use `claude -p --output-format json` se for automatizável; ele devolve `usage` e `total_cost_usd` [S16]. Para o interativo, use o `ccusage claude daily --json` depois da sessão [T16].
3. **Contexto fixo.** Rode `/context` no início de cada execução e anote: system tools, MCP, skills e memory. Para o número de 229.8k, compare uma sessão com `disableClaudeAiConnectors: true` e outra sem. Se o total de tokens por turno não mudar, o número é só de exibição [S2]. Isso ainda não está verificado para o seu ambiente.
4. **Por turno.** Do statusline, anote `context_window.current_usage` (input, cache_creation e cache_read) e `prompt_cache` (hit ratio e misses) [S10]. Anote também o `context_tokens` que o gate grava em `~/.claude/state/context-latest.json` [L1].
5. **Saída do Bash.** `rtk gain` antes e depois da execução. Use `rtk bypass` em um comando de controle para comparar [T1].
6. **Qualidade (guard).** Cada braço precisa passar em: tabela de AC válida, linhas `AC-x.y -> test` completas, testes verdes, e `/code-review` sem findings novos. Se qualidade cair, o saving não conta.
7. **Critério de adoção.** Adote só se houver redução medida no total de input consumido ou no `context_tokens` final, sem queda de qualidade, em pelo menos 2 de 3 execuções.

O que a sua máquina já mostra sem nenhuma mudança: `rtk gain` com 83.4% de saving em Bash (medido localmente, estimado pelo próprio RTK) [L2].

O que não dá para medir sem teste: effect do `ENABLE_TOOL_SEARCH` sobre o custo real (não verificado), efeito de codegraph sobre o gate em sessão longa (vendor diz que aumenta o residual, não verificado aqui), e efeito de rtk-proxy sobre o `usage` lido pelo gate (não verificado).

---

## 7. Fontes

Docs oficiais Claude Code (code.claude.com/docs/en/):
- [S1] env-vars: https://code.claude.com/docs/en/env-vars
- [S2] mcp (tool search, disable, connectors): https://code.claude.com/docs/en/mcp
- [S3] settings-reference: https://code.claude.com/docs/en/settings-reference
- [S4] prompt-caching (Claude Code): https://code.claude.com/docs/en/prompt-caching
- [S5] costs: https://code.claude.com/docs/en/costs
- [S6] output-styles: https://code.claude.com/docs/en/output-styles
- [S7] memory: https://code.claude.com/docs/en/memory
- [S8] skills: https://code.claude.com/docs/en/skills
- [S9] sub-agents: https://code.claude.com/docs/en/sub-agents
- [S10] statusline: https://code.claude.com/docs/en/statusline
- [S11] context-window: https://code.claude.com/docs/en/context-window
- [S12] model-config: https://code.claude.com/docs/en/model-config
- [S13] hooks: https://code.claude.com/docs/en/hooks
- [S14] monitoring-usage (OpenTelemetry): https://code.claude.com/docs/en/monitoring-usage
- [S15] plugins/code-intelligence: https://code.claude.com/docs/en/plugins/code-intelligence
- [S16] headless: https://code.claude.com/docs/en/headless
- [S17] commands: https://code.claude.com/docs/en/commands
- [S18] tools-reference (output limits): https://code.claude.com/docs/en/tools-reference
- [S19] cli-reference: https://code.claude.com/docs/en/cli-reference
- [S20] settings: https://code.claude.com/docs/en/settings
- [S21] Context editing (API): https://platform.claude.com/docs/en/build-with-claude/context-editing
- [S22] Prompt caching (API, preços e TTL): https://platform.claude.com/docs/en/build-with-claude/prompt-caching

Repositórios e READMEs (primários, lidos na branch padrão em 2026-10-25):
- [T1] rtk-ai/rtk README: https://github.com/rtk-ai/rtk and https://raw.githubusercontent.com/rtk-ai/rtk/master/README.md
- [T2] rtk-ai/rtk proxy README: https://raw.githubusercontent.com/rtk-ai/rtk/master/proxy/README.md (e rtk-proxy.example.toml no mesmo diretório)
- [T3] rtk-ai/rtk hooks/claude README: https://raw.githubusercontent.com/rtk-ai/rtk/master/hooks/claude/README.md
- [T4] rtk-ai/rtk docs/TELEMETRY.md: https://raw.githubusercontent.com/rtk-ai/rtk/master/docs/TELEMETRY.md
- [T5] rtk-ai/rtk LICENSE: https://raw.githubusercontent.com/rtk-ai/rtk/master/LICENSE
- [T6] GitHub REST API, dados de saúde (estrelas, push, issues, licença) em 2026-10-25: https://api.github.com/repos/{owner}/{repo} para rtk-ai/rtk, mksglu/context-mode, oraios/serena, zilliztech/claude-context, colbymchenry/codegraph, Graphify-Labs/graphify, thedotmack/claude-mem, microsoft/LLMLingua, musistudio/claude-code-router, ast-grep/ast-grep-mcp, ccusage/ccusage, Maciek-roboblog/Claude-Code-Usage-Monitor, OthmanAdi/planning-with-files, Aider-AI/aider, e busca em repositórios com push após 2026-07-01
- [T7] mksglu/context-mode README: https://raw.githubusercontent.com/mksglu/context-mode/main/README.md
- [T8] oraios/serena README e licença: https://raw.githubusercontent.com/oraios/serena/main/README.md e https://raw.githubusercontent.com/oraios/serena/main/LICENSE
- [T9] zilliztech/claude-context README: https://raw.githubusercontent.com/zilliztech/claude-context/master/README.md
- [T10] colbymchenry/codegraph README: https://raw.githubusercontent.com/colbymchenry/codegraph/main/README.md
- [T11] Graphify-Labs/graphify README: https://raw.githubusercontent.com/Graphify-Labs/graphify/main/README.md
- [T12] thedotmack/claude-mem README e licença: https://raw.githubusercontent.com/thedotmack/claude-mem/main/README.md e https://raw.githubusercontent.com/thedotmack/claude-mem/main/LICENSE
- [T13] microsoft/LLMLingua README: https://raw.githubusercontent.com/microsoft/LLMLingua/main/README.md
- [T14] musistudio/claude-code-router README: https://raw.githubusercontent.com/musistudio/claude-code-router/main/README.md
- [T15] ast-grep/ast-grep-mcp README: https://raw.githubusercontent.com/ast-grep/ast-grep-mcp/main/README.md
- [T16] ccusage (apps/ccusage) README e licença: https://raw.githubusercontent.com/ccusage/ccusage/main/apps/ccusage/README.md e https://raw.githubusercontent.com/ccusage/ccusage/main/apps/ccusage/LICENSE
- [T17] Claude-Code-Usage-Monitor: somente dados de API (https://api.github.com/repos/Maciek-roboblog/Claude-Code-Usage-Monitor), README não lido
- [T18] OthmanAdi/planning-with-files README: https://raw.githubusercontent.com/OthmanAdi/planning-with-files/master/README.md
- [T19] Aider, repo map (doc oficial do Aider): https://aider.chat/docs/repomap.html

Arquivos locais consultados (no seu repositório e máquina):
- [L1] `G:\Antigravity\matt-jedi-skills\skills\skills\engineering\implement\scripts\context_gate.py` (lê `~/.claude/state/context-latest.json`; soma input, cache_creation e cache_read, sem output; compatível com a fórmula de [S10])
- [L1b] `G:\Antigravity\matt-jedi-skills\skills\skills\engineering\setup-jedi\templates\statusline-context-snippet.txt` (escritor do `context-latest.json`)
- [L2] Saída local de `rtk --version` (0.37.2) e `rtk gain` (9423 comandos, 83.4%), e `command -v jq` (não encontrado no PATH do bash), em 2026-10-25

Não utilizado: nenhuma fonte secundária. Não abri o BENCHMARK.md do context-mode, nem o site rtk-ai.app (retornou 404 para a leitura automatizada). Não verificado: qualquer claim de economia de fornecedor que não esteja marcado como medido.
