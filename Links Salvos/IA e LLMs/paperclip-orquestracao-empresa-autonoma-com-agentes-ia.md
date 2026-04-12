---
tags: [multi-agente, orquestracao, open-source, agentes-autonomos, empresa-ia, node-js]
source: https://x.com/0xCVYH/status/2039799055165895115
date: 2026-04-03
tipo: aplicacao
---
# Orquestrar Empresa Autônoma de Agentes IA com Paperclip

## O que é

Paperclip é um servidor Node.js + UI React que orquestra um time de agentes de IA como se fosse uma empresa real. Diferente de frameworks de agentes individuais (LangChain, CrewAI), Paperclip modela a estrutura organizacional completa: organograma hierárquico, cargos (CEO, CTO, engenheiros, marketing), orçamentos por agente, governança com aprovação humana, e sistema de tickets com auditoria. Cada agente opera via heartbeats agendados, retomando contexto entre execuções sem reiniciar do zero. Open-source MIT, 44K+ stars, self-hosted sem conta externa.

## Como implementar

**Setup rápido (1 comando)**

```bash
npx paperclipai onboard --yes
```

Isso clona o repo, instala dependências, e sobe o servidor com PostgreSQL embarcado em `http://localhost:3100`. Sem config de banco, sem Docker obrigatório.

**Setup manual (mais controle)**

```bash
git clone https://github.com/paperclipai/paperclip.git
cd paperclip
pnpm install
pnpm dev
```

Requisitos: Node.js 20+, pnpm 9.15+. O servidor sobe com Postgres embutido automaticamente. Para produção, aponte para seu próprio Postgres e faça deploy como preferir (Vercel, VPS, etc).

**Fluxo de operação em 3 passos**

1. **Definir objetivo**: Você declara a missão da empresa. Ex: "Construir o melhor app de notas com IA e chegar a $1M MRR". Todo o trabalho dos agentes deriva desse objetivo, cada task carrega a ancestralidade completa do goal.

2. **Contratar o time**: Cada agente recebe um cargo, job description, e ferramentas. Paperclip funciona com qualquer agente que aceite heartbeat: Claude Code, OpenClaw, Codex, Cursor, ou qualquer processo que responda via HTTP/bash. A config de cada agente fica em `AGENTS.md`:

```markdown
# agents/cto.md
name: CTO
role: Chief Technology Officer
provider: claude-code
budget_monthly: $200
heartbeat: every 2 hours
skills:
  - code-review
  - architecture
  - deployment
reports_to: CEO
```

3. **Aprovar e executar**: Você revisa a estratégia proposta, ajusta orçamentos, e dá play. O dashboard mostra: tasks em andamento, custos acumulados por agente, decisões tomadas (com justificativa), e permite pausar/retomar qualquer agente a qualquer momento.

**Arquitetura interna**

O que diferencia Paperclip de um simples task manager:

- **Checkout atômico**: quando um agente pega uma task, o checkout e a verificação de orçamento são atômicos. Sem trabalho duplicado, sem estouro de custo.
- **Estado persistente**: agentes retomam o mesmo contexto entre heartbeats. Se o PC reiniciar, o agente continua de onde parou.
- **Injeção de skills em runtime**: agentes aprendem workflows e contexto do projeto em execução, sem re-treinamento.
- **Governança com rollback**: aprovações são obrigatórias pra decisões críticas, configs são versionadas, e mudanças ruins podem ser revertidas.
- **Multi-empresa**: uma instalação roda N empresas com isolamento completo de dados.

**Integração com agentes existentes**

Se você já usa Claude Code em vários terminais, Paperclip organiza isso:

```bash
# Antes: 20 tabs de Claude Code sem contexto compartilhado
# Depois: cada tab é um agente com cargo, orçamento e objetivo

# Configurar agente Claude Code
paperclipai configure agent \
  --name "Backend Engineer" \
  --provider claude-code \
  --budget 50 \
  --heartbeat "every 30 minutes" \
  --reports-to "CTO"
```

**Monitoramento mobile**

O UI React é responsivo. Com Tailscale (VPN gratuita), você acessa o dashboard do celular pra monitorar seus agentes rodando em casa. Aprovações podem ser feitas pelo celular.

**Templates de empresa (Clipmart, em breve)**

Feature anunciada: importar templates completos de empresas (org chart + configs de agentes + skills) com um clique. `companies.sh` já permite exportar/importar organizações inteiras com scrubbing de secrets.

## Stack e requisitos

- **Runtime**: Node.js 20+, pnpm 9.15+
- **Banco**: PostgreSQL embarcado (dev) ou externo (prod)
- **Frontend**: React (embarcado no servidor)
- **Agentes compatíveis**: Claude Code, OpenClaw, Codex, Cursor, qualquer HTTP/bash
- **Hardware mínimo**: qualquer máquina que rode Node.js. Os agentes consomem recursos próprios (API tokens).
- **Custo**: $0 (MIT license) + custo dos agentes que você plugar (tokens Anthropic, OpenAI, etc)
- **Deploy prod**: Vercel, Railway, VPS. Para acesso mobile local: Tailscale (grátis)
- **Repo**: github.com/paperclipai/paperclip (44K+ stars)

## Armadilhas e limitações

**Custo de tokens escala com número de agentes**: cada heartbeat de cada agente consome tokens. Com 6 agentes rodando a cada 30 min, são 288 chamadas de API por dia. Se cada uma custa ~$0.05 (Sonnet), são $14.40/dia. Defina orçamentos agressivos no início e monitore pelo dashboard.

**Heartbeats não são tempo real**: agentes operam em ciclos (a cada N minutos/horas), não em loop contínuo. Para tarefas que precisam de resposta imediata (suporte ao cliente), o modelo de heartbeat pode ser lento. OpenClaw em modo contínuo é uma alternativa, mas consome mais.

**Complexidade organizacional real**: definir org chart, cargos e responsabilidades pra agentes IA exige pensar em design organizacional. Se a hierarquia for mal definida (ex: CTO e Lead Engineer com responsabilidades sobrepostas), os agentes vão conflitar nas tasks. Comece com 2-3 agentes e escale gradualmente.

**Postgres embarcado não escala**: o Postgres embutido é conveniente pra dev, mas pra produção com múltiplas empresas e centenas de tasks, use uma instância dedicada. Migração é simples (`pnpm db:migrate`).

**Governança requer disciplina humana**: o sistema permite aprovar tudo no automático, mas isso derrota o propósito. Se você rubber-stamp tudo, vai perder controle dos custos e da direção estratégica. Reserve 15-20 min/dia pra revisar decisões pendentes.

## Conexões

- [[empresas-operadas-por-ia]] — conceito similar mas sem ferramenta concreta; Paperclip é a implementação
- [[orquestracao-multi-agente-com-llms]] — Paperclip resolve o problema de coordenação descrito nessa nota
- [[agentes-autonomos-multi-agente]] — padrões de design que Paperclip implementa nativamente

## Histórico
- 2026-04-03: Nota criada a partir de Twitter (@0xCVYH)
