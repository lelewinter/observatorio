---
tags: [moc, dados, automacao, workflow, pipeline, data-engineering, agentes-autonomos, multi-agent]
date: 2026-04-02
tipo: moc
---
# Dados e Automação

Orquestração de workflows de dados, agentes autônomos para inteligência pessoal, e loops recursivos via Claude Code. O vault contém padrões para execução recorrente de tarefas, coordenação multi-agente em paralelo, e inteligência pessoal que monitora múltiplas fontes de dados estruturadas e não-estruturadas.

## Loops de Tarefas Recorrentes via Claude Code

[[loop-agenda-tarefas-recorrentes-ate-3-dias|/loop: Agendar Tarefas por até 3 Dias]] — comando nativo de Claude Code que permite agendar execução repetida de tarefa por período máximo de 72 horas. Syntax: `/loop --interval [interval] --max-duration 3d [task description]`. Casos práticos:

- `/loop --interval 1h: Verificar emails, summarizar importantes, criar tarefas` — agente roda a cada 1 hora por 3 dias
- `/loop --interval 30m: Monitorar alertas de preço em 10 ações, notificar via email se > 5% movimento` — trader automático
- `/loop --interval 2h: Verificar comentários em repositório GitHub, responder automáticamente a issues de bug reports` — bot de triage

Implementação técnica: `/loop` cria session recorrente que persiste em background. Outputs são salvos em shared history (accessível em próxima iteração). Limitação: máximo 72 horas (depois expirar). Para tarefas >3 dias, usar Windows Task Scheduler ou cron (como no pipeline de Leticia).

Vantagem vs. agendadores tradicionais: estado é compartilhado naturalmente (Claude vê outputs de iteração anterior), contexto persiste (não precisa re-onboarding em cada ciclo). Exemplo: `/loop --interval 4h: Processar novos links salvos no Telegram, extrair conteúdo, gerar resumo estruturado, salvar em Obsidian` — é exatamente pipeline de Leticia, mas embutido em Claude Code.

## Orquestração Multi-Agente com Estado Compartilhado

[[orquestracao-multi-agente-com-llms|Multi-Agente em Paralelo: 6+ Agentes com Coordenação via Shared Docs]] — arquitetura distribuída onde 6-10 instâncias paralelas de Claude Code (AUTH-Agent, API-Agent, UI-Agent, TEST-Agent, INFRA-Agent, DOCS-Agent) trabalham em paralelo em projeto único, cada um com escopo bem definido.

Estrutura: Master Coordinator Agent mantém estado global (roadmap, decision log, progress). Sub-agentes comunicam via message passing (conversation IDs em shared docs) e compartilham "living documents": change-philosophy.md (modo de pensar sobre mudanças), problem-space.md (quê está quebrado), solution-space.md (arquitetura), decision-log.json (quem decidiu o quê), progress-tracker.json (% completo por módulo).

Loop diário típico:
- 08:00 Master distribui tasks em Kanban
- 08:15 6 agentes trabalham em paralelo (cada um seu módulo)
- 09:00 TEST-Agent roda full test suite a cada 30 min, reporta failures → problem-space.md
- 09:30 Se failure: TEST → problema agente específico → diagnóstico → fix → re-test
- 17:00 Standup automático: progress-tracker atualizado, decision-log com decisões do dia
- 18:00 Resumo: "76% completo, 3 bloqueadores, 0 regressions"

Implementação técnica: cada agente é sessão de Claude Code distinta rodando em tmux (visual). Comunicação é file-based (não exige infrastructure compleja). Master coordena merge conflicts (each agent tem branch isolado, ex: auth/*, api/*, etc).

Vantagem: desenvolvimento distribuído, iteração paralela, debugging colaborativo. Armadilhas: coordination overhead (se não especificar bem, agentes entram em conflito), context explosion (cada agente recebe ~50KB de contexto, total é 300KB de leitura redundante).

## Inteligência Pessoal Distribuída

[[crucix_agente_inteligencia_pessoal|Crucix: Agente de Inteligência Pessoal]] — sistema que monitora múltiplas fontes (Twitter, news feeds, market data, email, Slack) e notifica quando algo relevante ocorre. Diferencia-se de alertas simples por compreender contexto pessoal: se você trabalha em IA, notifica sobre papers arXiv em ML; se você trader, notifica sobre dados económicos; se você gamer, notifica sobre releases.

Arquitetura: ingestion layer (fetch de múltiplas APIs), processing layer (Claude analisa relevância contextual), notification layer (email, Telegram, webhook). Estado persistente: preferências (o que é relevante pra você), histórico de notificações (evita duplicatas), engagement metrics (rastreia quais notificações você clicou, ajusta modelo).

Exemplo: novo paper no arXiv com 50 citações em 24h → Crucix avalia abstract → contexto (trabalha em agents + quantização) → relevância score 8.5/10 → notifica. Você clica + salva → sistema nota engagement, aumenta relevância scores pra papers similares no futuro.

Implementação: webhook que recebe dados → Claude API analisa → decision (notificar?) → persistência em DB (preferências, histórico). Iteração contínua: cada engagement alimenta classificador.

## Estado Atual e Tendências

2026 marca transição de "automação de tarefas isoladas" para "orquestração de sistemas inteligentes". `/loop` em Claude Code democratiza agendamento (qualquer pessoa pode escrever `/loop [tarefa]`, sem infraestrutura). Multi-agente frameworks emergem como padrão para projetos complexos (vs. agente único que fica bottleneck).

Tendência esperada: agentes agem autonomamente 95% do tempo, humano intervém 5% (quando ambiguidade ou decisão estratégica). Custo computacional é constraint principal (6+ agentes paralelos = multi-session Claude usage = $100-500/dia em API).

## Ferramentas e Stack Prático

**Agendamento**: Claude Code `/loop` (até 3 dias), Windows Task Scheduler (indefinido), cron jobs (Linux), GitHub Actions (CI/CD-style).

**Orquestração Multi-Agente**: tmux/screen (session management), Git (versionamento), shared filesystem ou DB (state sharing), file-based message passing (simplista) ou message queues (Redis, RabbitMQ) para scale.

**Processamento de Dados**: Pandas (tabular), DuckDB (OLAP local), Polars (high-performance), SQL (queries estruturadas).

**Monitoramento**: logs estruturados (cada agente loga decisões), prometheus/grafana (metrics), alertas (email/Slack).

**APIs de Ingestion**: Twitter/X API, RSS feeds, Alpha Vantage (mercado), email (IMAP), Slack API.

## Conexões com Outros Temas

Automação conecta com [[MOC - IA e LLMs]] via agentes (Claude como engine de decisão). Multi-agente é extensão de [[MOC - Dev e Open Source]] (padrões arquiteturais, orquestração). Inteligência pessoal (Crucix) alimenta [[MOC - Negocios e Startups]] (trader automático que monitora sentimento + dados financeiros). Dados fluem entre [[MOC - Games e 3D]] (telemetria de gameplay), [[MOC - Computacao Quantica]] (papers de pesquisa), [[MOC - Seguranca]] (alertas de vulnerabilidades).
