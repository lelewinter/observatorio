---
date: 2026-03-28
tags: [claude-code, prompt-engineering, configuracao, context-engineering, llm, produtividade]
source: https://www.humanlayer.dev/blog/writing-a-good-claude-md
tipo: aplicacao
autor: "HumanLayer + Anthropic"
---

# CLAUDE.md Otimizado: Máximo 200 Linhas para Máxima Aderência e Qualidade

## O que é

CLAUDE.md é o arquivo de instruções persistentes que é injetado em TODA sessão de Claude Code. Funciona como "system prompt reutilizável" que define comportamentos, constraints, ferramentas disponíveis e padrões de resposta. Pesquisa de 2026 mostra que arquivos CLAUDE.md que excedem 200 linhas sofrem degradação significativa de qualidade — Claude ignora partes, contradições surgem, conformidade geral cai 15–40%.

A raiz do problema é cognitiva: LLMs têm "span de atenção" finito para instruções. Após ~200 linhas, retenção e priorização caem. Adicionar mais instruções não garante que todas sejam seguidas — frequentemente dilui as mais importantes. Metáfora: mente humana tem limite de "cognitive load"; além disso, a pessoa relê instruções com menos atenção.

Assim, máximo de 200 linhas não é limit técnico, é limit cognitivo do próprio modelo.

## Como implementar

### Passo 1: Auditoria de Instruções Existentes

Lista TODAS as regras atuais de CLAUDE.md. Exemplo:

```markdown
# CLAUDE.md Atual (hipotético)

## Regra 1: Cite fontes
- Sempre cite links de origem
- Use formato markdown [Título](URL)
- Cite múltiplas fontes quando relevante
- Não repita citação se já feita

## Regra 2: Código Python
- Use Python 3.9+ features
- Type hints em todas funções
- Docstrings no padrão Google
- Testes unit em pytest

## Regra 3: Português Brasileiro
- Respostas sempre em PT-BR
- Termos técnicos em inglês OK
- Evite anglicismos
- Adapte exemplos para contexto BR

## Regra 4: Responses Diretas
- Sem preambulos desnecessários
- Foco em ação
- Evite "let me think about this"
- Direto ao ponto

# ... 20+ regras mais
```

Marca cada uma por **frequência de uso**:
- **Crítica**: regra que afeta toda sessão (ex: "respostas em PT-BR")
- **Importante**: regra que afeta muitas tarefas (ex: "cite fontes")
- **Nice-to-have**: regra que afeta tarefas específicas (ex: "type hints em Python")

### Passo 2: Consolidação de Redundâncias

Identifica 3+ formas diferentes de dizer a mesma coisa. Exemplo:

```markdown
# Antes (3 regras diferentes)
1. "Sempre cite origens com link"
2. "Use [Título](URL) para referências"
3. "Markdown links para sources"
4. "Não esqueça citations ao fim"

# Depois (1 regra clara)
## Citações
Sempre cite sources com markdown links: [Título](URL).
Adicione ao fim de respostas com dados externos.
```

Consolidação economiza ~10-15 linhas por redundância.

### Passo 3: Abstração e Referência

Em vez de repetir 20 linhas de detalhes em CLAUDE.md, cria referência a documentação existente. Exemplo:

```markdown
# Antes (20 linhas)
## Code Style
- PEP 8 compliant
- Lines max 100 chars
- 4 spaces indentation
- Type hints required
- Docstrings Google style
- No wildcard imports
- [... 14 linhas mais]

# Depois (2 linhas)
## Code Style
Seguir [[style-guide-python]] para PEP 8, type hints, docstrings.
```

Depois cria arquivo `style-guide-python.md` detalhado no vault. CLAUDE.md referencia, não repete.

### Passo 4: Priorização Brutal

Mantém apenas 5–10 regras críticas em CLAUDE.md. Delega resto a documentação linkedada. Exemplo:

```markdown
---
version: 2026-04-11
last_review: 2026-04-11
---

# CLAUDE.md — 120 linhas

## Comportamento Base
- Respostas em Português Brasileiro
- Termos técnicos em inglês OK
- Direto ao ponto, sem preambulos
- Cite sources com [Título](URL)

## Stack e Contexto
- Trabalha em vault Obsidian: [[Claude|Observatorio]]
- Usa git worktrees para desenvolvimento paralelo
- API Anthropic disponível para automação
- Tem acesso a Chrome MCP para web browsing

## Constraints
- Não entre dados financeiros sensíveis em formulários
- Não execute deletions permanentes sem confirmação explícita
- Não crie accounts em nome do usuário
- Não accept terms/conditions sem user approval

## Ao Editar Notas
- Preservar frontmatter YAML
- Manter [[wikilinks]] existentes
- Respeitar estrutura de tags
- Template padrão: "O que é / Como implementar / Stack / Armadilhas / Conexões / Histórico"

## Tools Disponíveis
- WebSearch: buscar informações atualizadas
- Claude Code: criar/editar código
- Bash: executar comandos
- Read/Write/Edit: manipular arquivos
- WebFetch: processar URLs
- Skill: usar plugins especializados

## Quando em Dúvida
- Referencie [[CLAUDE.md]] para instruções completas
- Consulte [[style-guide-python]], [[style-guide-markdown]] para detalhes
- Peça feedback explícito antes de ações destrutivas

---

Documentação Detalhada:
- [[style-guide-python]]: PEP 8, type hints, docstrings
- [[style-guide-markdown]]: frontmatter, wikilinks, estrutura
- [[workflow-pesquisa]]: como fazer pesquisa com WebSearch
- [[workflow-editar-notas]]: padrão para editar vault
- [[prompt-engineering-best-practices]]: otimizações de prompt
```

Essa estrutura é ~120 linhas, cobre o essencial, e delega detalhes a documentação.

### Passo 5: Validação A/B

Roda mesma tarefa 2x:
1. Com CLAUDE.md antigo (260 linhas)
2. Com CLAUDE.md novo (120 linhas)

Compara qualidade de output:
- Conformidade com regras críticas (ex: "cita sources"? "responde em PT-BR"?)
- Coerência e profundidade
- Ausência de contradições

Se qualidade em métrica crítica cair >10%, recupera a regra que foi removida.

## Stack e requisitos

- **Editor de texto**: qualquer (VSCode, Obsidian, Vim)
- **Git**: para versionamento de CLAUDE.md
- **Documentação linkedada**: markdown files no vault
- **Sem dependências técnicas**: é apenas texto

## Armadilhas e limitações

### 1. Remover Regra "Redundante" Que É Crítica em Context Específico

Você marca "Cite fontes" como "nice-to-have", remove de CLAUDE.md 120L. Depois, numa sessão de pesquisa complexa, Claude esquece de citar 50% dos links. Quebrado.

**Mitigação**: Antes de remover qualquer regra, roda teste específico que depende dela. Exemplo:
```python
# Teste: Pesquisar sobre "Multi-agent AI game studios"
# Validar: Todas sources estão citadas com [Título](URL)?
# Se falhar, recupera regra
```

### 2. Abstrair Demais Perde Especificidade

```markdown
# Ruim (genérico demais)
Sejam excelentes em tudo.

# Bom (específico)
Ao escrever código: use type hints, docstrings Google, max 100 chars/linha
Ao editar notas: preservar frontmatter YAML, [[wikilinks]], tags
```

Abstração extrema ("sejam bons developers") não tem poder — volta a regras específicas.

### 3. Arquivo Desatualiza Rapidamente

Se adiciona nova tool (ex: "Skill") ao environment mas não atualiza CLAUDE.md, contexto desatualiza. Claude não sabe que Skill existe, nunca usa.

**Solução**: Revisar CLAUDE.md a cada 2 semanas. Se adiciona tool/constraint novo, adiciona 1-2 linhas (sem remover outra, a menos que seja realmente redundante). Manter sync com realidade.

### 4. Context Managers Adicionais Competem por Atenção

Se você tem CLAUDE.md (120L) + um .claude/CLAUDE.md (200L) adicional + system prompts de Claude Code (50L) + skill prompts (100L), total é ~500L de instruções. Degradação de qualidade volta.

**Solução**: Uma source of truth. Consolidar tudo em um único CLAUDE.md, referenciar details.

## Exemplos de Regras Críticas vs Nice-to-Have

### Críticas (manter em CLAUDE.md)
- Idioma e tom (PT-BR, direto ao ponto)
- Constraints legais/security (não entre dados sensíveis)
- Contexto arquitetura (vault Obsidian, git worktrees, APIs disponíveis)
- Confirmação em ações irreversíveis (delete, publish)

### Nice-to-Have (delegar a documentação)
- Especificações de code style (referência [[style-guide-python]])
- Template de notas (referência [[template-nota-padrao]])
- Exemplos detalhados (referência [[exemplos-pesquisa]], [[exemplos-editar]])
- Listagem de fontes (referência [[sources]], [[learning-resources]])

## Conexões

[[contexto-persistente-em-llms|Contexto estruturado e retenção de instruções]]
[[designmd-como-contrato-de-design-para-llms|CLAUDE.md como contrato com modelo]]
[[prompt-engineering-best-practices|Otimização de prompts em 2026]]
[[git-worktrees-desenvolvimento-paralelo-claude-code|Usar CLAUDE.md para coordenar múltiplos Claudes]]

## Histórico

- 2026-03-28: Referência original da HumanLayer
- 2026-04-02: Reescrita pelo pipeline — documentação base
- 2026-04-11: Expansão com 80+ linhas — implementação step-by-step, exemplos práticos, validação A/B, armadilhas detalhadas
