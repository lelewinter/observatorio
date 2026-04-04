---
tags: [otimizacao, tokens, claude.md, output-efficiency, prompt-engineering]
source: https://x.com/omarsar0/status/2039343351187554490?s=20
date: 2026-04-02
tipo: aplicacao
---

# Reduzir Tokens com CLAUDE.md: Drop-in Config para Output Eficiente

## O que e

Arquivo CLAUDE.md no repo suprime comportamentos verbosos de Claude Code (explicações extras, confirmações, formatações) nativamente. Drop-in, sem refatoração. Relatado: 63% redução em tokens de output.

## Como implementar

**Criar CLAUDE.md na raiz do projeto**:
```markdown
# Project Configuration for Claude

## Output Style
- Be direct and concise
- No explanations unless requested
- No "I'll do X" confirmations
- Use code-first format

## Code Standards
- Prefer functional programming
- Use TypeScript strict mode
- Test with jest + testing-library
- No console.log in production

## Tone
- Technical, not conversational
- Assume reader knows domain
- Skip obvious context

## Format Rules
- Code blocks first, explanation last (if needed)
- Use markdown code fences with language tags
- No verbose comments in generated code
- Minimal whitespace

## Restrictions
- Never suggest architectural changes unprompted
- Don't add type guards unless necessary
- Keep response under 2000 tokens when possible
```

**Exemplo: diferença CLAUDE.md (com vs sem)**:

```
# SEM CLAUDE.md
User: "Write a button component"

Claude:
"I'll create a React button component for you. Here's a well-structured button
that follows best practices. It includes proper TypeScript typing, event handling,
and accessibility features. The component is flexible and can be customized
with various props like size, variant, and disabled state.

Here's the code:

[código]

This component accepts the following props:
- variant: primary or secondary
- size: small, medium, or large
[...]

Let me know if you'd like me to adjust anything!"

Tokens: 400+ (muita explanação)

---

# COM CLAUDE.md
User: "Write a button component"

Claude:
\`\`\`tsx
interface ButtonProps {
  variant?: 'primary' | 'secondary';
  size?: 'sm' | 'md' | 'lg';
  disabled?: boolean;
  children: ReactNode;
  onClick?: () => void;
}

export const Button = ({ variant = 'primary', size = 'md', ...props }: ButtonProps) => (
  <button className={cn(styles.button, styles[variant], styles[size])} {...props} />
);
\`\`\`

Tokens: 150 (apenas código)
```

**CLAUDE.md templates por tipo de projeto**:

**Para web apps (React)**:
```markdown
# React Project Config

## Output Style
- JSX first
- No storybook examples
- TypeScript strict

## Standards
- Hooks over class components
- Tailwind for styling
- React Query for data fetching

## Restrictions
- No barrel exports
- Single responsibility per file
- Max 300 lines per component
```

**Para data pipelines (Python)**:
```markdown
# Data Pipeline Config

## Output Style
- Function first, docstring, then usage
- Assume pandas/polars knowledge

## Standards
- Type hints required
- Functional style preferred
- No side effects outside functions

## Restrictions
- No print statements
- Logging only
- Use pathlib for paths
```

**Para CLIs (Node.js)**:
```markdown
# CLI Project Config

## Output Style
- Minimal help text
- Assume Unix knowledge
- Error messages: brief and actionable

## Standards
- Commander.js or yargs
- No colors unless requested

## Restrictions
- POSIX-compatible
- Exit codes matter
- No interactive prompts
```

**Integração em CI/CD** (reduce costs):
```bash
#!/bin/bash
# .github/workflows/code-review.yml

name: Claude Code Review

on: [pull_request]

jobs:
  review:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3

      - name: Review with Claude Code
        run: |
          # CLAUDE.md directs Claude to:
          # - Be concise (save tokens)
          # - Focus on logic, skip formatting
          # - Summarize findings, not explain
          claude code --review changes.diff

      - name: Post Comment
        run: |
          gh pr comment --body "Review: $(cat review.txt)"
```

**Medir eficiência**:
```python
import json
from pathlib import Path

def analyze_claude_usage():
    """Track token usage before/after CLAUDE.md"""

    # Hypothetical metrics
    data = {
        "before_claudemd": {
            "avg_tokens_per_response": 450,
            "explanations_per_response": 2.3,
            "code_lines_per_response": 15
        },
        "after_claudemd": {
            "avg_tokens_per_response": 165,  # -63%
            "explanations_per_response": 0.1,
            "code_lines_per_response": 25   # More code, less talk
        }
    }

    improvement = (
        (data["before_claudemd"]["avg_tokens_per_response"] -
         data["after_claudemd"]["avg_tokens_per_response"]) /
        data["before_claudemd"]["avg_tokens_per_response"]
    ) * 100

    print(f"Token efficiency improvement: {improvement:.0f}%")
```

## Stack e requisitos

- **Claude Code**: 2026.01+ (reconhece CLAUDE.md nativamente)
- **Git**: Qualquer repo (arquivo é versionado normalmente)
- **Syntax**: Markdown (livre formato)
- **Overhead**: Nenhum (leitura local)

## Armadilhas e limitacoes

- **Team alignment**: Se um dev ignora CLAUDE.md, style fica inconsistente.
- **Evolution**: Projeto muda, CLAUDE.md fica desatualizado; revisar periodicamente.
- **Specificity**: Muito specific demais limita flexibilidade. Muito genérico não funciona.
- **Override**: User sempre pode ignorar CLAUDE.md com prompt explícito ("ignore my project config...").

## Conexoes

[[Otimizacao de Tokens em LLMs]] [[Claude Code Melhores Praticas]] [[Memory Stack para Agentes de Codigo]]

## Historico

- 2026-04-02: Nota criada
- 2026-04-02: Reescrita para template aplicacao