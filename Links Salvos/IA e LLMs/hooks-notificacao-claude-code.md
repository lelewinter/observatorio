---
tags: [claude-code, configuração, hooks, notificações, automação]
source: https://www.linkedin.com/posts/vilson-ranijak-932041211_essa-semana-pedi-pro-claude-code-executar-share-7442211445062320128-wKJw
date: 2026-03-28
tipo: aplicacao
---

# Configure Notificações Sonoras no Claude Code com Hooks

## O que e

Hooks no ~/.claude/settings.json disparam notificações auditivas e visuais quando Claude Code conclui tarefas, solicita permissão ou requer atenção. Diferentes tons (Hero, Ping, Glass) diferem tipos de eventos em sessões paralelas, eliminando necessidade de monitorar tela.

## Como implementar

**Fundamento arquitetural**: Claude Code emite eventos padronizados (Stop, PermissionRequest, Notification) que podem ser capturados e transformados em ações do sistema operacional via hooks. A configuração ocorre em ~/.claude/settings.json, um arquivo JSON que persiste entre sessões.

**Estratégia de notificação**: Sons diferentes são processados em circuitos auditivos distintos pelo cérebro humano, permitindo identificação instantânea do tipo de evento sem visão visual. Hero (vitória) para conclusões, Ping (alerta simples) para permissões, Glass (alarme claro) para atenção imediata. Em workflows com múltiplas sessões, isso reduz tempo de resposta comparado a notificações visuais que competem por atenção na tela já saturada.

**Configuração completa** para macOS (arquivo ~/.claude/settings.json):

```json
{
  "hooks": {
    "Stop": [
      {
        "matcher": "",
        "hooks": [
          {
            "type": "command",
            "command": "osascript -e 'display notification \"Tarefa concluída!\" with title \"Claude Code\"' && afplay /System/Library/Sounds/Hero.aiff"
          }
        ]
      }
    ],
    "PermissionRequest": [
      {
        "matcher": "",
        "hooks": [
          {
            "type": "command",
            "command": "osascript -e 'display notification \"Esperando sua permissão!\" with title \"Claude Code\"' && afplay /System/Library/Sounds/Ping.aiff"
          }
        ]
      }
    ],
    "Notification": [
      {
        "matcher": "",
        "hooks": [
          {
            "type": "command",
            "command": "osascript -e 'display notification \"Preciso da sua atenção!\" with title \"Claude Code\"' && afplay /System/Library/Sounds/Glass.aiff"
          }
        ]
      }
    ]
  }
}
```

**Para Windows**, substituir osascript por PowerShell notification e caminhos de som por arquivos .wav locais (ex: C:\Windows\Media\Notification.Default.wav). **Para Linux**, usar notify-send (já incluso em desktops GNOME/KDE) e paplay ou ffplay para áudio.

**Adaptar para casos específicos**: matcher pode filtrar eventos por conteúdo (ex: "matcher": "Deploy" para tocar som apenas em deploys), hooks podem encadear múltiplas ações (notificação + email + POST webhook), type pode ser "command" ou "url" (HTTP POST).

## Stack e requisitos

- **Sistemas**: macOS 10.14+, Windows 10/11 (PowerShell 5+), Linux (systemd, GNOME/KDE)
- **Arquivo**: ~/.claude/settings.json (criado automaticamente se não existir)
- **Sons**: localizados em /System/Library/Sounds (macOS), C:\Windows\Media (Windows), /usr/share/sounds (Linux)
- **Overhead**: negligenciável, hooks rodam assincronamente

## Armadilhas e limitacoes

- Ordem de execução de hooks não é garantida; usar sleep se múltiplas ações precisam de sequência
- macOS pode bloquear alguns caminhos de som se SIP (System Integrity Protection) está ativo; verificar permissões
- Hooks globais; não há forma nativa de enviar notificações apenas a um usuário específico em shared machines
- JSON mal formatado silenciosamente falha; validar com jq antes de aplicar

## Conexoes

[[Claude Code - Melhores Práticas]] [[Otimizar Preferencias Claude Chief of Staff]] [[Conversas paralelas enquanto Claude trabalha em background]]

## Historico

- 2026-03-28: Nota original
- 2026-04-02: Reescrita para template aplicacao
