---
tags: [claude, prompts, financeiro, fpa, analise, visualizacao]
source: https://claude.ai/public/artifacts/cd62591d-5afb-495e-9013-31ebd88000fc
date: 2026-03-16
tipo: aplicacao
---

# Automatizar Análises FP&A com 30 Prompts Reutilizáveis do Claude

## O que é

Biblioteca de 30 prompts estruturados para Financial Planning & Analysis (FP&A): tendência, forecasting, variância, scenarios, dashboards. Cada prompt é parametrizável, iterativo, e combina-se em fluxos de análise completos, reduzindo semanas de trabalho manual para minutos.

## Como implementar

### Setup Base: Organizar Prompts em Diretório

Crie estrutura local:

```
fpa-prompts/
├── 1-tendencias/
│   ├── analise-tendencias-receita.md
│   ├── deteccao-anomalias.md
│   └── analise-variancia.md
├── 2-forecasting/
│   ├── previsao-receita-trimestral.md
│   ├── projecao-despesas.md
│   └── cenarios-sensibilidade.md
├── 3-visualizacao/
│   ├── dashboard-executivo.md
│   ├── narrativa-financeira.md
│   └── powerpoint-summary.md
└── 4-decisoes/
    ├── analise-e-se.md
    ├── impacto-investimento.md
    └── recomendacoes-acao.md
```

### Template Base de Prompt

Estrutura que funciona para todas as categorias:

```markdown
# [NOME DO PROMPT]

## Contexto
- Empresa/Departamento: [CUSTOMIZAR]
- Período: [Q1-Q4 2026]
- Dados disponíveis: [CSV, Planilha, JSON]

## Tarefa
[Descrever exatamente o que fazer]

## Formato de Input
```
CSV com colunas: Data, Receita, Despesa, Região, Produto
2026-01-01, 150000, 45000, LATAM, SaaS
2026-01-02, 160000, 46000, LATAM, SaaS
...
```

## Instruções Específicas
1. [Passo 1]
2. [Passo 2]
3. [Passo 3]

## Formato de Output
Tabela estruturada + visualização ASCII + insights top-3
```

### Prompt 1: Análise de Tendências de Receita

```
Contexto:
- Receita trimestral 2024-2026
- SaaS, 5 regiões, 3 produtos

Dados:
Q1 2024: $500K | Q2 2024: $520K | Q3 2024: $545K | Q4 2024: $580K
Q1 2025: $615K | Q2 2025: $640K | Q3 2025: $670K | Q4 2025: $710K
Q1 2026: $750K | Q2 2026: $785K | Q3 2026: ?

Tarefa:
1. Calcule CAGR (Compound Annual Growth Rate) por período
2. Identifique sazonalidade (Q1 vs Q4)
3. Analise impacto por região
4. Projete Q3 2026 com intervalo de confiança

Instruções:
- Use média móvel 4-trimestral para suavização
- Detecte outliers estatisticamente significativos (Z-score > 2)
- Retorne em formato Markdown com:
  * Gráfico ASCII de tendência
  * Tabela de CAGR por período
  * Top-3 insights acionáveis
```

**Output esperado:**

```
## Análise de Tendências de Receita FP&A

### Crescimento Anual
CAGR 2024-2025: +22.4%
CAGR 2025-2026 (YTD): +18.6%

### Sazonalidade
Q4 > Q3 > Q2 > Q1
Padrão: -12% em Q1 (início fiscal), +8% em Q4

### Projeção Q3 2026
Cenário Base: $810K (±$25K)
Intervalo 95%: $785K - $835K

### Insights Acionáveis
1. Crescimento desacelerando (22.4% → 18.6%) — investigar churn
2. Sazonalidade previsível — usar para planejamento de caixa
3. LATAM crescendo 28% YoY — aumentar alocação de marketing
```

### Prompt 2: Modelagem de Cenários (E-Se)

```
Dado: Projeção de receita $810K Q3 2026

Cenários:
- Base (current trend): $810K
- Otimista (+30% new deals): $1,053K
- Pessimista (-20% churn): $648K

Variáveis sensíveis:
- Novos clientes: ±10% = ±$81K receita
- Churn rate: +1% = -$25K receita
- Preço médio: +5% = +$41K receita

Tarefa:
1. Crie matriz de sensibilidade 3x3 (Novos Clientes vs Churn)
2. Quantifique impacto em Lucro Operacional
3. Recomende limites de ação ("se churn > 8%, ativar retention")

Output: Tabela com ranges, heatmap ASCII, recomendações
```

### Prompt 3: Análise de Variância (Orçado vs Realizado)

```
Orçamento 2026 (trimestral):
- Receita: $2,500K
- Despesa: $1,200K
- EBITDA: $1,300K

Realizado Q1+Q2 2026:
- Receita: $1,535K (vs $1,250K orçado)
- Despesa: $638K (vs $600K orçado)
- EBITDA: $897K (vs $650K orçado)

Tarefa:
1. Calcule variância em % (Realizado - Orçado) / Orçado
2. Decomponha: Volume vs Preço vs Mix vs Operacional
3. Retorne recomendações de reforecast para H2
```

**Output:**

```
### Variância Orçada vs Realizado (YTD)

| Métrica | Orçado | Realizado | Variância | % | Causa |
|---------|--------|-----------|-----------|---|-------|
| Receita | $1,250K | $1,535K | +$285K | +22.8% | Volume (+15%) + Preço (+6.2%) |
| Despesa | $600K | $638K | +$38K | +6.3% | Overhead novo headcount |
| EBITDA | $650K | $897K | +$247K | +38.0% | Synergy operacional |

Reforecast H2 2026:
- Receita: $1,400K (up from $1,250K)
- Despesa: $620K (disciplina de custo)
- EBITDA: $780K (37% margin)
```

### Prompt 4: Dashboard Executivo

```
Dados: Receita, Despesa, EBITDA, Churn, CAC (Customer Acquisition Cost)

Tarefa:
Gere dashboard de 1 página com:
1. KPI cards (receita YTD, crescimento %, margin %)
2. Série temporal (últimos 12 meses)
3. Comparação vs target/budget
4. Red flags (se algum métrico < target)
5. Recomendações top-3 para CFO

Output: Markdown + HTML renderizável + Excel
```

## Stack e requisitos

**Inputs:**
- CSV/Excel com dados mensais ou trimestrais
- Mínimo: Data, Receita, Despesa
- Ideal: + Região, Produto, Canal de venda, Churn

**Processamento:**
- Claude 3.5 Sonnet (multi-turn conversations)
- Token budget: ~1M tokens/mês para análises diárias
- Custo: ~$2-5 USD/mês por analista

**Outputs:**
- Markdown tables, ASCII charts, HTML
- Power BI / Looker integration via CSV export
- Email automático com relatórios (via Zapier/n8n)

**Ferramentas complementares:**
- Sheets/Excel API: importar dados
- Google Data Studio: visualização
- Coda/Notion: documentação

## Armadilhas e limitações

**Qualidade de dados:**
- Garbage in, garbage out. Se inputs têm inconsistências, outputs são enganosos
- Sempre validar dados antes de passar ao Claude
- Documentar ajustes (e.g., "Q1 2024 excluído por auditoria")

**Contexto insuficiente:**
- Sem contexto de fatores externos (M&A, mudança de preço, pandemia), análises serão incompletas
- Sempre incluir "eventos relevantes" no contexto do prompt

**Viés de prompt:**
- Prompt pode sugerir resposta. Ser neutro: "analise tendência" vs "por que cresceu?"

**Limites de iteração:**
- Cada refinamento custa tokens. Estruture bem o prompt inicial

**Compliance:**
- Alguns dados são sensíveis. Não enviar PII ou dados de segredo comercial direto para Claude
- Usar dados agregados/anonimizados

## Conexões

[[skill-pack-financeiro-para-agentes-ai]]
[[450_skills_workflows_claude]]
[[Last30Days Skill Prompts Comunidade]]
[[iteração-produto-feedback]]

## Histórico

- 2026-03-16: Nota criada
- 2026-04-02: Reescrita como guia prático com templates, exemplos, executáveis
