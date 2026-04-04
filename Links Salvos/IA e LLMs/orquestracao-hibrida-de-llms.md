---
tags: [orquestracao, llms, hibrido, rate-limits, arquitetura]
source: https://x.com/kmeanskaran/status/2036341914262482982?s=20
date: 2026-04-02
tipo: aplicacao
---

# Orquestração Híbrida: Distribuir Tarefas entre Claude Opus e Qwen Local

## O que e

Estratégia que aloca tarefas de desenvolvimento: Claude Opus/GPT-5 (premium, raro) para decisões arquiteturais/design. Qwen local (infinito, grátis) para bugs, testes, documentação. Contorna rate limits sem perder produtividade.

## Como implementar

**Classificação de tarefas por complexidade cognitiva**:

| Tarefa | Modelo | Racional |
|--------|--------|----------|
| Arquitetura de sistema | Claude Opus | High-stakes, raro, 1-2x/projeto |
| Primeira iteração código | Claude Opus | Scaffold define tudo, qualidade crítica |
| Code review | Claude Opus | Decisões de pattern, mentoring |
| Bug fixing (rotina) | Qwen local | Repetitivo, low-stake, feedback rápido |
| Documentação | Qwen local | Template-based, não precisa criatividade |
| Testes unitários | Qwen local | Mecânico, validar é fácil |
| Refactoring | Qwen local | Dado contexto existente, qualidade OK |

**Setup híbrido** (Claude Code + Ollama):
```bash
# Terminal 1: Rodar Ollama localmente
ollama serve

# Terminal 2: Rodar Claude Code normalmente
claude code
```

**Integração**: Script que route requests baseado em task type:
```python
# router.py
from anthropic import Anthropic
import subprocess
import json

class HybridRouter:
    def __init__(self):
        self.claude_client = Anthropic()
        self.local_model = "qwen2.5-7b-instruct"

    def classify_task(self, prompt: str) -> str:
        """Classifica se tarefa é HIGH ou LOW complexity"""
        classification_prompt = f"""
        Classify this development task as either HIGH or LOW complexity:

        Task: {prompt}

        HIGH = architectural, design decisions, initial coding, code review
        LOW = bug fixes, documentation, tests, refactoring

        Respond with single word: HIGH or LOW
        """

        response = self.claude_client.messages.create(
            model="claude-3-5-sonnet-20241022",
            max_tokens=10,
            messages=[{"role": "user", "content": classification_prompt}]
        )
        classification = response.content[0].text.strip()
        return "HIGH" if "HIGH" in classification else "LOW"

    def route(self, prompt: str, context: str = ""):
        """Route to Claude Opus (HIGH) or Qwen (LOW)"""
        task_type = self.classify_task(prompt)

        if task_type == "HIGH":
            print("[USING] Claude Opus (premium)")
            response = self.claude_client.messages.create(
                model="claude-3-opus-20250805",
                max_tokens=2000,
                messages=[
                    {"role": "user", "content": context + "\n\n" + prompt}
                ]
            )
            return response.content[0].text

        else:
            print("[USING] Qwen Local (free)")
            # Call Ollama locally
            result = subprocess.run(
                ["ollama", "run", self.local_model, context + "\n\n" + prompt],
                capture_output=True, text=True
            )
            return result.stdout

# Uso
router = HybridRouter()

# Arquitetura (HIGH) → Claude Opus
architecture_response = router.route(
    "Design the data model for a real-time collaboration app",
    "We're building a Figma competitor"
)

# Bug fix (LOW) → Qwen local
bugfix_response = router.route(
    "Fix this timeout error in auth.ts",
    "Error: [code snippet]"
)
```

**Workflow manual híbrido** (sem auto-routing):
```bash
# Fase 1: Arquitetura com Claude Code (Opus)
claude code
# @claude "Design architecture for payment system"
# [Recebe design detalhado]

# Fase 2: Implementação com Qwen local
# Editar código scaffolded por Opus
# Para refactoring menor, usar:
ollama run qwen2.5-7b "Refactor this function to be more readable"

# Fase 3: Testes com Qwen
ollama run qwen2.5-7b "Write pytest tests for this function"

# Volta a Opus apenas se feedback de testes indicar problema arquitetural
```

**Economia de tokens** (Claude Opus com 200K context):
```
Projeto típico:
- Arquitetura: 10K tokens (Claude Opus)
- Implementação: 50K tokens (Qwen, 50 iterações x 1K)
- Testes: 10K tokens (Qwen)
- Documentação: 5K tokens (Qwen)
- Reviews: 5K tokens (Claude Opus)

Total: 30K tokens Opus (economiza 50K que iriam para Qwen)
Custo: $3 Opus vs $500+ se toda feito com Opus @ $0.015/1K
```

**Decision tree para escolher modelo**:
```
Tarefa: [novo request]
  ├─ É planejamento/arquitetura?
  │  └─ SIM → Claude Opus
  ├─ É correção de bug existente?
  │  └─ SIM → Qwen local
  ├─ É refactoring de código existente?
  │  └─ SIM → Qwen local
  ├─ É teste/documentação?
  │  └─ SIM → Qwen local
  └─ Caso de uso único/crítico?
     └─ SIM → Claude Opus
```

## Stack e requisitos

- **Claude Opus**: API key (pagamento por uso)
- **Ollama**: 0.1.15+ com Qwen 2.5 7B (8GB VRAM)
- **Router logic**: Python com Anthropic SDK
- **Latência**: Opus ~5s, Qwen ~2-3s
- **Custo mensal**: ~$50 Opus + $0 Ollama (energy only)

## Armadilhas e limitacoes

- **Context mismatch**: Qwen local não tem acesso a contexto de Opus (arquitetura antiga). Passar contexto explicitamente.
- **Qualidade inconsistência**: Transição de Opus→Qwen pode ter drops de qualidade. Revisar output Qwen em code review.
- **Auto-routing impreciso**: Classifier pode confundir "refactor importante" com "bug fix rotina". Validar antes de usar.
- **State persistence**: Qwen não "lembra" de decisões Opus. Documentar decisões em CLAUDE.md para Qwen consultar.
- **API costs**: Se muito Opus due to misclassification, custos sobem rapidamente. Monitor usage.

## Conexoes

[[Otimizacao de Tokens em LLMs]] [[Setup Qwen 2.5 Local]] [[Claude Code Melhores Praticas]]

## Historico

- 2026-04-02: Nota criada
- 2026-04-02: Reescrita para template aplicacao