---
tags: [apresentações, prompting, frameworks, comunicação, claude, ai]
source: https://x.com/godofprompt/status/2039258111543046403?s=20
date: 2026-04-02
---
# Framework Winston para Apresentações

## Resumo
O framework de comunicação oral desenvolvido por Patrick Winston e ensinado no MIT por 40 anos pode ser aplicado via prompts no Claude para estruturar apresentações de alto impacto.

## Explicação
Patrick Winston foi professor do MIT por décadas e ficou famoso pela aula "How to Speak", considerada uma das mais assistidas da história do instituto. Seu framework identifica elementos fundamentais que tornam uma apresentação memorável e persuasiva: abertura sem piadas, uso de "promise" (o que o ouvinte vai ganhar), construção de cerca ("fence") para delimitar o assunto, uso de exemplos concretos, repetição estratégica de ideias-chave, e um fechamento forte — não um simples "perguntas?".

A novidade prática aqui é a aplicação desse framework via prompts estruturados no Claude. Em vez de o usuário precisar conhecer profundamente a teoria de Winston, ele pode usar um conjunto de 6 prompts que internalizam as diretrizes do framework e as aplicam automaticamente ao conteúdo fornecido. Isso representa um caso clássico de **destilação de conhecimento especializado em instrução de LLM**: o expertise humano vira prompt, o prompt vira output estruturado.

Isso é relevante porque demonstra como frameworks pedagógicos consagrados — originalmente transmitidos em sala de aula — ganham escala infinita quando codificados como instruções para modelos de linguagem. O valor não está no modelo em si, mas na qualidade do framework que orienta o prompt.

Do ponto de vista de engenharia de prompt, o caso ilustra o padrão **"persona especialista + estrutura de tarefa"**: o modelo assume o papel de um consultor treinado num método específico, e cada prompt cobre uma etapa do processo (abertura, estrutura, exemplos, fechamento etc.).

## Exemplos
1. **Prompt de abertura**: instruir o Claude a gerar uma abertura que estabeleça a "promise" — o benefício claro que o ouvinte terá ao final da apresentação.
2. **Prompt de estrutura**: pedir ao Claude para organizar o conteúdo usando "fence" (delimitar escopo) e repetição estratégica dos pontos centrais conforme Winston recomenda.
3. **Prompt de fechamento**: gerar um encerramento que deixe uma contribuição memorável, evitando o anticlímax do "alguma pergunta?" que Winston criticava.

## Relacionado
Nenhuma nota existente no vault para linkar no momento.

## Perguntas de Revisão
1. Quais são os elementos centrais do framework de Winston que mais diferenciam uma apresentação comum de uma memorável?
2. Como a codificação de frameworks pedagógicos em prompts se relaciona com o conceito mais amplo de destilação de conhecimento em LLMs?

## Histórico de Atualizações
- 2026-04-02: Nota criada a partir de Telegram