---
tags: [agentes-ia, orquestracao, visualizacao, claude-code, ferramentas-dev, debugging, observabilidade]
source: https://x.com/tom_doerr/status/2037413316537028899?s=20
date: 2026-04-02
tipo: aplicacao
---

# Usar agent-flow para Visualizar e Debugar Orquestração de Agentes Claude Code

## O que é

`agent-flow` é uma ferramenta VS Code que captura e visualiza em tempo real como um agente Claude Code executa tarefas complexas. Mostra como o agente decompõe problemas, invoca ferramentas (shell, filesystem, web), passa contexto entre chamadas e itera para resolver. Transforma uma execução de "caixa preta" em um grafo interativo de decisões, ramificações e resultados.

Versão: Está disponível como extensão VS Code (Open VSX + VS Code Marketplace) com suporte a JSONL event logs para análise offline.

## Por que importa agora

**1. Agentic AI é opaco por design**
Quando você pede ao Claude Code: "refatore meu projeto inteiro", ele dispara uma sequência de 50+ chamadas internas (lê arquivos, analisa estrutura, gera planos, executa edições, valida outputs). Sem visualização, você vê só o resultado final. Se algo falhar na iteração #47, é quase impossível diagnosticar.

**2. Produção exige observabilidade**
Sistemas LLM em produção (como pipelines de data engineering, automação de infra, code migration) precisam de **auditoria**, **debug** e **otimização**. Agent-flow torna isso possível:
- Detectar loops infinitos (agente tentando resolver problema X 10x)
- Identificar chamadas redundantes (ler arquivo Y múltiplas vezes)
- Mapear consumo de tokens por sub-tarefa

**3. Engenharia de prompts se torna científica**
Em vez de "por que o agente não fez Y?", você vê exatamente onde a decisão divergiu. Isso permite iterar prompts com dados, não intuição.

## Como funciona / Como implementar

### Setup Inicial

```bash
# 1. Instalar agent-flow no VS Code
# - Abrir Command Palette (Ctrl+Shift+P)
# - Digitar: "Extensions: Install Extensions"
# - Buscar: "agent-flow" ou "Agent Visualizer"
# - Instalar

# 2. Configurar Claude Code hooks (automático)
# - Ao abrir agent-flow panel, ele auto-detecta uma sessão Claude Code
# - Configura hooks automaticamente (salva em ~/.claude/hooks.json)

# 3. (Opcional) Configurar log file
# - Adicionar em VS Code settings.json:
```

```json
{
  "agentVisualizer.eventLogPath": "/path/to/events.jsonl",
  "agentVisualizer.captureLevel": "full"  // full | summary | errors-only
}
```

### Fluxo de Captura

```
Sessão Claude Code inicia
    ↓
Agent-flow hooks interceptam eventos
    ↓
Cada evento (tool call, decision, branch) é capturado:
  {
    "timestamp": "2026-04-11T14:23:45Z",
    "type": "tool_call",
    "tool": "bash",
    "input": "find . -name '*.js' | head -20",
    "output": "[lista de arquivos]",
    "tokens_used": 234,
    "latency_ms": 1240
  }
    ↓
VS Code panel atualiza em tempo real
    ↓
Grafo de nós e arestas renderizado interativamente
```

### Interface Típica do Agent-Flow

```
┌─ Histórico de Eventos (timeline)
│  ├─ 14:23:45 [BASH] find . -name *.js (234 tokens)
│  ├─ 14:23:47 [FILE_READ] Ler package.json (112 tokens)
│  ├─ 14:23:48 [DECISION] Analisar dependências → gerar plano
│  ├─ 14:23:50 [BASH] npm audit (401 tokens) ❌ ERRO
│  └─ 14:23:52 [RETRY] npm install (890 tokens) ✓

┌─ Visualização em Grafo
│  ┌─────────────┐
│  │   Task 1    │ ──→ [BASH: find]
│  │ "Analisar"  │
│  └─────────────┘
│         ↓
│  ┌─────────────┐
│  │   Task 2    │ ──→ [FILE: read]
│  │ "Planejar"  │ ──→ [DECISION]
│  └─────────────┘
│         ↓
│     ┌─ [RETRY] → ✓
│     └─ [FAIL] → 💥

┌─ Métricas
│  Total de eventos: 247
│  Tokens consumidos: 12,450 / 100,000
│  Tempo total: 2m 34s
│  Ferramentas invocadas: [bash, file_read, file_write, web]
│  Taxa de sucesso: 94% (1 retry, 2 branches)
```

## Stack técnico

| Componente | Implementação | Função |
|---|---|---|
| **Hook System** | Event listeners em Claude Code API | Captura todas as tool invocations |
| **Event Store** | JSONL (append-only) ou SQLite | Persist de eventos para análise |
| **Graph Builder** | Graphlib + D3.js | Construir/renderizar DAG de execução |
| **Panel UI** | VS Code Webview API | Interface interativa em TypeScript + React |
| **Query Engine** | Simple JSONL grep + custom indices | Buscar eventos por tool/timestamp/tokens |

## Código prático

### Exemplo 1: Estrutura de Evento Capturado

```json
{
  "id": "evt_abc123",
  "sessionId": "claude_code_xyz",
  "timestamp": "2026-04-11T14:23:45.123Z",
  "sequenceNumber": 47,
  
  "agent": {
    "model": "claude-opus-4.6",
    "temperature": 0.3,
    "systemPrompt": "Você é um assistente especializado..."
  },
  
  "decision": {
    "type": "tool_selection",
    "available_tools": ["bash", "file_read", "file_write", "web_fetch"],
    "chosen_tool": "bash",
    "reasoning": "Preciso listar arquivos para entender a estrutura do projeto"
  },
  
  "execution": {
    "tool": "bash",
    "input": "find . -type f -name '*.js' | grep -E '(test|spec)' | wc -l",
    "exitCode": 0,
    "output": "23\n",
    "stderr": "",
    "duration_ms": 234,
    "tokensUsed": {
      "input": 120,
      "output": 85
    }
  },
  
  "nextStep": {
    "action": "file_read",
    "files": ["package.json", ".eslintrc.js"],
    "reasoning": "Validar dependências e style guide"
  },
  
  "metadata": {
    "depth": 5,  // quanto nível no grafo
    "branch": "main",  // qual decisão anterior levou aqui
    "retriable": true,
    "hasErrors": false
  }
}
```

### Exemplo 2: Parser de Logs para Análise

```python
import json
from datetime import datetime
from collections import defaultdict

class AgentFlowAnalyzer:
    def __init__(self, jsonl_path):
        self.events = []
        with open(jsonl_path) as f:
            for line in f:
                self.events.append(json.loads(line))
    
    def token_usage_by_tool(self):
        """Quantos tokens cada ferramenta consumiu"""
        usage = defaultdict(int)
        for event in self.events:
            tool = event.get('execution', {}).get('tool')
            tokens = event.get('execution', {}).get('tokensUsed', {}).get('input', 0)
            if tool:
                usage[tool] += tokens
        return dict(sorted(usage.items(), key=lambda x: x[1], reverse=True))
    
    def retry_analysis(self):
        """Identificar padrões de retry/erro"""
        retries = []
        for i, event in enumerate(self.events):
            if event.get('execution', {}).get('exitCode') != 0:
                # Procurar se há retry dentro dos próximos 5 eventos
                for j in range(i+1, min(i+6, len(self.events))):
                    if self.events[j].get('execution', {}).get('exitCode') == 0:
                        retries.append({
                            'attempt': i,
                            'retry_at': j,
                            'tool': event.get('execution', {}).get('tool'),
                            'error': event.get('execution', {}).get('stderr')
                        })
                        break
        return retries
    
    def decision_tree(self):
        """Mapear sequência de decisões (como árvore)"""
        tree = []
        for event in self.events:
            decision = event.get('decision', {})
            tree.append({
                'seq': event.get('sequenceNumber'),
                'tool': decision.get('chosen_tool'),
                'reasoning': decision.get('reasoning'),
                'depth': event.get('metadata', {}).get('depth')
            })
        return tree
    
    def performance_summary(self):
        """Estatísticas de execução"""
        if not self.events:
            return None
        
        start = datetime.fromisoformat(self.events[0]['timestamp'])
        end = datetime.fromisoformat(self.events[-1]['timestamp'])
        
        total_tokens = sum(
            e.get('execution', {}).get('tokensUsed', {}).get('input', 0)
            for e in self.events
        )
        
        total_time = (end - start).total_seconds()
        errors = sum(1 for e in self.events if e.get('execution', {}).get('exitCode') != 0)
        
        return {
            'total_events': len(self.events),
            'total_tokens': total_tokens,
            'total_time_sec': total_time,
            'errors': errors,
            'success_rate': f"{(1 - errors/len(self.events))*100:.1f}%",
            'avg_time_per_event': total_time / len(self.events)
        }

# Uso
analyzer = AgentFlowAnalyzer('agent_events.jsonl')
print("Tokens por ferramenta:", analyzer.token_usage_by_tool())
print("Retries detectados:", analyzer.retry_analysis())
print("Resumo:", analyzer.performance_summary())
```

### Exemplo 3: Hook Simples para Capturar Eventos (protótipo)

```typescript
// Arquivo: ~/.claude/hooks.ts
import * as fs from 'fs';

interface AgentEvent {
  timestamp: string;
  tool: string;
  input: string;
  output: string;
  duration_ms: number;
}

class EventLogger {
  private logPath = '~/.claude/agent_events.jsonl';
  
  log(event: AgentEvent) {
    const line = JSON.stringify(event) + '\n';
    fs.appendFileSync(this.logPath, line);
  }
  
  onToolInvoked(tool: string, input: any) {
    const start = Date.now();
    
    return {
      tool,
      input,
      onComplete: (output: any) => {
        this.log({
          timestamp: new Date().toISOString(),
          tool,
          input: JSON.stringify(input),
          output: JSON.stringify(output),
          duration_ms: Date.now() - start
        });
      }
    };
  }
}

export const eventLogger = new EventLogger();
```

## Armadilhas e Limitações

### 1. **Overhead de captura pode desacelerar agentes**
Capturar eventos (serializar JSON, appendar em arquivo, atualizar UI) consome CPU. Em agentes que fazem 100+ tool calls por minuto, o overhead pode aumentar latência em 15-30%.

**Solução**: Usar níveis de captura:
- `errors-only`: só eventos com exitCode != 0
- `summary`: um evento por "fase" lógica, não por tool call
- `full`: tudo (dev mode)

### 2. **Visualização em grafo fica incompreensível após 200+ eventos**
Grafos D3.js começam a ficar lerdos com 300+ nós. Zoom, pan, searching viram painosos.

**Solução**: Impleemntar filtros e agregação:
- Agrupar por "tarefa lógica" (tool calls sequenciais para um objetivo)
- Permitir expandir/colapsar branches
- Busca por ferramenta, timestamp, keywords em output

### 3. **Privacidade: logs conterão dados sensíveis**
Logs contêm conteúdo completo (arquivo lido, output de comandos). Se o arquivo é um `.env` ou `.sql`, esses secrets acabam em logs.

**Solução**:
- Implementar masking automático (regex para AWS keys, DB strings, etc.)
- Configurar pastas excluídas de captura
- Logs armazenados localmente em `~/.claude/` (não upload automático)

### 4. **Falta de controle versional de prompts**
Se você iterar um prompt 10 vezes, qual evento corresponde a qual versão? Difícil traçar.

**Solução**: Adicionar `promptVersion` ou `promptHash` em cada evento:
```json
{
  "promptVersion": "v1.2.3",
  "promptHash": "sha256:abc...",
  "systemPromptChecksum": "xyz..."
}
```

### 5. **Análise de "por que o agente falhou" ainda requer humano**
Agent-flow mostra **o que** aconteceu, não **por que**. Se agente fez 47 calls corretas e falhou na 48ª, você vê a falha mas precisa manualmente analisar por que a decision na 47ª foi subótima.

**Solução prática**: Usar agent-flow + LLM analyzer:
```python
# Pedir ao Claude para analisar os eventos:
analyzer_prompt = f"""
Analise esses {len(events)} eventos de execução de agente.
Identifique:
1. Padrão de erro (repete?)
2. Decisão subótima (ferramenta errada para tarefa?)
3. Recomendação para prompt melhor

Eventos: {json.dumps(events)}
"""
```

## Conexões

- [[Claude Code]] — agente que gera eventos capturáveis por agent-flow
- [[Multi-Agent Decomposition]] — teoria de como decompor tarefas entre agentes
- [[Observabilidade em Sistemas de Produção]] — princípios de monitoring que agent-flow implementa
- [[Vibe Coding para Desenvolvimento de Jogos]] — vibe-coded projects precisam de agent-flow para iterar rápido
- [[LangSmith e Observabilidade em LLM Chains]] — paralelo em LangChain (agent-flow é para Claude Code)

## Perguntas de Revisão

1. **Qual é a diferença entre capturar eventos via hooks vs. via logs de stderr?** Quando cada abordagem é melhor?
2. **Como estruturar uma "fase" lógica** em um grafo de 500+ eventos para não virar sopa visual?
3. **Em um sistema multiagente (10+ agentes colaborando),** como visualizar comunicação entre eles? (Agent-flow é single-agent centric.)
4. **Como usar agent-flow para otimizar custos** — quais métricas priorizar?

## Histórico de Atualizações

- 2026-04-02: Nota criada a partir de Telegram
- 2026-04-11: Expandida com código de parser, estrutura de eventos, setup, armadilhas e conexões