---
tags: []
source: https://x.com/Butanium_/status/2037575095569269201?s=20
date: 2026-04-02
tipo: aplicacao
---

# Restaurar Exibição de Thinking Tokens no Claude Code via settings.json

## Resumo
Modelos com extended thinking (Claude Opus/Sonnet 4.6) geram "thinking tokens" (raciocínio privado interno antes da resposta). Claude Code v2.1.69+ suprime silenciosamente esses tokens por padrão, sem anúncio no changelog. Restaurável via `"showThinkingSummaries": true` em settings.json, mas opção não documentada. Questão crítica: observabilidade vs custo de token.

## O que é

**Thinking tokens** são uma categoria de output de LLMs com extended thinking:

1. **Content tokens** (visíveis ao usuário) — a resposta final em texto
2. **Thinking tokens** (privados, opcionais) — processo de raciocínio interno

No Claude API com extended thinking ativo:
```
┌─ Modelo delibera internamente (thinking mode)
│  - Percorre opções, testa hipóteses
│  - Gera "pensamentos" que representam esse processo
│  - Tokens custam dinheiro (billed como output tokens)
├─ Modelo "decide" em qual resposta chegar
└─ Emite content tokens (resposta final)
```

A Anthropic a partir de **January 2026** mudou o comportamento padrão: thinking tokens **existem internamente** mas são suprimidos na UI (Claude Code, Claude Web) e não são retornados na API a menos que explicitamente solicitado.

### Extended thinking vs Thinking tokens

- **Extended thinking** = modo do modelo que ativa raciocínio interno
- **Thinking tokens** = a representação desse raciocínio (vem como stream de dados)
- **Thinking summaries** = resumo humano-legível do thinking (o que `showThinkingSummaries` ativa)

Importante: thinking tokens continuam sendo **gerados e cobrados**, mesmo quando suprimidos na UI.

## Por que importa

**1. Observabilidade e debugging crítica**
- Quando Claude Code toma decisão inesperada (refatora seu código de forma estanha, cria arquivo indesejado), pensar tokens permitem ver "por quê".
- Sem visibility, é caixa-preta pura: você só vê ação final, não o raciocínio.
- Exemplo: Claude decide fazer `rm -rf /tmp` — com thinking visível, você vê que deliberou sobre cleanup; sem ele, parece aleatório.

**2. Custo transparente de tokens**
- Thinking tokens custam dinheiro. Claude Opus com 10k pensamentos + 200 conteúdo = cobração por ~10.2k tokens.
- Sem poder **ver** que 10k tokens foram gastos internamente, você fica surpreso com conta maior.
- Supressão silenciosa mascara esse custo na UI, mas cobrar de verdade acontece.

**3. Auditabilidade e compliance**
- Sistemas que processam dados sensíveis (médicos, legais) precisam rastrear "por que o modelo decidiu X".
- GDPR, HIPAA, auditorias internas: log de raciocínio é evidência.
- Supressão padrão quebra cadeia de auditabilidade.

**4. Calibração de confiança**
- Se você vê thinking, sabe se o modelo **realmente deliberou** vs adivinhou rápido.
- Ex: código crítico — você quer saber se Claude "pensou bastante" ou foi rápido demais.
- Sem visibility, você não consegue julgar confiabilidade da resposta.

**5. Questão de governança de produto**
- Mudança silenciosa (sem changelog, sem comunicação) em ferramenta crítica para devs é preocupante.
- Indica falta de transparência sobre mudanças de comportamento.
- Define precedente perigoso: Anthropic pode mudar outras coisas silenciosamente.

## Como funciona / Como implementar

### Extended Thinking na API

```python
import anthropic

client = anthropic.Anthropic(api_key="YOUR_API_KEY")

# Modo 1: Extended thinking com budget fixo (deprecado em favor de adaptive)
response = client.messages.create(
    model="claude-opus-4.6",
    max_tokens=1000,
    thinking={
        "type": "enabled",
        "budget_tokens": 5000  # Máximo de thinking tokens
    },
    messages=[
        {
            "role": "user",
            "content": "Escreva uma função em Rust que resolve o problema do caixeiro viajante com branch-and-bound."
        }
    ]
)

# Inspect thinking (se retornado)
for block in response.content:
    if block.type == "thinking":
        print("THINKING:", block.thinking[:500])  # Primeiros 500 chars
    elif block.type == "text":
        print("RESPONSE:", block.text)
```

### Adaptive thinking (padrão em 2026)

```python
# Modo 2: Adaptive thinking (novo padrão)
# Claude decide dinamicamente quanto pensar baseado em complexidade da query

response = client.messages.create(
    model="claude-opus-4.6",
    max_tokens=1000,
    thinking={
        "type": "adaptive"
        # Claude automaticamente aloca thinking se tarefa parecer complexa
    },
    messages=[...]
)

# Thinking é retornado se foi usado
for block in response.content:
    if block.type == "thinking":
        # A quantidade de thinking foi dinamicamente determinada
        tokens_used = len(block.thinking.split())  # Aproximado
        print(f"Claude pensou bastante: ~{tokens_used} thinking tokens")
```

### Configuração no Claude Code (settings.json)

```json
{
  "extensions.claude.settings.showThinkingSummaries": true,
  "extensions.claude.settings.showRawThinkingTokens": false,
  "extensions.claude.settings.extendedThinkingEnabled": true
}
```

**Explicação dos flags:**
- `showThinkingSummaries`: exibe resumo humano do thinking (padrão agora: false)
- `showRawThinkingTokens`: exibe tokens brutos (use com cuidado, output grande)
- `extendedThinkingEnabled`: ativa extended thinking para esse workspace

### Monitorar custo de thinking

```python
import anthropic

client = anthropic.Anthropic()

response = client.messages.create(
    model="claude-opus-4.6",
    max_tokens=2000,
    thinking={"type": "adaptive"},
    messages=[{"role": "user", "content": "Complex task..."}]
)

# Calcular custo
thinking_tokens = sum(
    len(block.thinking.split()) 
    for block in response.content 
    if block.type == "thinking"
)
content_tokens = response.usage.output_tokens
total_tokens = thinking_tokens + content_tokens

# Preço (Opus): $0.03/1k thinking, $0.12/1k content
thinking_cost = (thinking_tokens / 1000) * 0.03
content_cost = (content_tokens / 1000) * 0.12
total_cost = thinking_cost + content_cost

print(f"Thinking: {thinking_tokens} tokens (${thinking_cost:.4f})")
print(f"Content: {content_tokens} tokens (${content_cost:.4f})")
print(f"Total: ${total_cost:.4f}")
```

### Log estruturado de thinking para auditoria

```python
import json
from datetime import datetime

class AuditLog:
    def __init__(self, log_file="audit.jsonl"):
        self.log_file = log_file
    
    def log_inference(self, query, response, thinking_tokens=0, content_tokens=0, action=None):
        """Log completo de uma inferência para auditabilidade."""
        entry = {
            "timestamp": datetime.utcnow().isoformat(),
            "query": query,
            "thinking_tokens": thinking_tokens,
            "content_tokens": content_tokens,
            "response_preview": response[:200],
            "action_taken": action,  # Ex: "created_file", "deleted_file"
            "audit_required": True if action and "delete" in action else False
        }
        
        with open(self.log_file, "a") as f:
            f.write(json.dumps(entry) + "\n")
    
    def review_decision(self, decision_id):
        """Recupera thinking + resposta para uma decisão específica."""
        with open(self.log_file, "r") as f:
            for line in f:
                entry = json.loads(line)
                if entry.get("decision_id") == decision_id:
                    return entry
        return None

# Uso
audit = AuditLog()

response = client.messages.create(
    model="claude-opus-4.6",
    thinking={"type": "adaptive"},
    messages=[{"role": "user", "content": "Delete old cache files matching *.tmp"}]
)

# Log para auditoria
thinking_count = sum(len(b.thinking.split()) for b in response.content if b.type == "thinking")
audit.log_inference(
    query="Delete old cache files",
    response=response.content[-1].text,
    thinking_tokens=thinking_count,
    content_tokens=response.usage.output_tokens,
    action="delete_files"
)
```

## Stack técnico

**Modelos com Extended Thinking:**
- **claude-opus-4.6** — melhor thinking, mais tokens, mais caro
- **claude-sonnet-4.6** — thinking mais rápido, menor overhead
- **claude-haiku-4.5** — sem thinking (modelo rápido/barato)

**APIs e SDKs:**
- **Anthropic Python SDK** — oficial
- **Anthropic REST API** — direto HTTP
- **LangChain** — wrapper com integração thinking
- **LiteLLM** — abstração multi-provider

**Observabilidade:**
- **Anthropic Console** — view de thinking via web
- **Custom logging** — build seu próprio audit trail (JSONL, database)
- **Structured logging (Python)** — use logging.info com JSON dumps

**Custo monitoramento:**
- **Spreadsheet com tracking manual** — simples, controlar por task
- **Anthropic Usage API** — pull de estatísticas (em roadmap, não yet available)
- **Webhooks customizados** — integrate logging com Slack/email

## Código prático

### Benchmark: thinking budget vs qualidade

```python
import anthropic

client = anthropic.Anthropic()

# Tarefa complexa de raciocínio
task = """
Você é um revisor de código C++. Revise este algoritmo de busca binária:

```cpp
int binsearch(int arr[], int n, int target) {
    int left = 0, right = n;
    while (left < right) {
        int mid = (left + right) / 2;
        if (arr[mid] == target) return mid;
        else if (arr[mid] < target) left = mid + 1;
        else right = mid;
    }
    return -1;
}
```

Identifique bugs, propose melhorias, explique o trade-off tempo-espaço.
"""

budgets = [0, 1000, 5000, 10000]
results = {}

for budget in budgets:
    if budget == 0:
        # Sem thinking
        thinking_config = None
    else:
        thinking_config = {
            "type": "enabled",
            "budget_tokens": budget
        }
    
    response = client.messages.create(
        model="claude-opus-4.6",
        max_tokens=2000,
        thinking=thinking_config,
        messages=[{"role": "user", "content": task}]
    )
    
    # Extrair thinking e resposta
    thinking_text = ""
    content_text = ""
    for block in response.content:
        if block.type == "thinking":
            thinking_text = block.thinking
        elif block.type == "text":
            content_text = block.text
    
    results[budget] = {
        "thinking_length": len(thinking_text.split()),
        "response_quality": len(content_text.split()),  # Proxy simples
        "total_tokens": response.usage.output_tokens
    }

# Análise
print("Budget vs Qualidade:")
for budget, metrics in results.items():
    print(f"Budget {budget:5d}: thinking={metrics['thinking_length']:5d}, response_words={metrics['response_quality']:4d}")
```

### Detectar silenciamento de thinking

```python
def check_thinking_suppression():
    """Verifica se thinking está sendo suprimido silenciosamente."""
    
    client = anthropic.Anthropic()
    
    # Enviar tarefa que **claramente** requer thinking
    hard_task = """
    Prove que sqrt(2) é irracional usando redução ao absurdo.
    """
    
    response = client.messages.create(
        model="claude-opus-4.6",
        max_tokens=500,
        thinking={"type": "adaptive"},
        messages=[{"role": "user", "content": hard_task}]
    )
    
    # Checar se thinking foi usado
    thinking_found = any(block.type == "thinking" for block in response.content)
    total_tokens = response.usage.output_tokens
    
    print(f"Task complexity: High")
    print(f"Thinking tokens detected: {thinking_found}")
    print(f"Total output tokens: {total_tokens}")
    
    if not thinking_found and total_tokens > 100:
        print("⚠️ WARNING: Task likely used thinking internally but tokens suppressed!")
        return False
    
    return True
```

## Armadilhas e Limitações

**1. Supressão padrão mascara custo real**
- Você vê prompt "1k tokens" mas Claude internamente usou 11k (10k thinking + 1k content).
- Factura chega e é 10x maior do que esperado.
- Solução: monitorar `response.usage.output_tokens` agressivamente, implementar alertas de custo. Usar adaptive thinking em vez de budget alto fixo.

**2. Thinking tokens custam mais que content tokens em alguns modelos**
- Opus: thinking = $0.03/1k, content = $0.12/1k (thinking é mais barato)
- Mas em gerações futuras pode inverter.
- Solução: verificar tabela de preços oficial antes de escalar. Budget pequeno é conservador.

**3. Behavioral change entre versões**
- Se Anthropic mudou thinking v2.1.69 de novo em v2.1.70, sua configuração pode quebrar.
- Não há changelog confiável.
- Solução: add health check na CI: enviar query teste com thinking, verificar que thinking foi retornado.

**4. Incompatibilidade com ferramentas (tools/functions)**
- Nem todos os runtimes suportam mixing thinking + tool calls bem.
- Claude Web suporta, mas LangChain pode ter bugs.
- Solução: testar explicitamente em seu environment antes de assumir que funciona.

**5. Custo de latência**
- Thinking adiciona latência. Tarefa simples com thinking = mais lenta que sem.
- Se você usar adaptive, Claude pode "over-think" tarefas simples às vezes.
- Solução: use budget pequeno ou explicitamente disable thinking para tarefas que você sabe não precisam.

## Conexões

- [[Claude Opus 4.6 e Extended Thinking|claude-opus-extended-thinking]] — modelo base com thinking
- [[Observabilidade e Logging em LLMs|llm-observability]] — auditabilidade
- [[Claude Code com 26 Prompts Especializados|claude-code-prompts]] — como prompts internos do Code usam thinking
- [[Memory Stack para Agentes de Código|agent-memory]] — thinking em contexto de agents
- [[Agentic Patterns in Claude|agentic-patterns]] — quando thinking é crítico para agentes

## Histórico de Atualizações
- 2026-04-11: Expandida com extended thinking API, adaptive thinking, auditoria, monitoring de custo, benchmarks, armadilhas
- 2026-04-02: Nota criada a partir de Telegram