---
tags: []
source: https://www.linkedin.com/posts/vilson-ranijak-932041211_essa-semana-pedi-pro-claude-code-executar-share-7442211445062320128-wKJw?utm_source=social_share_send&utm_medium=android_app&rcm=ACoAAAgQrLIB4LHRfm8oNhRCsOv9i7wGJSYJXQs&utm_campaign=share_via
date: 2026-04-02
tipo: aplicacao
---
# Configurar Hooks de Notificação em Claude Code CLI

## O que é

Sistema de hooks configurável via `~/.claude/settings.json` que dispara eventos do SO (notificações visuais, sons, webhooks) quando [[Claude Code]] muda de estado (conclusão, requisição de permissão, atenção necessária). Soluciona problema de "agente esperando silenciosamente" ao oferecer feedback assíncrono.

## Como implementar

### Pré-requisito: Localize seu arquivo de configuração

```bash
# macOS/Linux
ls -la ~/.claude/settings.json

# Se não existe, crie:
mkdir -p ~/.claude
touch ~/.claude/settings.json
```

### Fase 1: Estrutura Básica do Arquivo

Abra `~/.claude/settings.json` e comece com:

```json
{
  "version": "1.0",
  "hooks": {}
}
```

### Fase 2: Adicionar Hook de Conclusão (Stop)

Quando Claude Code termina uma tarefa, notifique:

```json
{
  "hooks": {
    "Stop": [
      {
        "matcher": "",
        "hooks": [
          {
            "type": "command",
            "command": "osascript -e 'display notification \"Claude Code terminou!\" with title \"Tarefa Concluída\" subtitle \"Verifique o resultado.\"'"
          }
        ]
      }
    ]
  }
}
```

**Em Linux (libnotify):**

```json
{
  "hooks": {
    "Stop": [
      {
        "matcher": "",
        "hooks": [
          {
            "type": "command",
            "command": "notify-send 'Claude Code' 'Tarefa Concluída!' --urgency=normal"
          }
        ]
      }
    ]
  }
}
```

**Em Windows (PowerShell):**

```json
{
  "hooks": {
    "Stop": [
      {
        "matcher": "",
        "hooks": [
          {
            "type": "command",
            "command": "powershell -Command \"[Windows.UI.Notifications.ToastNotificationManager, Windows.UI.Notifications, ContentType = WindowsRuntime] | Out-Null; $template = @'...'@; \""
          }
        ]
      }
    ]
  }
}
```

### Fase 3: Hook de Permissão Solicitada

Claude Code precisa de sua permissão antes de executar uma ação:

```json
{
  "hooks": {
    "PermissionRequest": [
      {
        "matcher": "",
        "hooks": [
          {
            "type": "command",
            "command": "osascript -e 'display notification \"Claude está esperando sua permissão!\" with title \"Ação Pendente\" subtitle \"Volte ao terminal para aprovar.\"' && afplay /System/Library/Sounds/Ping.aiff"
          }
        ]
      }
    ]
  }
}
```

### Fase 4: Hook de Atenção Necessária

Claude encontrou ambiguidade ou precisa de input:

```json
{
  "hooks": {
    "Notification": [
      {
        "matcher": "",
        "hooks": [
          {
            "type": "command",
            "command": "osascript -e 'display notification \"Claude precisa de sua atenção!\" with title \"Input Solicitado\" subtitle \"Há uma pergunta no terminal.\"' && afplay /System/Library/Sounds/Glass.aiff"
          }
        ]
      }
    ]
  }
}
```

### Fase 5: Configuração Completa com Múltiplos Hooks

Arquivo final `~/.claude/settings.json`:

```json
{
  "version": "1.0",
  "hooks": {
    "Stop": [
      {
        "matcher": "",
        "hooks": [
          {
            "type": "command",
            "command": "osascript -e 'display notification \"Tarefa completa!\" with title \"Claude Code\" subtitle \"Verifique output.\"' && afplay /System/Library/Sounds/Hero.aiff"
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
            "command": "osascript -e 'display notification \"Esperando sua permissão!\" with title \"Claude Code\" subtitle \"Aprove no terminal.\"' && afplay /System/Library/Sounds/Ping.aiff"
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
            "command": "osascript -e 'display notification \"Preciso de sua atenção!\" with title \"Claude Code\" subtitle \"Há uma pergunta.\"' && afplay /System/Library/Sounds/Glass.aiff"
          }
        ]
      }
    ]
  }
}
```

### Fase 6: Validar Configuração

Teste se o JSON está válido:

```bash
# JSON validation
python3 -m json.tool ~/.claude/settings.json > /dev/null && echo "✓ JSON válido"

# Reinicie Claude Code para recarregar config
```

### Fase 7: Sounds Customizados (Opcional)

Use seus próprios áudios:

```json
{
  "command": "afplay /path/to/your/custom-sound.aiff"
}
```

Ou dispare som sem mensagem:

```json
{
  "command": "afplay /System/Library/Sounds/Purr.aiff"
}
```

Opções de som nativo macOS:
- `Alarm.aiff`, `Beep.aiff`, `Bomb.aiff`
- `Glass.aiff`, `Hero.aiff`, `Ping.aiff`
- `Pop.aiff`, `Purr.aiff`, `Sosumi.aiff`

## Stack e requisitos

- **macOS**: `osascript` (built-in) + `afplay` (built-in)
- **Linux**: `libnotify` (`apt install libnotify-bin`)
- **Windows**: PowerShell (built-in) com acesso à Toast Notifications API
- **Claude Code**: versão recente com suporte a hooks
- **Custo**: zero (usa ferramentas nativas do SO)

## Armadilhas e limitações

1. **Múltiplos hooks**: Se configurar muitos hooks, notificações podem ficar barulhentas. Domine a quantidade.

2. **Matcher pattern**: Campo `"matcher": ""` significa "para todos os eventos". Pode refinar com regex se necessário (veja docs).

3. **Delays**: Notificação pode levar 1-2 segundos. Para UX crítica, use visual + sonora em combo.

4. **Direitos de acesso**: Em alguns sistemas, pode ser necessário dar permissão ao terminal para enviar notificações.

5. **Falha silenciosa**: Se comando do hook falhar, nada é reportado. Teste com `sh -c "seu comando"` manualmente primeiro.

## Conexões

- [[hooks-notificacao-claude-code]] — versão Zettelkasten desta nota
- [[Otimizar Uso Rate Limit Claude Pro Max]] — coordenar múltiplos agentes
- [[Claude Code - Melhores Práticas]] — setup ótimo do Claude Code

## Histórico

- 2026-04-02: Nota criada
- 2026-04-02: Reescrita como guia de implementação

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