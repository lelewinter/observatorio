---
tags: [conceito, llm, prompts, agentes-autonomos, claude, reasoning]
date: 2026-04-02
tipo: conceito
aliases: [Prompt Engineering, System Prompts, Agent Prompts]
---
# Prompt Engineering para Agentes — Design de Comportamento Autônomo via Instrução

## O que e

Craft de prompts (instruções textuais) que transformam LLMs genéricos em agentes especializados com comportamento previsível. Diferencia-se de "simple prompting" (um prompt, uma resposta) por incluir: contexto persistente, definição de rol/identidade, restrições operacionais, ferramentas disponíveis, e feedback loops.

Um bom prompt de agente é programa: não apenas pede resposta, mas *programa o agente como especialista*.

## Como funciona

**Estrutura de System Prompt Eficaz**

```
1. IDENTIDADE: "Você é X especialista em Y"
2. OBJETIVO: "Sua tarefa é Z"
3. ESCOPO: "Você decide sobre A, B, C. Não decide sobre D, E, F (requer human)"
4. FERRAMENTAS: "Suas ferramentas: API X, DATABASE Y, TOOL Z"
5. CONSTRAINTS: "Restrições: orçamento <= $1k, confidencialidade em dados de clientes"
6. FEEDBACK: "Se acontecer X, reintentar. Se Y, chamar escalação."
7. OUTPUT FORMAT: "Sempre responda em JSON com fields: decision, rationale, next_steps"
```

Exemplo concreto (Sales Agent):

```
You are a senior sales agent at Acme SaaS.

OBJECTIVE:
Qualify leads and push deals to close. Target: $5k monthly revenue.

SCOPE:
- Can: Contact prospects, demo product, negotiate price
- Cannot: Offer discounts > 20%, sign contracts (needs CEO approval)

TOOLS:
- CRM API (get leads, update pipeline)
- Email (send proposals)
- Calendly (schedule demos)

CONSTRAINTS:
- Budget for ads: $2k/month
- Customer acquisition cost target: <= $500
- Never promise features not yet built

FEEDBACK LOOPS:
- If lead says "too expensive": offer 15% discount and resend proposal
- If lead ghosts after 2 weeks: transfer to nurture email sequence
- If 5+ prospects say same objection: report to marketing for messaging fix

OUTPUT: Always respond with:
{
  "action": "contact|demo|proposal|close",
  "prospect_id": "string",
  "details": "what you're doing",
  "next_review": "when to follow up"
}
```

**Roles vs. Generic Prompting**

Generic prompt: "Analyze this lead"
→ LLM just analyzes, no clear action

Role prompt: "You are a sales qualifier. Leads come with 5 fields. Your job: score 1-10 and recommend CONTACT, NURTURE, or DISQUALIFY. You have access to CRM API to check customer history. Always prioritize leads from vertical X. If lead spent > $10k with us before, auto-CONTACT."
→ LLM acts as specific agent with clear decision framework

**Variáveis e Contexto Dinâmico**

Prompts devem aceitar variáveis:

```python
def sales_prompt(lead: dict, company_state: dict) -> str:
    return f"""
You are a sales agent. Here's your current state:

Revenue this month: ${company_state['revenue']}
Target: $5000

Lead information:
- Name: {lead['name']}
- Company: {lead['company']}
- Budget: ${lead['budget']}
- Pain: {lead['pain_point']}
- Prior interactions: {lead['interactions_count']}

You've already contacted them {lead['interactions_count']} times.

Decision: Is it worth contacting again? If yes, what's your pitch?
    """
```

Cada chamada, prompt é parametrizado com estado atual. Isso permite agente aprender do contexto.

**Técnicas de Reliability**

1. **Chain-of-Thought**: "Let's think step by step..." força modelo a raciocinar, reduz alucinações
2. **Few-Shot Examples**: Mostrar 2-3 exemplos de boa decisão antes de pedir que faça uma
3. **Structured Output**: Forçar JSON schema reduz ambigüidade
4. **Temperature Control**: Determinístico (temp=0) para decisões críticas, criativo (temp=0.7) para brainstorm

## Pra que serve

**Quando Usar Prompt Engineering vs. Fine-Tuning**

| Aspecto | Prompt Engineering | Fine-Tuning |
|---------|-------------------|------------|
| Setup | Horas | Dias |
| Custo | Baixo | Médio-Alto |
| Flexibilidade | Alta | Baixa |
| Accuracy | 85-95% | 95-99% |
| Iteration | Rápido | Lento |

✓ **Usar Prompt Engineering quando**: Tarefa é bem-definida, exemplos disponíveis, agilidade importa
✗ **Usar Fine-Tuning quando**: Tarefa requer conhecimento "indômito" que modelo não tem, ou accuracy crítica

**Estágios de Sophistication**

1. **Simple**: Single shot, sem contexto. "Analyze this"
2. **Contextual**: Variáveis + rol. "You're X, aqui está situação Y"
3. **Tool-Integrated**: Prompts mencionam ferramentas, LLM chama conforme precisa
4. **Feedback Loop**: LLM vê resultados de suas ações, ajusta próximas
5. **Multi-Step Reasoning**: Chain-of-thought, iteração interna antes de output

## Exemplo pratico

**Evolução de Prompt: Sales Lead Qualification**

**V1 (Naive):**
```
Analyze this lead: Name: John, Company: Acme, Budget: $50k
```
Output: "John seems interested, contact him"
Problem: Vago, sem framework, sem ação concreta

**V2 (Contextual):**
```
You are a sales qualifier. Score leads 1-10.

Lead: Name John, Company Acme, Budget $50k, Time to Decide 2 weeks
CRM shows: Acme already uses competitor (Z), last interaction 3 months ago

Score this lead. Output: PRIORITY (1-10), ACTION (CONTACT|NURTURE|PASS), REASON
```
Output: "9, CONTACT, Budget is good and competitor relationship stale"
Better, but still improvable.

**V3 (Tool-Aware):**
```
You are a sales qualifier with access to:
- CRM API: Look up customer history, deal stage
- Email API: Send proposals
- Calendar API: Schedule calls

Lead: John, Acme, $50k budget

Instructions:
1. Query CRM for Acme history
2. If lifetime value > $100k: auto-priority 10
3. If no interaction in 30+ days: offer redemo
4. Response JSON: {score, action, proposal, next_date}

After you respond, I'll execute your action.
```
Output: Complete JSON with decision + tooling

**V4 (Feedback Loop):**
```
[same as v3]

Previous outcome: John scheduled for demo on 2026-04-05.
Demo happened. Feedback: "John liked product but concerns about integration time"

Given this feedback, what's your next action?
- Introduce engineer for integration discussion?
- Offer implementation services?
```
Output: Adapts to new information, iterates

## Aparece em
- [[12-prompts-options-trading-theta-decay-claude]] — 12 prompts especializados de trading
- [[empresas-operadas-por-ia]] — Prompts definem comportamento dos agentes
- [[reasoning-llm]] — Técnicas de raciocínio para qualidade de output
- [[claude-api-best-practices]]

---
*Conceito extraído em 2026-04-02 a partir de análise de padrões de automação com LLMs*
