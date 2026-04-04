---
tags: [Claude, pesquisa, literature review, prompts, PhD, papers, conhecimento estruturado, synthesis]
source: https://x.com/aiwithjainam/status/2031282913422225567
date: 2026-03-10
tipo: aplicacao
---

# Sistematizar Literature Review com 9 Prompts para Análise Crítica

## O que é

Sequência de 9 prompts que transforma pilha de 30-50 papers acadêmicos em análise estruturada: mapeamento, contradições, genealogia de conceitos, gaps de pesquisa, síntese integrada, pressupostos testáveis, outliers, recomendações. Simula rigor de PhD em Stanford.

## Como implementar

### Setup: Preparar Corpus de Papers

```python
# Struktur local
research-corpus/
├── papers.pdf/
│   ├── paper-1.pdf (Smith et al 2023)
│   ├── paper-2.pdf (Jones et al 2023)
│   └── ... (30-50 papers)
├── prompts.md
└── outputs/
    ├── 1-intake-protocol.md
    ├── 2-contradictions.md
    ├── 3-citation-chains.md
    └── ... (9 outputs)

# Para uso com Claude:
# 1. Upload todos os PDFs (ou copiar texto)
# 2. Executar Prompt 1
# 3. Guardar output
# 4. Executar Prompt 2 com contexto de Prompt 1
# ... e assim sucessivamente
```

### Prompt 1: The Intake Protocol

```
PROMPT 1: Organizar Corpus

Vou compartilhar [X] papers sobre [TÓPICO].

Antes de qualquer pergunta, faça isso:

1. **Tabela de Resumo:**
   | # | Autor | Year | Core Claim (1 frase) | Método | Achado Principal |
   |---|-------|------|----------------------|--------|-----------------|
   | 1 | Smith | 2023 | Hallucinations vêm de training data | Experimento | Correlação 0.87 |
   | 2 | Jones | 2023 | Hallucinations vêm de decoding | Teórico | Mecanismo proposto |

2. **Clusters de Premissas Compartilhadas:**
   - Grupo A (N papers): Assumem que "X causa Y"
   - Grupo B (N papers): Assumem que "Y não existe"
   - Grupo C (N papers): Agnóstico

3. **Gaps Óbvios:**
   - Ninguém estudou Z
   - Poucos papers testam em contextos reais
   - Faltam replicações

[COLAR AQUI RESUMO OU LISTA DE PAPERS]

OUTPUT:
- Tabela estruturada
- Mapa visual (ASCII) de clusters
- Top-5 pressupostos compartilhados
```

### Prompt 2: The Contradiction Finder

```
PROMPT 2: Encontrar Contradições

Com base no corpus analisado no Prompt 1:

Identifique CADA PONTO onde 2+ autores contradizem diretamente.

Para CADA contradição, retorne:
| Paper A | Paper B | Posição A | Posição B | Por Que Contradizem | Resolução Possível |
|---------|---------|-----------|-----------|-------------------|-------------------|
| Smith 23 | Jones 23 | "Causa é training data" | "Causa é decoding" | Diferentes mecanismos | Ambos podem estar certos (contribuições multifatoriais) |

IMPORTANTE:
- Contradição = afirmações inversas, não apenas diferentes ênfases
- Se Paper A diz "90%" e Paper B diz "80%" = diferença, não contradição
- Se Paper A diz "causa X" e Paper B diz "causa NOT X" = contradição

OUTPUT:
- Tabela de contradições
- Para cada contradição: qual paper tem evidência mais forte?
- Quais contradições são resolveís vs. genuinamente disputadas?
```

### Prompt 3: The Citation Chain

```
PROMPT 3: Genealogia de Conceitos

Identifique os 5 CONCEITOS mais citados across papers.

Para CADA conceito, retorne:

## Conceito: [NOME]

**Origem:** Quem introduziu? Quando? [Ano, autor, paper] Contexto original?

**Evolução:**
- [Ano]: Introdução → [Descrição exata]
- [Ano]: Desafio por X → [Como foi contestado?]
- [Ano]: Refinamento por Y → [Melhoria específica]
- [Ano]: Estado atual → [Como entendemos agora?]

**Árvore genealógica ASCII:**
```
[Autor Original] 2020
    │
    ├─→ [Crítico] 2021 (quebrou pressupostos)
    │    └─→ [Refinador] 2022 (propôs fix)
    │
    └─→ [Extensão] 2021 (novo domínio)
         └─→ [Aplicador] 2023 (prática)
```

**Consenso Atual:** (unificado? Fragmentado? Disputado?)

OUTPUT:
- 5 genealogias completas
- Matriz: qual autor cita quem (pode usar | para referências)
```

### Prompt 4: The Gap Scanner

```
PROMPT 4: Identificar Gaps de Pesquisa

Com base em tudo analisado:

Identifique as 5 QUESTÕES QUE NINGUÉM RESPONDEU COMPLETAMENTE.

Para CADA gap:

## Gap #1: [PERGUNTA]

**Por que existe este gap?**
- Muito difícil de estudar? (por quê?)
- Pouco interesse acadêmico? (por quê?)
- Negligenciado? (por quê?)
- Novo demais?

**Qual paper chegou mais perto?**
- [Paper X]
- Respondeu [X%] da pergunta
- Faltou [o quê?]

**Como fechar este gap?**
- Que metodologia seria adequada?
- Que dados faltam?
- Que colaboração ajudaria?

**Impacto:** Se fechado, qual seria o avanço?

OUTPUT:
- 5 gaps priorizados por impacto
- Para cada: roadmap de pesquisa
```

### Prompt 5: The Methodology Audit

```
PROMPT 5: Auditoria de Metodologias

Compare métodos usados across papers.

## Inventário

| Tipo | # Papers | Exemplos | Rigor | Escalabilidade |
|------|----------|----------|-------|---|
| Survey | 5 | Authors: A, B, C | Baixo | Alta |
| Experimento | 15 | Controlled, N>100 | Alto | Média |
| Simulação | 8 | Synthetic data | Médio | Alta |
| Case Study | 12 | Real-world, N<10 | Médio | Baixa |

## Análise

**Metodologia dominante:** [X tipo] (N% dos papers)
- Por que domina? Maturidade do campo? Viés de publicação?

**Metodologia underutilizada:** [Y tipo]
- Por que falta? Caro demais? Difícil logisticamente?

**Metodologia mais rigorosa:** [Z tipo]
- Qual paper? Por que é rigoroso?

**Metodologia menos rigorosa:** [W tipo]
- Qual paper? Quais são as limitações?

OUTPUT:
- Mapa de metodologias
- Gaps metodológicos
- Recomendação: qual metodologia faria sentido explorar?
```

### Prompt 6: The Master Synthesis

```
PROMPT 6: Síntese Integrada (APÓS prompts 1-5)

Com tudo analisado, escreva síntese que NÃO resume papers individuais.

Em vez disso:

## O que o campo coletivamente acredita?

[2-3 parágrafos sobre verdades compartilhadas]

## O que permanece contestado?

[Contradições fundamentais não resolvidas]

## O que permanece incerto?

[Gaps verdadeiros, pressupostos testáveis]

## Consenso por subtópico

Subtópico A:
- Consenso: [X]
- Evidência: Força: Média/Alta/Baixa
- Dissidentes: [Quem discorda e por quê]

OUTPUT:
- Síntese de 2-3 páginas
- Mapa visual do que se sabe vs. não se sabe
- Recomendação de donde partir daqui
```

### Prompt 7: The Assumption Killer

```
PROMPT 7: Questionar Pressupostos

Que PRESSUPOSTOS a MAIORIA dos papers compartilha
mas NUNCA explicitamente testa ou justifica?

Para CADA pressuposto não-testado:

## Pressuposto: [AFIRMAÇÃO]

**Quantos papers o compartilham?** [X%]

**Evidência que o suporta:**
- Teórica? Empírica? Nenhuma, é apenas assumi

**O que quebraria este pressuposto?**
- Que evidência o destruiria?
- É testável?

**Quais papers dependeriam disso?**
- Se este pressuposto falhar, esses papers caem:
- Paper A (hipótese inteira depende disso)
- Paper B (um resultado depende disso)

**É provável que o pressuposto esteja errado?**
- Baixa chance: evidência indireta é forte
- Média chance: nunca foi testado, poderia falhar
- Alta chance: evidência teórica o contradiz

OUTPUT:
- Top 5 pressupostos perigosos
- Para cada: teste proposto que confirmaria/refutaria
```

### Prompt 8: The Outlier Analysis

```
PROMPT 8: Detectar Outliers

Identifique papers que:
- Ficam sozinhos (única visão)
- Contradizem consenso
- Vêm de outro campo (cross-disciplinar)

Para CADA outlier:

## Paper: [Título]

**Por que é outlier?**
- Metodologia única?
- Conclusão oposta ao consenso?
- De campo diferente?

**É genuinamente diferente, ou foi rejeitado?**
- Boa evidência?
- Replicado? Citado?
- Por que comunidade ignorou?

**Poderia estar certo (e o consenso errado)?**
- Quão credível é o outlier?
- Que evidência o tornaria convincente?

**O que podemos aprender de perspectivas negligenciadas?**
- Qual insight único esse paper tem?

OUTPUT:
- Outliers identificados
- "Heróis não reconhecidos" (outliers que mereciam mais atenção)
- Perspectivas que foi negligenciadas
```

### Prompt 9: The Next Step Recommender

```
PROMPT 9: Recomendar Pesquisa Futura

Dado TUDO acima (Prompts 1-8):

Recomende:

## Gap mais importante a fechar

**Gap:** [Pergunta]
**Por que agora?** Contexto mudou? Ferramentas novas? Aplicações urgentes?
**Quem deveria pesquisar?** Qual expertise é necessária?

## Metodologia ideal

**Proposta:** [Tipo de estudo]
**Por que bater?** (vs. outras metodologias)
**Tamanho esperado:** Quantos participantes/dados?
**Tempo esperado:** Quanto tempo levaria?
**Custo:** Estimativa?

## Ferramentas/dados existentes

**Que pode reaproveitar?** Datasets, code, frameworks publicados
**Que não existe?** O que precisa ser criado

## Colaboração

**Quem deveria colaborar?**
- Grupo A traz expertise em [X]
- Grupo B traz expertise em [Y]
- Resultado esperado de colaboração: [Z]

## Success Criteria

Se você fizesse este estudo, como saberia que funcionou?
- Métrica quantitativa:
- Métrica qualitativa:
- Impacto esperado:

OUTPUT:
- Proposta de pesquisa de 1 página
- "Pitch" do próximo projeto
```

## Stack e requisitos

**Processamento:**
- Claude 3.5 Sonnet (melhor para análise de nuances contraditórias)
- ~50-100K tokens por literatura review completa
- Custo: ~$0.50-1.00 para workflow completo

**Inputs:**
- 30-50 papers (PDF ou texto)
- Tópico bem-definido
- Contexto do pesquisador

**Outputs:**
- 9 documentos estruturados (markdown)
- Síntese integrada
- Roadmap de pesquisa futura

## Armadilhas e limitações

**Sequência importa:**
- Não pule Prompt 1 (organize antes de analisar)
- Prompts 2-5 devem rodar antes de 6 (síntese)
- Prompts 7-8 complementam (questione pressupostos)
- Prompt 9 é final (recomendações)

**Qualidade dos papers:**
- Se corpus é biased (todos mesma visão), análise reflete isso
- Sempre validar que corpus é representativo

**Claude limitations:**
- Pode errar em contradições sutis (linguística vs. substância)
- Pode perder nuances ao sintetizar 50 papers
- Sempre validar manualmente achados principais

**Tempo:**
- 1-2 horas por workflow (vs. 40-60 horas manual)
- Maior impacto em literatura reviews largas (>30 papers)

## Conexões

[[retrieval-augmented-generation]]
[[agente-de-pesquisa-cientifica-com-llm]]
[[agente-de-pesquisa-local-autonomo]]
[[9-prompts-renda-claude-monetizacao-habilidades]]

## Histórico

- 2026-03-10: Nota criada
- 2026-04-02: Reescrita como guia prático com 9 prompts sequenciais executáveis
