---
tags: [claude, skills, workflows, produtividade, ferramentas]
source: https://www.linkedin.com/posts/sairam-sundaresan_think-youve-mastered-claude-you-havent-share-7436968814027763713-XNeu
date: 2026-03-13
tipo: aplicacao
---

# Implementar Skills e Workflows Reutilizáveis com Claude

## O que é

Skills são workflows estruturados e testados pela comunidade que transformam Claude em especialista para domínio específico (dev, pesquisa, análise, segurança). Repositório com 450+ skills categorizado em 25+ categorias, prontos para copiar, adaptar, e integrar.

## Como implementar

### Setup: Organizar Skills Localmente

Estrutura recomendada:

```
claude-skills/
├── dev/
│   ├── code-review-3-fases/
│   │   ├── SKILL.md         # Documentação + prompts
│   │   ├── config.json      # Parâmetros
│   │   └── examples/
│   │       └── exemplo-review.md
│   ├── generate-unit-tests/
│   ├── refactoring-assistant/
│   └── documentation-auto/
├── research/
│   ├── paper-summarizer/
│   ├── extract-citations/
│   ├── correlate-papers/
│   └── literature-review/
├── data/
│   ├── csv-explorer/
│   ├── anomaly-detector/
│   ├── visualization-suggester/
│   └── insight-generator/
├── security/
│   ├── log-forensics/
│   ├── threat-hunter/
│   ├── metadata-extractor/
│   └── incident-reporter/
└── business/
    ├── fpa-analyzer/
    ├── market-tracker/
    ├── competitor-intel/
    └── kpi-dashboard/
```

### Skill Template

Estrutura padrão de um skill:

```markdown
---
name: "Code Review - 3 Fases"
version: "1.2"
category: "dev"
tags: [code-review, quality, best-practices]
author: "Comunidade Claude"
---

# Code Review - 3 Fases

## O que faz
Realiza revisão de código em 3 fases estruturadas:
1. Superficial: syntaxe, naming, anti-patterns
2. Estrutural: arquitetura, modularidade, testes
3. Estratégica: performance, segurança, manutenibilidade

## Como usar

### Input
- Linguagem: [Python/JavaScript/Go/Rust]
- Código: [Cole o código a revisar]
- Contexto: [Framework, padrões usados, constraints]

### Prompt Fase 1: Superficial
\`\`\`
Revise este código focando em:
1. Convenções de naming (snake_case em Python, camelCase em JS)
2. Linhas muito longas (>80 chars)
3. Funções muito grandes (>20 linhas)
4. Variáveis reutilizadas / shadowing
5. Anti-patterns óbvios (nested ifs profundos, copy-paste)

[CÓDIGO]

Formato: Markdown com line-by-line comments, não reescrever tudo.
\`\`\`

### Prompt Fase 2: Estrutural
\`\`\`
Agora foco em:
1. Modularidade: funções fazem UMA coisa?
2. Abstrações: há níveis apropriados?
3. Testes: há coverage para casos principais?
4. Error handling: trata casos edge?
5. Dependências: acoplamento necessário ou pode reduzir?

[CÓDIGO + COMENTÁRIOS DA FASE 1]

Retorne: estruturas a refatorar + exemplos.
\`\`\`

### Prompt Fase 3: Estratégica
\`\`\`
Finalmente, analize:
1. Performance: há O(N²) que poderia ser O(N)?
2. Segurança: entrada validada? SQL injection? XXS?
3. Escalabilidade: funciona com 1M registros?
4. Testabilidade: fácil de mockar dependências?
5. Manutenibilidade: 6 meses depois alguém consegue entender?

[CÓDIGO COMPLETO + TODAS AS FASES]

Output: Top-5 achados críticos + plano de refactoring.
\`\`\`

## Armadilhas
- Fase 1 muito rápida: pular erros óbvios
- Fase 2 sem exemplos: recomendações genéricas
- Fase 3 sem métricas: "melhore performance" sem dados
```

### Skill Prático: CSV Explorer

```markdown
# CSV Explorer - Análise Rápida de Dados

## Input
- Arquivo CSV (cole os primeiros 50 linhas)
- Pergunta: "O que há de interessante aqui?"

## Execução

### Prompt 1: Diagnóstico
\`\`\`
Analise este CSV:

[CSV SAMPLE]

Retorne:
1. Dimensões: quantas linhas, colunas, tipos de dados
2. Qualidade: nulls %, duplicatas %, tipos inconsistentes
3. Range: min/max para numéricos, cardinalidade para categoriais
4. Curiosidades: distribuição não-uniforme, outliers óbvios
\`\`\`

### Prompt 2: Exploração
\`\`\`
Dado [RESULTADO PROMPT 1], sugira:
1. Visualizações mais úteis (histograma, scatter, boxplot)
2. Correlações interessantes a investigar
3. Segmentações possíveis
4. Anomalias a investigar

Foco: 5 perguntas que poderia fazer depois.
\`\`\`

### Prompt 3: Insights
\`\`\`
Com tudo analisado, resuma em 1 parágrafo:
- Qual é a história dos dados?
- O que mudou ao longo do tempo?
- Qual segmento é mais interessante?
- Recomendação para próximo passo.
\`\`\`
```

### Integração em Workflow: Sequência de Skills

Exemplo pipeline: Dev + Research + FP&A

```python
from claude_sdk import Claude

client = Claude()

# Skill 1: Code Review
code = """
def calculate_revenue(orders):
    total = 0
    for order in orders:
        total = total + order.amount
    return total
"""

review_1 = client.run_skill(
    skill="code-review-3-fases",
    inputs={"code": code, "language": "python"}
)
# Output: Fase 1 superficial

# Skill 2: Generate Tests (baseado em review)
tests = client.run_skill(
    skill="generate-unit-tests",
    inputs={"code": code, "review": review_1}
)

# Skill 3: Document (baseado em tudo)
docs = client.run_skill(
    skill="documentation-auto",
    inputs={"code": code, "review": review_1, "tests": tests}
)

# Output final: Code + Tests + Documentation
```

## Stack e requisitos

**Descoberta:**
- Repositório oficial: https://github.com/anthropics/...
- Filtros: por categoria, linguagem, tempo de execução
- Versionamento: semantic versioning (v1.0, v1.1, v2.0)

**Implementação:**
- Claude 3.5 Sonnet: roda maioria dos skills
- Token budget: ~50K-100K tokens por skill grande
- Custo: ~$0.02-0.10 por execução

**Otimizações:**
- Cache prompts (Claude prompt caching)
- Batch processing: rodar múltiplos skills em paralelo
- Versionar resultados (git, Notion)

**Ferramentas complementares:**
- Integração VS Code: Codeium, GitHub Copilot + Claude skills
- Pipeline CI/CD: rodar skill em cada PR
- Documentação: Obsidian + skills para research

## Armadilhas e limitações

**Descoberta:**
- 450+ skills é avassalador. Comece com 5-10 no seu domínio
- Skills podem estar desatualizadas (versão 1.0 pode ter bugs)
- Comunidade = qualidade variável

**Implementação:**
- Adaptar skill para seu contexto requer entender a lógica
- Skill pode referenciar ferramentas externas não instaladas
- Output de uma skill pode não ser compatível com entrada de outra (coupling)

**Custo:**
- Skills complexas (code review de 1000 linhas) = $0.50+
- Iteração = custos acumulam rapidamente
- Batch processing reduz custo em 10x

**Risco:**
- Skills públicas podem gerar output sensível (PII, secrets)
- Sempre revisar output antes de usar em produção
- Validar dados antes de passar para skill

## Conexões

[[30_prompts_claude_fp_a_analise]] - FP&A skills
[[Last30Days Skill Prompts Comunidade]] - Comunidade e descoberta
[[claude-code-superpowers]]
[[boas-praticas-claude-code]]
[[code-review-checklist-3-fases-claude-code]]

## Histórico

- 2026-03-13: Nota criada
- 2026-04-02: Reescrita como guia prático com exemplos, templates, integração
