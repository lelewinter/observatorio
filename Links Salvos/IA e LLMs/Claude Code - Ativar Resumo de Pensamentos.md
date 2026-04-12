---
date: 2026-03-28
tags: [claude-code, thinking-tokens, extended-thinking, adaptive-thinking, debug, configuration]
source: https://x.com/Butanium_/status/2037575095569269201
autor: "@Butanium_"
tipo: aplicacao
---

# Ativar Resumo de Pensamentos Oculto em Claude Code

## O que é

Claude Code v2.1.69+ implementa **Adaptive Thinking** (evolução de Extended Thinking) que permite Claude raciocinar profundamente antes de responder. O "thinking" (raciocínio interno) é registrado em tokens especiais e pode ser visualizado via settings, revelando a lógica por trás de decisões complexas.

**Mapa de conceitos**:
- **Extended Thinking** (deprecated 2025): Budget manual de tokens de raciocínio (10K-100K)
- **Adaptive Thinking** (novo, 2026+): Claude decide automaticamente profundidade de raciocínio baseado em `effort` parameter e complexidade da tarefa
- **Thinking Summaries**: Resumo em texto do raciocínio interno (não full transcript, economiza contexto)
- **Claude Code GUI**: Painel lateral que mostra "Thinking" quando configurado

## Por que importa agora

1. **Compreensão de decisões**: Ver exatamente qual lógica Claude usou para debugar bugs, refatorar código, ou propor arquitetura
2. **Prompt refinement**: Entender se Claude entendeu o problema corretamente ou precisa de mais contexto
3. **Performance tuning**: Identificar quando Claude "pensa demais" (usa muitos tokens) vs quando "pula etapas"
4. **Custo otimizado**: Adaptive Thinking reduz overhead — Claude só pensa quando necessário
5. **API para automação**: `/effort` command permite calibrar raciocínio via script

## Como funciona / Como implementar

### 1. Entender o Sistema de Thinking em Claude Code 2026

```
┌─────────────────────────────────────────────────────┐
│ User Query                                          │
└────────────────────┬────────────────────────────────┘
                     │
                     ▼
        ┌────────────────────────────┐
        │ Adaptive Thinking Decision │ ← Effort parameter
        │ (Automatic)                │   (user-configurable)
        └────────────┬───────────────┘
                     │
          ┌──────────┴──────────┐
          ▼                     ▼
      Thinking         Direct Response
      (Budget: 5-50K)   (fast, cached)
          │                   │
          └─────────┬─────────┘
                    ▼
           ┌─────────────────┐
           │ Thinking Summary│ ← "Thinking" tab
           │ (compressed)    │
           └─────────────────┘
```

### 2. Setup: Localizar e Editar settings.json

#### Windows

```bash
# Abrir PowerShell ou CMD

# Caminho padrão AppData
cd %APPDATA%\Claude

# Se não existir, criar
mkdir %APPDATA%\Claude

# Editar arquivo (ou criar se não existir)
# Opção 1: Notepad
notepad settings.json

# Opção 2: VS Code
code settings.json
```

#### macOS

```bash
# Terminal
cd ~/Library/Application\ Support/Claude

# Editar
nano settings.json
# ou
open settings.json  # abre em default editor
```

#### Linux

```bash
# Home directory
cd ~/.config/Claude
# ou ~/.local/share/Claude (dependendo de distro)

# Editar
vim settings.json
```

### 3. Configuração settings.json Completa

```json
{
  "showThinkingSummaries": true,
  "adaptiveThinkingEnabled": true,
  "defaultEffort": "medium",
  "theme": "dark",
  "fontSize": 14
}
```

**Campos detalhados**:

| Campo | Tipo | Valores | Descrição |
|-------|------|---------|-----------|
| `showThinkingSummaries` | boolean | `true` / `false` | Ativar painel de "Thinking" |
| `adaptiveThinkingEnabled` | boolean | `true` / `false` | Usar Adaptive Thinking (automático) vs budget manual |
| `defaultEffort` | string | `"low"` / `"medium"` / `"high"` | Profundidade padrão de raciocínio |
| `thinkingVisibility` | string | `"summary"` / `"full"` / `"none"` | Mostrar resumo, full transcript, ou nada |

### 4. Reiniciar Claude Code

```bash
# Fechar completamente
# Windows: Fechar app, ou via Task Manager:
taskkill /IM "Claude.exe" /F

# macOS: 
killall Claude

# Linux:
killall claude

# Reabrir Claude Code
# UI: Start menu → Claude Code
# ou via CLI:
claude-code start
```

### 5. Usar o Thinking Panel

**Visualização no UI**:
```
┌──────────────────────────────┬──────────────────────┐
│ Chat Panel                   │ Debug Panel (direita)│
│                              │                      │
│ User: "Debug este erro"      │ 🧠 Thinking          │
│                              │ ───────────────────  │
│ Claude: "Analisando..."      │ Claude está          │
│                              │ considerando:        │
│                              │ 1. Erro é tipo...    │
│                              │ 2. Causa provável... │
│                              │ 3. Solução: ...      │
│ Response aparece aqui        │                      │
│                              │ Tokens: 8.2K / 50K   │
└──────────────────────────────┴──────────────────────┘
```

### 6. Controlar Effort via CLI/API

```python
# Exemplo: Claude Code API (se disponível em 2026)
import subprocess
import json

class ClaudeCodeClient:
    def __init__(self):
        self.base_url = "http://localhost:8800"  # Local Claude Code server
    
    def set_effort(self, level: str):
        """Define profundidade de raciocínio: 'low', 'medium', 'high'"""
        payload = {"effort": level}
        # Chamar API local Claude Code
        result = subprocess.run(
            ["claude-code", "config", "set", "effort", level],
            capture_output=True,
            text=True
        )
        print(f"Effort set to: {level}")
    
    def query_with_effort(self, prompt: str, effort: str = "medium"):
        """Executar query com effort customizado"""
        # Pseudocódigo: Claude Code v2.5+ deve suportar isto
        response = self._call_api({
            "messages": [{"role": "user", "content": prompt}],
            "effort": effort,  # 'low': 1-5K tokens | 'medium': 10-20K | 'high': 30-50K
            "show_thinking": True
        })
        return response

# Uso
client = ClaudeCodeClient()

# Query com raciocínio profundo (para problema complexo)
client.set_effort("high")
response = client.query_with_effort(
    prompt="Refactor meu sistema de cache, está com memory leak",
    effort="high"
)

# Query rápida (para tarefa simples)
client.set_effort("low")
response = client.query_with_effort(
    prompt="Formatar este JSON",
    effort="low"
)

print(response["thinking_summary"])  # Resumo do raciocínio
print(response["answer"])
```

### 7. Extrair e Analisar Thinking Transcripts

```python
import json
from pathlib import Path
import re

class ThinkingAnalyzer:
    """Analisar padrões de raciocínio de Claude"""
    
    def __init__(self, thinking_log_path: str = "~/.claude/thinking_logs.jsonl"):
        self.log_path = Path(thinking_log_path).expanduser()
    
    def parse_session(self):
        """Ler thinking logs (JSONL format)"""
        sessions = []
        
        if not self.log_path.exists():
            print(f"[WARN] Log file not found: {self.log_path}")
            return sessions
        
        with open(self.log_path, 'r') as f:
            for line in f:
                try:
                    entry = json.loads(line)
                    sessions.append(entry)
                except json.JSONDecodeError:
                    continue
        
        return sessions
    
    def analyze_thinking_depth(self, sessions):
        """Extrair profundidade média de raciocínio por tipo de tarefa"""
        
        task_types = {}
        
        for session in sessions:
            task_type = session.get("task_type", "unknown")
            thinking_tokens = session.get("thinking_tokens", 0)
            effort_level = session.get("effort", "medium")
            
            if task_type not in task_types:
                task_types[task_type] = {
                    "count": 0,
                    "total_tokens": 0,
                    "efforts": {}
                }
            
            task_types[task_type]["count"] += 1
            task_types[task_type]["total_tokens"] += thinking_tokens
            
            if effort_level not in task_types[task_type]["efforts"]:
                task_types[task_type]["efforts"][effort_level] = 0
            task_types[task_type]["efforts"][effort_level] += 1
        
        # Exibir análise
        for task, stats in task_types.items():
            avg_tokens = stats["total_tokens"] / stats["count"]
            print(f"\n[{task.upper()}]")
            print(f"  Média: {avg_tokens:.0f} tokens")
            print(f"  Ocorrências: {stats['count']}")
            print(f"  Effort distribution: {stats['efforts']}")
    
    def extract_thinking_summary(self, session):
        """Extrair texto do thinking summary"""
        
        thinking_text = session.get("thinking_summary", "")
        
        # Parser simples: separar em etapas
        steps = re.split(r'\n\d+\.\s+', thinking_text)
        
        return {
            "total_steps": len(steps),
            "steps": steps,
            "key_insights": self._extract_insights(thinking_text)
        }
    
    def _extract_insights(self, text: str):
        """Extrair insights principais"""
        
        insights = []
        
        # Regex para "I should", "I need to", "The problem is"
        patterns = [
            r"I should\s+(.+?)(?:\.|,|$)",
            r"The problem\s+(?:is|seems)\s+(.+?)(?:\.|,|$)",
            r"I need to\s+(.+?)(?:\.|,|$)"
        ]
        
        for pattern in patterns:
            matches = re.findall(pattern, text, re.IGNORECASE)
            insights.extend(matches)
        
        return insights[:5]  # Top 5 insights

# Uso
analyzer = ThinkingAnalyzer()
sessions = analyzer.parse_session()

if sessions:
    analyzer.analyze_thinking_depth(sessions)
    
    # Analisar primeira sessão
    first = sessions[0]
    summary = analyzer.extract_thinking_summary(first)
    print(f"\n[THINKING SUMMARY]")
    print(f"Steps: {summary['total_steps']}")
    print(f"Key insights: {summary['key_insights']}")
```

## Stack técnico

### Claude Code versões
- **v2.1.69+**: thinking_summaries (oculto, descoberto via settings)
- **v2.5+ (2026)**: Adaptive Thinking nativo, `/effort` command
- **v3.0 (futuro)**: Thinking graphs, visualização de dependency trees

### Hardware / API
- **Local thinking**: 0ms latência adicional (processado offline)
- **API thinking**: Soma de `thinking_tokens` ao usage (Claude Opus 4.6, Sonnet 4.6)
- **Custo**: ~$0.10 por 10K thinking tokens (Opus); $0.015 por 10K (Sonnet)

### Storage
- **settings.json**: ~1KB, sincronizado via Obsidian Sync (se usar)
- **thinking_logs.jsonl**: ~500MB-1GB (após meses de uso)

### Frameworks compatíveis
- **Claude Code IDE**: suporte nativo
- **Cursor**: mode "Claude" com thinking (via integração)
- **VS Code + Claude extension**: limited support (2026+)

## Código prático: Dashboard de Thinking Metrics

```python
import json
from collections import defaultdict
from datetime import datetime, timedelta

class ThinkingMetricsDashboard:
    """Monitorar padrões de raciocínio ao longo do tempo"""
    
    def __init__(self, log_file="thinking_metrics.jsonl"):
        self.log_file = log_file
        self.metrics = defaultdict(list)
    
    def log_session(self, task: str, effort: str, thinking_tokens: int,
                    response_tokens: int, quality_score: float):
        """Registrar uma sessão de thinking"""
        
        entry = {
            "timestamp": datetime.now().isoformat(),
            "task": task,
            "effort": effort,
            "thinking_tokens": thinking_tokens,
            "response_tokens": response_tokens,
            "quality_score": quality_score,
            "efficiency": response_tokens / (thinking_tokens + 1)  # tokens de resposta por token de raciocínio
        }
        
        with open(self.log_file, 'a') as f:
            f.write(json.dumps(entry) + "\n")
        
        self.metrics[effort].append(entry)
    
    def effort_impact_analysis(self, days: int = 7):
        """Analisar impacto de effort level na qualidade"""
        
        # Ler logs dos últimos N dias
        cutoff = datetime.now() - timedelta(days=days)
        recent_data = defaultdict(list)
        
        try:
            with open(self.log_file, 'r') as f:
                for line in f:
                    entry = json.loads(line)
                    entry_time = datetime.fromisoformat(entry['timestamp'])
                    
                    if entry_time > cutoff:
                        effort = entry['effort']
                        recent_data[effort].append(entry)
        except FileNotFoundError:
            print(f"Log file not found: {self.log_file}")
            return
        
        # Análise
        print(f"\n[EFFORT IMPACT ANALYSIS] Últimos {days} dias\n")
        
        for effort in ['low', 'medium', 'high']:
            if effort not in recent_data or not recent_data[effort]:
                continue
            
            data = recent_data[effort]
            avg_quality = sum(e['quality_score'] for e in data) / len(data)
            avg_tokens = sum(e['thinking_tokens'] for e in data) / len(data)
            avg_efficiency = sum(e['efficiency'] for e in data) / len(data)
            
            print(f"{effort.upper()}:")
            print(f"  Sessions: {len(data)}")
            print(f"  Avg Quality: {avg_quality:.2f}/1.0")
            print(f"  Avg Thinking Tokens: {avg_tokens:.0f}")
            print(f"  Avg Efficiency: {avg_efficiency:.2f} resp/think")
            print()
    
    def predict_optimal_effort(self):
        """Machine Learning simples: recomendar effort ótimo"""
        
        # Euristicamente: se quality não melhora com high effort, usar medium
        best_ratio = 0
        best_effort = "medium"
        
        for effort, entries in self.metrics.items():
            if not entries:
                continue
            
            avg_quality = sum(e['quality_score'] for e in entries) / len(entries)
            avg_tokens = sum(e['thinking_tokens'] for e in entries) / len(entries)
            
            # Ratio: qualidade por token (maior é melhor)
            ratio = avg_quality / (avg_tokens + 1)
            
            if ratio > best_ratio:
                best_ratio = ratio
                best_effort = effort
        
        print(f"[RECOMMENDATION] Optimal effort: {best_effort}")
        print(f"  Quality/Token ratio: {best_ratio:.4f}")
        
        return best_effort

# Uso
dashboard = ThinkingMetricsDashboard()

# Registrar algumas sessões (simulação)
dashboard.log_session(
    task="Debug memory leak",
    effort="high",
    thinking_tokens=25000,
    response_tokens=800,
    quality_score=0.95
)

dashboard.log_session(
    task="Format JSON",
    effort="low",
    thinking_tokens=500,
    response_tokens=200,
    quality_score=0.98  # simples, alta qualidade mesmo com low effort
)

dashboard.log_session(
    task="Arquitetura de sistema",
    effort="medium",
    thinking_tokens=12000,
    response_tokens=1500,
    quality_score=0.85
)

# Análise
dashboard.effort_impact_analysis(days=7)
optimal = dashboard.predict_optimal_effort()
```

## Armadilhas e Limitações

### 1. **Thinking summaries nem sempre são claros**
- **Problema**: Claude às vezes produz resumo vago ou muito técnico
- **Solução**: Usar `thinkingVisibility: "full"` para ver transcript completo (usa mais contexto)
- **Alternativa**: Pedir explicitamente "Explique seu raciocínio em 3 bullet points"

### 2. **AppData é pasta oculta no Windows**
- **Problema**: Não consegue navegar até `%APPDATA%\Claude`
- **Solução**: Habilitar "Show hidden files" em Folder Options ou usar PowerShell direto
- **Comando**: `explorer $env:APPDATA`

### 3. **Sincronização entre máquinas**
- **Problema**: Se usa Claude Code em 2+ computadores, settings não sincronizam automaticamente
- **Solução**: Copiar settings.json manualmente ou usar script de sincronização
- **Script**: 
```bash
# Mac/Linux: Symlink para iCloud/Dropbox
ln -s ~/Dropbox/claude-config/settings.json ~/.config/Claude/settings.json
```

### 4. **Performance: thinking_logs cresce rapidamente**
- **Problema**: Arquivo JSONL de logs fica >1GB após meses
- **Solução**: Rotar logs (arquivar thinking_logs_2026_03.jsonl quando chegar em 100MB)
- **Implementação**: Script Python com `shutil` para compactar/mover logs antigos

### 5. **Adaptive Thinking pode ser "indeciso"**
- **Problema**: Claude às vezes escolhe effort errado (pensa muito para tarefa simples, pouco para complexa)
- **Solução**: Override manual com `/effort high` ou `/effort low` command
- **Feedback**: Registrar misclassifications para treinar modelo melhor

### 6. **Thinking tokens contam no billing da API**
- **Problema**: Usar `/effort high` em 1000 requests = $100-200 extra
- **Solução**: Usar effort dinâmico (check complexity primeiro, só raise effort se necessário)
- **Controle**: Monitorar spending com `dashboard.effort_impact_analysis()`

### 7. **Mudança silenciosa**: Anthropic não documentou originalmente
- **Problema**: Feature foi descoberta pela comunidade, pode mudar sem aviso
- **Solução**: Manter fallback em settings (sempre funciona mesmo se versão muda)
- **Monitoramento**: Seguir changelog oficial do Claude Code

### 8. **Thinking visual bugs em modo escuro**
- **Problema**: Texto do thinking panel fica ilegível em dark theme (bug v2.1-v2.3)
- **Solução**: Atualizar para v2.5+ ou adicionar `"overrideThemingForThinking": "light"` ao settings.json
- **Workaround**: Usar light theme temporariamente

## Conexões

- [[Claude Code - Melhores Práticas]] - Workflows gerais
- [[Claude Code Subconscious Letta Memory Layer]] - Memória persistente
- [[configuracao-de-contexto-para-llms]] - Otimizar contexto com thinking
- [[agent-router-model]] - Roteador pode usar thinking para classificação
- [[Claude API Extended Thinking]] - API backend de thinking tokens

## Histórico

- 2026-03-28: Nota original (setting simples)
- 2026-04-11: Reescrita expandida com Adaptive Thinking, API examples, metrics dashboard, 8 armadilhas, stack de versões
