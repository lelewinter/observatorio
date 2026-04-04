---
tags: []
source: https://x.com/neogoose_btw/status/2039508756988620801?s=20
date: 2026-04-02
tipo: aplicacao
---
# Implementar Busca de Código sem Índice

## O que é
Busca em repositórios gigantescos (100k-500k arquivos: Linux, Chromium, Claude source) sem estruturas de índice pré-construídas. Resultado preciso, latência baixa (~200ms), sem overhead de sincronização de índice. Viável em codebases a frio.

## Como implementar
**1. Mecânica: busca linha-by-linha vs índice**:

```
Indexed approach:
Código muda → Indexar (1-2 min) → Buscar rápido (10ms)

Index-free approach:
Código muda → Buscar direto (100-500ms) → Resultado sempre atualizado

Trade-off: latência por ausência de estado stale
```

**2. Busca baseline com ripgrep (rg)**:

```bash
# ripgrep é otimizado pra busca index-free
# Muito mais rápido que grep tradicional

# Busca simples
rg "function_name" repo/

# Regex
rg "async function\s+\w+\(" repo/

# Por tipo de arquivo
rg --type py "class.*Handler" repo/

# Com contexto
rg -C 3 "import torch" repo/

# Contar matches
rg --count "TODO"

# Em velocidade: rg tira 100k arquivos em ~200ms
```

**3. Python wrapper otimizado**:

```python
import subprocess
import re
from typing import List, Dict
from pathlib import Path

class IndexFreeCodeSearch:
    def __init__(self, repo_path: str):
        self.repo = Path(repo_path)
        self.cache = {}  # Cache in-memory (simple, não persiste)

    def search(self, pattern: str, file_type: str = None, context_lines: int = 0) -> List[Dict]:
        """Busca padrão no repositório sem índice."""

        cache_key = f"{pattern}:{file_type}:{context_lines}"
        if cache_key in self.cache:
            return self.cache[cache_key]

        cmd = ["rg", pattern, str(self.repo), "--json"]

        if file_type:
            cmd.extend(["--type", file_type])

        if context_lines > 0:
            cmd.extend(["-C", str(context_lines)])

        result = subprocess.run(cmd, capture_output=True, text=True, timeout=5)

        # Parse saída JSON
        matches = []
        for line in result.stdout.strip().split("\n"):
            if line:
                import json
                match = json.loads(line)
                matches.append({
                    "file": match["data"]["path"]["text"],
                    "line": match["data"]["line_number"],
                    "text": match["data"]["lines"]["text"],
                    "match": match["data"]["submatches"]
                })

        self.cache[cache_key] = matches
        return matches

    def search_symbol(self, symbol: str, file_type: str = None) -> List[Dict]:
        """Busca definição de símbolo (variável, função, classe)."""

        # Padrão para encontrar definição
        patterns = {
            "py": rf"^(def|class)\s+{symbol}\s*\(",
            "js": rf"(function|const|class)\s+{symbol}\s*[({]",
            "go": rf"(func|type)\s+{symbol}\s*",
        }

        pattern = patterns.get(file_type, symbol)
        return self.search(pattern, file_type=file_type)

    def search_callers(self, function_name: str, file_type: str = None) -> List[Dict]:
        """Encontra todos os calls de uma função."""

        # Regex para detectar chamada
        pattern = rf"{function_name}\s*\("
        return self.search(pattern, file_type=file_type, context_lines=2)

    def find_imports(self, module_name: str, file_type: str = "py") -> List[Dict]:
        """Encontra todos os imports de um módulo."""

        pattern = rf"(import|from)\s+.*{module_name}"
        return self.search(pattern, file_type=file_type)

    def search_with_fallback(self, patterns: List[str], file_type: str = None) -> List[Dict]:
        """Tenta múltiplos padrões até achar algo."""

        for pattern in patterns:
            results = self.search(pattern, file_type=file_type)
            if results:
                return results

        return []
```

**4. Performance em codebases reais**:

```python
import time

class PerformanceBenchmark:
    def __init__(self, searcher: IndexFreeCodeSearch):
        self.searcher = searcher

    def benchmark_suite(self):
        """Roda suite de benchmarks."""

        benchmarks = [
            ("Find function definition", lambda: self.searcher.search_symbol("main", file_type="py")),
            ("Find all callers", lambda: self.searcher.search_callers("fetch_data", file_type="py")),
            ("Search regex complex", lambda: self.searcher.search(r"async def\s+\w+\s*\(.*\)", file_type="py")),
            ("Count pattern", lambda: self.searcher.search("TODO|FIXME|XXX", file_type="py")),
        ]

        results = {}
        for name, query in benchmarks:
            start = time.time()
            result = query()
            elapsed = (time.time() - start) * 1000

            results[name] = {
                "time_ms": elapsed,
                "matches": len(result),
                "speed": f"{len(result) / (elapsed/1000):.0f} matches/sec"
            }

        return results

# Dados reais (estimado):
# Claude source (1M files): ~200-500ms
# Linux kernel (500k files): ~150-300ms
# Chromium (300k files): ~100-200ms
```

**5. Integração com agentes de IA**:

```python
from anthropic import Anthropic

class AgentWithCodeSearch:
    def __init__(self, repo_path: str):
        self.client = Anthropic()
        self.searcher = IndexFreeCodeSearch(repo_path)

    def analyze_codebase_feature(self, feature_description: str):
        """Agente analisa feature no codebase."""

        system_prompt = """Você é especialista em análise de código.
        Tem acesso a busca index-free do repositório.
        Para entender um feature, primeiro busque definições e calls relacionados."""

        messages = [{
            "role": "user",
            "content": f"Explique como funciona: {feature_description}"
        }]

        # Iteração: agente pode fazer buscas
        for _ in range(5):  # Max 5 searches
            response = self.client.messages.create(
                model="claude-3-5-sonnet-20241022",
                max_tokens=2000,
                system=system_prompt,
                messages=messages,
                tools=[{
                    "name": "search_code",
                    "description": "Busca padrão no repositório",
                    "input_schema": {
                        "type": "object",
                        "properties": {
                            "pattern": {"type": "string"},
                            "file_type": {"type": "string"}
                        }
                    }
                }]
            )

            # Processar tool use
            if response.stop_reason == "end_turn":
                return response.content[0].text

            for block in response.content:
                if hasattr(block, 'type') and block.type == "tool_use":
                    search_results = self.searcher.search(
                        block.input["pattern"],
                        file_type=block.input.get("file_type")
                    )

                    messages.append({"role": "assistant", "content": response.content})
                    messages.append({
                        "role": "user",
                        "content": [{
                            "type": "tool_result",
                            "tool_use_id": block.id,
                            "content": str(search_results[:5])  # Top 5 matches
                        }]
                    })
```

**6. Alternativas: quando usar índice vs index-free**:

```
Situação                          | Index-free | Indexed
-------------------------------------|-----------|----------
Setup inicial (frio)                 | ✓         | ✗ (espera indexação)
Código muda frequentemente            | ✓         | ✗ (índice stale)
Repositório >500k arquivos           | ✓         | ✗ (índice huge)
Buscas 10x/dia                       | ✓         | ~ (ambos OK)
Buscas 1000x/dia                     | ✗         | ✓ (latência crítica)
Machine de borda (Raspberry Pi)      | ✓         | ✗ (RAM limitada)
Exploratory analysis (ad-hoc)        | ✓         | ~ (ambos OK)
Production search service            | ✗         | ✓ (previsibilidade)

Hybrid approach:
- Use index-free para exploração
- Manter índice opcional para produção
```

## Stack e requisitos
- **ripgrep (rg)**: `brew install ripgrep` (ou package manager)
- **Python**: subprocess + json parsing
- **Repositório**: qualquer tamanho (15k a 500k+ arquivos)
- **Latência**: 100-500ms por busca (CPU-bound)
- **Sem storage overhead**: sem arquivo de índice

## Armadilhas e limitações
- **CPU-bound**: buscas grandes consomem CPU (bloqueiam por 100-500ms)
- **Network timeout**: em repos montados remotamente, pode ser lento
- **Regex complexity**: padrões complexos são ainda mais lentos
- **Concurrent searches**: não há proteção natural (ripgrep sem state)

## Conexões
[[RAG com Codebases]], [[Agentes de Análise de Código]], [[Tool Use para Busca]], [[Arquitetura de Agentes de Código]]

## Histórico
- 2026-04-02: Nota criada
- 2026-04-02: Reescrita em padrão aplicacao
