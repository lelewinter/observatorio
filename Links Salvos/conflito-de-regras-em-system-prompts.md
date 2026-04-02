---
tags: [prompt-engineering, llm, instrucoes-contraditorias, degradacao-de-output]
source: https://x.com/itsolelehmann/status/2036836910971470319?s=20
date: 2026-04-02
---
# Conflito de Regras em System Prompts

## Resumo
Acumular instruções incrementais em prompts de sistema ao longo do tempo tende a gerar contradições internas que degradam silenciosamente a qualidade dos outputs do modelo.

## Explicação
Ao customizar modelos de linguagem como o Claude via system prompts, é comum a prática de adicionar novas regras e comportamentos de forma incremental — uma instrução por vez, ao longo de semanas ou meses. O problema é que esse processo orgânico raramente inclui uma revisão holística do conjunto de regras já existentes. O resultado é um prompt que cresce em volume, mas decresce em coerência interna.

Quando duas ou mais regras se contradizem, o modelo não lança um erro explícito. Em vez disso, ele tenta reconciliar as instruções conflitantes, geralmente produzindo outputs mediocres, inconsistentes ou que atendem parcialmente a múltiplos critérios ao mesmo tempo — o pior dos mundos. Esse fenômeno é especialmente insidioso porque a degradação é gradual e difícil de atribuir a uma causa específica.

A solução proposta é um processo de "detox" do prompt: uma revisão deliberada e periódica de todas as regras ativas, com o objetivo de identificar contradições, eliminar redundâncias e consolidar instruções conflitantes em diretrizes unificadas. Esse processo funciona como uma refatoração de código — não adiciona novas funcionalidades, mas restaura a integridade estrutural do sistema.

Do ponto de vista técnico, isso reflete uma limitação fundamental dos LLMs: eles não possuem mecanismo nativo de resolução de conflitos entre instruções. O modelo é treinado para obedecer ao prompt, não para auditá-lo. A responsabilidade de manter a coerência interna das instruções recai inteiramente sobre o engenheiro de prompt ou o usuário.

## Exemplos
1. **Customização de assistente de escrita**: após meses adicionando regras ("seja conciso", "sempre forneça contexto histórico", "use bullet points", "prefira parágrafos corridos"), o modelo alterna aleatoriamente entre formatos sem critério claro.
2. **Agente de suporte ao cliente**: regras de tom ("seja empático e acolhedor" vs. "seja direto e objetivo") geram respostas que soam artificialmente neutras e sem personalidade.
3. **Processo de detox**: exportar todas as regras do system prompt, pedir ao próprio modelo para identificar contradições e propor uma versão consolidada e coerente.

## Relacionado
*(Nenhuma nota existente no vault para linkar no momento.)*

## Perguntas de Revisão
1. Por que um LLM não sinaliza explicitamente quando recebe instruções contraditórias em um system prompt?
2. Qual é a diferença entre um prompt com muitas regras coerentes e um prompt com poucas regras contraditórias — qual tende a produzir melhores outputs?

## Histórico de Atualizações
- 2026-04-02: Nota criada a partir de Telegram