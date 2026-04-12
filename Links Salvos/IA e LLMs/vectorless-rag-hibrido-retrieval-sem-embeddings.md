---
tags: [rag, retrieval, busca-semantica, knowledge-graph, arquitetura-dados]
source: https://x.com/dkare1009/status/2039665922185589044
date: 2026-04-03
tipo: aplicacao
---
# Vectorless RAG / Hybrid Retrieval: Recuperação sem Embeddings

## O que é

A abordagem tradicional de RAG (Retrieval-Augmented Generation) assume que você precisa de embeddings + vetores para busca semântica. Vectorless RAG ou Hybrid Retrieval descarta essa premissa. Ao invés disso, combina múltiplos métodos de recuperação nativamente: busca por keywords (BM25), queries SQL estruturadas, traversal de knowledge graphs, injeção direta de contexto. O resultado: menos custo de infraestrutura, menos problemas de chunking, e frequentemente melhor precisão porque você combina "busca exata" com "busca semântica" dinamicamente.

## Como implementar

### Passo 1: Entender o Problema com RAG Tradicional

Antes de soluções, deixa claro o que falha:

1. **Chunking quebra contexto**: Um documento dividido em chunks de 512 tokens perde coesão. Contexto que conecta chunk A com chunk B é perdido.
2. **Embedding drift**: Modelos de embedding mudam. Seu banco de vetores fica obsoleto se retraina o embedding model.
3. **Custo de infraestrutura**: Vector databases (Pinecone, Weaviate) têm custos de armazenamento + query.
4. **Misses em buscas exatas**: Um usuário pergunta "qual é o preço de X?" e RAG busca semanticamente por "valores monetários". Pode pegar dados sobre outro produto.
5. **Sem entendimento de types**: Um embedding não sabe se "2025" é um ano, preço, ou ID de produto. Contexto semântico fica plano.

### Passo 2: Arquitetura Vectorless - Multi-Retriever

Ao invés de um retriever (embeddings), use vários em paralelo:

```python
from typing import List, Dict
from abc import ABC, abstractmethod
import re
from datetime import datetime

class Retriever(ABC):
    @abstractmethod
    def retrieve(self, query: str, top_k: int = 5) -> List[Dict]:
        pass

class BM25Retriever(Retriever):
    """
    Busca por keywords com ranking BM25 (probabilístico).
    Ótimo para: termos exatos, nomes de produtos, termos técnicos.
    """
    def __init__(self, documents: List[str]):
        from rank_bm25 import BM25Okapi
        import nltk
        from nltk.tokenize import word_tokenize
        
        # Tokeniza documentos
        tokenized_docs = [word_tokenize(doc.lower()) for doc in documents]
        self.bm25 = BM25Okapi(tokenized_docs)
        self.documents = documents
    
    def retrieve(self, query: str, top_k: int = 5) -> List[Dict]:
        from nltk.tokenize import word_tokenize
        query_tokens = word_tokenize(query.lower())
        scores = self.bm25.get_scores(query_tokens)
        
        # Retorna top_k docs com scores
        top_indices = sorted(range(len(scores)), key=lambda i: scores[i], reverse=True)[:top_k]
        return [
            {
                "content": self.documents[i],
                "score": float(scores[i]),
                "method": "bm25"
            }
            for i in top_indices
        ]

class StructuredRetriever(Retriever):
    """
    Queries em banco SQL estruturado.
    Ótimo para: dados tabulares, filtros exatos, agregações.
    """
    def __init__(self, db_connection_string: str):
        import sqlite3
        self.conn = sqlite3.connect(db_connection_string)
        self.cursor = self.conn.cursor()
    
    def retrieve(self, query: str, top_k: int = 5) -> List[Dict]:
        # Parse a query para extrair entidades estruturadas
        # Ex: "produtos de preço < 100" → SELECT * FROM products WHERE price < 100
        
        # Exemplo simplificado:
        if "preço" in query.lower():
            price_match = re.search(r'(\d+)', query)
            if price_match:
                price = float(price_match.group(1))
                self.cursor.execute(
                    "SELECT name, price, description FROM products WHERE price < ? LIMIT ?",
                    (price, top_k)
                )
                results = self.cursor.fetchall()
                return [
                    {
                        "content": f"{r[0]} - ${r[1]}: {r[2]}",
                        "score": 1.0,
                        "method": "sql"
                    }
                    for r in results
                ]
        
        return []

class KnowledgeGraphRetriever(Retriever):
    """
    Traversal em knowledge graph.
    Ótimo para: relacionamentos, hierarquias, entidades e suas conexões.
    """
    def __init__(self, graph_data: Dict):
        # graph_data = {
        #     "Claude": {"type": "LLM", "creator": "Anthropic", "features": ["reasoning", "vision"]},
        #     "GPT-4": {"type": "LLM", "creator": "OpenAI", "features": ["reasoning", "vision"]},
        #     "Anthropic": {"type": "Company", "products": ["Claude"]},
        #     ...
        # }
        self.graph = graph_data
    
    def retrieve(self, query: str, top_k: int = 5) -> List[Dict]:
        # Extrai entidade mencionada
        for entity in self.graph.keys():
            if entity.lower() in query.lower():
                # Retorna o nó + seus vizinhos
                neighbors = self._get_neighbors(entity, depth=2)
                return [
                    {
                        "content": f"{entity}: {self.graph[entity]}",
                        "score": 1.0 - (depth * 0.2),  # Penaliza distância
                        "method": "knowledge_graph"
                    }
                    for entity, depth in neighbors
                ][:top_k]
        
        return []
    
    def _get_neighbors(self, entity: str, depth: int = 1) -> List[tuple]:
        """Traversa graph até depth, retorna (entity, distance)"""
        visited = set()
        queue = [(entity, 0)]
        neighbors = []
        
        while queue:
            current, dist = queue.pop(0)
            if current in visited or dist > depth:
                continue
            visited.add(current)
            neighbors.append((current, dist))
            
            # Adiciona conexões
            if current in self.graph:
                # Assume que graph[current] tem valores que são entidades
                for key, val in self.graph[current].items():
                    if isinstance(val, str) and val in self.graph:
                        queue.append((val, dist + 1))
                    elif isinstance(val, list):
                        for item in val:
                            if isinstance(item, str) and item in self.graph:
                                queue.append((item, dist + 1))
        
        return neighbors

# Uso
bm25 = BM25Retriever(["Claude is an LLM by Anthropic", "GPT-4 is made by OpenAI"])
sql_db = StructuredRetriever("products.db")
kg = KnowledgeGraphRetriever({
    "Claude": {"creator": "Anthropic"},
    "Anthropic": {"founded": 2021}
})

query = "Qual LLM é feito pela Anthropic?"
results = []
results.extend(bm25.retrieve(query, top_k=3))
results.extend(sql_db.retrieve(query, top_k=3))
results.extend(kg.retrieve(query, top_k=3))

# Dedup + ranking
final_results = rank_and_dedup(results)
```

### Passo 3: Routing - Decidir Qual Retriever Usar

Ao invés de rodar todos, use um router inteligente:

```python
class HybridRouter:
    """
    Classifica a query e rota para retriever apropriado.
    """
    def route(self, query: str) -> List[str]:
        """Retorna lista de retrievers a usar"""
        methods = []
        
        # Padrão 1: Query estruturada (contém operadores)
        if any(op in query.lower() for op in ["preço", "maior que", "menor que", "custa"]):
            methods.append("sql")
        
        # Padrão 2: Query sobre relacionamentos
        if any(word in query.lower() for word in ["criador", "empresa", "relacionado", "conexão"]):
            methods.append("knowledge_graph")
        
        # Padrão 3: Query sobre conceitos (fallback)
        methods.append("bm25")
        
        return methods

router = HybridRouter()
methods = router.route("Qual empresa fez Claude?")
# Resultado: ["knowledge_graph", "bm25"]

# Agora roda só os retrievers relevantes
for method in methods:
    if method == "bm25":
        results.extend(bm25.retrieve(query))
    elif method == "knowledge_graph":
        results.extend(kg.retrieve(query))
```

### Passo 4: Context Injection Direto (Sem Retrieval)

Às vezes você não precisa buscar — você JÁ SABE qual contexto é relevante. Injete direto:

```python
class DirectContextInjection:
    """
    Para dados que mudam frequentemente (últimas notícias, cotações),
    buscar é ineficiente. Injete direto na prompt.
    """
    def __init__(self, external_api_key: str):
        self.api_key = external_api_key
    
    def get_market_data(self) -> str:
        """Fetch dados recentes de um endpoint"""
        import requests
        resp = requests.get(
            "https://api.example.com/latest-prices",
            headers={"Authorization": f"Bearer {self.api_key}"}
        )
        data = resp.json()
        return f"Latest market prices: {data}"
    
    def inject_into_prompt(self, user_query: str) -> str:
        """Cria prompt com contexto injetado"""
        market_data = self.get_market_data()
        
        augmented_prompt = f"""
Você é um assistente financeiro.
Contexto de mercado (atualizado em tempo real):
{market_data}

Pergunta do usuário: {user_query}

Responda baseado no contexto acima. Se informação não for relevante, ignore.
"""
        return augmented_prompt

injector = DirectContextInjection("api_key_here")
prompt = injector.inject_into_prompt("Como está o preço do Bitcoin?")
# Agora chame Claude com prompt augmentado
```

### Passo 5: Integração com Claude API

```python
from anthropic import Anthropic

class VectorlessRAG:
    def __init__(self):
        self.client = Anthropic()
        self.bm25 = BM25Retriever([...])
        self.sql = StructuredRetriever("db.sqlite")
        self.kg = KnowledgeGraphRetriever({...})
        self.router = HybridRouter()
    
    def query(self, user_question: str) -> str:
        # 1. Rota para retrievers apropriados
        methods = self.router.route(user_question)
        
        # 2. Recupera contexto
        context_pieces = []
        for method in methods:
            if method == "bm25":
                context_pieces.extend(self.bm25.retrieve(user_question))
            elif method == "sql":
                context_pieces.extend(self.sql.retrieve(user_question))
            elif method == "knowledge_graph":
                context_pieces.extend(self.kg.retrieve(user_question))
        
        # 3. Formata contexto
        context_str = "\n".join([f"[{piece['method']}] {piece['content']}" for piece in context_pieces])
        
        # 4. Aumenta prompt
        system_prompt = f"""You are a helpful assistant. Use the context below to answer questions.

Retrieved Context:
{context_str}

Important: If context doesn't answer the question, say so rather than guessing."""
        
        # 5. Chama Claude
        response = self.client.messages.create(
            model="claude-3-5-sonnet-20241022",
            max_tokens=1024,
            system=system_prompt,
            messages=[
                {"role": "user", "content": user_question}
            ]
        )
        
        return response.content[0].text

# Uso
rag = VectorlessRAG()
answer = rag.query("Qual é o preço de produtos com menos de 50 reais da Anthropic?")
```

## Stack e requisitos

- **Bibliotecas Python**:
  - `rank-bm25` — BM25 retrieval
  - `sqlite3` — banco SQL estruturado (ou PostgreSQL, MySQL)
  - `networkx` — knowledge graph manipulation
  - `anthropic` — Claude API
  - Opcional: `neo4j` se usar graph DB profissional

- **Armazenamento**:
  - **BM25**: Índice em memória (RAM) ou arquivo. ~100k documentos = 500MB.
  - **SQL**: Qualquer banco relacional. SQLite (file) para small data, PostgreSQL para production.
  - **Knowledge Graph**: Em-memory dict (pequeno) ou Neo4j (escalável).

- **Hardware**: CPU suficiente. Nenhuma exigência de GPU.

- **Custo**: 
  - BM25 + SQL + KG = zero custo extra (open-source)
  - Claude API = ~$0.003 por query (input: 1k tokens, output: 100 tokens)
  - Sem custo de vector database (Pinecone, Weaviate) = 80% economia comparado a RAG tradicional

- **Tempo setup**: 2-4 horas para implementar os 3 retrievers + router básico.

- **Escalabilidade**:
  - BM25: até 1M documentos em memória (com otimizações, até 10M)
  - SQL: depende do banco (PostgreSQL: 1B+ linhas)
  - Knowledge Graph: até 100k entidades com traversal rápido

## Armadilhas e limitações

### Armadilha 1: Completude de dados
Se dados estruturados (SQL) não existem, você não consegue recuperá-los via StructuredRetriever. Se knowledge graph não foi construído, traversal falha. **Mitigação**: Hibridize. Sempre tenha BM25 como fallback.

### Armadilha 2: Qualidade de parsing
O router depende de heurísticas (regex, keyword matching) para rotear. Queries ambíguas são roteadas errado. Exemplo: "Claude é um navio?" — pode ser roteado para knowledge graph buscando a entidade "Claude" sem saber que é um navio, não LLM. **Mitigação**: Use LLM pequeno para classificação de queries antes de rotear (custo: ~0.001 por query em Claude API).

### Pitfall técnico 3: Manutenção de knowledge graph
Construir e manter KG é custoso. Precisa de curadoria humana ou NLP avançado para extração automática. **Mitigação**: Use KG apenas para domínios bem-definidos (ex: catálogo de produtos já estruturado).

### Pitfall técnico 4: Ranking entre métodos diferentes
BM25 retorna scores [0, 1], SQL retorna apenas relevância booleana, KG retorna distância de graph. Como comparar e rankear junto? **Mitigação**: Normalize scores de cada método antes de combinar. Use score = relevância_método / max_relevância_método.

### Armadilha 5: Sem semântica profunda
Vectorless RAG é excelente para dados estruturados e exatos, mas fraco em nuance. Pergunta: "Qual ferramenta é melhor para iniciantes?" — palavra "melhor" é vaga, "iniciantes" é contextual. Embeddings capturavam esse vagueness. **Mitigação**: Combine com embeddings leves (um modelo pequeno como sentence-transformers) para queries sobre preferências/comparações.

### Pitfall técnico 6: Atualização lenta de índices
BM25 precisa ser reindexado quando documentos mudam. SQL pode ser atualizado live, mas KG não. Se seu conhecimento muda frequentemente, você fica desatualizado. **Mitigação**: Para dados em tempo real (preços, notícias), use DirectContextInjection ao invés de retrieval.

## Conexões

[[RAG Tradicional vs Vectorless - Comparativo]] - quando usar cada um
[[Knowledge Graphs - Construção e Manutenção]] - como estruturar dados relacionais
[[BM25 e Busca Lexical]] - fundamentos de busca por keywords
[[SQL Query Optimization]] - escalabilidade de structured retrieval
[[Hybrid Search - Combinando Múltiplos Métodos]] - arquitetura de multi-retriever
[[LLMs em Produção - Retrieval e Inference]] - deployment de RAG sem vetores

## Histórico

- 2026-04-03: Nota criada com implementação completa de 3 retrievers (BM25, SQL, Knowledge Graph), router inteligente, e integração com Claude API