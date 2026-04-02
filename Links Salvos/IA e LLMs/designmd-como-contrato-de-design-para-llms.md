---
tags: []
source: https://x.com/GithubProjects/status/2039274093657325783?s=20
date: 2026-04-02
---
# DESIGN.md como Contrato de Design para LLMs

## Resumo
`DESIGN.md` é um arquivo Markdown colocado na raiz de um projeto para descrever o sistema de design em linguagem natural, funcionando como instrução estrutural que agentes de IA leem para gerar interfaces consistentes.

## Explicação
O conceito surge do Google Stitch e estende a convenção do `README.md` — arquivo de documentação técnica amplamente adotado em repositórios — para o domínio de sistemas de design. Enquanto o `README.md` descreve *o que o projeto faz e como rodar*, o `DESIGN.md` descreve *como o projeto deve parecer e se comportar visualmente*: paleta de cores, tipografia, espaçamento, tom de voz, componentes recorrentes e princípios de UI.

A relevância prática está na relação com LLMs e agentes de codificação. Modelos de linguagem como GPT-4, Claude ou Gemini não têm acesso implícito ao design system de um projeto — eles inferem padrões a partir do código existente, o que gera inconsistências. O `DESIGN.md` funciona como um **contrato explícito de contexto de design** injetado no prompt ou no contexto do agente, reduzindo alucinações visuais e garantindo coerência entre componentes gerados automaticamente.

Do ponto de vista técnico, por ser plain Markdown, o arquivo é leve, versionável via Git, legível por humanos e facilmente consumível por ferramentas como Cursor, GitHub Copilot Workspace ou qualquer pipeline RAG sobre o repositório. A iniciativa de criar coleções de `DESIGN.md` inspiradas em empresas como Stripe, Vercel, Linear e Figma transforma o conceito em um padrão emergente de comunidade, análogo aos *dotfiles* ou *boilerplates* de configuração.

O ponto de tensão relevante é que o arquivo depende de manutenção manual: se o design system evoluir e o `DESIGN.md` não for atualizado, o agente passa a gerar UI baseada em especificações desatualizadas. Isso cria uma nova categoria de débito técnico — o **débito de contexto de IA**.

## Exemplos
1. **Agente de codificação gerando formulários**: com um `DESIGN.md` descrevendo border-radius de 8px, fonte Inter e paleta de cores específica, o agente gera inputs e botões visualmente consistentes sem precisar inspecionar o CSS existente.
2. **Onboarding de novos devs com IA**: um desenvolvedor novo usa o Cursor com o `DESIGN.md` do projeto e recebe sugestões de componentes já alinhadas ao design system da empresa, sem precisar ler documentação extensa.
3. **Prototipagem rápida**: ao iniciar um projeto do zero, copiar um `DESIGN.md` inspirado no design system da Linear ou Vercel permite que o agente construa o MVP com identidade visual coerente desde o primeiro componente.

## Relacionado
*(Nenhuma nota existente no vault para conectar neste momento.)*

## Perguntas de Revisão
1. Qual a diferença fundamental entre `README.md` e `DESIGN.md` em termos de audiência e propósito?
2. Como o conceito de **débito de contexto de IA** se distingue do débito técnico tradicional, e quais estratégias mitigam esse problema?

## Histórico de Atualizações
- 2026-04-02: Nota criada a partir de Telegram