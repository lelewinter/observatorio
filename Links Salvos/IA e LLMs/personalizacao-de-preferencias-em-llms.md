---
tags: [claude, preferences, system-prompt, personalization, workflow, socratic-method]
source: https://support.claude.com/en/articles/10185728-understanding-claude-s-personalization-features
date: 2026-04-02
tipo: aplicacao
---

# Personal Preferences Claude: System Prompt Global Persistente

## O que é
**Personal Preferences** é uma camada de system prompt que aplica *globalmente* a todas as suas conversas com Claude, sem repetição manual. 

Diferente de:
- **Project-level system prompt** (Claude Code) — aplica só naquele projeto
- **Custom instructions** (ChatGPT) — estilo livre, menos estruturado

Personal Preferences = *configuração imutável* que condiciona o modelo *antes* de qualquer conversação.

## Por que importa agora
- **Consistência:** Sua personalidade/estilo aplica automaticamente em 100% das conversas
- **Eficiência:** Não repete instruções, economiza tokens + mensagens
- **Controle:** Você define o "norte magnético" que redireciona qualquer desvio
- **Produtividade:** Setup 15min uma vez, benefício permanente

## Como funciona

### Layer 0: Onde vivem as Preferences

**Claude Web/Desktop:**
```
Settings → Profile → Personal Preferences
```

**Claude Code (~/.claude/):**
```
~/.claude/settings.json (user-level config)
~/.claude/CLAUDE.md (instructions globais)
```

**Scope hierarchy:**
```
System prompt (Anthropic hardcoded)
    ↓
Personal Preferences (you set once)
    ↓
Project system prompt (Claude Code, Projects)
    ↓
Conversation-level prompt (your message)
```

Cada layer *pode override* a anterior, mas Personal Preferences se aplica universalmente.

### Layer 1: Modo de operação (Socratic)

**O problema:** Você pede "Brainstorm project ideas" e Claude retorna lista de 5 ideias pronta.
Mas você quer explorar, questionar, iterar.

**A solução:** Personal Preferences estabelecem "modo exploratório por default"

```
Personal Preferences text box:
════════════════════════════════════════════════════════════

MODO OPERACIONAL:

Não crie deliverables finalizados até receber sinal explícito
("proceder", "executar", "gerar", "finalizar").

Até então, permaneça em MODO EXPLORATÓRIO:
1. Questione suposições minhas
2. Ofereça alternativas conflitantes (não consenso)
3. Peça esclarecimentos antes de dar "resposta"
4. Explore trade-offs antes de recomendar

Exemplos de sinais explícitos:
- "proceder com opção A"
- "gerar documento final"
- "execute o plano"

Sem sinal = continue em análise, não colapsa em conclusão.
════════════════════════════════════════════════════════════
```

**Impacto:** Quando você pede "Qual framework escolher?", Claude agora responde:

❌ Antes:
```
Recomendo React porque é popular, tem comunidade grande...
[lista de 5 razões pré-cocinadas]
```

✅ Depois:
```
Antes de recomendar, preciso entender seus constraints:
1. Equipe já sabe qual framework?
2. Projeto é greenfield ou legacy migration?
3. Performance crítica ou escalabilidade crítica?
4. Tempo de market importante?

Sem essas respostas, recomendação vai ser genérica.
Qual você pode clarificar?
```

### Layer 2: Eliminação de ruído linguístico

Marca d'água de "IA-ness" que você não quer.

```
COMUNICAÇÃO:

Estilo:
- Sem dashes (—) para separar ideias
- Sem filler phrases: "but here's the thing", "so basically",
  "at the end of the day", "it goes without saying"
- Sem múltiplas opções numeradas como default
- Sem "I hope this helps!" em final

Tom:
- Direto, como quem já conhece contexto
- Técnico quando apropriado
- Português BR, termos técnicos em English
- Sem emojis (a menos que eu use primeiro)
```

**Impacto:** Output é lido 2x mais rápido, soa mais humano.

### Layer 3: Ancoragem contextual (seu role)

Se você atua num role específico, Claude consegue manter focus.

**Exemplo Chief of Staff:**
```
CONTEXTO:

Você atua como AI assistant para Chief of Staff.

Chief of Staff: ponte entre CEO e operações.
Responsabilidades: priorização, comunicação, execução.

Todas as respostas devem se alinhar com:
- Impacto na execução do roadmap
- Clareza de comunicação (CEO precisa entender)
- Viabilidade operacional (time consegue fazer?)
- Timeline (quando?)

Se uma sugestão é "boa em teoria mas impraticável",
sinalize explicitamente. COS prefere "hard truth" a "nice idea".
```

**Impacto:** Próxima vez que você pede "Estratégia de marketing", Claude não retorna "generic growth hacking advice", mas **"estratégia de marketing que COS consegue executar com recursos atuais"**.

### Layer 4: Brand guide + style consistency

Para quem gera muitos documentos (relatórios, presentations, email templates).

**Workflow:**
1. Cria brand guide usando Claude (tom, cores, vocabulário)
2. Salva em arquivo (brand-guide.md)
3. Anexa em projeto Claude Code
4. Todos docs naquele projeto herdam estilo automaticamente

```markdown
# Brand Guide

## Tone
- Authoritative but approachable
- Direct, no jargon for non-technical audience
- Confident but humble

## Vocabulary
✓ Use: customer, user, team
✗ Avoid: client (too formal), stakeholder (vague)

## Structure
- Headlines: H2 only
- Lists: bullet (—) for benefits, numbers for steps
- Color: #2563EB (blue), #1F2937 (dark gray)
```

**Impacto:** Relatório gerado = já segue brand sem você reeditar.

## Stack técnico
- **Frontend:** Claude web ou desktop app v2.1+
- **Storage:** Anthropic cloud (associated com account)
- **Scoping:** Query-level precedence (conversation msg > preferences > project)
- **Limits:** ~5000 tokens de preferences (mantenha <500 pra eficiência)
- **Versioning:** Preferences não têm history/undo — document no Obsidian se importante

## Código prático: Estrutura recomendada

```markdown
# PERSONAL PREFERENCES (sua estrutura recomendada)

## 1. OPERATIONAL MODE
[Socratic method / exploratório / decisório — escolha]

## 2. COMMUNICATION STYLE
[Seu tom preferido]

## 3. CONTEXT (opcional)
[Seu role / missão]

## 4. CONSTRAINTS & GUARDRAILS
[O que NÃO fazer]

## 5. FORMATTING (opcional)
[Preferências de estrutura]
```

**Template recomendado (copiar e colar):**

```
OPERATIONAL MODE:
Before giving final recommendations, ask clarifying questions.
Maintain exploratory mode unless I say "proceed".

COMMUNICATION:
- Portuguese BR, technical terms in English
- Direct tone, no filler
- Structure with ## headings
- Code in markdown blocks with language tags

CONTEXT:
I'm a developer/researcher/manager [choose your role].
Responses should consider: [your priorities]

CONSTRAINTS:
- Don't assume I want lists of options
- Don't use [banned phrases]
- Prioritize [your priority] over [alternative]
```

## Código: Auto-generate Preferences

```python
def generate_preferences(role: str, priorities: list, style: str):
    """Generate structured personal preferences"""
    
    from anthropic import Anthropic
    client = Anthropic()
    
    response = client.messages.create(
        model="claude-opus-4",
        max_tokens=1024,
        messages=[{
            "role": "user",
            "content": f"""Generate well-structured Personal Preferences for Claude.

Role: {role}
Priorities: {', '.join(priorities)}
Communication style: {style}

Output format:
## OPERATIONAL MODE
[your preference]

## COMMUNICATION
[specifics]

etc.

Keep under 500 tokens total."""
        }]
    )
    
    return response.content[0].text

# Usage
prefs = generate_preferences(
    role="AI researcher",
    priorities=["reproducibility", "clarity", "depth"],
    style="technical, direct"
)
print(prefs)
# Copy to Settings → Profile → Personal Preferences
```

## Armadilhas e limitações

### 1. **Restrição rígida demais afeta uso casual**
Se adiciona "Sempre use Socratic method", conversas casuais (piadas, small talk) ficam estranhas.

**Solução:** Use preference em "exploration vs decision" context. Para casual, prefere direto.

### 2. **Preferences não sobrescrevem project prompts**
Se projeto tem system prompt conflitante, ambos rodam.

Exemplo:
- Personal Preference: "Use Socratic method"
- Project prompt: "Give direct answers, no questions"
→ Conflito. Project *pode* ganhar dependendo de implementação.

**Solução:** Mantenha project prompts também alinhados com preferences.

### 3. **Mudanças não afetam conversas já iniciadas**
Você atualiza Preferences, mas conversa aberta anterior não vê mudança.

**Solução:** Comece nova conversa pós-update.

### 4. **Overload de preferências dilui atenção**
>500 tokens de preferences = Claude vira "confused bot" tentando satisfazer tudo.

**Solução:** Máximo 3-4 preferências fortes. Deletar as fracas.

### 5. **Preferences são "always-on"**
Às vezes você quer quebrar a regra (ex: "preciso de lista rápida agora, sem Socratic").
Mas preferences forçam o método.

**Solução:** Sinal explícito: "Override preferences: give me quick list" — Claude entende.

## Conexões
- [[Simplificar Setup Claude Deletar Regras Extras]]
- [[Claude Code - Melhores Práticas]]
- [[Prompt Engineering Estruturado]]
- [[System Prompt Anatomy]]
- [[Personalization at Scale]]

## Histórico
- 2026-04-02: Nota criada
- 2026-04-11: Reescrita com Layer structure, brand guide example, auto-generate script e 5 armadilhas