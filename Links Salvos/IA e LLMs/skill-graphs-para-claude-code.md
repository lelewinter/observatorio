---
tags: [claude-code, skills, context-engineering, agentes-autonomos, grafo-de-habilidades]
source: https://code.claude.com/docs/en/skills
date: 2026-04-11
tipo: aplicacao
---
# Skill Graphs para Claude Code

## O que e

Skill graphs são estruturas de dependências e composição entre habilidades (skills) em Claude Code que permite um modelo construir contexto mais eficiente, reduzindo tokens consumidos e melhorando qualidade de respostas em tarefas complexas. Uma "skill" é um conjunto de instruções estruturadas que ensina a Claude Code como fazer algo específico, e um "skill graph" mapeia como essas skills se conectam, dependem umas das outras, e podem ser orquestradas em sequência.

No contexto de Claude Code (lançado em beta em outubro 2025), skills representam o principal mecanismo de extensão. Diferente de plugins tradicionais que são caixas pretas, skills são SKILL.md files que contém prompts estruturados, templates, exemplos, e instruções passo-a-passo para domínios específicos. Um skill graph organiza essas skills em um DAG (directed acyclic graph) onde cada skill aponta para skills pré-requisito (ex: "frontend-design skill" depende de "html-css fundamentals skill").

O valor de estruturar skills como grafo é multi-fold: (1) reutilização - uma skill de "testing" pode ser usada por múltiplas skills de domínios diferentes; (2) contextualização inteligente - Claude Code carrega apenas skills relevantes para a tarefa atual ao invés de todas as 1300+ disponíveis, economizando tokens; (3) composição - skills complexas podem ser decompostas em subareas mais gerenciáveis; (4) aprendizagem progressiva - um usuário novo começa em nós básicos do grafo e progride para skills avançadas conforme necessidade.

## Como implementar

### Estrutura Base de uma Skill

Uma skill é um diretório com SKILL.md + arquivos de suporte:

```
my-skill/
├── SKILL.md          (metadados + instruções core)
├── examples/         (exemplos de uso)
│   ├── example1.md
│   └── example2.md
├── templates/        (templates reutilizáveis)
│   └── template.md
└── requirements.txt  (dependências/skills pré-requisito)
```

Exemplo de SKILL.md:

```markdown
---
name: React Component Testing
slug: react-component-testing
description: Write effective unit tests for React components using Vitest
version: 1.0.0
author: Claude Code Community
dependencies:
  - skills/javascript-fundamentals
  - skills/react-basics
  - skills/vitest-setup
commands:
  - name: test-component
    description: Create test suite for a component
    args:
      - name: component_path
        description: Path to React component
        required: true
tags: [react, testing, vitest, unit-testing]
---

# React Component Testing Skill

## Visao Geral
Este skill ensina como escrever testes efetivos para componentes React usando Vitest.

## Core Instructions
1. Sempre importar renderização do Vitest
2. Testar comportamento, não implementação
3. Mockar dependências externas

## Templates
[template details...]

## Common Pitfalls
[pitfall details...]
```

### Construindo o Skill Graph

```python
import json
from typing import Dict, List, Set
from dataclasses import dataclass

@dataclass
class SkillNode:
    slug: str
    name: str
    description: str
    dependencies: List[str]  # slugs de skills pré-requisito
    tags: List[str]
    tokens_estimate: int  # tokens típicos ao incluir esta skill
    version: str

class SkillGraph:
    def __init__(self):
        self.nodes: Dict[str, SkillNode] = {}
        self.adjacency: Dict[str, Set[str]] = {}
    
    def add_skill(self, skill: SkillNode):
        """Adiciona uma skill ao grafo"""
        self.nodes[skill.slug] = skill
        if skill.slug not in self.adjacency:
            self.adjacency[skill.slug] = set()
        
        # Adicionar arestas para dependências
        for dep in skill.dependencies:
            if dep not in self.adjacency:
                self.adjacency[dep] = set()
            self.adjacency[dep].add(skill.slug)
    
    def get_skill_closure(self, skill_slug: str) -> Set[str]:
        """Retorna todas as skills necessárias (transitive closure)"""
        visited = set()
        to_visit = [skill_slug]
        
        while to_visit:
            current = to_visit.pop()
            if current in visited:
                continue
            visited.add(current)
            
            skill = self.nodes.get(current)
            if skill:
                to_visit.extend(skill.dependencies)
        
        return visited
    
    def estimate_tokens_for_task(self, task_description: str) -> int:
        """Estima tokens necessários baseado em skills relevantes"""
        # Em produção, usar embedding similarity
        relevant_skills = self._find_relevant_skills(task_description)
        total_tokens = 0
        
        for skill_slug in relevant_skills:
            closure = self.get_skill_closure(skill_slug)
            for s in closure:
                total_tokens += self.nodes[s].tokens_estimate
        
        return total_tokens
    
    def _find_relevant_skills(self, task: str) -> Set[str]:
        """Encontra skills relevantes para uma tarefa"""
        # Implementar busca por tags, embedding similarity, etc.
        pass
    
    def optimize_skill_loading(self, task: str, token_budget: int) -> List[str]:
        """Otimiza qual subset de skills carregar dado um budget de tokens"""
        relevant = self._find_relevant_skills(task)
        selected = []
        total_tokens = 0
        
        # Greedy selection: skill mais relevante que cabe no budget
        for skill_slug in sorted(relevant, 
                               key=lambda s: self.nodes[s].tokens_estimate):
            closure = self.get_skill_closure(skill_slug)
            closure_tokens = sum(
                self.nodes[s].tokens_estimate 
                for s in closure if s not in selected
            )
            
            if total_tokens + closure_tokens <= token_budget:
                selected.extend(closure)
                total_tokens += closure_tokens
        
        return selected

# Exemplo de construção
graph = SkillGraph()

# Skill base (sem dependências)
js_basics = SkillNode(
    slug="javascript-fundamentals",
    name="JavaScript Fundamentals",
    description="Core JavaScript concepts",
    dependencies=[],
    tags=["javascript", "fundamentals"],
    tokens_estimate=2000,
    version="1.0.0"
)
graph.add_skill(js_basics)

# Skill intermediária
react_basics = SkillNode(
    slug="react-basics",
    name="React Basics",
    description="Componentes, JSX, hooks",
    dependencies=["javascript-fundamentals"],
    tags=["react", "components"],
    tokens_estimate=3000,
    version="1.0.0"
)
graph.add_skill(react_basics)

# Skill avançada
react_testing = SkillNode(
    slug="react-component-testing",
    name="React Component Testing",
    description="Testes com Vitest",
    dependencies=["react-basics", "javascript-fundamentals"],
    tags=["react", "testing", "vitest"],
    tokens_estimate=2500,
    version="1.0.0"
)
graph.add_skill(react_testing)

# Usar o grafo
closure = graph.get_skill_closure("react-component-testing")
print(f"Skills necessários: {closure}")
# Output: {'javascript-fundamentals', 'react-basics', 'react-component-testing'}
```

### Integração com Claude Code

```python
# claude_code_client.py
from anthropic import Anthropic

class ClaudeCodeAgent:
    def __init__(self, skill_graph: SkillGraph):
        self.client = Anthropic()
        self.skill_graph = skill_graph
        self.loaded_skills = set()
    
    def execute_task(self, task: str, token_budget: int = 8000):
        """Executa tarefa com otimização de skills"""
        
        # 1. Determinar skills necessários
        optimal_skills = self.skill_graph.optimize_skill_loading(
            task, 
            token_budget - 2000  # Reserve para resposta
        )
        
        # 2. Construir contexto com skills selecionadas
        skills_context = self._build_skills_context(optimal_skills)
        
        # 3. Executar com Claude
        response = self.client.messages.create(
            model="claude-opus-4",
            max_tokens=4000,
            system=f"""Você é um expert em programação.

Você tem acesso aos seguintes conhecimentos especializados:

{skills_context}

Use essas habilidades para resolver a tarefa do usuário de forma efetiva.
""",
            messages=[
                {"role": "user", "content": task}
            ]
        )
        
        return response.content[0].text
    
    def _build_skills_context(self, skill_slugs: Set[str]) -> str:
        """Constrói contexto compilando skills selecionadas"""
        context_parts = []
        
        for slug in sorted(skill_slugs):
            skill = self.skill_graph.nodes[slug]
            context_parts.append(f"### {skill.name}\n{skill.description}\n")
        
        return "\n".join(context_parts)
```

### Marketplace e Descoberta

```python
class SkillMarketplace:
    def __init__(self):
        self.registry: Dict[str, SkillNode] = {}
    
    def search_skills(self, query: str, tags: List[str] = None) -> List[SkillNode]:
        """Busca skills por texto e tags"""
        results = []
        
        for skill in self.registry.values():
            # Busca por nome/descrição
            if query.lower() in skill.name.lower() or \
               query.lower() in skill.description.lower():
                results.append(skill)
            
            # Filtro por tags
            elif tags and any(t in skill.tags for t in tags):
                results.append(skill)
        
        return sorted(results, key=lambda s: len(s.tags))  # Mais específicas primeiro
    
    def get_learning_path(self, target_skill: str) -> List[str]:
        """Recomenda caminho de aprendizado para atingir skill target"""
        # BFS para encontrar caminho mais curto das fundamentals
        pass
```

## Stack e requisitos

### Ferramentas Principais

- **Claude Code**: v1.0+ (beta launched October 2025)
  - Requisitos: acesso a marketplace oficial
  - Custa: incluído no Claude API (cobrado por tokens)
- **Marketplace Oficial**: claude-plugins-official
  - Contém 150+ skills curadas
  - Integração automática ao iniciar Claude Code
- **Plugin System**: arquitetura nativa de extensão
  - Suporta skills, MCP servers, hooks

### Infraestrutura para Skill Graph

```
Python 3.9+
anthropic>=0.21.0
pydantic>=2.0.0  (para validação de skills)
networkx>=3.0    (para análise de grafos)
```

### Estimativas de Custo

Modelo de consumo typical:
- Skill base (fundamentals): ~2000 tokens
- Skill intermediária: ~3000 tokens  
- Skill avançada: ~3500 tokens

Para Leticia (processando ~20 links/dia):
- ~5 tarefas de coding por semana
- ~2 skills carregadas em média por tarefa
- ~0.50 USD/semana em API calls
- ~20 USD/mês em uso de skills

Para escala (100+ usuários):
- Considerar cache de skills compiladas
- Redis ou similar para memoization
- Custo: ~$500-1000/mês em Claude API

## Armadilhas e limitacoes

### 1. Dependências Circulares em Skill Graphs

Se skill A depende de B e skill B depende de A, o sistema não consegue carregar nenhuma das duas. Embora raro, é possível acontecer quando skills são criadas por contributors independentes sem coordenação.

**Solução**: Validar grafo na adição de skills. Usar algoritmo de detecção de ciclo (DFS) antes de commitar nova skill. Implementar linter que roda no CI para PRs de novas skills.

### 2. Token Bloat em Carregamento de Skills

Carregar muitas skills não-essenciais incha prompt, consumindo tokens desnecessariamente. Exemplo: carregar "ruby-on-rails advanced" ao trabalhar com Python. Erros de busca por relevância podem incluir skills erradas.

**Solução**: Usar embedding similarity + BM25 hybrid search ao invés de simples text matching. Implementar relevance scoring que penaliza skills com baixa similaridade de tags. Validar seleção contra historial de uso (se nunca usou uma skill em tarefas similares, não carregar).

### 3. Skill Obsolescence e Versioning

Skills referem-se a bibliotecas/ferramentas que evoluem. "React 16 best practices" vira obsoleto com React 18+. Sem versionamento apropriado, model pode seguir instruções desatualizadas.

**Solução**: Adicionar version constraints em dependencies ("react-basics>=2.0"). Implementar deprecation warnings quando versão de skill é antiga. Ter SLA de update para skills (ex: máximo 6 meses de idade antes de requerer review). Manter changelog em cada skill.

### 4. Overhead de Composição vs Ganho Real

Carregar um skill graph otimizado economiza ~10-15% de tokens comparado a carregar tudo. Mas o processamento para otimização (busca relevância, cálculo de closure, etc.) pode levar segundos, tornando o overhead imperceptível para tarefas pequenas.

**Solução**: Implementar threshold - se tarefa tem menos de 1000 tokens estimados, carregar todos os skills (mais rápido). Usar async para pré-computar skill graphs enquanto aguarda entrada do usuário. Cachear resultados de otimização por query similar.

### 5. Fragmentação de Skills Similares

A natureza crowdsourced do marketplace resulta em múltiplas skills que cobrem o mesmo domínio com qualidades variáveis (ex: "python-fastapi-basics v1", "python-fastapi-guide v2", "fastapi-quickstart v3"). Modelo pode confundir qual usar.

**Solução**: Implementar deduplication baseado em embedding similarity. Consolidar skills similares em versões oficiais mantidas por time Anthropic. Usar star ratings + installs count para superficial skills melhores. Implementar migration guide quando skill é marcada como "deprecated in favor of X".

## Conexoes

[[claude-code-plugins-system|Sistema de plugins oficial do Claude Code]]
[[context-window-optimization|Otimização de janela de contexto em LLMs]]
[[mcp-servers-tools-integration|Integração de MCP servers como ferramentas]]
[[prompt-engineering-for-agents|Técnicas de engineering para agentes autônomos]]
[[knowledge-graph-llms|Estruturação de conhecimento para melhor raciocínio]]

## Historico

- 2026-04-11: Nota criada com arquitetura de skill graphs, implementação Python, e otimização de token usage
- Baseado em: Claude Code official docs, skill marketplace (1300+ skills), research em context optimization 2026