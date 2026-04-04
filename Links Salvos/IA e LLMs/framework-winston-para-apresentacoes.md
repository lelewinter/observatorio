---
tags: [apresentações, prompting, frameworks, comunicação, claude, ai]
source: https://x.com/godofprompt/status/2039258111543046403?s=20
date: 2026-04-02
tipo: aplicacao
---
# Framework Winston: Estrutura de Apresentação Oral via Prompts no Claude

## O que e
Patrick Winston (MIT) desenvolveu framework de comunicação oral ensinado por 40 anos que destila uma apresentação memorável em elementos específicos: abertura impactante, promise clara, cerca de escopo, exemplos concretos, repetição estratégica, fechamento forte. Framework codificado em 6 prompts estruturados transforma conteúdo bruto em apresentação profissional via Claude.

## Como implementar
**6-prompt sequence**: (1) **Abertura**: Claude gera gancho que não é piada (Winston detesta piadas em abertura), estabelece promise ("ao final você vai saber como implementar RAG em produção"), (2) **Fence**: define limites do assunto ("vamos cobrir apenas text-to-vector, não image embeddings"), (3) **Exemplos**: estrutura exemplos progressivos do simples ao complexo, (4) **Tema repetido**: identifica ideia central e a repete em variações (3-5x) ao longo da apresentação sem ser repetitivo, (5) **Estrutura interna**: organiza blocos com transições claras, cada slide contribui ao promise, (6) **Fechamento**: gera conclusão memorável que deixa contribuição clara (não "alguma pergunta?"). Cada prompt recebe conteúdo anterior como input, refinando progressivamente. Usuário fornece: tópico, audiência, duração, contexto. Claude estrutura seguindo Winston.

Padrão é essencialmente "persona especialista + tarefa estruturada": modelo assume papel de consultor treinado em retórica de Winston, aplica método sistematicamente.

## Stack e requisitos
Claude 3.5 Sonnet+. Sem dependências técnicas. Inputs: slide deck ou outline (txt/md). Tempo: 1-2 horas para estruturar apresentação de 30 minutos completa. Saída: Markdown estruturado ou notas speaker prontas para Powerpoint/Keynote.

## Armadilhas e limitacoes
Framework de Winston é para oralidade, não para leitura de slides — apresentação final deve ser entregue verbalmente, não lida. IA pode gerar "cerca" genérica; validar que é específica ao seu conteúdo. Promise precisa ser honrada — se estrutura diz "vou ensinar", você DEVE ensinar; promise vazio destrói credibilidade. Repetição estratégica pode virar repetição óbvia se não for subtil — revisar áudio gravado para checar naturalidade.

## Conexoes
[[geracao-automatizada-de-prompts|Prompt engineering]]
[[contexto-persistente-em-llms|Contexto estruturado]]
[[explicabilidade-como-medida-de-compreensao|Clareza conceitual]]

## Historico
- 2026-04-02: Nota criada
- 2026-04-02: Reescrita pelo pipeline
