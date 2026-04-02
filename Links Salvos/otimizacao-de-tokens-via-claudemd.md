---
tags: []
source: https://x.com/omarsar0/status/2039343351187554490?s=20
date: 2026-04-02
---
# Otimização de Tokens via CLAUDE.md

## Resumo
O arquivo `CLAUDE.md` é um mecanismo de configuração do Claude Code que permite direcionar o comportamento do modelo sem alterações de código, com relatos de redução de até 63% nos tokens de output gerados.

## Explicação
O `CLAUDE.md` é um arquivo de instruções persistentes reconhecido nativamente pelo Claude Code (a interface de linha de comando da Anthropic). Quando presente no repositório ou diretório de trabalho, ele funciona como um sistema de prompt implícito que condiciona o comportamento do modelo em todas as interações daquela sessão — sem necessidade de modificar o código da aplicação ou injetar prompts manualmente a cada chamada.

A eficiência reportada (redução de ~63% nos tokens de output) decorre de instruções que suprimem comportamentos verbosos padrão do Claude, como explicações não solicitadas, confirmações redundantes, e formatações extensas. O repositório `drona23/claude-token-efficient` fornece um template universal de `CLAUDE.md` projetado como "drop-in", ou seja, basta adicionar o arquivo ao projeto para obter o efeito sem qualquer refatoração.

Do ponto de vista técnico, isso representa uma forma de **prompt engineering estrutural**: em vez de otimizar prompts individuais, a otimização é feita uma vez no nível do ambiente de execução. Isso é relevante tanto para custos de API (tokens faturados) quanto para latência e qualidade de resposta em fluxos automatizados de desenvolvimento assistido por IA.

A abordagem complementa práticas de engenharia de prompts mais tradicionais ao operar em uma camada anterior à conversa — configurando restrições e preferências de estilo antes mesmo da primeira mensagem do usuário.

## Exemplos
1. **Redução de custos em pipelines CI/CD**: Adicionar `CLAUDE.md` a um repositório que usa Claude Code para revisão automática de PRs pode cortar substancialmente o custo por execução sem alterar a lógica de integração.
2. **Padronização de estilo de resposta em times**: Equipes podem versionar o `CLAUDE.md` no repositório para garantir que todos os desenvolvedores recebam respostas no mesmo nível de verbosidade e formato.
3. **Supressão de output redundante em automações**: Scripts que chamam Claude Code repetidamente se beneficiam de respostas mais curtas e diretas, reduzindo tempo de parsing e tokens consumidos.

## Relacionado
*(Nenhuma nota existente no vault para linkar no momento.)*

## Perguntas de Revisão
1. Qual é a diferença entre usar `CLAUDE.md` e injetar um system prompt via API diretamente? Quando cada abordagem é preferível?
2. A redução de tokens de output implica necessariamente perda de qualidade informacional nas respostas, ou é possível manter a utilidade com menos tokens?

## Histórico de Atualizações
- 2026-04-02: Nota criada a partir de Telegram