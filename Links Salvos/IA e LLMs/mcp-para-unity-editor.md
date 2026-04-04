---
tags: [mcp, unity, ai-tools, game-dev, llm-integrations]
source: https://github.com/CoderGamester/mcp-unity
date: 2026-04-02
tipo: aplicacao
---

# MCP Unity Editor: Conectar Agentes IA ao Editor para Automação de Cenas

## O que e

Plugin que expõe funcionalidades do Unity Editor via Model Context Protocol, permitindo agentes IA (Claude Code, Cursor, Windsurf) executar operações (criar GameObjects, modificar componentes, rodar testes) natively. Muda paradigma de "copiloto de código" para "agente com capacidade de ação".

## Como implementar

**Instalação via Package Manager**:
```
Window > Package Manager > (+) Add package from git URL
https://github.com/CoderGamester/mcp-unity.git
```

Ou manualmente clonando:
```bash
git clone https://github.com/CoderGamester/mcp-unity.git Assets/Plugins/MCP
```

**Configurar servidor Node.js**:
```bash
cd Assets/Plugins/MCP/Server~
npm install
npm run build
node build/index.js
# Servidor escuta em localhost:8090 por padrão
```

**Integração em IDE (Cursor/Windsurf/Claude Code)**. Adicionar ao .cursor/config.json ou .windsurf/config.json:
```json
{
  "mcpServers": {
    "unity-mcp": {
      "command": "node",
      "args": ["/absolute/path/to/mcp-unity/Server~/build/index.js"],
      "env": {
        "UNITY_PROJECT_PATH": "/path/to/unity/project"
      }
    }
  }
}
```

**Acessar ferramentas no chat do IDE** (exemplo em Claude Code):
```
@claude "Create a GameObject called 'Enemy' with tag 'Enemy', disabled by default"
```

Claude pode invocar:
```
{
  "tool": "create_gameobject",
  "params": {
    "name": "Enemy",
    "tag": "Enemy",
    "active": false
  }
}
```

**Ferramentas disponíveis** (100+):
- **Hierarquia**: `select_gameobject(id)`, `get_gameobject_info(id)`, `list_gameobjects()`
- **Transformações**: `move_gameobject(id, position)`, `rotate_gameobject(id, rotation)`
- **Componentes**: `create_component(id, type)`, `update_component(id, type, property, value)`
- **Assets**: `create_material(name)`, `assign_material(objectId, materialId)`, `add_package(packageName)`
- **Cenas**: `create_scene(name)`, `load_scene(sceneName)`, `save_scene()`
- **Testes**: `run_tests(testMode)`, `get_test_results()`
- **Debug**: `execute_menu_item(path)`, `send_console_log(message)`

**Recursos inteligentes** (contexto automático):
```
unity://scenes-hierarchy              # Lista GameObjects com transformações
unity://gameobject/{id}              # Inspeciona componentes específicos
unity://packages                     # Pacotes instalados
unity://assets                       # Assets disponíveis
unity://logs                         # Console output
unity://tests/{testMode}            # Info de testes
unity://menu-items                   # Items de menu disponíveis
```

**Exemplo de automação**: Criar inimigo com IA comportamento:
```csharp
[MCPTool("SpawnEnemy")]
public void SpawnEnemyWithAI(string enemyType, Vector3 position) {
    var enemy = Instantiate(enemyPrefab, position, Quaternion.identity);
    enemy.GetComponent<AIController>().SetBehavior(enemyType);
}

[MCPResource("EnemyBehaviors")]
public List<string> GetAvailableBehaviors() {
    return new List<string> { "patrol", "chase", "ranged_attack", "melee" };
}
```

Agent então pode invocar:
```
@claude "spawn 3 enemies of type 'patrol' in the scene"
```

## Stack e requisitos

- **Unity**: 6.0+ (ou 2022.3.18 LTS)
- **Node.js**: 18.0+
- **IDEs**: Cursor, Windsurf, Claude Code, GitHub Copilot (qualquer com suporte MCP)
- **OS**: Windows 10/11, macOS 11+, Linux
- **Portas**: TCP 8090 (customizável) para servidor MCP
- **Workspace**: Plugin auto-adiciona Library/PackedCache ao workspace do IDE

## Armadilhas e limitacoes

- **Sincronização**: Quando IA modifica cena, você vê mudanças em tempo real no editor, mas pode gerar conflitos se ambos (você e IA) editam simultaneamente.
- **Type information**: Pacotes custom C# requerem adicionar à Library/PackedCache para IntelliSense; sem isso, agente pode invocar ferramentas com parâmetros inválidos.
- **Tool discoverability**: Agente só consegue usar tools que foram explicitamente expostas com `[MCPTool]`; métodos privados ou internos não ficam acessíveis.
- **Editor-only**: Ferramentas executam no contexto do Editor; não funcionam em builds standalone (usar [[MCP em Jogos Compilados Unity]] para builds).
- **Determinismo**: Operações podem falhar silenciosamente se gameobject é deletado ou cena descarrega durante execução.

## Conexoes

[[MCP em Jogos Compilados Unity]] [[Model Context Protocol MCP Padrao Aberto]] [[Indexacao de Codebase para Agentes IA]]

## Historico

- 2026-04-02: Nota criada
- 2026-04-02: Reescrita para template aplicacao