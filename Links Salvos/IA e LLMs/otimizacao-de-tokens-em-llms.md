---
tags: [otimizacao, tokens, economia, contexto, llms]
source: https://x.com/aibuilderclub_/status/2038174485053046868?s=20
date: 2026-04-02
tipo: aplicacao
---

# Reduzir Consumo de Tokens sem Perder Qualidade: Estratégias Práticas

## O que e

Técnicas de compressão de contexto em Claude Code/agentes: resumir histórico em lugar de carregar tudo, passar snippets não arquivos inteiros, resetar contexto para tarefas independentes. Reduz custos 30-50% mantendo qualidade.

## Como implementar

**Tática 1: Compressão de histórico de sessão**:

Problema: Sesão longa acumula 10K+ tokens de histórico irrelevante.

Solução:
```
User (ao mudar de task): "Summarize what we've done so far in 3 bullets"
Claude: "1. Implemented auth module using Passport.js...
        2. Created database schema for users/posts...
        3. Built REST endpoints for CRUD operations..."

# Reset context
Claude: "Let's start fresh. Previous work summary:
[3 bullets above]

What's the next task?"
```

Économia: ~5K tokens por reset.

**Tática 2: Carregamento seletivo de arquivos**:

```python
# MÁ PRÁTICA: Passar arquivo inteiro
@claude "Help me fix this file"
[Arquivo inteiro: 2000 linhas, 50K tokens]

# BÁ PRÁTICA: Passar apenas o relevante
@claude """Fix this function:

\`\`\`typescript
function authenticate(email, password) {
  // [30 linhas de função]
}
\`\`\`

Error: "Invalid token format"
Stack trace: ...
"""
# 1K tokens vs 50K
```

**Tática 3: Prompts de sistema curtos e reutilizáveis**:

```yaml
# System prompt (arquivo ~/.claude/system-prompt.md)

You are a TypeScript specialist.

Core rules:
- Prefer async/await
- Use type inference where possible
- Prefer const, avoid let/var
- Test first (TDD)

---

# Uso
@claude """
$(cat ~/.claude/system-prompt.md)

New task: Implement user registration endpoint
"""
```

Economia: Reutilizar prompt evita reescrevê-lo a cada sessão.

**Tática 4: Context windowing inteligente**:

```python
# Estratégia: manter "janela deslizante" de arquivos relevantes

class SmartContextManager:
    def __init__(self, max_tokens=8000):
        self.max_tokens = max_tokens
        self.token_count = 0
        self.context_files = []

    def add_file(self, filepath, content):
        tokens = len(content.split()) * 1.3  # Aproximação
        if self.token_count + tokens > self.max_tokens:
            # Remove arquivo menos relevante
            self.context_files.pop(0)
        self.context_files.append((filepath, content))
        self.token_count += tokens

    def get_context(self):
        return "\n".join([f"// File: {f}\n{c}" for f, c in self.context_files])

# Uso
mgr = SmartContextManager(max_tokens=8000)
mgr.add_file("auth.ts", read_file("auth.ts"))
mgr.add_file("db.ts", read_file("db.ts"))
mgr.add_file("server.ts", read_file("server.ts"))

prompt = f"""
{mgr.get_context()}

Why is authentication timing out?
"""
```

**Tática 5: Resumos estruturados vs narrativos**:

```
# MÁ PRÁTICA (narrativo, verboso)
"We've been working on a complex authentication system.
Started with basic login, then added multi-factor...
Ran into issues with session management, so we refactored...
Now the system handles OAuth, SAML, and custom strategies...
Token expiration is 24 hours..."

# BÓA PRÁTICA (estruturado, denso)
Auth System Status:
- Strategies: OAuth, SAML, Custom
- Session TTL: 24h
- Issues: none
- Next: Add 2FA
```

Economia: ~30% menos tokens, melhor rastreabilidade.

**Tática 6: Lazy loading de contexto (sob demanda)**:

```python
# Ao invés de: "aqui está todo arquivo de config"
# Usar: "se precisar, peça mais detalhes"

@claude """
Simplify this config file:
[apenas top-level keys, não nested values]

If you need to see nested config, ask.
"""

# Se Claude responder "I need to see the database config",
# você passa apenas aquela seção
```

**Tática 7: Tokens counter para monitorar**:
```python
def estimate_tokens(text):
    """Rough estimate: ~1.3 tokens per palavra em inglês"""
    return len(text.split()) * 1.3

session = []
max_tokens = 50000  # Assinatura típica

for prompt in user_prompts:
    estimated = estimate_tokens(prompt)
    if sum(estimate_tokens(m) for m in session) + estimated > max_tokens:
        print(f"WARNING: Approaching limit. Reset context.")
        session = []  # Reset
    session.append(prompt)
```

## Stack e requisitos

- **Claude Code**: qualquer versão (3.5+ recomendado)
- **Monitoring**: token counter (script Python simples)
- **Práticas**: disciplina em prompt engineering
- **Assinatura**: Claude API ou Pro ($20/mês)

## Armadilhas e limitacoes

- **Context loss**: Comprimir contexto demais piora raciocínio. Encontrar equilíbrio.
- **Reutilização de prompts**: System prompts genéricos podem ser menos eficazes que específicos por projeto.
- **Lazy loading risk**: Se não passar suficiente contexto inicialmente, Claude pode fazer suposições erradas.
- **False economy**: Economizar tokens em tarefas críticas pode custar mais em iterações de correção.

## Conexoes

[[Otimizacao de Tokens via CLAUDE.md]] [[Memory Stack para Agentes de Codigo]] [[Claude Code Melhores Praticas]]

## Historico

- 2026-04-02: Nota criada
- 2026-04-02: Reescrita para template aplicacao