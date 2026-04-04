---
tags: [ia, ferramentas, unity, mcp, desenvolvimento-de-jogos, automacao]
source: https://github.com/CoderGamester/mcp-unity
date: 2026-03-28
tipo: aplicacao
---

# Expor Métodos C# como Tools IA com MCP Unity (Uma Linha de Código)

## O que e

Plugin MCP Unity que expõe qualquer método C# como ferramenta invocável por agentes IA via atributo `[MCPTool]`. Suporta 100+ operações nativas (GameObjects, componentes, cenas, assets), funcionando em Cursor, Windsurf, Claude Code e qualquer IDE com suporte MCP.

## Como implementar

**Pré-requisito**: Instalar plugin (Package Manager ou git submodule).

**Expor método customizado** (UMA LINHA):
```csharp
[MCPTool("SpawnBoss")]
public void SpawnBossEnemy(string bossType, Vector3 spawnPos) {
    var boss = Instantiate(GetBossPrefab(bossType), spawnPos, Quaternion.identity);
    boss.GetComponent<BossController>().Init();
}
```

Agora agente pode invocar:
```
@claude "spawn a FireBoss at position (10, 5, 20)"
# Claude invoca tool automaticamente
```

**Expor recursos (contexto persistente)**:
```csharp
[MCPResource("GameState")]
public string GetGameState() {
    return JsonUtility.ToJson(new {
        playerHealth = player.health,
        enemyCount = FindObjectsOfType<Enemy>().Length,
        currentLevel = SceneManager.GetActiveScene().name
    });
}
```

Agent lê recurso antes de decidir ação, garantindo decisões baseadas em estado real.

**Configurar servidor MCP**:
```bash
cd Assets/Plugins/MCP/Server~
npm install && npm run build
node build/index.js  # Escuta 0.0.0.0:8090
```

**Registrar no IDE** (arquivo .cursor/config.json ou .claude/settings.json):
```json
{
  "mcpServers": {
    "unity": {
      "command": "node",
      "args": ["/absolute/path/to/Server~/build/index.js"]
    }
  }
}
```

**Ferramentas built-in** que agent pode usar nativamente:
- `create_gameobject(name, parent_id)` — criar GO
- `update_component(id, type, field, value)` — modificar component
- `move_gameobject(id, target_position, speed)` — animar movimento
- `load_scene(sceneName)` — carregar cena
- `run_tests(mode=EditMode|PlayMode)` — executar testes automaticamente
- `get_console_logs()` — ler output do console
- `execute_menu_item(path)` — executar menu items

**Batch operations** (otimizar latência):
```csharp
await mcp.BatchExecute(new[] {
    new Tool("create_gameobject", new { name = "Enemy1" }),
    new Tool("move_gameobject", new { id = "Enemy1", position = new Vector3(5, 0, 5) }),
    new Tool("move_gameobject", new { id = "Enemy1", position = new Vector3(10, 0, 5) })
});
```

**Depuração**: Usar MCP Inspector para validar tools:
```bash
npx @modelcontextprotocol/inspector node Server~/build/index.js
# Abre UI em localhost:3000 para testar chamadas
```

## Stack e requisitos

- **Unity**: 6.0+ (suporte LTS 2022.3.18+)
- **Node.js**: 18.0+ (npm 9+)
- **RAM**: +50MB por sessão MCP
- **Latência**: 50-200ms por tool call (JSON-RPC overhead)
- **IDEs**: Cursor, Windsurf, Claude Code, GitHub Copilot, VSCode
- **Port**: TCP 8090 (customizável via env var UNITY_MCP_PORT)

## Armadilhas e limitacoes

- **Segurança**: Qualquer método exposto fica acessível ao agente; NÃO expor métodos destrutivos sem validação (deletar scenes, resetar game state).
- **Sincronização**: Se múltiplos agentes (ou você manual) editam cena simultaneamente, conflitos ocorrem; usar mutex/locks para operações críticas.
- **Type safety**: Agente pode passar tipos inválidos; adicionar validação robusta em métodos expostos.
- **Performance**: `batch_execute` é crítico; 100 tool calls individuais em serial é muito lento (use batch para 10+ operações).
- **Breaking changes**: Mudar assinatura de `[MCPTool]` quebra prompts existentes; considerar versionamento.
- **Editor-only**: Tools executam no contexto do Editor Unity; builds standalone precisam [[MCP em Jogos Compilados Unity]].

## Conexoes

[[MCP em Jogos Compilados Unity]] [[MCP para Unity Editor Automacao Cenas]] [[Model Context Protocol MCP Padrao Aberto]] [[Agentes Autonomos Game Development]]

## Historico

- 2026-03-28: Nota original
- 2026-04-02: Reescrita para template aplicacao
