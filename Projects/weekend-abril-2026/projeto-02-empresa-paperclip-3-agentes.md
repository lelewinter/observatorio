---
tags: [projeto, paperclip, agentes-autonomos, multi-agente, orquestracao]
date: 2026-04-11
tipo: projeto
status: pendente
prioridade: alta
tempo-estimado: 3-4 horas
---
# Projeto 2: Empresa Paperclip com 3 Agentes

## Objetivo

Subir o framework Paperclip com 3 agentes Claude Code trabalhando coordenados em um micro-projeto. Entender na pratica como funciona orquestracao de agentes com hierarquia, orcamento e governanca.

## Por que fazer isso agora

Paperclip tem 44K+ stars no GitHub, e o framework mais maduro para "empresa de agentes". 57% das organizacoes ja tem agentes em producao. O conceito de one-person company operada por IA esta se materializando (Medvi fez $401M com 2 funcionarios). Entender orquestracao multi-agente e skill critico pra 2026.

## Pre-requisitos

- Node.js 20+ (`node --version`)
- pnpm 9.15+ (`pnpm --version`, instalar com `npm install -g pnpm`)
- API key Anthropic (quando creditos voltarem)
- Git

## Passo a Passo

### Etapa 1: Instalar Paperclip (15 min)

```powershell
# Onboarding automatico
npx paperclipai onboard --yes

# Verificar instalacao
npx paperclipai status
```

O onboarding cria a estrutura de pastas, configura o provider (Claude) e gera os arquivos base.

### Etapa 2: Definir a Missao (15 min)

Escolher um micro-projeto concreto. Sugestao: "Criar landing page responsiva para o Observatorio".

Editar o arquivo de missao:

```yaml
# mission.yaml
company:
  name: "Observatorio Lab"
  mission: "Criar uma landing page responsiva e bonita para o vault Observatorio"
  budget_total: 15.00  # USD, limite para nao gastar demais

departments:
  engineering:
    head: "CTO Agent"
    budget: 7.00
  frontend:
    head: "Frontend Dev Agent"
    budget: 5.00
  quality:
    head: "QA Agent"
    budget: 3.00
```

### Etapa 3: Configurar os 3 Agentes (30 min)

```yaml
# agents/cto.yaml
name: "CTO"
role: "Architect and technical decision maker"
responsibilities:
  - Definir stack tecnico (HTML/CSS/JS puro ou framework)
  - Decompor o projeto em tarefas
  - Revisar decisoes tecnicas dos outros agentes
  - Aprovar PRs antes de merge
provider: claude
model: claude-sonnet-4-6

# agents/frontend-dev.yaml
name: "Frontend Dev"
role: "Implementation specialist"
responsibilities:
  - Implementar HTML/CSS/JS conforme spec do CTO
  - Criar componentes responsivos
  - Otimizar performance e acessibilidade
provider: claude
model: claude-sonnet-4-6

# agents/qa.yaml
name: "QA Engineer"
role: "Quality assurance and testing"
responsibilities:
  - Testar em multiplos viewports (mobile, tablet, desktop)
  - Verificar acessibilidade (contrast ratio, alt text, keyboard nav)
  - Reportar bugs com screenshots e steps to reproduce
  - Validar HTML/CSS no W3C validator
provider: claude
model: claude-haiku-4-5
```

### Etapa 4: Rodar e Observar (1.5-2h)

```powershell
# Iniciar a empresa
npx paperclipai run

# Acompanhar no dashboard
npx paperclipai dashboard
```

O que observar:
1. **Ciclo de heartbeats**: como os agentes se comunicam entre si
2. **Decomposicao de tarefas**: como o CTO quebra o projeto em tasks
3. **Feedback loop**: quando o QA encontra bug, como o Frontend Dev responde
4. **Consumo de tokens**: quanto cada agente gasta (comparar com orcamento)
5. **Decisoes autonomas**: quais decisoes o CTO toma sem pedir aprovacao

### Etapa 5: Analise Post-Mortem (30 min)

Apos o projeto terminar (ou orcamento acabar):

```powershell
# Exportar log de decisoes
npx paperclipai export --format markdown > post-mortem.md
```

Perguntas para responder:
- O resultado final e utilizavel?
- Quanto custou? ($5? $10? $15?)
- Onde os agentes erraram?
- Qual agente foi mais eficiente?
- Valeria ter mais agentes? Menos?
- Como isso se compara a voce fazer sozinha com Claude?

## Checklist de Conclusao

- [ ] Paperclip instalado
- [ ] Missao definida
- [ ] 3 agentes configurados
- [ ] Empresa rodou ate completar ou atingir budget
- [ ] Dashboard observado durante execucao
- [ ] Post-mortem escrito (o que funcionou, o que nao)
- [ ] Decisao: vale usar Paperclip para projetos futuros?

## Variacoes (se quiser ir alem)

- Trocar o projeto para "Criar script Python que faz X"
- Adicionar 4o agente: "Docs Agent" que documenta tudo
- Testar com modelos locais (Gemma 4 via Ollama) como provider em vez de Claude API
- Comparar custo de 3 agentes Paperclip vs 1 sessao Claude Code fazendo tudo

## Notas Relacionadas

- [[paperclip-orquestracao-empresa-autonoma-com-agentes-ia]]
- [[orquestracao-multi-agente-com-llms]]
- [[arquitetura-multi-agente-com-avaliador-separado]]
- [[construir-empresa-solo-de-alto-faturamento-com-ai-agents-e-audiencia-digital]]
- [[agentscope-framework-multi-agente]]

## Criterios de Sucesso

Minimo: Paperclip instalado, 3 agentes configurados, executou pelo menos 1 ciclo.
Ideal: Projeto completo entregue, post-mortem com insights uteis.
Bonus: Testou com modelo local como provider alternativo.

## Historico

- 2026-04-11: Projeto criado
