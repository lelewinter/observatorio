---
tags: [graphify, knowledge-graph, karpathy, token-efficiency, claude-code, rag]
source: https://x.com/RoundtableSpace/status/2041421970546528318
date: 2026-04-07
tipo: aplicacao
---
# Graphify: Knowledge Graph com 71.5x Menos Tokens (Resposta ao Karpathy LLM Wiki)

## O que é
Graphify é um sistema de transformação de pastas em grafos de conhecimento consulta-ável construído em 48 horas como resposta ao proposal de Karpathy sobre LLM Wiki. Reduz tokens por query em 71.5x (de ~123K tokens ingênuos para ~1.7K tokens estruturados). Usa parsing AST determinístico de código (sem LLM), processa docs/papers/imagens em paralelo com subagentes Claude, e retorna grafo consolidado em NetworkX com clustering via Leiden detection. Suporta 20+ linguagens e é completamente multimodal. Disponível em GitHub: safishamshi/graphify.

## O que é

## Como implementar

### Instalação e Setup Básico
```bash
# Clone repositório
git clone https://github.com/safishamsi/graphify
cd graphify

# Instalar dependências
pip install -r requirements.txt
# Inclui: anthropic, networkx, tree-sitter, pdf2image, pytesseract, pillow

# Rodar análise
graphify analyze ./seu-projeto
```

### Entendendo o Pipeline de Duas Fases

**Fase 1: AST Parsing Determinístico (Sem LLM)**

Esta fase NÃO chama Claude. É puramente estrutural:

```python
import tree_sitter
from tree_sitter import Language, Parser
import json
from pathlib import Path
from typing import List, Dict

class ASTCodeExtractor:
    def __init__(self):
        # Carregar linguagens suportadas
        LANGUAGES = {
            "python": Language("build/my-languages.so", "python"),
            "javascript": Language("build/my-languages.so", "javascript"),
            "typescript": Language("build/my-languages.so", "typescript"),
        }
        self.languages = LANGUAGES
        self.parser = Parser()
    
    def extract_from_file(self, filepath: str, language: str) -> Dict:
        """
        Extrai estrutura sem interpretar semântica
        Determinístico: mesmo arquivo sempre gera mesma saída
        """
        
        with open(filepath, "rb") as f:
            source_code = f.read()
        
        self.parser.set_language(self.languages[language])
        tree = self.parser.parse(source_code)
        
        functions = []
        classes = []
        imports = []
        
        # Traverse AST
        def walk_tree(node):
            if node.type == "function_definition":
                functions.append({
                    "name": self._extract_identifier(node),
                    "start_line": node.start_point[0],
                    "end_line": node.end_point[0],
                    "parameters": self._extract_params(node),
                    "return_type": self._extract_return_type(node),
                })
            elif node.type == "class_definition":
                classes.append({
                    "name": self._extract_identifier(node),
                    "start_line": node.start_point[0],
                    "methods": [],  # Preenchido recursivamente
                    "inherits_from": self._extract_inheritance(node),
                })
            elif node.type in ["import_statement", "import_from_statement"]:
                imports.append({
                    "module": self._extract_module(node),
                    "items": self._extract_import_items(node),
                })
            
            for child in node.children:
                walk_tree(child)
        
        walk_tree(tree.root_node)
        
        return {
            "file": filepath,
            "language": language,
            "functions": functions,
            "classes": classes,
            "imports": imports,
            "total_lines": len(source_code.split(b"\n")),
        }
    
    def _extract_identifier(self, node) -> str:
        """Extrai nome de função/classe"""
        for child in node.children:
            if child.type == "identifier":
                return child.text.decode()
        return "unknown"
    
    def _extract_params(self, node) -> List[str]:
        """Extrai parâmetros de função"""
        params = []
        for child in node.children:
            if child.type == "parameters":
                for param_node in child.children:
                    if param_node.type == "identifier":
                        params.append(param_node.text.decode())
        return params
    
    def _extract_return_type(self, node) -> str:
        """Extrai tipo de retorno se declarado"""
        for child in node.children:
            if child.type == "type_annotation":
                return child.text.decode()
        return "unknown"
    
    def _extract_inheritance(self, node) -> List[str]:
        """Extrai classes pai"""
        bases = []
        for child in node.children:
            if child.type == "argument_list":
                for arg in child.children:
                    if arg.type == "identifier":
                        bases.append(arg.text.decode())
        return bases
    
    def _extract_module(self, node) -> str:
        """Extrai nome do módulo importado"""
        for child in node.children:
            if child.type in ["dotted_name", "relative_import", "identifier"]:
                return child.text.decode()
        return ""
    
    def _extract_import_items(self, node) -> List[str]:
        """Extrai o que está sendo importado"""
        items = []
        for child in node.children:
            if child.type == "identifier":
                items.append(child.text.decode())
        return items

# Uso: processar inteiro diretório
extractor = ASTCodeExtractor()
code_structure = {}
for py_file in Path("src").rglob("*.py"):
    code_structure[str(py_file)] = extractor.extract_from_file(str(py_file), "python")

# Resultado: ~1.7K tokens quando enviado a Claude depois
print(json.dumps(code_structure, indent=2))
```

**Fase 2: Processamento de Docs/Papers/Imagens em Paralelo**

Agora sim usamos Claude, mas de forma smart:

```python
import asyncio
from anthropic import Anthropic
from concurrent.futures import ThreadPoolExecutor
import base64
from pathlib import Path

class DocumentProcessor:
    def __init__(self, api_key: str):
        self.client = Anthropic()
    
    async def process_markdown(self, filepath: str) -> Dict:
        """Processa arquivo markdown em contexto estruturado"""
        with open(filepath) as f:
            content = f.read()
        
        # Quebrar em chunks (5K tokens each)
        chunks = [content[i:i+20000] for i in range(0, len(content), 20000)]
        
        extracted_items = []
        
        for chunk in chunks:
            # Prompt estruturado reduz output desnecessário
            response = self.client.messages.create(
                model="claude-3-5-sonnet-20241022",
                max_tokens=500,  # Limite output
                messages=[{
                    "role": "user",
                    "content": f"""Extraia APENAS estruturado:
                    
1. Conceitos principais (lista)
2. Dependências/relações
3. Exemplos práticos (código se houver)

Arquivo: {Path(filepath).name}

Conteúdo:
{chunk}

Responda em JSON:
{{"concepts": [...], "relations": [...], "examples": [...]}}"""
                }]
            )
            
            try:
                extracted = json.loads(response.content[0].text)
                extracted_items.extend(extracted.get("concepts", []))
            except json.JSONDecodeError:
                pass  # Skip se não for JSON válido
        
        return {
            "file": filepath,
            "type": "markdown",
            "concepts": extracted_items,
        }
    
    async def process_pdf(self, filepath: str) -> Dict:
        """Processa PDF: extrai texto + imagens com OCR"""
        import pdf2image
        import pytesseract
        
        images = pdf2image.convert_from_path(filepath)
        
        extracted_text = ""
        for img in images:
            # OCR se houver imagens
            text = pytesseract.image_to_string(img)
            extracted_text += text + "\n"
        
        # Processar como markdown
        return await self.process_markdown_text(extracted_text)
    
    async def process_image(self, filepath: str) -> Dict:
        """Processa imagem com visão multimodal do Claude"""
        with open(filepath, "rb") as f:
            image_data = base64.standard_b64encode(f.read()).decode()
        
        response = self.client.messages.create(
            model="claude-3-5-sonnet-20241022",
            max_tokens=300,
            messages=[{
                "role": "user",
                "content": [
                    {
                        "type": "image",
                        "source": {
                            "type": "base64",
                            "media_type": "image/png",
                            "data": image_data,
                        },
                    },
                    {
                        "type": "text",
                        "text": "Descreva sucintamente: elementos-chave, relacionamentos, caso de uso. JSON: {elements: [...], relationships: [...]}",
                    }
                ],
            }]
        )
        
        return {
            "file": filepath,
            "type": "image",
            "visual_description": response.content[0].text,
        }
    
    async def process_all_documents(self, folder: Path) -> List[Dict]:
        """Processa todos documentos em paralelo"""
        tasks = []
        
        for file in folder.rglob("*"):
            if file.suffix == ".md":
                tasks.append(self.process_markdown(str(file)))
            elif file.suffix == ".pdf":
                tasks.append(self.process_pdf(str(file)))
            elif file.suffix in [".png", ".jpg", ".jpeg"]:
                tasks.append(self.process_image(str(file)))
        
        # Executar todas em paralelo (throttled por Anthropic rate limits)
        results = await asyncio.gather(*tasks, return_exceptions=True)
        return [r for r in results if not isinstance(r, Exception)]

# Uso
processor = DocumentProcessor(api_key="seu-api-key")
docs = asyncio.run(processor.process_all_documents(Path("docs")))
```

### Consolidação em NetworkX Graph com Clustering

Após extrair tudo, montar grafo:

```python
import networkx as nx
from sklearn.cluster import SpectralClustering
from itertools import combinations

class KnowledgeGraphBuilder:
    def __init__(self):
        self.graph = nx.Graph()
    
    def build_from_extracted_data(self, code_structure: Dict, documents: List[Dict]) -> nx.Graph:
        """
        Consolida AST + docs em grafo unificado
        Nodes: funções, classes, conceitos, arquivos
        Edges: imports, calls, relacionamentos
        """
        
        # Adicionar nós de código
        for filepath, file_data in code_structure.items():
            # Nós de arquivo
            self.graph.add_node(filepath, type="file", language=file_data["language"])
            
            # Nós de função
            for func in file_data.get("functions", []):
                func_id = f"{filepath}:{func['name']}"
                self.graph.add_node(
                    func_id,
                    type="function",
                    name=func["name"],
                    start_line=func["start_line"],
                    file=filepath
                )
                # Conectar ao arquivo
                self.graph.add_edge(filepath, func_id, relationship="contains")
            
            # Nós de classe
            for cls in file_data.get("classes", []):
                class_id = f"{filepath}:{cls['name']}"
                self.graph.add_node(
                    class_id,
                    type="class",
                    name=cls["name"],
                    file=filepath
                )
                self.graph.add_edge(filepath, class_id, relationship="contains")
                
                # Herança
                for parent in cls.get("inherits_from", []):
                    self.graph.add_edge(class_id, parent, relationship="inherits_from")
            
            # Imports
            for imp in file_data.get("imports", []):
                module = imp["module"]
                for item in imp.get("items", []):
                    target_id = f"{module}:{item}"
                    self.graph.add_edge(filepath, target_id, relationship="imports")
        
        # Adicionar nós de documentação
        for doc in documents:
            doc_id = f"doc:{Path(doc['file']).stem}"
            self.graph.add_node(doc_id, type="document", file=doc["file"])
            
            # Adicionar conceitos como nós
            for concept in doc.get("concepts", [])[:10]:  # Limitar
                concept_id = f"concept:{concept}"
                self.graph.add_node(concept_id, type="concept", name=concept)
                self.graph.add_edge(doc_id, concept_id, relationship="defines")
        
        return self.graph
    
    def detect_clusters_leiden(self) -> Dict[str, List[str]]:
        """
        Usa Leiden para detectar comunidades (clusters temáticos)
        Cada cluster = área de conhecimento coesa
        """
        try:
            import leidenalg
            import igraph
            
            # Converter NetworkX -> igraph
            ig = igraph.Graph.from_networkx(self.graph)
            
            # Rodar Leiden
            partition = leidenalg.find_partition(
                ig,
                leidenalg.ModularityOptimizer(),
                seed=42,
            )
            
            # Mapear de volta para nós
            clusters = {}
            for cluster_id, members in enumerate(partition):
                cluster_name = f"cluster_{cluster_id}"
                node_names = [ig.vs[m]["_nx_name"] for m in members]
                clusters[cluster_name] = node_names
            
            return clusters
        
        except ImportError:
            # Fallback: usar community detection nativa
            from networkx.algorithms import community
            communities = community.greedy_modularity_communities(self.graph)
            
            clusters = {}
            for i, comm in enumerate(communities):
                clusters[f"cluster_{i}"] = list(comm)
            
            return clusters
    
    def export_as_json(self, filepath: str, clusters: Dict = None):
        """Exportar para JSON consultável"""
        data = {
            "nodes": [
                {
                    "id": node,
                    **self.graph.nodes[node]
                }
                for node in self.graph.nodes()
            ],
            "edges": [
                {
                    "source": u,
                    "target": v,
                    **self.graph[u][v]
                }
                for u, v in self.graph.edges()
            ],
            "clusters": clusters or {},
        }
        
        with open(filepath, "w") as f:
            json.dump(data, f, indent=2)
    
    def export_as_html(self, filepath: str):
        """Exportar visualização interativa (vis.js)"""
        import pyvis.network as net
        
        net_vis = net.Network(
            height="750px",
            width="100%",
            directed=False,
            physics=True
        )
        net_vis.from_nx(self.graph)
        net_vis.show(filepath)

# Uso completo
builder = KnowledgeGraphBuilder()

# 1. Extrair código
code_data = {}
for py_file in Path("src").rglob("*.py"):
    code_data[str(py_file)] = extractor.extract_from_file(str(py_file), "python")

# 2. Processar documentos
docs = asyncio.run(processor.process_all_documents(Path("docs")))

# 3. Construir grafo
graph = builder.build_from_extracted_data(code_data, docs)

# 4. Detectar clusters
clusters = builder.detect_clusters_leiden()

# 5. Exportar
builder.export_as_json("knowledge-graph.json", clusters)
builder.export_as_html("knowledge-graph.html")

print(f"✓ Grafo com {len(graph.nodes())} nós, {len(graph.edges())} edges")
print(f"✓ {len(clusters)} clusters detectados")
```

### Queryando o Grafo com Token Efficiency

Agora, ao invés de enviar 123K tokens de código bruto para Claude:

```python
class GraphQueryEngine:
    def __init__(self, graph_json_path: str):
        with open(graph_json_path) as f:
            self.graph_data = json.load(f)
        self.graph = self._rebuild_graph()
    
    def _rebuild_graph(self) -> nx.Graph:
        g = nx.Graph()
        for node in self.graph_data["nodes"]:
            g.add_node(node["id"], **node)
        for edge in self.graph_data["edges"]:
            g.add_edge(edge["source"], edge["target"], **edge)
        return g
    
    def query_relevant_context(self, question: str, max_tokens: int = 2000) -> str:
        """
        Extrai APENAS contexto relevante para a pergunta
        Em vez de enviar inteiro codebase, envia apenas ~1.7K tokens
        """
        
        # 1. Buscar nós relevantes (BFS)
        keywords = question.lower().split()
        relevant_nodes = set()
        
        for node in self.graph.nodes():
            node_id_lower = str(node).lower()
            if any(kw in node_id_lower for kw in keywords):
                relevant_nodes.add(node)
        
        # 2. Expandir: incluir vizinhos (depth=2)
        expanded = set(relevant_nodes)
        for node in relevant_nodes:
            for neighbor in self.graph.neighbors(node):
                expanded.add(neighbor)
                for neighbor2 in self.graph.neighbors(neighbor):
                    expanded.add(neighbor2)
        
        # 3. Montar contexto (respeitando token limit)
        context = []
        current_tokens = 0
        
        for node in expanded:
            node_data = self.graph.nodes[node]
            node_str = f"[{node_data.get('type', 'unknown')}] {node}\n"
            
            node_tokens = len(node_str.split()) * 1.3  # Aproximação
            if current_tokens + node_tokens < max_tokens:
                context.append(node_str)
                current_tokens += node_tokens
        
        return "\n".join(context)
    
    def answer_with_context(self, question: str, client) -> str:
        """
        Query + Claude = resposta com contexto compacto
        """
        
        context = self.query_relevant_context(question, max_tokens=1700)
        
        response = client.messages.create(
            model="claude-3-5-sonnet-20241022",
            max_tokens=500,
            messages=[{
                "role": "user",
                "content": f"""Baseado neste grafo de conhecimento:

{context}

Pergunta: {question}

Responda resumidamente."""
            }]
        )
        
        return response.content[0].text

# Uso
engine = GraphQueryEngine("knowledge-graph.json")

question = "Como o módulo de autenticação interage com o banco de dados?"
answer = engine.answer_with_context(question, client)
print(answer)
```

## Stack e Requisitos

### Dependências Principais
```
python>=3.9
anthropic>=0.25.0        # API Claude
networkx>=3.0            # Grafo
tree-sitter>=0.20.1      # AST parsing
pdf2image>=1.16.3        # PDFs
pytesseract>=0.3.10      # OCR
pillow>=10.0             # Processamento imagem
leidenalg>=0.10.1        # Community detection
```

### Suporte de Linguagens (20+)
- **Código**: Python, JavaScript, TypeScript, Go, Rust, Java, C++, C#, Ruby, PHP, Swift, Kotlin
- **Markup**: Markdown, HTML, XML, JSON, YAML
- **Data**: CSV, SQL
- **Documentação**: PDF, images, text

### Hardware/Custo
- **CPU**: Qualquer (Python puro)
- **Memória**: 2-8GB (repo até 500K LOC)
- **API Anthropic**: ~$0.05-0.10 por codebase (usar Sonnet, não Opus)
- **Armazenamento**: knowledge-graph.json ~ 5-15% do tamanho original

## Armadilhas e Limitações

### 1. Token Reduction é Teórico se Query Mal Feita
Graphify reduz 71.5x IF query é bem estruturada. Query genérica: "Explique tudo" = volta a 100K+ tokens.

**Mitigação**:
```python
# ✓ BOM: Query específica
"Como a função validateUser interage com o banco de dados?"

# ✗ RUIM: Query vaga
"Explique o projeto inteiro"

# Forçar specificity
def refine_question(question: str) -> str:
    """Converte pergunta vaga em específica"""
    if len(question.split()) < 3:
        return question + " (especifique módulo/função)"
    return question
```

### 2. AST Parsing Perde Contexto Semântico
Tree-sitter vê `handlers[name]()` mas não sabe qual handler é chamado. Graphify vê sintaxe, não lógica.

**Mitigação**:
- Adicionar anotações em código: `# @calls: getUserHandler`
- Executar análise estática de tipo: `mypy` antes de Graphify
- Incluir testes que revelam relações dinâmicas

### 3. Clustering Pode Ser Ruim se Código é Caótico
Leiden detecta densidade, não intenção. Monolith mal estruturado = 1 cluster gigante.

**Mitigação**:
```python
# Validar clusters e refinar manualmente
for cluster_name, nodes in clusters.items():
    avg_type = most_common(node.get("type") for node in nodes)
    if avg_type == "function" and len(nodes) > 50:
        print(f"⚠ {cluster_name} muito grande - considere refatorar código")
```

### 4. Multimodal Não é Perfeito em Imagens Complexas
Visão do Claude é bom mas perde detalhes em screenshots com UI densa, diagramas com muitos elementos.

**Mitigação**:
- Complementar com OCR: `pytesseract` antes de enviar à Claude
- Se diagrama: preferencialmente SVG ou descrição textual
- Reviewar extrações de imagem manualmente

### 5. Documentação Pode ser Desatualizada
Se docs não são sincronizados com código, grafo tem conflitos.

**Mitigação**:
```bash
# Validação: achar discrepâncias
# Nó em docs mas não em código = feature removida
# Função em código mas não em docs = função nova/undocumented

for doc_node in doc_nodes:
    if doc_node not in code_nodes:
        print(f"⚠ Documentado mas não encontrado em código: {doc_node}")
```

## Conexões
- [[token-optimization-rag]] - Técnicas de compressão de contexto
- [[semantic-search-embeddings]] - Buscar por significado, não keyword
- [[ast-parsing-tree-sitter]] - Como Tree-sitter funciona
- [[leiden-community-detection]] - Algoritmo de clustering
- [[karpathy-llm-wiki-proposal]] - Proposta original que inspirou Graphify
- [[multimodal-vision-documents]] - Processamento de PDFs/imagens

## Histórico
- 2026-04-07: Nota criada com análise completa do pipeline de duas fases, consolidação em grafo, query optimization
