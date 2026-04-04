---
tags: [conceito, prompts, FP&A, template, reutilização]
date: 2026-04-02
tipo: conceito
aliases: [Prompt Templates, FP&A Automation]
---

# FP&A Prompt Templating

## O que é

Técnica de construir prompts reutilizáveis para Financial Planning & Analysis usando variáveis parametrizáveis. Template define estrutura (contexto, tarefa, formato de input/output), deixando espaços em branco para dados específicos (período, valores, regiões).

## Como funciona

Um template é um markdown estruturado com placeholders:

```markdown
# Análise de Tendências [PRODUTO]

## Contexto
- Empresa: [EMPRESA]
- Período: [PERÍODO]
- Segmento: [SEGMENTO]

## Dados
[DADOS_CSV]

## Tarefa
Analise tendência de [MÉTRICA] para [PERÍODO].
Retorne: CAGR, sazonalidade, outliers, projeção.

## Instruções
- Usar média móvel [JANELA]-períodos
- Threshold de outlier: Z-score > [THRESHOLD]
- Output em formato Markdown com gráfico ASCII
```

Ao usar, substitui placeholders:

```markdown
# Análise de Tendências SaaS

## Contexto
- Empresa: TechCorp
- Período: 2024-2026
- Segmento: Enterprise

## Dados
Q1 2024,$500K
Q2 2024,$520K
...
```

**Benefícios:**
- Reutilização: mesmo template para 10 empresas diferentes
- Consistência: mesma estrutura, mesma qualidade
- Velocidade: preencher 5 variáveis vs escrever novo prompt
- Escalabilidade: templates podem ser versionadas e melhoradas

## Pra que serve

- Criar biblioteca de prompts reutilizáveis para equipe FP&A
- Padronizar análises (tendência, variância, cenários)
- Reduzir tempo de setup para cada novo relatório
- Permitir non-technical users usarem Claude sem escrever prompts
- [[450_skills_workflows_claude]]
- [[30_prompts_claude_fp_a_analise]]

## Exemplo prático

**Template em YAML:**

```yaml
name: "Análise de Variância Orçada vs Realizado"
version: "1.0"
category: "reporting"
parameters:
  - name: "período"
    type: "string"
    example: "Q1-Q2 2026"
  - name: "orçado"
    type: "dict"
    example: {"receita": 1250000, "despesa": 600000}
  - name: "realizado"
    type: "dict"
    example: {"receita": 1535000, "despesa": 638000}
  - name: "thresholds"
    type: "dict"
    default: {"warning": 0.05, "critical": 0.10}

prompt_template: |
  Período: {{ período }}

  Orçamento:
  {{ orçado | format_table }}

  Realizado:
  {{ realizado | format_table }}

  Tarefa:
  1. Calcule variância em % para cada linha
  2. Identifique drivers principais (volume, preço, mix, operacional)
  3. Flag items com variância > {{ thresholds.warning }}
  4. Retorne recomendações de reforecast

  Output: Tabela + narrativa executiva (máx 5 insights)
```

**Uso em Python:**

```python
from jinja2 import Template
import yaml

# Carrega template
with open("variance-analysis.yaml") as f:
    template_spec = yaml.safe_load(f)

# Substitui variáveis
template = Template(template_spec["prompt_template"])

params = {
    "período": "Q1-Q2 2026",
    "orçado": {"receita": 1250000, "despesa": 600000},
    "realizado": {"receita": 1535000, "despesa": 638000},
    "thresholds": {"warning": 0.05, "critical": 0.10}
}

prompt_final = template.render(**params)

# Envia para Claude
response = client.messages.create(
    model="claude-3-5-sonnet-20241022",
    max_tokens=2000,
    messages=[{"role": "user", "content": prompt_final}]
)
```

## Armadilhas

- **Template pollution**: muitos placeholders = prompt confuso. Manter <= 10 variáveis
- **Falta de validação**: se passar dados inválidos (e.g., strings em campo numérico), Claude pode falhar
- **Atualização de templates**: se descobrir template ruim, precisa reprocessar histórico
- **Coupling**: se mudar template, pode quebrar pipelines antigos

## Aparece em
- [[30_prompts_claude_fp_a_analise]] - Biblioteca de prompts FP&A
- [[450_skills_workflows_claude]] - Workflows reutilizáveis

---
*Conceito extraido em 2026-04-02*
