---
tags: [ai-engineering, developer-tools, spec-driven-development, llm-agents]
source: https://x.com/_vmlops/status/2035205552394182853?s=20
date: 2026-04-02
---
# Spec-Driven AI Coding

## Resumo
Spec-kit é um toolkit do GitHub que substitui o "vibe coding" por um fluxo estruturado: descrição em linguagem natural → especificações geradas por IA → plano de execução → código. A ideia central é que a IA deve primeiro formalizar o entendimento antes de escrever código.

## Explicação
O "vibe coding" tornou-se um termo pejorativo para o uso irresponsável de agentes de IA em desenvolvimento de software: o usuário descreve vagamente o que quer, o agente escreve código diretamente, e o resultado é difícil de auditar, manter ou escalar. O spec-kit surge como uma resposta estrutural a esse problema, introduzindo uma camada intermediária obrigatória de especificação.

O fluxo do spec-kit segue três etapas distintas: (1) o desenvolvedor descreve a funcionalidade desejada em linguagem natural; (2) a IA transforma essa descrição em uma especificação formal — requisitos, contratos, comportamentos esperados; (3) a especificação é usada como base para gerar um plano de implementação e, só então, o código final. Isso inverte a lógica do "prompt → código direto" e insere um artefato intermediário verificável.

A compatibilidade com múltiplos agentes de IA (Copilot, Cursor, Claude, etc.) é um sinal de que o spec-kit busca ser uma camada de orquestração agnóstica, não um produto fechado. Isso posiciona a ferramenta no espaço de "meta-prompting" ou "prompt engineering estruturado", onde o objetivo é disciplinar o comportamento do agente antes da geração de código, reduzindo ambiguidade e alucinações contextuais.

A abordagem tem paralelos com práticas de engenharia de software clássicas — especificações formais, TDD, design por contrato — mas adaptadas para o paradigma de geração assistida por IA. O valor não está apenas na qualidade do código gerado, mas na rastreabilidade: a especificação se torna documentação viva do que foi intencionado.

## Exemplos
1. **Feature development**: Desenvolvedor descreve "quero um sistema de autenticação com OAuth e suporte a MFA" → spec-kit gera spec com fluxos, edge cases e contratos de API → agente implementa seguindo a spec.
2. **Onboarding de equipe**: A spec gerada serve como documentação de intenção, permitindo que outros engenheiros entendam o "porquê" antes de ler o código.
3. **Auditoria de segurança**: A spec formal pode ser revisada por humanos antes da execução, criando um checkpoint de validação que o vibe coding elimina.

## Relacionado
*(Nenhuma nota existente no vault para conectar neste momento.)*

## Perguntas de Revisão
1. Qual é a diferença fundamental entre "vibe coding" e spec-driven development, e por que a camada intermediária de especificação é crítica para rastreabilidade?
2. Como o modelo de spec → plano → código se relaciona com práticas clássicas de engenharia como TDD ou design por contrato? O spec-kit é uma evolução ou uma adaptação?

## Histórico de Atualizações
- 2026-04-02: Nota criada a partir de Telegram