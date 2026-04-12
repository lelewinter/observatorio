---
date: 2026-03-23
tags: [claude, produtividade, setup-otimizacao, ia, prompts, prompt-engineering, token-waste]
source: https://support.tools/claude-code-system-prompt-behavior-claude-md-optimization-guide/
author: "@itsolelehmann"
tipo: aplicacao
---

# Auditoria de Setup Claude: Deletar Regras Contraditórias para Output Melhor

## O que é
**Minimum Viable Prompt Theorem:** Você não melhora Claude adicionando mais regras. Você melhora *deletando ruído*. Menos instruções = mais contexto para o que importa = output melhor.

Problema: setups evoluem por acréscimo. Você topa em uma semana com outputs ruins, adiciona regra. Próxima semana, outro problema, mais regra. Após 3 meses tem 40+ regras, muitas contradizendo e competindo por "atenção do modelo".

Discovery de Ole Lehmann + Anthropic: deletar *metade* do setup resultou em outputs *melhores*, não piores. Porque cada regra custa tokens e atenção.

## Por que importa agora
- **Qualidade:** Menos ruído = modelo foca nas coisas que importam
- **Velocidade:** Menos tokens em setup = mais tokens para sua prompt + saída
- **Custo API:** Fewer tokens = cheaper bills (se roda em escala)
- **Clareza:** Setup pequeno é fácil de manter e debugar
- **Descoberta:** Auditoria revela quais regras você REALMENTE precisa vs superstição

## Como funciona / Como implementar

### 1. Audit Framework: 5 perguntas para cada regra

Para cada linha do seu setup (claude.md, skills, context files):

```
Q1: Claude já faz isso por default?
    Exemplos de "SIM": "Explique em português"
    → Claude faz por design

Q2: Contradiz outra regra no setup?
    Exemplos: "Seja conciso" vs "Sempre explique"
    → Conflito direto

Q3: Repete coisa já coberta?
    Exemplos: "Use markdown" aparece em 3 lugares
    → Redundância

Q4: Parece adicionado para corrigir UM problema específico?
    Exemplos: "Use heading 3, não heading 2 porque..."
    → Ad-hoc para edge case do passado

Q5: É tão vago que interpretação muda cada prompt?
    Exemplos: "Sé criativo e útil" (o que é criativo?)
    → Vagueza inútil
```

### 2. Audit Script (roda em Claude)

```python
# Prompt para executar em Claude Code/Cowork
AUDIT_PROMPT = """
Você é expert em prompt optimization. 

Analize meu setup inteiro:
1. Leia arquivo: ~/.claude/CLAUDE.md
2. Leia: ~/.claude/settings.json
3. Leia skills em: ~/.claude/skills/
4. Leia files em: ~/Projects/claude-context/

Para cada regra/instrução encontrada, avalie:
- Q1: Is this something Claude does by default anyway?
- Q2: Does this conflict with another rule?
- Q3: Is this redundant (stated elsewhere)?
- Q4: Looks like a one-off fix for a past problem?
- Q5: Too vague to be actionable?

Output estruturado:
## RULES TO DELETE (no value)
- [rule name] because [reason]

## RULES TO MERGE (redundant)
- [rule 1] + [rule 2] → single statement

## RULES TO CLARIFY (too vague)
- [rule] → proposed clearer version

## CONFLICTS DETECTED
- "Rule A" contradicts "Rule B" because...

## MINIMUM VIABLE SETUP
[Rewritten claude.md with all cruft removed]
"""

# Rodar
import subprocess
result = subprocess.run(
    ["claude-code", "run", AUDIT_PROMPT],
    capture_output=True,
    text=True
)
```

### 3. Exemplo: Antes vs Depois

**ANTES (40 linhas, muita redundância):**
```yaml
# CLAUDE.md

Você é um assistant técnico.
Explique tudo em português.
Use sempre português brasileiro.
PT-BR é sua língua padrão.

Seja conciso mas completo.
Seja direto, sem enrolação.
Não seja muito verboso.
Mas sempre explique seu raciocínio.
Explique sempre o por quê.
Quando der, de exemplos.
Exemplos ajudam a entender.

Estruture respostas.
Use heading 2 (##) para seções.
NÃO use heading 1 (#).
Use listas com • quando relevante.
Use bullet points para clareza.

Code blocks:
- Sempre em markdown ```lang
- Indente com 2 espaços
- Add comments no código

Se o usuário pedir pra estudar algo, use /study
Se pedir pra aprender algo, use /study
Se pedir pra ensinar, ativa learn mode

Não faça coisas ilegais.
Respeite privacidade.
Não compartilhe dados sensíveis.
```

**Conflitos detectados:**
- "Seja conciso" vs "Sempre explique seu raciocínio" ← contraditório
- "Explique em português" aparece 3x ← redundante
- "Use heading 2, NÃO heading 1" ← ad-hoc specific
- "Se X, use /study; se Y, use /study; se Z, use learn" ← desordenado

**DEPOIS (15 linhas, clean):**
```yaml
# CLAUDE.md

Linguagem: português brasileiro
Tom: técnico, direto, sem fluff

Estrutura:
- Headings: use ## para seções
- Code: markdown blocks com language tags
- Lists: use • para clareza

Modo estudo: Se usuário pedir /study ou aprender,
ativa learning mode (questões, exemplos, hands-on)

Constraints: 
- Respeite privacidade e legalidade
- Não compartilhe dados sensíveis
```

**Redução:** 40 → 15 linhas (-62%), mantém essência

### 4. Processo gradual (safe)

Não delete tudo de uma vez. Siga:

**Fase 1: Audit (não muda nada)**
```bash
# Roda audit, gera relatório
claude-code run "Audit setup, list what to delete"
# Output: audit-report.md
```

**Fase 2: Delete lowest-priority items**
```bash
# Teste sem as regras mais óbvias (redundantes/vagas)
# Execute 3 tarefas que você faz todo dia
# Verificar: outputs iguais ou melhores?
```

**Fase 3: Validate**
```bash
# Se outputs = melhor, delete confirmado
# Se outputs = pior, restore seletivamente
git diff CLAUDE.md  # Review exatas mudanças
```

**Fase 4: Iterate**
```bash
# Próxima semana, delete próximo tier de rules
# Monitor quality, not quantity
```

## Stack técnico
- **Audit:** Claude Code / Cowork (acesso filesystem)
- **Storage:** ~/.claude/CLAUDE.md (user-level), ~/.claude/settings.json
- **Skills:** ~/.claude/skills/*.md (modular instructions)
- **Monitoring:** Logger de qual regra foi usada (hard to measure, but proxy: token count)
- **Version control:** Git para CLAUDE.md (track changes ao longo tempo)

## Código prático: Auto-auditar

```python
#!/usr/bin/env python3
import os
import json
from anthropic import Anthropic

client = Anthropic()

def read_setup():
    """Read all Claude setup files"""
    setup = {}
    
    # Read CLAUDE.md
    claude_md = os.path.expanduser("~/.claude/CLAUDE.md")
    if os.path.exists(claude_md):
        with open(claude_md) as f:
            setup['claude_md'] = f.read()
    
    # Read settings.json
    settings = os.path.expanduser("~/.claude/settings.json")
    if os.path.exists(settings):
        with open(settings) as f:
            setup['settings'] = json.load(f)
    
    # Read skills
    skills_dir = os.path.expanduser("~/.claude/skills")
    if os.path.exists(skills_dir):
        setup['skills'] = {}
        for skill_file in os.listdir(skills_dir):
            if skill_file.endswith('.md'):
                with open(os.path.join(skills_dir, skill_file)) as f:
                    setup['skills'][skill_file] = f.read()
    
    return setup

def audit_setup(setup):
    """Ask Claude to audit the setup"""
    
    setup_text = json.dumps(setup, indent=2)
    
    response = client.messages.create(
        model="claude-opus-4",
        max_tokens=4096,
        messages=[{
            "role": "user",
            "content": f"""Analyze this Claude setup and identify rules to delete:

{setup_text}

For each rule/instruction, evaluate:
1. Does Claude do this by default?
2. Does it conflict with other rules?
3. Is it redundant (stated elsewhere)?
4. Looks like a one-off fix?
5. Too vague to be actionable?

Provide:
1. LIST OF RULES TO DELETE (with reason)
2. CONFLICTING RULES
3. MINIMUM VIABLE SETUP (cleaned version)
4. ESTIMATED TOKEN SAVINGS"""
        }]
    )
    
    return response.content[0].text

# Run
setup = read_setup()
audit_result = audit_setup(setup)
print(audit_result)

# Save to file
with open("claude-audit.md", "w") as f:
    f.write(audit_result)
print("\nAudit saved to: claude-audit.md")
```

**Executar:**
```bash
python3 audit-claude.py
cat claude-audit.md
```

## Armadilhas e limitações

### 1. **Deletar demais quebra funcionalidade específica**
Se você tem rule "Sempre comente code blocks" para uma tarefa específica (teaching), remover sem contexto é bad.

**Solução:** Scope rules — marcas-as com tags [teaching], [technical], [casual]. Delete por scope, não global.

### 2. **Cumulação volta rapidinho**
Você limpa setup, próximas 2 semanas adiciona 10 novas regras de novo.

**Solução:** Estabelecer "rule budget" — máximo X linhas. Se adicionar, precisa deletar outra.

### 3. **Regras vão silenciosamente mortas**
Rule antigo sobre "Sempre use Python 3.8" não quebra nada, só ignora. Você não percebe.

**Solução:** Audit trimestral, não anual. Rápido + habitualmente incorporado.

### 4. **Otimização local, não global**
Deletar regra "Explique em português" melhora tokens mas piora qualidade para usuário PT. Trade-off invisível.

**Solução:** Meça output quality (não só tokens). Rubric simples: [1-5] qual score você dá à resposta?

## Conexões
- [[Personalizacao-de-Preferencias-em-LLMs]]
- [[Claude Code - Melhores Práticas]]
- [[Prompt Engineering Estruturado]]
- [[Token Optimization Strategies]]
- [[System Prompt Anatomy]]

## Histórico
- 2026-03-23: Nota original
- 2026-04-11: Reescrita com audit framework, before/after exemplo, código auto-audit, e 4 armadilhas
