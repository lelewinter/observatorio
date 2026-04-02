---
tags: [first-principles, prompt-engineering, llm, raciocinio, ia]
source: https://x.com/aiwithmayank/status/2035314341965447270?s=20
date: 2026-04-02
---
# Prompt First Principles para LLMs

## Resumo
Um prompt estruturado que força LLMs a desmontar suposições sobre um tema e reconstruir o conceito a partir apenas do que é fundamentalmente verdadeiro, evitando respostas baseadas em conhecimento convencional repetido.

## Explicação
O raciocínio por primeiros princípios é uma técnica filosófica e científica — popularizada por pensadores como Aristóteles e, modernamente, por engenheiros como Elon Musk — que consiste em decompor um problema até suas verdades irredutíveis, eliminando suposições herdadas. O insight aqui é que LLMs, sem instrução específica, tendem a reproduzir o entendimento médio e consensual sobre um tema, ou seja, o "conhecimento herdado" presente em seu corpus de treinamento.

O prompt proposto atua como um operador cognitivo explícito: ao incluir a instrução "strip each assumption away", o modelo é forçado a iterar camada por camada, identificando e removendo cada pressuposto até atingir o que o prompt chama de "bedrock" — a base factual irredutível. A reconstrução a partir desse ponto gera uma compreensão estruturalmente diferente da resposta padrão.

O mecanismo funciona porque LLMs são sensíveis à estrutura e ao vocabulário do prompt. A frase-chave "strip each assumption away" serve como gatilho para um modo de decomposição analítica, diferente do modo padrão de recuperação e síntese de informação. É engenharia de prompt aplicada à epistemologia: você não está pedindo *o que* o modelo sabe, mas *como* ele deve processar o conhecimento antes de responder.

Do ponto de vista prático, este prompt é especialmente útil quando se estuda um tema que carrega muita bagagem conceitual — economia, saúde, educação, física — onde as explicações convencionais mascaram os mecanismos reais com metáforas e simplificações consolidadas.

## Exemplos
1. **Aprendizado:** "Break 'memorização é inferior à compreensão' down using first principles..." → força questionar o que é compreensão, o que é memorização e se a distinção é real ou cultural.
2. **Negócios:** Aplicar ao conceito de "reunião produtiva" para descobrir quais suposições sobre colaboração são herdadas de modelos industriais e quais são fundamentalmente necessárias.
3. **Tecnologia:** Usar o prompt para decompor "banco de dados relacional é o padrão" e identificar quais propriedades são fisicamente necessárias versus historicamente contingentes.

## Relacionado
*(Nenhuma nota existente no vault para linkar neste momento.)*

## Perguntas de Revisão
1. Qual é a diferença entre pedir a um LLM para "explicar" um tema versus usar este prompt de primeiros princípios — o que muda estruturalmente na resposta?
2. Em quais tipos de temas o raciocínio por primeiros princípios é mais valioso, e por quê temas com alto "conhecimento herdado" são os candidatos ideais?

## Histórico de Atualizações
- 2026-04-02: Nota criada a partir de Telegram