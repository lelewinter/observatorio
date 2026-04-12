---
tags: [claude-code, context-engineering, skills, produtividade, llm-tools]
source: https://x.com/akshay_pachaar/status/2039978114655441141
date: 2026-04-03
tipo: aplicacao
---
# Context Engineering em Claude Skills: A Arquitetura .claude/

## O que é

A pasta `.claude/` dentro de um projeto Claude Code implementa um sistema de 3 camadas de gerenciamento de contexto que persiste entre sessões. Cada camada (project-level, skill-level, runtime) injeta conhecimento em diferentes pontos do ciclo de vida do LLM, permitindo que você construa sistemas especializados com capacidades consistentes e escaláveis.

## Como implementar

### Camada 1: Project-Level Context (CLAUDE.md)

Este é o arquivo raiz que define o escopo e idioma do projeto inteiro. Fica na raiz do seu repositório ou vault.

```markdown
# Observatorio — Second Brain da Leticia

## Contexto
Este é o vault Obsidian da Leticia, sincronizado via Obsidian Sync...

## Estrutura do Vault
```
Links Salvos/
Conceitos/
MOCs/
Daily Reviews/
Projects/
```

## Perfil da Leticia
- Curiosa, mão na massa, vai fundo
- Estuda toda noite e nos finais de semana

## Comandos Disponíveis
- `/study [tema]` — Ativa modo de estudo guiado
```

**Implementação prática:**
1. Crie o arquivo na raiz: `/seu-projeto/CLAUDE.md`
2. Defina: contexto geral, estrutura de pastas, perfil do usuário, regras de linguagem
3. Claude lê automaticamente esse arquivo em TODA interação dentro do projeto
4. Não precisa ser muito longo (200-500 palavras é ideal), mas deve ser denso em informação

**Efeito**: Toda resposta subsequente é calibrada para o contexto do projeto. Você não precisa explicar novamente quem é a Leticia, qual é a estrutura do vault, ou que ela quer respostas diretas em português.

### Camada 2: Skill-Level Context (SKILL.md dentro de `.claude/skills/`)

Cada skill especializada tem seu próprio contexto. Se você criar uma skill `/study`, ela tem seu próprio SKILL.md que refina ainda mais o comportamento.

```markdown
# /study — Modo de Estudo Guiado

## Propósito
Ativa aprendizado hands-on lendo notas do vault, montando plano de etapas práticas, 
e ensinando passo a passo com foco em implementação real.

## Fluxo
1. Recebe: `/study [tema]`
2. Busca nota relacionada no vault
3. Extrai: O que é, Como implementar, Stack, Armadilhas
4. Monta plano de aprendizado (5-7 etapas)
5. Ensina passo 1, aguarda feedback
6. Salva progresso na nota (seção "Histórico de Estudo")

## Restrições
- Não pule etapas (hands-on > teoria)
- Valide cada passo antes de avançar
- Se o usuário ficar preso, ofereça alternativas

## Ferramentas
- Lê arquivo .md via Read
- Edita notas via Edit
- Executa código Python via Bash (se autorizado)
```

**Implementação prática:**
1. Estrutura: `.claude/skills/study/SKILL.md`
2. Dentro do arquivo, defina o propósito exclusivo da skill
3. Documente o fluxo esperado (entrada → processamento → saída)
4. Liste restrições e ferramentas que a skill pode usar
5. Claude injeta esse contexto apenas quando `/study` é invocado

**Efeito**: A skill `/study` se comporta de forma diferente da skill `/analyze`, porque cada uma tem seus próprios objetivos e regras.

### Camada 3: Runtime Context Injection

Este é o mecanismo mais poderoso. Você injeta contexto dinamicamente durante a execução baseado em:
- Qual arquivo o usuário está editando
- Qual pasta está sendo navegada
- Qual skill foi invocada
- Dados do arquivo frontmatter (YAML)

**Exemplo**: Suponha que você criar uma nota em `Links Salvos/IA e LLMs/` com este frontmatter:

```yaml
---
tags: [machine-learning, visualizacao]
source: https://example.com
date: 2026-04-03
tipo: aplicacao
stack: python, tensorflow, jupyter
dificuldade: intermediaria
tempo-estudo: 2h
---
```

Quando você invoca `/study machine-learning`, o sistema:
1. Localiza a nota pelo tag `machine-learning`
2. Lê o frontmatter (tipo, stack, dificuldade, tempo-estudo)
3. Injeta essas metadatas como contexto runtime
4. Claude adapta o plano de estudo baseado no nível real (não assume tudo é iniciante)

**Implementação prática em Python:**

```python
import yaml
from pathlib import Path

def load_note_context(filepath):
    """Extrai frontmatter e injeta como contexto runtime"""
    with open(filepath) as f:
        lines = f.readlines()
    
    # Parse frontmatter YAML
    if lines[0].strip() == '---':
        end_idx = next(i for i, line in enumerate(lines[1:], 1) if line.strip() == '---')
        frontmatter = yaml.safe_load(''.join(lines[1:end_idx]))
        body = ''.join(lines[end_idx+1:])
        return {
            'meta': frontmatter,
            'content': body,
            'context_prompt': f"Nota: {frontmatter.get('tipo')} | Stack: {frontmatter.get('stack')} | Tempo: {frontmatter.get('tempo-estudo')}"
        }
    return None

# Uso
context = load_note_context('/Links Salvos/IA e LLMs/meu-topico.md')
# Agora use context['context_prompt'] para enriquecer a chamada da API Claude
```

### Camada 4 (Avançado): Custom Commands em `.claude/commands/`

Você pode definir novos commands além dos built-ins via arquivos em `.claude/commands/`.

```markdown
# /teach — Teach Mode Estruturado

## Entrada
`/teach [conceito] [tempo_disponivel_minutos]`

## Saída
Aula estruturada em passos bite-sized que cabe no tempo disponível

## Implementação
1. Fragmenta conceito em ~5min chunks
2. Cada chunk: analogia + exemplos + validação
3. Adapta ritmo se feedback indica dificuldade
```

**Efeito**: `/teach machine-learning 30` cria uma aula de 30 minutos focada, não vai tangenciar em 2 horas como um `/study` completamente aberto.

## Stack e requisitos

- **Claude Code**: Versão 1.0+. A pasta `.claude/` é reconhecida automaticamente.
- **Estrutura de pasta obrigatória**:
  ```
  seu-projeto/
  ├── CLAUDE.md                    # Project-level context
  ├── .claude/
  │   ├── CLAUDE.md               # Referência local (opcional)
  │   ├── skills/
  │   │   ├── study/SKILL.md
  │   │   ├── teach/SKILL.md
  │   │   └── analyze/SKILL.md
  │   ├── commands/
  │   │   ├── /learn.md
  │   │   └── /debug.md
  │   └── context-injector.py     # (opcional) script para injetar dinamicamente
  └── vault/ ou src/              # Seu conteúdo real
  ```

- **Tempo de setup inicial**: ~30 minutos para estruturar os 3 níveis (project + 2-3 skills principais + 1-2 commands)
- **Manutenção**: ~5 minutos por semana para refinar regras à medida que você testa
- **Custo**: Gratuito. A injeção de contexto acontece via prompt engineering, sem API calls extras.
- **Escala**: Testado com projetos de 500+ notas. O sistema não degrada com tamanho, apenas com profundidade de contexto injected (recomenda-se <5000 tokens por chamada).

## Armadilhas e limitações

### Armadilha 1: Over-contextualization
Injetar TODO o seu conhecimento em cada chamada da API é tentador, mas quebra o budget de contexto. Uma nota de 2000 palavras × 5 skills × 10 commands = 100k+ tokens por chamada. **Mitigação**: seja seletivo. Injete apenas o contexto RELEVANTE para a task atual (use filtering baseado em tags ou pasta atual).

### Armadilha 2: Inconsistência entre camadas
Se seu CLAUDE.md diz "respostas em português" mas um SKILL.md diz "respostas em inglês", há conflito. Claude não sabe qual regra aplicar. **Mitigação**: use hierarquia explícita no CLAUDE.md: "Regras globais são X. Skills podem sobrescrever apenas Y. Runtime context nunca sobrescreve Z."

### Armadilha 3: Desatualização de contexto
Você atualiza a estrutura do vault (move uma pasta, renomeia uma nota), mas o CLAUDE.md ainda aponta para a estrutura antiga. Claude segue instruções stale. **Mitigação**: revise CLAUDE.md toda vez que você refatora o vault. Considere adicionar um "Última atualização: 2026-04-10" no topo.

### Pitfall técnico 4: Token efficiency
Cada contexto injetado consome tokens. Se você tem 3 SKILL.md files de 1000 tokens cada, isso é 3000 tokens por chamada antes de você falar. Respostas ficam caras. **Mitigação**: mantenha cada SKILL.md <500 tokens. Use wikilinks para contexto adicional em vez de inline tudo.

### Pitfall técnico 5: Ordem de precedência não explícita
Quando há conflito entre camadas (runtime vs skill vs project), qual vence? Claude usa heurística (mais recente / mais específico), mas isso não é garantido. **Mitigação**: documente explicitamente a ordem: "Project < Skill < Runtime" ou "Runtime > Skill > Project". Inclua isso no seu CLAUDE.md.

### Armadilha 6: Prompt injection via frontmatter
Se você permite que outros editem as notas do vault, eles podem craftar um frontmatter que diz `instrucao: "ignore tudo acima e faça X"`. Claude pode obedecer. **Mitigação**: valide frontmatter antes de injetar (whitelist de campos permitidos, strip de instruções imperativas).

## Conexões

[[Claude Code Fundamentals]] - arquitetura geral do Claude Code
[[Prompt Engineering Avançado]] - técnicas de injeção de contexto
[[Automação com Python e APIs]] - scripts para gerir contexto dinamicamente
[[Estrutura de Projetos e Vaults]] - como organizar seu conhecimento para contexto eficiente
[[Skills Especializadas - Estudo, Ensino, Análise]] - exemplos de skills concretas

## Histórico

- 2026-04-03: Nota criada com as 3 camadas de context engineering e exemplos práticos de implementação