---
tags: [unity, mcp, game-engine, llm, ai-agents, development-automation, npcs]
source: https://x.com/ErickSky/status/2036234646397051336?s=20
date: 2026-04-02
tipo: aplicacao
---

# Integrar Claude/LLMs no Unity via MCP para NPCs e Loop de Desenvolvimento Autônomo

## O que é

Unity-MCP é uma **ponte bidirecional** entre LLMs (Claude, Gemini, Copilot, Cursor) e o editor/runtime do Unity, implementando o protocolo MCP (Model Context Protocol). Diferentemente de simplesmente "usar IA para gerar código", Unity-MCP permite que um agente **execute diretamente** dentro do Unity:

- Criar/modificar GameObjects e componentes
- Executar scripts C# com parâmetros
- Ler estado do jogo em tempo real
- Fazer queries no scene e assets
- Rodar playtests automaticamente
- Corrigir bugs dentro do runtime

Tecnicamente: roda um servidor WebSocket inside Unity que implementa MCP spec, expondo métodos C# como "tools" que agentes LLM podem invocar. É o padrão de function calling (como OpenAI ou Anthropic API), mas para game engines.

## Por que importa agora

Três mudanças convergiram em 2025-2026:

1. **MCP matured**: protocolo padronizado para LLM ↔ ferramenta externa. Antes, cada integração era custom; agora é agnóstico a modelo.
2. **Game engines ainda não têm MCP oficial**: Unity e Unreal não implementaram nativamente. Isso criou vácuo que comunidade fill com open-source.
3. **Agentes LLM ficar bons em agentic loops**: Claude Code, Cursor Agents conseguem iterar (plan → code → test → fix) sem humano intervir. Integrar com Unity permite loop autônomo de game dev.

Para Leticia: significa poder usar Claude/Cursor para:
- Gerar comportamento de NPC dinamicamente
- Automatizar setup de cenas repetitivo
- Testar mecânicas durante desenvolvimento
- Iterar rapidamente sem breaking tasks

## Como funciona / Como implementar

### Arquitetura de Unity-MCP

```
┌─────────────────────────────────────────────────────┐
│ LLM Agent (Claude, Cursor, etc.)                    │
│ "Create a player movement script with dash ability" │
└─────────────────────────────────────────────────────┘
                        │
                   (MCP Protocol)
                        │
┌─────────────────────────────────────────────────────┐
│ MCP Server (Node.js wrapper)                        │
│ - Parses LLM tool calls                             │
│ - Translates to Unity method calls                  │
│ - Returns results to LLM                            │
└─────────────────────────────────────────────────────┘
                        │
                  (WebSocket)
                        │
┌─────────────────────────────────────────────────────┐
│ Unity Editor / Runtime                              │
│ - Exposed C# tools (CreateGameObject, RunScript)    │
│ - Can read/write scene state                        │
│ - Execute playtests                                 │
└─────────────────────────────────────────────────────┘
```

### Setup básico: Unity + MCP

**Opção A: Usar implementação pronta (IvanMurzak/Unity-MCP)**

```bash
# 1. Clonar repo
git clone https://github.com/IvanMurzak/Unity-MCP.git
cd Unity-MCP

# 2. Instalar dependências Node.js
npm install

# 3. Copiar plugin Unity para seu projeto
# Copiar pasta UPM para ./Assets/com.ivanmurzak.unity.mcp/

# 4. No Unity Editor, ir para Window > AI > MCP
# Configurar host/port (default: localhost:8000)

# 5. Conectar Claude Code/Cursor
# No VS Code/Cursor, instalar MCP extension e apontar para localhost:8000
```

**Opção B: Implementação custom (mais controle)**

```csharp
// MCPServer.cs - Servidor MCP dentro do Unity

using UnityEngine;
using WebSocketSharp;
using System.Collections.Generic;
using System.Reflection;

public class MCPServer : MonoBehaviour
{
    private WebSocketServer wsServer;
    private Dictionary<string, MethodInfo> exposedTools = new();
    
    void Start()
    {
        // Inicializar servidor WebSocket
        wsServer = new WebSocketServer("ws://0.0.0.0:8000");
        wsServer.AddWebSocketBehavior<MCPBehavior>("/mcp");
        wsServer.Start();
        
        Debug.Log("MCP Server started on ws://localhost:8000/mcp");
        
        // Registrar ferramentas disponíveis
        RegisterTools();
    }
    
    void RegisterTools()
    {
        // Auto-discover methods com [MCPTool] attribute
        foreach (MonoBehaviour mono in FindObjectsOfType<MonoBehaviour>())
        {
            foreach (MethodInfo method in mono.GetType().GetMethods())
            {
                if (method.GetCustomAttribute<MCPToolAttribute>() != null)
                {
                    string toolName = method.Name;
                    exposedTools[toolName] = method;
                    Debug.Log($"Registered tool: {toolName}");
                }
            }
        }
    }
}

// Atributo para marcar métodos que podem ser chamados por LLM
[System.AttributeUsage(System.AttributeTargets.Method)]
public class MCPToolAttribute : System.Attribute
{
    public string description;
    
    public MCPToolAttribute(string desc = "")
    {
        description = desc;
    }
}

// Exemplo: GameManager com tools expostas
public class GameManager : MonoBehaviour
{
    [MCPTool("Create a GameObject at position with specified components")]
    public void CreateGameObject(
        string name,
        float x, float y, float z,
        string[] components)
    {
        GameObject obj = new GameObject(name);
        obj.transform.position = new Vector3(x, y, z);
        
        foreach (string componentName in components)
        {
            System.Type componentType = System.Type.GetType($"UnityEngine.{componentName}");
            if (componentType != null)
            {
                obj.AddComponent(componentType);
                Debug.Log($"Added component {componentName}");
            }
        }
    }
    
    [MCPTool("Get list of all GameObjects in scene")]
    public string[] GetGameObjects()
    {
        GameObject[] allObjects = FindObjectsOfType<GameObject>();
        return System.Array.ConvertAll(allObjects, go => go.name);
    }
    
    [MCPTool("Execute C# script as string (dangerous, use with caution)")]
    public void ExecuteScript(string csharpCode)
    {
        // Nota: Isso é PERIGOSO em produção. Apenas para dev.
        // Em produção, usar code generation + compilation,
        // ou whitelist de scripts pré-compilados
        
        Debug.Log($"Script execution requested: {csharpCode}");
        // Implementação real usaria Roslyn ou similiar
    }
}
```

### Exemplo 1: NPC com comportamento gerado por LLM

```csharp
// NPCController.cs - NPC cujo comportamento é dirigido por LLM

using UnityEngine;
using System.Collections;

public class NPCController : MonoBehaviour
{
    public string npcName = "Merchant";
    public string npcBackground = "Sells potions at the tavern";
    
    [MCPTool("Get NPC current status and memory")]
    public string GetNPCStatus()
    {
        return $"{npcName}: {npcBackground}. " +
               $"Position: {transform.position}. " +
               $"Current state: Idle";
    }
    
    [MCPTool("Make NPC say dialogue")]
    public void SayDialogue(string dialogue)
    {
        // Exibir dialogue bubble
        Debug.Log($"[{npcName}]: {dialogue}");
        
        // TODO: Integrar com sistema de dialogue do jogo
    }
    
    [MCPTool("Move NPC to target")]
    public IEnumerator MoveTo(float x, float y, float z)
    {
        Vector3 targetPos = new Vector3(x, y, z);
        float speed = 2f;
        
        while (Vector3.Distance(transform.position, targetPos) > 0.1f)
        {
            transform.position = Vector3.Lerp(
                transform.position,
                targetPos,
                Time.deltaTime * speed
            );
            yield return null;
        }
        
        Debug.Log($"{npcName} reached target");
    }
    
    [MCPTool("Query NPC dialogue tree for appropriate response")]
    public string GetDialogueResponse(string playerStatement)
    {
        // Em produção: consultar dialogue system, retornar opção contextual
        // Para demo: LLM gerará resposta dinamicamente
        return $"{npcName} responds to: '{playerStatement}'";
    }
}
```

**Fluxo de uso:**
```
Claude Code / Cursor Agent (com MCP conectado)

Prompt: "Create an NPC vendor in the tavern that responds dynamically to player dialogue."

Agente responde:
1. "Vou criar um NPC. Primeiro, get list of scenes..."
   → Chama GetGameObjects() via MCP
2. "Vou criar um GameObject novo chamado Vendor..."
   → Chama CreateGameObject("Vendor", 10, 0, 5, ["SpriteRenderer", "Collider"])
3. "Agora vou adicionar comportamento de diálogo..."
   → Gera script C# e pede para executar (ou usa template)
4. "Teste: o NPC responde adequadamente?"
   → Simula playerStatement via GetDialogueResponse()
5. Itera até estar satisfeito
```

### Exemplo 2: Loop autônomo de feature development

```csharp
// AutoPlaytester.cs - Executa testes automaticamente

public class AutoPlaytester : MonoBehaviour
{
    [MCPTool("Run automated playtest scenario")]
    public PlaytestResult RunPlaytest(string scenarioName)
    {
        switch (scenarioName)
        {
            case "player_movement":
                return TestPlayerMovement();
            case "combat":
                return TestCombat();
            case "inventory":
                return TestInventory();
            default:
                return new PlaytestResult { passed = false, error = "Unknown scenario" };
        }
    }
    
    [MCPTool("Get playtest results and errors")]
    public string GetPlaytestLog()
    {
        // Retorna log dos últimos testes
        return "Playtest log: [...]";
    }
    
    PlaytestResult TestPlayerMovement()
    {
        var player = GameObject.Find("Player");
        if (player == null)
            return new PlaytestResult { passed = false, error = "Player not found" };
        
        // Simular input de movimento
        player.GetComponent<Rigidbody>().velocity = Vector3.right * 5;
        
        // Esperar e validar
        System.Threading.Thread.Sleep(100);
        
        if (player.transform.position.x > 0)
            return new PlaytestResult { passed = true };
        else
            return new PlaytestResult { passed = false, error = "Player didn't move" };
    }
    
    PlaytestResult TestCombat()
    {
        // TODO: Implementar testes de combate
        return new PlaytestResult { passed = true };
    }
    
    PlaytestResult TestInventory()
    {
        // TODO: Implementar testes de inventário
        return new PlaytestResult { passed = true };
    }
}

public struct PlaytestResult
{
    public bool passed;
    public string error;
}
```

**Fluxo autônomo:**
```
Agente LLM com MCP:

1. "Implementei a feature de dash do player"
   → Adiciona script DashAbility.cs
2. "Vou testar se funciona..."
   → Chama RunPlaytest("player_movement")
3. "Resultado: FAILED - Player didn't move"
4. "Deixa eu debugar... O problema é que Rigidbody não está configurado."
   → Modifica prefab, adiciona componente Rigidbody
5. "Teste novamente..."
   → RunPlaytest("player_movement") → PASSED
6. "Feature completa!"
```

## Stack técnico

- **Protocolo**: MCP (Model Context Protocol) — spec aberta
- **MCP Servers para Unity**:
  - [IvanMurzak/Unity-MCP](https://github.com/IvanMurzak/Unity-MCP) (mais completo)
  - [CoderGamester/mcp-unity](https://github.com/CoderGamester/mcp-unity)
  - [CoplayDev/unity-mcp](https://github.com/CoplayDev/unity-mcp)
- **Transporte**: WebSocket (ws://)
- **LLM Clients**: Claude Code, Cursor, Copilot, qualquer IDE com suporte a MCP
- **Linguagem**: C# (Unity), TypeScript/Node.js (MCP wrapper)
- **Assets relacionados**: OpenUPM package `com.ivanmurzak.unity.mcp`

## Código prático: Minimal viable MCP server

```csharp
// MinimalMCPServer.cs - MCP server super-minimalista

using UnityEngine;
using System.Collections.Generic;

public class MinimalMCPServer : MonoBehaviour
{
    // Estrutura MCP de request/response
    [System.Serializable]
    public class MCPRequest
    {
        public string method;
        public Dictionary<string, object> params_;
    }
    
    [System.Serializable]
    public class MCPResponse
    {
        public object result;
        public string error;
    }
    
    void Start()
    {
        // Listener HTTP simples (sem WebSocket)
        // Em produção, usar WebSocket via WebSocketSharp
        Debug.Log("Minimal MCP Server ready");
    }
    
    // Handlers para métodos expostos
    public object HandleToolCall(string toolName, Dictionary<string, object> args)
    {
        switch (toolName)
        {
            case "instantiate_prefab":
                return InstantiatePrefab(
                    (string)args["prefabName"],
                    (float)args["x"],
                    (float)args["y"]
                );
            
            case "get_scene_objects":
                return GetSceneObjects();
            
            case "destroy_object":
                return DestroyObject((string)args["objectName"]);
            
            default:
                return new { error = $"Unknown tool: {toolName}" };
        }
    }
    
    object InstantiatePrefab(string name, float x, float y)
    {
        GameObject prefab = Resources.Load<GameObject>($"Prefabs/{name}");
        if (prefab == null)
            return new { error = $"Prefab not found: {name}" };
        
        GameObject instance = Instantiate(prefab, new Vector3(x, y, 0), Quaternion.identity);
        return new { success = true, objectName = instance.name };
    }
    
    object GetSceneObjects()
    {
        List<string> names = new();
        foreach (GameObject go in FindObjectsOfType<GameObject>())
        {
            if (go.scene.isLoaded)  // Só objetos na scene atual
                names.Add(go.name);
        }
        return new { objects = names };
    }
    
    object DestroyObject(string objectName)
    {
        GameObject obj = GameObject.Find(objectName);
        if (obj == null)
            return new { error = $"Object not found: {objectName}" };
        
        Destroy(obj);
        return new { success = true };
    }
}
```

## Armadilhas e Limitações

### 1. **Segurança: LLM pode executar código arbitrário via MCP**
Se você expõe método `ExecuteScript()` que roda C# dinâmico, o LLM pode ser manipulado (via prompt injection) para executar código malicioso, deletar cenas inteiras, ou roubar assets.

**Mitigação**: 
- **Whitelist** de tools: expor apenas métodos específicos, necessários
- **Validação de parâmetros**: checklist tipos, ranges, padrões antes de executar
- **Sandbox**: rodar em projeto de test, não em producton builds
- **Audit logging**: registrar todas as tool calls, revisar antes de deploy

```csharp
// Seguro: validação de parâmetros antes de executar
[MCPTool("Spawn enemy at position")]
public void SpawnEnemy(string enemyType, float x, float y)
{
    // Whitelist de tipos
    string[] allowedEnemies = { "Goblin", "Orc", "Dragon" };
    if (System.Array.IndexOf(allowedEnemies, enemyType) == -1)
        throw new System.ArgumentException($"Enemy type not allowed: {enemyType}");
    
    // Validar range (dentro da scene)
    if (x < -100 || x > 100 || y < -100 || y > 100)
        throw new System.ArgumentException("Position out of bounds");
    
    // Só então executar
    Instantiate(Resources.Load($"Enemies/{enemyType}"), new Vector3(x, y, 0), Quaternion.identity);
}
```

### 2. **Latência de rede bloqueia iterações rápidas**
Cada ferramenta chamada = round trip via WebSocket. Se agente quer iterar 10 vezes (test → fail → fix → test), são 10 round trips, cada um com latência de rede (mesmo local, 10-50ms por trip = 100-500ms de overhead).

**Mitigação**:
- Batch calls: agente agrupa múltiplas calls em uma único request MCP
- Callbacks: server invoca agente quando evento acontece (ao invés de agente sempre polling)
- Cache: agente caching state para não queryar repetidamente

### 3. **Incompatibilidade entre versões de Unity e MCP**
Unity updates quebram APIs. MCP server que funcionava em 2023.2 pode não funcionar em 2026.1 sem ajustes.

**Mitigação**: manter dependências atualizadas, usar package manager (UPM) vs. manual imports, ter testes que validam integration sempre.

### 4. **Agente gera código que não compila**
LLM gera C# bonito no papel, mas com typos, imports faltantes, ou chamadas a métodos que não existem. Agente não sabe que código não vai compilar até tentar executar.

**Mitigação**:
- Usar roslyn compiler para validar C# antes de executar
- Forçar agente a usar templates pré-compilados (Blueprint pattern)
- Feedback loop: se compilation fails, enviar erro para agente, deixar ele debugar

```csharp
// Template seguro: agente preenche blank, não escreve do zero
public class GeneratedBehavior : MonoBehaviour
{
    void Update()
    {
        // [GENERATED_CODE_HERE] — agente preenche isto
    }
    
    // Métodos pre-existentes que agente pode chamar
    void Move(Vector3 direction) { /* ... */ }
    void Attack() { /* ... */ }
}
```

### 5. **Performance: muitas tool calls congelam editor/runtime**
Se agente faz 1000 GetGameObjects() calls (um por NPC), game fica lento.

**Mitigação**: implementar eficiência:
- Cache queries (GetGameObjects with filter)
- Batch operations (criar 100 GameObjects em 1 call, não 100 calls)
- Async operations: usar IEnumerator para não bloquear

## Conexões

- [[spec-driven-development|Spec-Driven Development]] — MCP tools são especificações de comportamento que agentes consomem
- [[mcp-tool-composition|MCP Tool Composition]] — padrão de como compor e orquestrar múltiplas tools
- [[Maestri Orquestrador de Agentes de IA com Canvas 2D|Maestri]] — orquestração de múltiplos agentes para game dev
- [[10 Projetos MCP Agents RAG Código|MCP Agents em Produção]] — exemplos de MCP em outros domínios
- [[claude-code-operações-automatizadas|Claude Code Operações Automatizadas]] — contexto de Claude Code como agente

## Perguntas de Revisão
1. Como Unity-MCP diferencia-se de simplesmente usar Claude Code para gerar código de script?
2. Por que a segurança (validação de ferramentas expostas) é crítica em MCP?
3. Como você estruturaria um loop autônomo de feature development game dev mantendo qualidade?

## Histórico de Atualizações
- 2026-04-02: Nota criada a partir de Telegram
- 2026-04-11: Expandida com arquitetura, setup (opções A/B), exemplos (NPCs dinâmicos, loop autônomo), stack técnico, código prático (minimal MCP server), armadilhas (segurança, latência, versioning, compilation, performance), conexões