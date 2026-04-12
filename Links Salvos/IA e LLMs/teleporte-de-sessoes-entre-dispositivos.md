---
tags: [claude-code, remote-control, teleport, sessions, cross-platform, workflow, productivity]
source: https://x.com/bcherny/status/2038454339933548804?s=20
date: 2026-04-02
tipo: aplicacao
---

# Teleporte & Remote Control: Mover Sessões Claude entre Desktop/Mobile/Web/Terminal

## O que é

**Teleporte e Remote Control são dois fluxos de sincronização de sessões Claude que eliminam a fragmentação de contexto entre plataformas.**

Diferença:
- **`--teleport` / `/teleport`**: Puxa uma sessão da nuvem (web/mobile) para sua máquina local (terminal). Ganha acesso ao sistema de arquivos, pode rodar scripts, build tools.
- **`/remote-control`**: Expõe uma sessão local (terminal/código) para controle remoto via browser, mobile ou outro dispositivo. Você inicia agente no terminal, monitora/controla do celular.

Antes (2025): Sessões isoladas por plataforma. Inicias tarefa no terminal, depois no web continua é outra sessão. Contexto perdido.

Agora (2026): **Uma sessão, múltiplos pontos de acesso.** Inicia no terminal, continua no celular, retorna ao desktop — mesmo histórico, mesmo estado, sem duplicação de contexto.

## Por que importa

### Problema: Context thrashing

Seu fluxo de trabalho típico (sem Remote Control):
```
1. Terminal: claude start project
   → Inicia session, carrega files, contexto = 20KB
   → Cria 3 files, 100 linhas de código
   
2. Celular: Quer revisar resultado (no metrô)
   → Abre claude.ai/code
   → Nova sessão (perdeu contexto anterior)
   → Precisa recarregar files, re-explicar o que estava fazendo
   → Context novo = 20KB (de novo)
   
3. Volta ao desktop: Quer continuar
   → Terminal original não tem mensagens do celular
   → Cria TERCEIRA sessão (context thrashing)
   
Resultado: Contexto pulverizado, duplicado, difícil rastrear o que foi feito onde.
```

### Solução: Remote Control

```
1. Terminal: claude start project --with-remote-control
   → Inicia session, carrega files
   → Imprime: "Session accessible at: https://claude.ai/code?session=abc123"
   
2. Celular: Clica link
   → Mesmo histórico, mesmo context, mesmo estado
   → Envia mensagem do celular
   → Terminal recebe em tempo real
   
3. Volta ao desktop: Terminal ainda rodando
   → Vê mensagens do celular no histórico
   → Continua conversa, mesmo contexto
   → Agente roda na máquina local (acesso a sistema de arquivos)
```

**Benefício**: 1 sessão, múltiplos pontos de acesso, contexto nunca perdido.

## Como funciona / Como implementar

### Fluxo 1: Remote Control (Local → Remote)

**Cenário**: Você startou agente no terminal, quer monitorar/controlar do celular.

```bash
# Terminal: Inicia sessão com Remote Control ativa
claude code ./meu-projeto

# Dentro da sessão, ativa Remote Control:
/remote-control

# Output:
# ✅ Remote Control enabled
# 🔗 Access this session from any device:
#    https://claude.ai/code?session=xyz789
# 📱 Share link com celular, abra no browser/app

# Agente continua rodando no terminal
# Você controla do celular (envia mensagens)
# Terminal executa e relata de volta
```

**Internals**:
- Sessão roda **localmente no seu PC** (não na nuvem)
- Comunicação é **outbound-only** (PC faz HTTPS request a code.claude.com)
- Nenhuma porta inbound aberta
- Histórico sincronizado em tempo real via cloud relay

### Fluxo 2: Teleport (Remote → Local)

**Cenário**: Você começou sessão no web (claude.ai/code), agora quer controle local (terminal, system files).

```bash
# Opção 1: Na sessão web, execute:
/teleport

# Output:
# ✅ Teleport URL gerado
# 🔗 No seu terminal, execute:
#    claude --teleport xyz789
# 📁 Ganhará acesso ao sistema de arquivos local

# Opção 2: Terminal
claude --teleport xyz789

# Output:
# ✅ Sessão puxada da nuvem
# 📂 Acesso a ~/Documents, ~/Downloads, etc
# ▶️  Agora você pode rodar scripts localmente
```

**O que muda**:
- Antes: Sessão roda na nuvem (sem acesso a arquivos locais, sem system commands)
- Depois: Sessão roda no seu PC (acesso completo a `ls`, `node`, `python`, `git`, etc)

### Configuração Global: Enable para todas as sessões

```bash
# Terminal
claude config

# Abre arquivo de config (~/.claude/config.json ou similar)
# Adicione:
{
  "remote_control": {
    "enabled_by_default": true,
    "auto_share_urls": false
  }
}

# Salve, próximas sessões já iniciam com RC ativa
```

## Fluxo prático: Build + Mobile review

```
Sua tarefa: Refatorar React component (2-3 horas)

1. TERMINAL START
   $ cd ~/projects/myapp
   $ claude code --with-remote-control
   
   > Refactor Button component to use Tailwind + reduce bundle size
   
   [Claude analisa files, propõe refactor]
   
   /remote-control
   # ✅ Output: https://claude.ai/code?session=sess_abc123

2. COMEÇAR IMPLEMENTAÇÃO
   > Implement the refactor on Button.tsx
   
   [Claude edita arquivo, roda build]
   $ npm run build  # Execute no terminal, Claude vê output
   
   ⚠️  Erro: "Unused import 'useMemo'"
   [Claude corrige]
   
   ✅ Build success: 45KB → 38KB (15% reduction)

3. MOBILE REVIEW (você está no sofá agora)
   [Abre celular, visita: https://claude.ai/code?session=sess_abc123]
   
   [Vê histórico completo: análise, refactor, build output]
   
   > Rodar visual diff do component antigo vs novo?
   
   [Claude tira screenshot, mostra lado-a-lado]
   [Você aprova no celular]

4. VOLTA AO DESKTOP
   [Terminal original ainda está rodando]
   
   [Vê mensagem do celular no histórico]
   
   > Commitar changes e criar PR
   
   [Claude executa: git add, git commit, git push]
   [Pronto, mesma sessão do início]
```

## Stack técnico

**Arquitetura:**
- Cloud relay: `code.claude.com` sincroniza sessões
- Client local: `claude` CLI (terminal) ou SDK
- Múltiplos clientes: web, mobile, desktop podem se conectar a mesma sessão
- Hybrid execution: Session pode rodar localmente ou na nuvem (seleciona automaticamente)

**Segurança:**
- SSL/TLS para todas as comunicações
- Session tokens únicos por sessão
- Sessão local: zero exposição à Internet (você controla quem tem o link)
- Sessão cloud: apenas autenticados conseguem acessar

**Performance:**
- Remote Control: Latência ~100-500ms (relay cloud, aceitável)
- Teleport: Instant (sessão simplesmente muda de contexto)
- Ideal para: Desenvolvimento assíncrono (não real-time pair programming)

**Requisitos:**
- Claude Pro ou Claude Code subscription (free tier limitado)
- Internet connection (para sync)
- Terminal + web/mobile app (qualquer combinação)

## Código prático

### Exemplo: Agente que usa Remote Control para relatar progresso

```bash
# script.sh — Agente executado via Claude Remote Control

#!/bin/bash

# 1. Terminal: Start agente
claude code ./src

# 2. Dentro de Claude:
/remote-control
# → Pode acompanhar do celular

> Refactor this codebase to use TypeScript. Report progress hourly.

# Claude executa:
# → Analisa estrutura
# → Cria plano (5 passos)
# → Começa passo 1
# → A cada 30min, você recebe update no celular
# → Você pode interromper/ajustar via celular
# → Terminal continua executando
```

### Config para automação de relatórios

```json
// ~/.claude/config.json
{
  "remote_control": {
    "enabled_by_default": true,
    "notify_remote": {
      "enabled": true,
      "interval_minutes": 30,
      "on_events": ["file_created", "error", "task_completed"]
    },
    "auto_reconnect": true,
    "max_sessions": 5
  }
}
```

## Armadilhas e limitações

### 1. **Segurança: Remote Control expõe sua máquina**

Problema: Se você faz `/remote-control` e compartilha o link, qualquer pessoa com o link pode:
- Ver histórico da sessão
- Enviar comandos
- Acessar arquivos (potencialmente)

Exemplo perigoso:
```bash
$ claude code ~/my-api-key-folder

/remote-control
# Gera link: https://claude.ai/code?session=xyz123

# ❌ Você coloca link em Slack public channel

# Alguém vê, acessa, vê arquivo de API keys, cópia

# ✅ Mitigação:
# - Nunca compartilhar link em public channels
# - Usar /config para desabilitar RC por padrão
# - Deletar sessão quando não precisar (/close)
# - Sensitive files em .gitignore + NEVER no contexto
```

Mitigação:
- **Sessões expiram** automaticamente após X horas (default 6h)
- **Revoke link**: Feche sessão (`/close`), link fica inválido
- **Não compartilhar** em canais públicos
- **Use cases seguros**: Sessões de estudos, projetos públicos, demos

### 2. **Latência: Remote Control não é real-time**

Problema: Se você tenta fazer pair programming em tempo real, latência de 200-500ms de relay é chata.

Exemplo:
```
Você digita mensagem no celular: "Muda cor do botão"
Demora 1-2 segundos para chegar ao terminal/Claude processar
Claude executa, volta resposta: demora mais 1-2 segundos

Total: 2-4 segundos por interação (chato para real-time)
```

Mitigação:
- **Remote Control é para async review**, não live collaboration
- Se precisa real-time pair programming, use screen share + zoom
- Para código, melhor: enviar changes via commits + code review

### 3. **Múltiplas sessões remotas podem conflitar**

Problema: Você abre Remote Control em 2 celulares diferentes ao mesmo tempo.

```
Terminal: Session A rodando
Celular 1: Conecta, envia "Refactor Button.tsx"
Celular 2: Conecta, envia "Revert Button.tsx"

Claude recebe 2 comandos conflitantes
```

Mitigação:
- Claude processa **sequencialmente** (FIFO), não paralelo
- Ordem: whichever command chega primeiro
- **Melhor prática**: Uma pessoa por sessão, ou coordenar explicitamente

### 4. **Teleport quebra se você fecha PC**

Problema:
```bash
Terminal: Session rodando
/remote-control ativado

Você coloca PC em sleep

Celular: Tenta enviar comando
→ Terminal/session não responde
→ Comando fica em queue
→ Quando PC acorda, processa fila
```

Problema real: Se você precisa que agente rode **24/7**, Teleport não ajuda (ele roda na sua máquina).

Mitigação:
- **Para 24/7**: Deixe sessão na nuvem (sem teleport)
- **Para sessy local**: Accept que machineoffline = session pause
- **Usar docker/VPS** se precisa 24/7 (miúdo é que não é Teleport)

### 5. **Contexto gigante pode causar timeout**

Problema: Se sua sessão tem 10K+ linhas de histórico, sync entre devices fica lento.

Mitigação:
- Periodicamente `/save` e inicie nova sessão
- Arquivar histórico antigo
- Usar context windows smaller (Haiku instead of Sonnet se budget)

### 6. **Mobile network instability**

Problema: Você está no 4G/mobile network, conexão cai.

Resultado:
- Timeout na sincronização
- Mensagens não chegam
- State fica inconsistente entre dispositivos

Mitigação:
- **Sessão mantém state** — quando reconecta, recupera
- **Sempre usar HTTPS** (nunca HTTP)
- **Accept eventual consistency** — não espere confirmação instant

## Conexões

[[claude-code|Claude Code — plataforma base para sessões]]
[[agentes-autonomos|Agentes Autônomos — podem rodar remotamente e ser monitorados]]
[[contexto-persistente-em-llms|Contexto Persistente — sessão é contexto que persiste entre devices]]
[[desenvolvimento-assincrono|Desenvolvimento Assíncrono — modelo ideal para Remote Control]]
[[seguranca-em-cloud|Segurança — implicações de expor sessão remotamente]]

## Histórico de Atualizações

- 2026-04-02: Nota criada a partir de Telegram
- 2026-04-11: Expandida com arquitetura, fluxos práticos, código, armadilhas, security considerations