---
tags: []
source: https://x.com/itsolelehmann/status/2036065138147471665?s=20
date: 2026-04-02
---
# Degradação por Excesso de Instruções em LLMs

## Resumo
Acumular regras em prompts de sistema ao longo do tempo degrada a qualidade das saídas de LLMs, pois instruções redundantes, contraditórias ou desnecessárias competem entre si durante a geração.

## Explicação
Modelos de linguagem como Claude possuem comportamentos padrão bem calibrados. Quando um usuário adiciona instruções customizadas para corrigir outputs pontuais, cada regra nova tem custo cognitivo implícito: o modelo precisa reconciliar todas elas simultaneamente durante a inferência. Com o tempo, esse acúmulo cria conflitos internos — regras que se contradizem ("seja conciso" vs. "explique sempre seu raciocínio") ou que cobrem problemas que o modelo já não apresenta.

O fenômeno é análogo ao overfitting em machine learning: o sistema se torna altamente especializado em casos históricos específicos, perdendo generalização para novos contextos. A própria equipe de engenharia da Anthropic identificou esse padrão ao construir o Claude Code, descobrindo que o scaffolding excessivo piorava o agente — evidência de que o problema é estrutural, não apenas de uso final.

A solução prática é uma auditoria periódica do sistema de instruções, preferencialmente delegada ao próprio modelo. O modelo pode identificar quais regras são redundantes com seu comportamento padrão, quais se contradizem, quais foram adicionadas para corrigir um único output ruim (e não como política geral), e quais são vagas demais para serem interpretadas de forma consistente. Esse processo de "poda" das instruções tende a produzir outputs mais coerentes do que continuar empilhando regras.

A metáfora do chef com 47 passos de receita captura bem o mecanismo: instruções excessivas não apenas adicionam ruído, mas ativamente interferem nas competências que o modelo já possui, forçando-o a "segunda-adivinhar" comportamentos que seriam naturais sem a instrução.

## Exemplos
1. **Auditoria de CLAUDE.md**: Pedir ao próprio Claude que leia todos os arquivos de instrução e classifique cada regra segundo os cinco critérios (redundante com padrão, contraditória, repetida, corretiva pontual, vaga demais).
2. **Refatoração de system prompts corporativos**: Equipes que constroem pipelines de produção sobre LLMs devem revisar system prompts trimestralmente, removendo regras adicionadas reativamente a incidentes já resolvidos pelo modelo base.
3. **Teste A/B de complexidade**: Comparar outputs de um prompt com 30 regras versus uma versão podada com 10 regras essenciais para medir impacto real na qualidade.

## Relacionado
*(Nenhuma nota existente no vault para conectar no momento.)*

## Perguntas de Revisão
1. Por que instruções que parecem complementares podem degradar a performance de um LLM quando empilhadas?
2. Qual é a analogia entre acúmulo de regras em prompts e overfitting em treinamento de modelos, e onde a analogia quebra?

## Histórico de Atualizações
- 2026-04-02: Nota criada a partir de Telegram