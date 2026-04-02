---
tags: []
source: https://x.com/gregisenberg/status/2038220390665724001?s=20
date: 2026-04-02
---
# Configuração de Contexto para LLMs

## Resumo
Arquivos `.md` de configuração funcionam como memória persistente e instruções sistêmicas para modelos como Claude, amplificando consistência e qualidade das respostas sem alterar o modelo em si.

## Explicação
A ideia central é usar quatro arquivos Markdown estruturados para fornecer ao Claude (ou qualquer LLM com suporte a contexto persistente) um conjunto fixo de instruções, preferências e conhecimento de domínio. Esses arquivos substituem a necessidade de repetir instruções a cada sessão, funcionando como uma camada de personalização que persiste entre interações.

Na prática, esses arquivos tipicamente cobrem: (1) **perfil do usuário** — quem você é, seu contexto profissional e objetivos; (2) **regras de comportamento** — tom, formato de resposta, restrições; (3) **conhecimento de domínio** — glossários, frameworks e conceitos recorrentes do seu trabalho; (4) **fluxos ou projetos ativos** — contexto situacional de tarefas em andamento. Juntos, eles constroem um "sistema de instrução" informal sem necessidade de fine-tuning.

O mecanismo subjacente é simples: LLMs como Claude operam dentro de uma janela de contexto. Ao injetar arquivos `.md` no início de cada sessão (manualmente ou via ferramentas como o Project Knowledge do Claude), o modelo passa a ter acesso a metadados ricos sobre o usuário e a tarefa. Isso reduz ambiguidade, elimina retrabalho de briefing e eleva a especificidade das respostas. É engenharia de prompt elevada ao nível de infraestrutura pessoal.

A abordagem é especialmente poderosa porque é **composável e versionável** — os arquivos podem ser editados, combinados e mantidos em controle de versão (Git), tratando a configuração do LLM como código. Isso transforma o uso do modelo de uma prática ad hoc em um sistema reproduzível.

## Exemplos
1. **Consultor de produto** cria um `perfil.md` com sua especialidade, `projetos.md` com os clientes ativos e `formato.md` exigindo respostas em bullet points executivos — Claude responde como um analista já contextualizado.
2. **Desenvolvedor solo** mantém um `stack.md` com as tecnologias do projeto e convenções de código, eliminando a necessidade de reexplicar arquitetura a cada sessão.
3. **Criador de conteúdo** usa um `voz.md` descrevendo tom, expressões preferidas e audiência-alvo, garantindo consistência entre rascunhos gerados pelo modelo.

## Relacionado
*(Nenhuma nota existente no vault para conectar neste momento.)*

## Perguntas de Revisao
1. Quais são os quatro tipos de informação que os arquivos `.md` de configuração devem cobrir para maximizar a utilidade de um LLM?
2. Qual a diferença prática entre usar arquivos `.md` de contexto e fazer fine-tuning do modelo para um caso de uso específico?

## Historico de Atualizacoes
- 2026-04-02: Nota criada a partir de Telegram