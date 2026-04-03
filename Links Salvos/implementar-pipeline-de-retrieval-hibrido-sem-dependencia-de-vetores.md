---
tags: []
source: https://x.com/i/status/2039665922185589044
date: 2026-04-03
tipo: aplicacao
---
# Implementar Pipeline de Retrieval Hibrido sem Dependencia de Vetores

## O que e

Vectorless RAG é uma abordagem de recuperação aumentada que abandona (ou reduz) o uso de embeddings e bancos de dados vetoriais, substituindo-os por mecanismos como BM25, SQL, grafos de conhecimento e injeção direta de contexto. O argumento central é que RAG moderno não é mais sobre *retrieval* em si, mas sobre **roteamento inteligente de queries** para o mecanismo de busca mais adequado ao tipo de dado e pergunta. Isso importa porque reduz custo de infraestrutura, elimina problemas de drift de embeddings e aumenta precisão em domínios com dados estruturados.

---

## Como implementar

### 1. Diagnóstico: qual é o seu tipo de dado?

Antes de qualquer código, você precisa classificar sua base de dados. A escolha do retriever depende disso:

- **Dados estruturados** (tabelas SQL, CSVs com schema fixo, registros) → SQL retriever ou BM25
- **Dados semi-estruturados** (JSONs, logs, documentos com campos identificáveis) → BM25 + filtros de metadados
- **Dados relacionais com entidades e conexões** (ontologias, bases de conhecimento, wikis corporativas) → Knowledge Graph (Neo4j, Wikidata-style)
- **Contexto pequeno e estável** (documentação curta, FAQ, regras de negócio) → injeção direta no system prompt (context stuffing)
- **Documentos longos e semânticos** (artigos, e-mails, transcrições) → aqui ainda faz sentido embeddings, mas combinado

### 2. Implementando BM25 como retriever principal

BM25 é o algoritmo clássico de recuperação por relevância de termos (TF-IDF melhorado). Não precisa de GPU, não precisa de modelo de embedding.

```python
# pip install rank_bm25 nltk
from rank_bm25 import BM25Okapi
import nltk
nltk.download('punkt')
from nltk.tokenize import word_tokenize

corpus = [
    "Política de reembolso para produtos físicos exige nota fiscal",
    "Cancelamento de assinatura pode ser feito pelo painel do usuário",
    "Prazo de entrega para regiões Norte é de 10 dias úteis",
]

tokenized_corpus = [word_tokenize(doc.lower()) for doc in corpus]
bm25 = BM25Okapi(tokenized_corpus)

query = "como cancelar minha assinatura"
tokenized_query = word_tokenize(query.lower())
scores = bm25.get_scores(tokenized_query)
top_n = sorted(enumerate(scores), key=lambda x: x[1], reverse=True)[:3]

results = [corpus[i] for i, _ in top_n]
print(results)
```

Para escala maior, use **Elasticsearch** ou **OpenSearch** com o campo `match` ou `multi_match`, que já implementam BM25 nativamente:

```json
GET /docs/_search
{
  "query": {
    "multi_match": {
      "query": "cancelar assinatura",
      "fields": ["titulo^2", "conteudo"],
      "type": "best_fields"
    }
  }
}
```

### 3. Implementando SQL retriever (Text-to-SQL)

Para dados em banco relacional, a abordagem é converter a pergunta do usuário em SQL usando um LLM e executar a query diretamente.

```python
# pip install langchain langchain-openai sqlalchemy
from langchain_community.utilities import SQLDatabase
from langchain_community.agent_toolkits import create_sql_agent
from langchain_openai import ChatOpenAI

db = SQLDatabase.from_uri("sqlite:///empresa.db")
llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)

agent = create_sql_agent(llm=llm, db=db, verbose=True)
response = agent.invoke("Qual foi o total de vendas em março de 2024?")
print(response["output"])
```

Para produção, adicione validação antes de executar a SQL gerada. Nunca execute queries de escrita (INSERT, DELETE, UPDATE) nesse fluxo sem revisão humana.

### 4. Implementando roteador de queries (o núcleo do sistema híbrido)

Este é o ponto central da proposta: um único ponto de entrada que distribui a query para o retriever correto. Pode ser baseado em regras, em classificação por LLM ou em intenção detectada.

```python
from enum import Enum
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from pydantic import BaseModel

class RouteDecision(BaseModel):
    retriever: str  # "bm25", "sql", "graph", "direct", "vector"
    reasoning: str

llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)
structured_llm = llm.with_structured_output(RouteDecision)

router_prompt = ChatPromptTemplate.from_messages([
    ("system", """Você é um roteador de queries para um sistema RAG híbrido.
Analise a pergunta e classifique qual retriever usar:
- 'sql': perguntas numéricas, agregações, filtros em dados estruturados
- 'bm25': perguntas sobre documentos, políticas, buscas por termos específicos
- 'graph': perguntas sobre relacionamentos entre entidades
- 'direct': perguntas respondíveis com contexto fixo já conhecido
- 'vector': perguntas semânticas, conceituais, sobre temas abstratos"""),
    ("human", "{query}")
])

router_chain = router_prompt | structured_llm

def route_query(query: str) -> RouteDecision:
    return router_chain.invoke({"query": query})

# Exemplo de uso
decision = route_query("Quantos pedidos foram feitos em janeiro?")
print(decision.retriever)  # → "sql"
```

### 5. Implementando Knowledge Graph retriever com Neo4j

Para dados com relações complexas entre entidades:

```python
# pip install langchain-neo4j
from langchain_neo4j import Neo4jGraph, GraphCypherQAChain
from langchain_openai import ChatOpenAI

graph = Neo4jGraph(
    url="bolt://localhost:7687",
    username="neo4j",
    password="sua_senha"
)

llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)
chain = GraphCypherQAChain.from_llm(
    llm=llm,
    graph=graph,
    verbose=True,
    allow_dangerous_requests=True
)

response = chain.invoke("Quais fornecedores estão conectados ao produto X?")
print(response["result"])
```

### 6. Injeção direta de contexto (context stuffing)

Para bases pequenas e estáveis (até ~100KB de texto), simplesmente injete tudo no system prompt. Com janelas de contexto de 128k tokens (GPT-4o, Claude 3.5, Gemini 1.5), isso é completamente viável:

```python
with open("faq_completo.txt", "r") as f:
    contexto_fixo = f.read()

system_prompt = f"""Você é um assistente especializado. 
Use APENAS as informações abaixo para responder:

{contexto_fixo}

Se a informação não estiver no contexto, diga que não sabe."""
```

Essa abordagem elimina completamente o retrieval — zero latência de busca, zero complexidade de indexação.

### 7. Montando o pipeline híbrido completo

```python
def hybrid_rag_pipeline(query: str) -> str:
    decision = route_query(query)
    
    if decision.retriever == "sql":
        context = sql_agent.invoke(query)["output"]
    elif decision.retriever == "bm25":
        context = "\n".join(bm25_search(query, top_k=5))
    elif decision.retriever == "graph":
        context = graph_chain.invoke(query)["result"]
    elif decision.retriever == "direct":
        context = contexto_fixo
    else:  # vector como fallback
        context = vector_store.similarity_search(query, k=5)
    
    final_prompt = f"Contexto:\n{context}\n\nPergunta: {query}"
    return llm.invoke(final_prompt).content
```

---

## Stack e requisitos

**Linguagem:** Python 3.10+

**Bibliotecas principais:**
- `rank_bm25==0.2.2` — BM25 puro, sem dependências pesadas
- `langchain==0.3.x` + `langchain-community` — orquestração dos retrievers
- `langchain-openai` — LLM para roteador e geração final
- `langchain-neo4j` — se usar Knowledge Graph
- `elasticsearch-py==8.x` ou `opensearch-py` — BM25 em escala
- `sqlalchemy` — abstração de banco relacional
- `pydantic==2.x` — estruturação de outputs do roteador

**Infraestrutura:**
- Banco SQL: PostgreSQL, SQLite (local), ou qualquer RDBMS
- Elasticsearch ou OpenSearch: mínimo 2GB RAM para instância local
- Neo4j Community Edition: gratu