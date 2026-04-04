---
date: 2026-03-23
tags: [ia, claude-code, colaboracao, multi-agent, coordenacao]
source: https://x.com/NainsiDwiv50980/status/2036012777211559946?s=20
autor: "@NainsiDwiv50980"
tipo: aplicacao
---

# Configurar Claude Peers para Coordenação Automática Multi-Instância

## O que é

Sistema que conecta múltiplas sessões Claude Code em tempo real via descoberta automática em localhost. Instâncias se comunicam, compartilham contexto (repositório, arquivos editados, tarefa atual), sincronizam parallelamente sem conflitos. Transforma desenvolvimento serial em paralelo automático.

## Como implementar

**1. Inicializar broker daemon local**

```bash
claude-peers start-broker
```

Roda em localhost (padrão: port 9000). Não requer cloud, funciona offline.

**2. Registrar instâncias**

Em cada sessão Claude Code, declare:
```
set_summary: "backend API — auth.ts, routes/* — integrating OAuth"
```

Auto-registra sessão. Broker sincroniza com outras instâncias.

**3. Descobrir pares**

```
list_peers
```

Retorna:
```
Peer 1: frontend-ui (working on components/Header.tsx)
Peer 2: database (working on migrations/)
Peer 3: devops (working on docker-compose.yml)
```

**4. Comunicação natural**

```
message peer 2: "are you handling user schema updates? I'm working on auth"
```

Instância 2 responde instantaneamente via mensagens. Sem API, sem orquestrador — MCP nativo.

**5. Sincronização automática de dependências**

Quando Peer 1 (backend) edita `auth.ts`:
- Broker notifica Peer 3 (frontend): "auth.ts mudou"
- Peer 3 obtém diffs automaticamente
- Evita conflitos: "vejo que você está editando auth, deixo para você"

**6. Configuração avançada**

Arquivo `~/.claude/peers-config.json`:
```json
{
  "brokerPort": 9000,
  "autoSync": true,
  "conflictResolution": "last-write-wins",
  "messagingProtocol": "mcp",
  "discoveryMode": "localhost"
}
```

## Stack e requisitos

- Claude Code (local nativo)
- SQLite (registra pares conectados, incluído)
- MCP servers por sessão (automático)
- Daemon Python/Node (incluído no plugin)
- Zero cloud, funciona offline

## Armadilhas e limitações

- **Escopo localhost**: Requer máquina local. Para remoto, use SSH tunneling
- **Falhas de comunicação**: Se daemon cai, instâncias perdem contato (restart automático)
- **Conflitos em git**: Múltiplos Claudes em mesmo repo podem criar merge conflicts (mitigado com worktrees)
- **Overhead de sincronização**: Cada edit notifica broker; muita atividade = latência
- **Não é distribuído**: Designed para máquina única com múltiplas sessões, não para múltiplos PCs

## Conexões

[[git-worktrees-desenvolvimento-paralelo-claude-code]]
[[git-worktrees-para-agentes]]
[[consolidacao-de-memoria-em-agentes]]
[[Claude Code Subconscious Letta Memory Layer]]
[[empresa-virtual-de-agentes-de-ia]]

## Histórico

- 2026-03-23: Nota criada
- 2026-04-02: Reescrita como guia de configuração
