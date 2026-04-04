---
tags: [unity, mcp, ai, game-dev, plugins]
source: https://x.com/tom_doerr/status/2036191401524801831?s=20
date: 2026-04-02
tipo: aplicacao
---

# Integrar MCP em Builds Compilados Unity para NPCs e QA Autômatos

## O que e

Plugin que implementa Model Context Protocol em jogos Unity compilados, permitindo agentes de IA (Claude, GPT) ler estado de jogo, controlar NPCs e executar ações em tempo real via tool calls padronizados. Diferencia-se de integrações editor-only ao persistir interface MCP mesmo após build/compilação.

## Como implementar

**Arquitetura fundamentação**: Plugin funciona como servidor MCP local que expõe uma API via WebSocket ou stdio ao agente de IA. Quando compilado, o jogo inclui binário MCP server que aguarda conexões de clientes (IDE com agentes, processos CLI).

**Instalação e setup básico**:
```bash
# Opção 1: via git submodule (recomendado)
cd Assets
git submodule add https://github.com/CoderGamester/mcp-unity.git Plugins/MCP
```

**Configuração C# mínima** (script no projeto):
```csharp
[MCPTool("AgressiveNPC")]
public void AttackPlayer() {
    // Lógica de combate do NPC
    playerTarget.TakeDamage(20);
}

[MCPResource("WorldState")]
public string GetWorldState() {
    return JsonUtility.ToJson(new {
        playerPos = player.transform.position,
        npcs = FindObjectsOfType<NPC>().Length,
        time = Time.time
    });
}
```

O atributo `[MCPTool]` transforma qualquer método C# em ferramenta invocável por IA, sem reescrita. `[MCPResource]` expõe estado legível.

**Configuração de cliente** (arquivo mcpConfig em projeto IDE):
```json
{
  "mcpServers": {
    "game-mcp": {
      "command": "node",
      "args": ["/path/to/mcp-unity/server/build/index.js"],
      "env": {
        "GAME_PID": "12345",
        "GAME_PORT": "8090"
      }
    }
  }
}
```

**Exposição de ferramentas complexas** (100+ built-in):
- Movimento: `move_gameobject(id, position, speed)`
- Componentes: `update_component(id, componentType, property, value)`
- Cenas: `load_scene(sceneName)`, `save_scene()`
- Testes: `run_tests(testMode=EditMode)`
- Debug: `get_console_logs()`, `set_breakpoint()`

**QA automatizado**: Criar agente que testa fluxos de gameplay:
```csharp
// Agent script
public async Task<bool> TestMainMenuFlow() {
    var mcp = new MCPClient("localhost:8090");
    await mcp.Call("execute_menu_item", "File > New Game");
    await Task.Delay(3000);
    var gameState = await mcp.Call("get_worldstate");
    return gameState.playerHP > 0;
}
```

**NPC dinâmico**: Agente recebe observação do mundo e decide ações:
```csharp
// No jogo
public void ProcessAIDecision(string claudeResponse) {
    var action = JsonUtility.FromJson<NPCAction>(claudeResponse);
    StartCoroutine(ExecuteAction(action));
}
```

## Stack e requisitos

- **Unity**: 6.0+ (ou 2022.3.18 LTS)
- **Node.js**: 18.0+
- **Plataformas build**: Standalone (Win/Mac/Linux), WebGL parcialmente suportado
- **Latência esperada**: 50-200ms por tool call (depende de complexidade)
- **VRAM**: +10-30MB por instância de servidor MCP
- **Network**: Localhost (recomendado) ou TCP aberto para IA cloud

## Armadilhas e limitacoes

- **Segurança**: MCP server expõe TODA a lógica do jogo; restringir em produção (apenas ferramentas whitelisted).
- **Serialização**: Dados Unity (Vector3, Quaternion) requerem conversão JSON explícita; LLM pode produzir formato inválido.
- **Determinismo**: Se IA modifica estado de jogo em tempo real, multiplayer sincronizado pode desincronizar.
- **WebGL**: Limited tool exposure (sem acesso full scripting); preferir standalone builds.
- **Versionamento**: Mudar assinatura de `[MCPTool]` quebra backward compatibility com prompts existentes.

## Conexoes

[[MCP Unity Editor Ferramentas 100+]] [[Model Context Protocol MCP Padrao Aberto]] [[Agentes Autonomos em Game Development]]

## Historico

- 2026-04-02: Nota criada
- 2026-04-02: Reescrita para template aplicacao