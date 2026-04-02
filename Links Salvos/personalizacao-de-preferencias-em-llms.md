---
tags: []
source: https://www.linkedin.com/posts/clarama_if-youre-a-chief-of-staff-switching-to-claude-share-7441832145192472576-d926?utm_source=share&utm_medium=member_android&rcm=ACoAAAgQrLIB4LHRfm8oNhRCsOv9i7wGJSYJXQs
date: 2026-04-02
---
# Personalização de Preferências em LLMs

## Resumo
Configurar preferências pessoais em modelos de linguagem como o Claude reduz comportamentos genéricos e transforma o modelo em um parceiro de pensamento mais eficaz e menos subserviente.

## Explicação
Modelos de linguagem grandes (LLMs) como o Claude possuem comportamentos padrão que, embora funcionais para o público geral, introduzem ruídos específicos em contextos profissionais: linguagem terapêutica desnecessária, ganchos narrativos artificiais, formatações que sinalizam autoria por IA (como o travessão em excesso) e a tendência de gerar entregáveis imediatamente sem explorar o problema junto ao usuário.

A personalização via "Personal Preferences" (Settings → Profile → Personal Preferences) atua como uma camada de instrução persistente que condiciona o comportamento do modelo antes mesmo de qualquer prompt. É funcionalmente equivalente a um system prompt de nível usuário — diferente dos system prompts de projetos, que têm escopo mais restrito. Isso significa que as instruções de preferências se aplicam globalmente a todas as conversas, tornando-se uma forma de engenharia de comportamento contínua sem necessidade de repetição.

Um aspecto técnico relevante destacado no conteúdo é a separação entre modo exploratório e modo de entrega: instruir o modelo a "não pular para entregáveis" até receber um sinal explícito ("proceed") força o LLM a operar em modo socrático antes do modo executivo. Isso combate a tendência dos modelos de colapsar prematuramente a incerteza do usuário em outputs — um problema conhecido como "solucionismo prematuro" em design de prompts. A combinação com um tópico-âncora definido na primeira mensagem cria um mecanismo de escopo conversacional que o modelo usa como referência para redirecionar desvios.

A eliminação de marcadores linguísticos de IA (contrast framing, em dashes, engagement bait) também serve a um segundo propósito além da qualidade textual: reduzir a friction cognitiva de revisar outputs antes de publicação, já que o texto chega mais próximo do estilo humano desejado desde a primeira geração.

## Exemplos
1. **Controle de entrega via trigger word:** Adicionar "não crie nada até eu dizer 'executar'" nas preferências evita que o Claude gere documentos longos no meio de uma sessão de brainstorming ainda em aberto.
2. **Brand guide como arquivo de projeto:** Criar um guia de marca via Claude, exportá-lo e anexá-lo como arquivo em um projeto faz com que todos os documentos gerados naquele contexto sigam automaticamente o tom, vocabulário e estética definidos — sem repetir instruções a cada conversa.
3. **Redução de sinalização de IA em textos:** Remover o uso de travessões (em dashes) e fórmulas como "but here's the thing" das preferências produz textos com menor probabilidade de serem identificados como gerados por IA em publicações profissionais como o LinkedIn.

## Relacionado
*(Nenhuma nota relacionada disponível no vault no momento.)*

## Perguntas de Revisão
1. Qual a diferença funcional entre configurar preferências pessoais globais e usar system prompts dentro de projetos específicos no Claude?
2. Por que instruir o modelo a permanecer em modo exploratório antes de gerar entregáveis pode melhorar a qualidade final do output?

## Histórico de Atualizações
- 2026-04-02: Nota criada a partir de Telegram