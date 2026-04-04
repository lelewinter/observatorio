---
tags: [prompt-engineering, llm, instrucoes-contraditorias, qualidade]
source: https://x.com/itsolelehmann/status/2036836910971470319?s=20
date: 2026-04-02
tipo: aplicacao
---

# Auditar e Resolver Conflitos em System Prompts

## O que é

System prompts crescem incremental, acumulam contradições (silenciosas), degradam output. Solução: "prompt detox" — revisão periódica, eliminar conflitos, consolidar regras.

## Como implementar

**1. Audit: Encontrar conflitos**

Script para detectar contradições:

```python
def audit_prompt(system_prompt_text):
    """Find contradictions in system prompt"""

    rules = extract_rules(system_prompt_text)
    # rules = ["sempre resumir em 2 paragrafos",
    #          "detalhe completo sem truncar",
    #          "máx 100 palavras", ...]

    conflicts = []

    # Exemplo: "resumir" vs "detalhe completo" = conflito
    if any("resumir" in r.lower() for r in rules) and \
       any("detalhe" in r.lower() for r in rules):
        conflicts.append({
            "rule1": "Keep summaries short",
            "rule2": "Provide complete detail",
            "resolution": "Specify: 'Summary (2 paragraphs) + detailed analysis (if requested)'"
        })

    # Mais audits...
    return conflicts
```

**2. Checklist: Padrões de conflito**

| Padrão | Conflito | Resolução |
|--------|----------|-----------|
| "Resumir" + "Detalhe" | Ambíguo | Especifique quando cada um aplica |
| "Ser conciso" + "Ser criativo" | Criatividade requer espaço | Separe por seção |
| "Sempre X" + "Nunca X" | Contradição | Escolha um ou contextualize |
| "Obedecer tudo" + "Usar julgamento" | Conflito de autoridade | Priorize: "Follow rules UNLESS unsafe" |

**3. Exemplo prático: refatorar prompt**

Antes (conflitante):

```markdown
# System Prompt (accumulated over 6 months)

1. Always provide detailed explanations
2. Keep responses concise and brief
3. Include all relevant context
4. Avoid unnecessary information
5. Be creative with explanations
6. Stick to facts, no conjecture
7. Write in professional tone
8. Use casual language for relatable content
9. Prioritize accuracy
10. Prioritize engagement

[...]
```

Depois (consolidado):

```markdown
# System Prompt v2 (consolidated)

## Core Rules
1. Accuracy is non-negotiable
2. Structure: Summary → Details (user requests more if needed)

## Tone & Style
- Professional by default
- Casual only for explicitly social content
- Explain concepts at clear/relatable level

## Detail Level
- Provide summary (1-2 sentences)
- If user asks "explain more" or "detalhe", expand to full detail
- Don't include unnecessary context unless requested

## Creativity
- Facts first, creative framing second
- Never invent data
- Can suggest interpretations (labeled as such)

## Trade-offs Resolved
- "Concise" + "Detailed" → Summary first, detail on demand
- "Professional" + "Casual" → Default professional, switch for social
- "Accuracy" + "Engagement" → Accuracy wins, engagement via clarity
```

**4. Processo de consolidação**

```bash
# 1. Extract all rules from current system prompt
grep "^-" system_prompt.md | sort | uniq > rules_list.txt

# 2. Human review: group related rules
# Group A: Length/Conciseness
# Group B: Tone/Style
# Group C: Accuracy/Truthfulness
# Group D: Creativity/Interpretation

# 3. For each group, identify conflicts
# "Always detailed" vs "Always brief" = CONFLICT

# 4. Resolve conflicts (choose or contextualize)
# Resolution: "Provide summary + expand if requested"

# 5. Rewrite prompt with consolidated rules

# 6. Test: Run through old examples, verify output quality improved
```

**5. Template consolidado para qualidade**

```markdown
# System Prompt v2: Consolidated Rules

## Non-Negotiable Principles (Top Priority)
- Accuracy over engagement
- Safety over everything
- User intent over default behavior

## Tone
- [One chosen tone: Professional / Casual / Balanced]
- Adjust ONLY when explicitly requested

## Structure Template
For technical questions:
1. Quick answer (1-2 lines)
2. Detailed explanation (if complex)
3. Examples (if relevant)
4. Trade-offs / caveats

For creative questions:
1. Main idea
2. Variations
3. Pros/cons of each

## Boundaries
- Do NOT: [explicit list of prohibited]
- Do ALWAYS: [explicit list of required]
- Ask for clarification when: [ambiguous scenarios]

## Conflict Resolution (Internal)
If rules conflict, priority order:
1. Safety guardrails (always win)
2. Accuracy
3. User preference
4. Consistency
5. Brevity
```

**6. Maintenance cadence**

```
Monthly:
- Review outputs that felt "off"
- Did conflicting rules cause it?

Quarterly:
- Full audit of system prompt
- Remove unused rules
- Consolidate similar rules
- Test quality on benchmark set

Annually:
- Complete rewrite/restructure
- Get external review (colleague)
- Update documentation
```

## Stack e requisitos

- Current system prompt (text)
- Python script (optional, to detect conflicts)
- Test set (to verify refactor improves quality)

## Armadilhas e limitações

- **Hard to detect all conflicts**: LLMs don't error on contradictions, they degrade silently
- **Refactoring breaks things**: Removing/changing rules may impact unrelated outputs. Test thoroughly
- **Team friction**: If team added the rules, removing them might be politically hard
- **Ongoing drift**: Even consolidated prompts drift over time as new rules accumulate

## Conexões

[[configuracao-de-contexto-para-llms]]
[[CLAUDE-md-template-plan-mode-self-improvement]]

## Histórico

- 2026-04-02: Nota criada
- 2026-04-02: Reescrita como guia de implementação
