---
tags: []
source: https://x.com/rubenhassid/status/2034999221703581818?s=20
date: 2026-04-02
---
# Contexto Persistente em LLMs

## Resumo
Em vez de depender apenas de prompts isolados, é possível fornecer ao modelo um conjunto de arquivos de contexto pessoal que ele lê antes de cada resposta, tornando a interação muito mais consistente e alinhada ao estilo do usuário.

## Explicação
A ideia central é que **prompting pontual é uma forma fraca de usar modelos de linguagem avançados como o Claude**. O problema com prompts isolados é que eles não carregam memória de longo prazo sobre quem é o usuário, como ele pensa, como ele escreve, ou quais são seus critérios de qualidade. Cada sessão começa do zero.

A solução proposta é construir um **sistema de contexto persistente**: criar arquivos `.md` que descrevem o usuário — identidade, estilo de escrita, exemplos de trabalho, restrições ("do nots") — e carregá-los automaticamente antes de cada interação. No Claude, isso é feito via a aba "Cowork", que permite fazer upload de uma pasta inteira de arquivos `.md`. O modelo lê todos esses arquivos antes de responder, funcionando como uma memória externa estruturada.

Esse padrão é essencialmente uma forma manual e explícita de **RAG (Retrieval-Augmented Generation)** aplicado ao nível do usuário: em vez de recuperar documentos de uma base de conhecimento externa, o sistema recupera documentos de contexto pessoal. A diferença é que aqui o "retrieval" é total e explícito — todos os arquivos são lidos, não apenas os mais relevantes por similaridade.

O workflow também propõe dois meta-prompts importantes: um para iniciar tarefas pedindo ao modelo que faça perguntas de esclarecimento antes de agir, e outro para redirecionar conversas que saíram do trilho sem perder o contexto acumulado. Isso introduz um princípio de **controle de trajetória conversacional**, tratando a sessão como um projeto iterativo, não como uma troca de mensagens.

## Exemplos
1. **Criação de conteúdo consistente**: Um criador de conteúdo sobe arquivos `.md` com exemplos de posts anteriores, tom de voz e temas proibidos. O Claude escreve novos posts alinhados ao estilo histórico sem precisar reexplicar a cada sessão.
2. **Consultoria técnica personalizada**: Um desenvolvedor cria um arquivo `about-me.md` descrevendo sua stack, nível de senioridade e preferências de código. O modelo evita sugerir tecnologias fora do escopo e calibra a profundidade das explicações.
3. **Atualização incremental de contexto**: À medida que o gosto ou os critérios do usuário evoluem, ele faz upload do arquivo antigo e pede ao modelo que o atualize com as mudanças, criando um ciclo de refinamento contínuo do contexto.

## Relacionado
*(Nenhuma nota existente no vault para linkar no momento.)*

## Perguntas de Revisão
1. Qual é a diferença fundamental entre um prompt isolado e um sistema de contexto persistente em termos de coerência de saída do modelo?
2. Em que sentido esse método se assemelha a RAG, e em que ponto ele diverge da abordagem clássica de recuperação por similaridade?

## Histórico de Atualizações
- 2026-04-02: Nota criada a partir de Telegram