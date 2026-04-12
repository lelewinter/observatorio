---
tags: [gitnexus, knowledge-graph, mcp, claude-code, code-intelligence, ast]
source: https://x.com/heygurisingh/status/2040464288264139002
date: 2026-04-04
tipo: aplicacao
---
# GitNexus: Knowledge Graph de Codebase via AST + MCP para Claude Code

## O que é
GitNexus é um mecanismo de inteligência de código que constrói um grafo de conhecimento completo do seu repositório usando parsing AST (Abstract Syntax Tree) via Tree-sitter. Mapeia cada chamada de função, import, herança de classe, interfaces, e agrupa código em clusters funcionais com scores de coesão. Integra-se via MCP com Claude Code para enriquecer automaticamente chamadas grep/glob/bash com contexto do grafo, permitindo análise de "blast radius" (impacto de mudanças) antes de refatorações. Gera skills automaticamente detectando áreas funcionais via Leiden community detection.

## Como implementar

### Instalação e Setup Básico
GitNexus é um zero-server CLI - executa localmente no seu repositório:

```bash
# Instalação simples
npm install -g gitnexus
# ou
npx gitnexus analyze

# No seu repositório
cd seu-repo
npx gitnexus analyze

# Output: gitnexus.json com grafo completo
```

### Entendendo a Estrutura do Grafo
O arquivo `gitnexus.json` resultante contém:

```json
{
  "nodes": [
    {
      "id": "src/auth/loginService.ts",
      "type": "file",
      "functions": [
        {
          "name": "validateToken",
          "type": "function",
          "startLine": 12,
          "endLine": 28,
          "imports": ["jwt", "crypto"]
        },
        {
          "name": "refreshToken",
          "type": "function",
          "startLine": 30,
          "endLine": 42,
          "calls": ["validateToken"]
        }
      ],
      "exports": ["validateToken", "refreshToken"],
      "metrics": {
        "cyclomaticComplexity": 3,
        "linesOfCode": 45,
        "cohesion": 0.92
      }
    }
  ],
  "edges": [
    {
      "source": "src/auth/loginService.ts:refreshToken",
      "target": "src/auth/loginService.ts:validateToken",
      "type": "calls"
    },
    {
      "source": "src/auth/loginService.ts",
      "target": "src/utils/jwt-handler.ts",
      "type": "imports"
    }
  ],
  "clusters": {
    "auth": {
      "files": ["src/auth/loginService.ts", "src/auth/permissionCheck.ts"],
      "cohesion": 0.88,
      "boundaryViolations": 1
    }
  }
}
```

### Implementação Python para Análise do Grafo
Após rodar `gitnexus analyze`, você pode processar o grafo:

```python
import json
import networkx as nx
from pathlib import Path
from typing import List, Dict, Set

class CodebaseGraphAnalyzer:
    def __init__(self, gitnexus_json_path: str = "gitnexus.json"):
        with open(gitnexus_json_path) as f:
            self.graph_data = json.load(f)
        
        # Construir grafo em memória
        self.graph = nx.DiGraph()
        self._build_graph()
    
    def _build_graph(self):
        """Reconstrói NetworkX graph a partir de gitnexus.json"""
        for node in self.graph_data.get("nodes", []):
            self.graph.add_node(node["id"], **node)
        
        for edge in self.graph_data.get("edges", []):
            self.graph.add_edge(
                edge["source"],
                edge["target"],
                type=edge.get("type")
            )
    
    def find_blast_radius(self, modified_file: str, depth: int = 3) -> Dict:
        """
        Encontra todos os arquivos afetados por mudança em modified_file
        Depth: quantas camadas de dependências seguir
        """
        affected = set()
        queue = [(modified_file, 0)]
        
        while queue:
            node, current_depth = queue.pop(0)
            if current_depth > depth:
                continue
            
            # Arquivos que importam este (downstream)
            for successor in self.graph.successors(node):
                if successor not in affected:
                    affected.add(successor)
                    queue.append((successor, current_depth + 1))
        
        return {
            "modified": modified_file,
            "affected_count": len(affected),
            "affected_files": list(affected),
            "risk_score": len(affected) / len(self.graph.nodes())  # 0-1
        }
    
    def find_circular_dependencies(self) -> List[List[str]]:
        """Detecta ciclos que violam DAG"""
        try:
            nx.topological_sort(self.graph)
            return []  # Sem ciclos
        except nx.NetworkXError:
            # Extrair ciclos
            cycles = list(nx.simple_cycles(self.graph))
            return cycles
    
    def analyze_cohesion(self, cluster_name: str) -> Dict:
        """Analisa coesão de um cluster detectado por Leiden"""
        cluster = self.graph_data["clusters"].get(cluster_name, {})
        
        internal_edges = 0
        external_edges = 0
        
        for file in cluster.get("files", []):
            # Contar edges internos vs externos
            for successor in self.graph.successors(file):
                if successor in cluster["files"]:
                    internal_edges += 1
                else:
                    external_edges += 1
        
        return {
            "cluster": cluster_name,
            "files": cluster.get("files", []),
            "internal_edges": internal_edges,
            "external_edges": external_edges,
            "cohesion_score": cluster.get("cohesion", 0),
            "boundary_violations": cluster.get("boundaryViolations", 0)
        }
    
    def get_function_call_chain(self, start_function: str, max_depth: int = 5) -> Dict:
        """Rastreia execução de uma função até suas chamadas folha"""
        call_chain = {start_function: []}
        queue = [(start_function, 0)]
        
        while queue:
            func, depth = queue.pop(0)
            if depth >= max_depth:
                continue
            
            # Achar todas as funções que esta chama
            for target in self.graph.successors(func):
                call_chain[func].append(target)
                if (target, depth + 1) not in [(q[0], q[1]) for q in queue]:
                    queue.append((target, depth + 1))
        
        return call_chain
    
    def suggest_skill_boundaries(self) -> List[Dict]:
        """
        Usa resultados de Leiden para sugerir skill boundaries
        Cada skill = um cluster com alta coesão interna, baixas dependências externas
        """
        skills = []
        for cluster_name, cluster_data in self.graph_data.get("clusters", {}).items():
            skill = {
                "name": cluster_name,
                "files": cluster_data["files"],
                "cohesion": cluster_data.get("cohesion", 0),
                "complexity": len(cluster_data["files"]),
                "recommended_skill": cluster_data.get("cohesion", 0) > 0.75,
                "description": f"Cluster '{cluster_name}' - {len(cluster_data['files'])} files"
            }
            skills.append(skill)
        
        return sorted(skills, key=lambda x: x["cohesion"], reverse=True)

# Uso prático
analyzer = CodebaseGraphAnalyzer()

# 1. Verificar impacto de mudança
blast = analyzer.find_blast_radius("src/auth/loginService.ts")
print(f"Modificar loginService afeta {blast['affected_count']} arquivos")
print(f"Risk score: {blast['risk_score']:.1%}")

# 2. Detectar ciclos problemáticos
cycles = analyzer.find_circular_dependencies()
if cycles:
    print(f"⚠ {len(cycles)} ciclos detectados:")
    for cycle in cycles:
        print(f"  {' -> '.join(cycle)} -> {cycle[0]}")

# 3. Analisar coesão de clusters
for skill in analyzer.suggest_skill_boundaries():
    print(f"📦 {skill['name']}: cohesion={skill['cohesion']:.2f}, files={len(skill['files'])}")
```

### Integração com Claude Code via MCP

GitNexus fornece um hook MCP que enriquece automaticamente consultas:

```python
# Arquivo: gitnexus-mcp-adapter.py
# Este é o serviço que Claude Code consultará

import json
from pathlib import Path

class GitNexusMCPAdapter:
    """
    Adapter MCP que Claude Code usa para enriquecer buscas
    """
    
    def __init__(self, repo_path: str):
        self.repo_path = Path(repo_path)
        self.analyzer = CodebaseGraphAnalyzer(repo_path / "gitnexus.json")
    
    def handle_grep_enrichment(self, pattern: str, files: List[str]) -> Dict:
        """
        Claude Code: grep -r "updateUser" --include="*.ts"
        GitNexus MCP enriquece com contexto de relações
        """
        
        matches = []
        for file in files:
            # Procurar pattern no arquivo
            full_path = self.repo_path / file
            if full_path.exists():
                with open(full_path) as f:
                    content = f.read()
                    for line_num, line in enumerate(content.split("\n"), 1):
                        if pattern in line:
                            matches.append({
                                "file": file,
                                "line": line_num,
                                "content": line.strip()
                            })
        
        # Enriquecer com contexto do grafo
        enriched = []
        for match in matches:
            file = match["file"]
            
            # Quais arquivos dependem deste?
            dependents = list(self.analyzer.graph.predecessors(file))
            
            # Quais arquivos este depende?
            dependencies = list(self.analyzer.graph.successors(file))
            
            enriched.append({
                **match,
                "impact_files": dependents,
                "dependency_files": dependencies,
                "blast_radius": len(dependents)
            })
        
        return {
            "pattern": pattern,
            "total_matches": len(enriched),
            "matches": enriched
        }
    
    def handle_glob_context(self, glob_pattern: str) -> Dict:
        """
        Claude Code: ls -la src/auth/*.ts
        GitNexus retorna estrutura + relacionamentos
        """
        
        matching_files = list(self.repo_path.glob(glob_pattern))
        
        context = {
            "glob": glob_pattern,
            "matching_files": [str(f) for f in matching_files],
            "structure": {}
        }
        
        # Para cada arquivo, incluir informações estruturais
        for file in matching_files:
            file_key = str(file.relative_to(self.repo_path))
            
            # Buscar no grafo
            node_data = next(
                (n for n in self.analyzer.graph_data["nodes"] if n["id"] == file_key),
                None
            )
            
            if node_data:
                context["structure"][file_key] = {
                    "functions": [f["name"] for f in node_data.get("functions", [])],
                    "exports": node_data.get("exports", []),
                    "complexity": node_data.get("metrics", {}).get("cyclomaticComplexity"),
                    "lines_of_code": node_data.get("metrics", {}).get("linesOfCode")
                }
        
        return context
    
    def handle_refactor_analysis(self, target_file: str, proposed_changes: str) -> Dict:
        """
        Antes de refatorar, analyze o impacto
        """
        
        blast = self.analyzer.find_blast_radius(target_file, depth=3)
        
        return {
            "target": target_file,
            "affected_files": blast["affected_files"],
            "affected_count": blast["affected_count"],
            "risk_score": blast["risk_score"],
            "recommendation": "SAFE" if blast["risk_score"] < 0.1 else "RISKY" if blast["risk_score"] > 0.3 else "CAUTION"
        }
```

### Geração Automática de Skills
GitNexus detecta automaticamente limites de skill usando Leiden community detection:

```python
def generate_skills_from_clusters(analyzer: CodebaseGraphAnalyzer, output_dir: str = "skills"):
    """
    Gera SKILL.md para cada cluster de alta coesão
    """
    Path(output_dir).mkdir(exist_ok=True)
    
    for skill in analyzer.suggest_skill_boundaries():
        if skill["recommended_skill"]:
            skill_name = skill["name"]
            files = skill["files"]
            
            # Template SKILL.md
            skill_md = f"""---
name: {skill_name}
description: {skill['description']}
files: {json.dumps(files)}
cohesion: {skill['cohesion']:.2f}
---

# {skill_name.title()}

## Overview
Cluster '{skill_name}' contém {len(files)} arquivos altamente coesos (cohesion={skill['cohesion']:.2f}).

## Files
{chr(10).join(f'- `{f}`' for f in files[:10])}

## Commands
- `/understand-{skill_name}` — Entenda a estrutura deste módulo
- `/refactor-{skill_name}` — Refatore mantendo interfaces
- `/test-{skill_name}` — Gere testes para este cluster
"""
            
            with open(f"{output_dir}/{skill_name}.md", "w") as f:
                f.write(skill_md)
            
            print(f"✓ Skill criada: {skill_name}")
```

## Stack e Requisitos

### Instalação
- **Node.js**: v16+ (npm necessário)
- **Tree-sitter**: incluído via npm, suporta 19+ linguagens (Python, TypeScript, Go, Rust, Java, etc)
- **Dependências Python** (análise): networkx, json (standard library)

### Suporte de Linguagens
- **Full Support**: JavaScript, TypeScript, Python, Go, Rust, Java, C++, C#, Ruby, PHP
- **Partial**: CSS, HTML, JSON, YAML (estrutura apenas, sem AST completo)
- **Detecta**: 200+ frameworks/libraries (React, Django, Spring, etc)

### Saída Gerada
```
gitnexus.json          — Grafo completo em JSON
gitnexus.html          — Visualização interativa do grafo
blast-radius.json      — Análise de impacto pré-computada
clusters.json          — Detecção de módulos
```

### Custo e Performance
- **Runtime**: 5-30 segundos para repo de 100-500K linhas
- **Memória**: ~500MB-2GB dependendo do tamanho
- **Armazenamento**: gitnexus.json ~ 10-50% do tamanho do código
- **Custo**: Gratuito (open source), sem API external

### Integração com Pipeline Existente
Pode ser integrado em:
```bash
# Pre-commit hook
pre-commit hook: npx gitnexus analyze

# CI/CD
github-actions: uses: ./gitnexus-action

# Local development
npm run analyze  # Atualizar grafo antes de refatoração
```

## Armadilhas e Limitações

### 1. AST Parsing Não Entende Dinâmica
Tree-sitter analisa sintaxe estática. Chamadas dinâmicas em runtime são perdidas:

```typescript
// GitNexus VÊ
function callHandler(name) {
  handlers[name]();  // ← Desconhecido qual é o handler
}

// Solução: anotações
/** @calls getUserHandler, updateUserHandler */
function callHandler(name) {
  handlers[name]();
}
```

**Mitigação**:
- Adicionar comentários JSDoc/docstring com @calls
- Executar análise de tipo com TypeScript: `tsc --noEmit` primeiro
- Usar linter que detecta dinâmica (eslint-plugin-import)

### 2. Performance em Repos Massivos
100K+ linhas começa a ficar lento. Tree-sitter é single-threaded.

**Mitigação**:
```bash
# Excluir pastas que não precisam de análise
npx gitnexus analyze --ignore="node_modules,dist,coverage,tests"

# Ou processar por módulo
npx gitnexus analyze --focus="src/auth"  # Apenas este módulo
```

### 3. Ciclos de Atualização
gitnexus.json fica desatualizado conforme código muda. Recalcular a cada commit é lento.

**Mitigação**:
```bash
# Incremental (mais rápido)
npx gitnexus analyze --incremental

# Ou integrar com git hooks
echo "npx gitnexus analyze" > .git/hooks/post-merge
chmod +x .git/hooks/post-merge
```

### 4. Falsos Positivos em Blast Radius
Arquivo A importa arquivo B, mas só usa 1 função. Mudar outras funções em B não afeta A, mas blast radius retorna "affected".

**Mitigação**:
```python
# Análise mais granular: qual função especificamente é usada?
def find_precise_blast_radius(self, modified_function: str) -> Set[str]:
    """Retorna apenas arquivos que usam modified_function específico"""
    affected_files = set()
    
    for source, target in self.graph.edges():
        if target == modified_function:
            # source depende de modified_function
            affected_files.add(source.split(":")[0])  # Extrair arquivo
    
    return affected_files
```

### 5. Leiden Clustering Pode Separar Código Logicamente Relacionado
Leiden detecta clusters por densidade de conexões, não por intenção de domínio. Auth e Permissions podem ficar separados mesmo sendo logicamente ligados.

**Mitigação**:
- Validar skills geradas antes de finalizar
- Usar `modulepath-structure` (convenção de pastas) como hint
- Refinar manualmente: `gitnexus.json` é editável

## Conexões
- [[ast-parsing-tree-sitter]] - Entender como Tree-sitter funciona
- [[code-metrics-cyclomatic-complexity]] - Métricas incluídas no grafo
- [[mcp-protocol-claude-code]] - Como MCP enriches Claude Code
- [[refactoring-safe-strategies]] - Usar blast radius para refatorações seguras
- [[modular-monolith-architecture]] - Organizar código em skills
- [[community-detection-graphs]] - Como Leiden agrupa nós

## Histórico
- 2026-04-04: Nota criada com análise completa de AST, MCP integration, skill generation
