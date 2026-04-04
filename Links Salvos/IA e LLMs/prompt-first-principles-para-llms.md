---
tags: [first-principles, prompt-engineering, llm, raciocinio, ia]
source: https://x.com/aiwithmayank/status/2035314341965447270?s=20
date: 2026-04-02
tipo: aplicacao
---

# Usar Prompts de Primeiros Princípios para Decomposição Analítica

## O que é

Padrão de prompt que força LLM a desmontar suposições camada por camada até base irredutível (bedrock), reconstruindo entendimento sem conhecimento herdado. Alterna LLM de modo "recuperação de informação" para modo "decomposição epistemológica".

## Como implementar

**Template base:**
```
Analise [CONCEITO] usando primeiros princípios.

Instruções:
1. Identifique TODAS as suposições implícitas que você carrega sobre [CONCEITO]
2. Para cada suposição, questione:
   - É uma verdade física/lógica, ou uma construção social?
   - Qual é a evidência mais primitiva para isso?
   - Se remover essa suposição, o que permanece verdadeiro?
3. Strip each assumption away iterativamente até atingir bedrock
4. A partir do bedrock, reconstrua [CONCEITO] do zero

Formato de resposta:
- Camada 1: Suposições superficiais
- Camada 2: Suposições subjacentes
- ...
- Bedrock: Verdade irredutível
- Reconstrução: Novo entendimento sem suposições
```

**Exemplo prático:**
```
Analise "reunião produtiva" usando primeiros princípios.

Instruções: [template acima]
```

Esperado:
```
Camada 1: "Uma reunião produtiva é quando todos falam"
  Questão: Por que "falar" = produtivo?
  Insight: Assumimos que comunicação verbal é necessária

Camada 2: "Reunião requer presença síncrona"
  Questão: É síncrono fundamental, ou conveniência histórica?
  Insight: Síncronismo vem de era pré-digital; pode ser assíncrono

Camada 3: "Reunião precisa resolver problema"
  Questão: E se objetivo é socializar ou informar, não resolver?
  Insight: "Produtivo" é definido por resultado, não atividade

Bedrock: Reunião produtiva = transferência eficiente de contexto entre pessoas

Reconstrução: Uma reunião é produtiva se:
- Reduz tempo para que pessoas alcancem goal (cualquer goal, não só "resolver problema")
- Pode ser síncrona, assíncrona, ou híbrida — o meio é irrelevante
- Métrica: Tempo economizado vs. Tempo gasto
```

**Aplicação temática:**

Para **economia:**
```
Analise "inflação é ruim" usando primeiros princípios.
[template padrão]
```

Para **desenvolvimento:**
```
Analise "código limpo é sempre melhor" usando primeiros princípios.

Bedrock esperado: Código é ferramenta para intenção. "Limpo" é trade-off entre legibilidade (humana) e velocidade (desenvolvimento).
```

Para **educação:**
```
Analise "memorização é inferior à compreensão" usando primeiros princípios.

Bedrock esperado: Memorização e compreensão são dimensões ortogonais. Ambas têm valor em contextos diferentes.
```

**Estrutura de iteração.** Se resposta do LLM fica superficial, re-prompt:
```
Você ainda está usando conhecimento herdado. Para a suposição "X",
desça uma camada: qual é a verdade MAIS PRIMITIVA que suporta X?
Ignora convenção.
```

Força LLM a descer mais fundo.

## Stack e requisitos

- LLM com capacidade de raciocínio estendido (Claude 3.5 Sonnet+, GPT-4, Gemini 2.0 recomendado)
- Tema com alta "bagagem conceitual" (educação, economia, negócios, filosofia)
- Tempo: 5-15 minutos por análise
- Sem custos adicionais (usa LLM já disponível)

## Armadilhas e limitações

LLM pode travar em loops de auto-referência ("o que é verdade? a verdade é...") — interrompa e re-direcione. Para temas com base física bem estabelecida (física, química), bedrock é alcançado rápido; para temas sociais (economia, educação), bedrock é multifacetado. LLM pode confundir "primeiros princípios" com "definiçõe simples" — re-enforce que "bedrock" é evidência mais primitiva, não resumo. Resposta fica muito longa — considere dividir por suposição individual.

## Conexões

[[Simplificar Setup Claude Deletar Regras Extras]], [[Plan Mode Claude Code]], [[Spec-Driven Development]]

## Histórico

- 2026-04-02: Nota criada
- 2026-04-02: Reescrita como guia de uso