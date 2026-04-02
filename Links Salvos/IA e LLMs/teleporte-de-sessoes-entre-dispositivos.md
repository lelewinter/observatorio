---
tags: []
source: https://x.com/bcherny/status/2038454339933548804?s=20
date: 2026-04-02
---
# Teleporte de Sessões entre Dispositivos

## Resumo
O Claude permite mover sessões ativas entre diferentes ambientes (mobile, web, desktop, terminal) de forma contínua, sem perder contexto, através dos comandos `--teleport` e `/remote-control`.

## Explicação
O conceito de **teleporte de sessões** no Claude refere-se à capacidade de transferir uma sessão de trabalho em andamento entre diferentes interfaces sem interromper o fluxo. Isso significa que uma conversa ou tarefa iniciada no terminal pode ser continuada no browser ou no celular, e vice-versa, mantendo o estado completo da sessão.

O comando `claude --teleport` (ou `/teleport` dentro de uma sessão) permite que uma sessão em nuvem seja transferida para a máquina local do usuário. O fluxo inverso é coberto pelo comando `/remote-control`, que expõe uma sessão local para ser controlada remotamente via browser ou dispositivo móvel. A configuração "Enable Remote Control for all sessions" no `/config` automatiza esse comportamento para todas as sessões, eliminando a necessidade de ativar o recurso manualmente a cada uso.

Esse mecanismo representa uma evolução significativa na forma como agentes de IA são operados: ao invés de sessões isoladas por plataforma, o contexto se torna um recurso persistente e portátil. Isso é especialmente relevante para fluxos de trabalho longos, onde o usuário precisa alternar entre ambientes — por exemplo, iniciar uma tarefa de desenvolvimento no terminal e revisar resultados no celular durante o deslocamento.

A arquitetura subjacente depende de sessões armazenadas em nuvem (`code.claude.com`), que funcionam como ponto de sincronização central entre os diferentes clientes. O modelo de execução é híbrido: a sessão pode rodar localmente ou na nuvem, e o controle pode vir de qualquer dispositivo conectado.

## Exemplos
1. Iniciar uma sessão de refatoração de código no terminal via `claude`, depois continuar a revisão dos resultados pelo browser sem perder o histórico.
2. Configurar `/remote-control` globalmente e monitorar um agente rodando localmente pelo celular enquanto está fora do computador.
3. Usar `--teleport` para "puxar" para a máquina local uma sessão iniciada na interface web do Claude, ganhando acesso ao sistema de arquivos local.

## Relacionado
*(Nenhuma nota relacionada disponível no vault no momento da criação.)*

## Perguntas de Revisão
1. Qual é a diferença funcional entre `--teleport` e `/remote-control`? Em qual direção cada um transfere o controle da sessão?
2. Que implicações de segurança existem ao habilitar "Remote Control for all sessions" globalmente no `/config`?

## Histórico de Atualizações
- 2026-04-02: Nota criada a partir de Telegram