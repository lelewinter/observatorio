---
date: 2026-03-28
tags: [claude-code, code-review, qualidade, debugging, contexto]
source: https://x.com/techNmak/status/2037788648691884207
autor: "@techNmak"
tipo: aplicacao
---

# Usar Segunda Sessão Claude para Code Review com Contexto Fresco

## O que é

Nova sessão Claude Code (contexto limpo) revisa código e encontra 10-30% mais bugs que sessão original. Sessão 1 tem "cegueiras do criador"; sessão 2 não assume nada. Estratégia: build + fresh review em paralelo.

## Como implementar

**1. Fluxo de duas sessões**

```
Sessão 1 (Original):
- Criador escreve código
- Testa, debugga
- Assume que funciona

Sessão 2 (Fresh Review):
- Recebe APENAS código + spec
- Sem contexto de criação
- Testa assumptions ceticisticamente
- Encontra bugs que Session 1 perdeu
```

**2. Prompt para sessão de review (fresco)**

```
Você está revisando código NOVO de outro desenvolvedor.
Você NÃO tem contexto de como foi criado.
Seu objetivo: encontrar bugs que desenvolvedor original perdeu.

Código para revisar:
[PASTE CODE HERE]

Especificação (o que deveria fazer):
[PASTE SPEC HERE]

PERGUNTA AGRESSIVAMENTE:
- Por que essa variável existe?
- E se esse valor for null/undefined/empty?
- Esse loop sempre termina?
- Qual é o pior caso de input?
- Como isso quebra se...?

Assume que desenvolvedor é competente, mas humano:
- Pode ter missed edge case
- Pode ter assumptions implícitas
- Pode ter deixado TODO/FIXME não finalizado

Reporta cada potencial bug:
- Linha: [numero]
- Descrição: [o que é problema]
- Cenário: [input que quebra]
- Severity: [critical/high/medium]
```

**3. Comparação de achados**

Arquivo `code_review_comparison.md`:

```markdown
# Code Review Comparison

## Arquivo Revisado: app.py

### Session 1 (Original) Encontrou:
- [ ] Line 42: Missing error handling
- [ ] Line 58: Variable naming could be clearer

### Session 2 (Fresh Context) Encontrou:
- [ ] Line 15: Input validation missing (CRITICAL)
- [ ] Line 32: Race condition in async code
- [ ] Line 42: Missing error handling ✓ (agreed with Session 1)
- [ ] Line 58: Variable naming ✓ (agreed with Session 1)
- [ ] Line 67: Off-by-one in loop

### NEW Issues Found by Session 2:
- [ ] Line 15: Input validation → ACTION: Add validation
- [ ] Line 32: Race condition → ACTION: Add mutex lock
- [ ] Line 67: Off-by-one → ACTION: Change loop condition

### Agreement Rate: 50% (4/8 total issues)
### New Issues Rate: 50% (4/8 from Session 2 only)
```

**4. Automação (parallel reviews)**

```python
import threading
from anthropic import Anthropic

def run_parallel_reviews(code, spec):
    """Run original + fresh review in parallel"""

    client = Anthropic()
    results = {}

    def session1_original_review():
        # Session 1: Original context (creator's context)
        response = client.messages.create(
            model="claude-opus-4-1",
            max_tokens=2000,
            messages=[{
                "role": "user",
                "content": f"""Review this code as the original developer:
                Spec: {spec}
                Code: {code}
                What could improve?"""
            }]
        )
        results['session1'] = response.content[0].text

    def session2_fresh_review():
        # Session 2: Fresh context (no bias)
        response = client.messages.create(
            model="claude-opus-4-1",
            max_tokens=2000,
            messages=[{
                "role": "user",
                "content": f"""Review this code FRESH (no context of creation):
                Spec: {spec}
                Code: {code}
                Find bugs original developer missed."""
            }]
        )
        results['session2'] = response.content[0].text

    # Run parallel
    t1 = threading.Thread(target=session1_original_review)
    t2 = threading.Thread(target=session2_fresh_review)

    t1.start()
    t2.start()

    t1.join()
    t2.join()

    return results

# Uso
reviews = run_parallel_reviews(code=my_code, spec=my_spec)
print("Session 1 (Original):", reviews['session1'])
print("Session 2 (Fresh):", reviews['session2'])
```

**5. Quando usar (estratégia)**

| Situação | Usar Double Review? |
|----------|-------------------|
| Simple bug fix (<20 lines) | ❌ Overkill |
| Feature (100+ lines) | ✅ Yes |
| Security-critical code | ✅ Yes (mandatory) |
| Performance optimization | ✅ Yes |
| Refactor > 500 lines | ✅ Yes |
| Tests | ❌ Only if complex logic |

## Stack e requisitos

- Claude API (2 separate calls)
- Code to review
- Specification/requirements
- ~$0.10-0.30 per review (2x calls)

## Armadilhas e limitações

- **Token cost**: Double review = 2x cost. Budget trade-off
- **Time**: Parallel reviews still take time (wait for both)
- **Not comprehensive**: Still not as good as human expert
- **Session2 bias**: If spec vague, both sessions may miss same issues
- **Agreement false confidence**: If both agree on wrong thing, problem escalates

## Conexões

[[code-review-checklist-3-fases-claude-code]]
[[CLAUDE-md-template-plan-mode-self-improvement]]

## Histórico

- 2026-03-28: Nota criada
- 2026-04-02: Reescrita como guia de implementação
