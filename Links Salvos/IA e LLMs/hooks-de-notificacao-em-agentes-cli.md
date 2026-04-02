---
tags: []
source: https://www.linkedin.com/posts/vilson-ranijak-932041211_essa-semana-pedi-pro-claude-code-executar-share-7442211445062320128-wKJw?utm_source=social_share_send&utm_medium=android_app&rcm=ACoAAAgQrLIB4LHRfm8oNhRCsOv9i7wGJSYJXQs&utm_campaign=share_via
date: 2026-04-02
---
# Hooks de Notificação em Agentes CLI

## Resumo
Agentes de IA no terminal (como Claude Code) podem bloquear silenciosamente aguardando input do usuário. Hooks de sistema operacional permitem disparar notificações nativas e sons para alertar o desenvolvedor sobre mudanças de estado do agente.

## Explicação
Ferramentas de agentes de IA que operam no terminal enfrentam um problema fundamental de UX: o modelo pode pausar a execução aguardando permissão ou input humano sem nenhum sinal perceptível ao usuário que trocou de contexto. Isso gera desperdício de tempo — o desenvolvedor retorna ao terminal e descobre que o agente está parado há minutos esperando uma resposta simples.

O Claude Code expõe um sistema de hooks configurável via `~/.claude/settings.json`. Esses hooks são gatilhos baseados em eventos do ciclo de vida do agente: `Stop` (tarefa concluída), `Notification` (agente requer atenção) e `PermissionRequest` (agente solicita permissão explícita). Cada hook executa um comando de shell arbitrário, o que permite integração com qualquer sistema de notificação do SO.

No macOS, o comando `osascript` permite disparar notificações nativas do sistema e reproduzir sons do sistema via `afplay`. O mecanismo é agnóstico ao sistema operacional — no Linux, equivalentes como `notify-send` (libnotify) cumprem a mesma função; no Windows, PowerShell pode ser usado para o mesmo fim. A lógica de extensibilidade via hooks de shell é uma arquitetura comum em ferramentas de desenvolvimento (git hooks, webhooks, CI/CD), aplicada aqui ao ciclo de vida de um agente autônomo.

Essa abordagem evidencia uma tensão crescente no desenvolvimento com agentes: quanto mais autônomo o agente, mais crítico se torna o mecanismo de interrupção e notificação assíncrona. Ferramentas como Cursor resolvem isso com UX integrada; Claude Code delega ao desenvolvedor via hooks — uma filosofia de composabilidade Unix aplicada a agentes de IA.

## Exemplos
1. **Notificação sonora diferenciada por evento**: sons distintos para tarefa concluída (Hero), aguardando input (Glass) e pedindo permissão (Ping), permitindo ao desenvolvedor identificar o tipo de evento sem ver a tela.
2. **Notificação com contexto de git worktree**: um hook pode executar `git worktree list` e incluir o nome da árvore de trabalho na mensagem de voz, informando em qual janela/projeto o evento ocorreu.
3. **Integração com ferramentas externas**: o mesmo mecanismo pode disparar webhooks, mensagens no Slack ou ativar ferramentas dedicadas como PeonPing, que monitora processos de terminal e notifica externamente.

## Relacionado
*(Nenhuma nota relacionada disponível no vault no momento.)*

## Perguntas de Revisão
1. Qual é a diferença semântica entre os eventos `Notification` e `PermissionRequest` no ciclo de vida do Claude Code, e por que tratá-los separadamente é útil?
2. A arquitetura de hooks de shell é uma filosofia Unix aplicada a agentes — quais são os limites dessa abordagem comparada a soluções de UX integradas como as do Cursor?

## Histórico de Atualizações
- 2026-04-02: Nota criada a partir de Telegram