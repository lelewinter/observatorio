---
tags: [ebooks, busca, semantica, nlp, embeddings, chromadb, rag]
source: https://medium.com/@bella.belgarokova_79633/mastering-chromadb-for-semantic-search-a-comprehensive-guide-875a7f42c39e
date: 2026-04-11
tipo: aplicacao
---
# Leitor de E-Books com Busca Semântica Baseada em Embeddings

## O que é

Aplicação que carrega EPUBs/PDFs, fragmenta em chunks, converte cada chunk para embedding (vetor semântico 384D ou 768D), armazena em ChromaDB (vector database), permite busca por significado em português natural. Buscas não são keyword-matching: "explicação de gravidade" encontra seções sobre relatividade geral, queda livre, orbitas—mesmo que palavra "gravidade" não apareça literalmente.

**Diferença semântica vs keyword**:
- Keyword: "como funciona motor" → encontra strings exatas "motor funciona"
- Semântica: "como funciona motor" → encontra seções sobre combustão, pistões, ciclo de Otto (conceitos relacionados, não match literal)

**Stack moderno (2026)**:
- **Embeddings**: SentenceTransformers ("all-MiniLM-L6-v2" 384D, rápido) ou "all-mpnet-base-v2" (768D, mais denso)
- **Vector DB**: ChromaDB (open-source, local, simples) ou Pinecone (cloud, escalável)
- **LLM reranking**: (opcional) reclassificar top-5 resultados com Claude/GPT para responder pergunta
- **Chunking**: simple (512 tokens + overlap 50) ou inteligente (semantic boundaries)

**Aplicações reais**:
- Ler "Designing Data-Intensive Applications" (1000 págs): pergunta "qual cache invalidation strategy" → encontra seções dispersas sobre TTL, eviction policies, consistency models
- PDF manual técnico: pergunta "como debuggar conexão lenta" → encontra troubleshooting sections mesmo se estrutura for diferente da pergunta

## Como implementar

### 1. Setup: Instalar dependências

```bash
# Python 3.10+
pip install langchain chromadb sentence-transformers pypdf ebooklib lxml

# Ou isolado em venv
python -m venv ebook_env
source ebook_env/bin/activate  # ou ebook_env\Scripts\activate no Windows
pip install -r requirements.txt
```

**requirements.txt**:
```
langchain==0.1.13
chromadb==0.4.21
sentence-transformers==2.2.2
pypdf==4.0.1
ebooklib==0.18
pydantic==2.5.0
```

### 2. Carregar EPUB/PDF

```python
from pathlib import Path
from ebooklib import epub
from pypdf import PdfReader
from langchain.text_splitter import RecursiveCharacterTextSplitter

class EbookLoader:
    def load_epub(self, filepath: str) -> str:
        """Extrair texto de EPUB"""
        book = epub.read_epub(filepath)
        text = ""
        for item in book.get_items():
            if item.get_type() == epub.ITEM_DOCUMENT:
                text += item.get_content().decode('utf-8')
        # Limpar HTML tags (básico)
        import re
        text = re.sub('<[^<]+?>', '', text)
        return text
    
    def load_pdf(self, filepath: str) -> str:
        """Extrair texto de PDF"""
        reader = PdfReader(filepath)
        text = ""
        for page in reader.pages:
            text += page.extract_text()
        return text
    
    def load(self, filepath: str) -> str:
        """Detectar tipo e carregar"""
        if filepath.endswith('.epub'):
            return self.load_epub(filepath)
        elif filepath.endswith('.pdf'):
            return self.load_pdf(filepath)
        else:
            raise ValueError(f"Format not supported: {filepath}")

# Uso
loader = EbookLoader()
text = loader.load("designing-data-intensive-apps.epub")
print(f"Carregado: {len(text)} caracteres")
```

### 3. Chunking com overlap inteligente

```python
from langchain.text_splitter import RecursiveCharacterTextSplitter

def chunk_text(text: str, chunk_size=512, overlap=50) -> list[str]:
    """
    Dividir em chunks de ~512 tokens (4 caracteres/token)
    Overlap = 50 garante contexto entre chunks
    
    Alternativa semântica (mais lenta): 
    - Detectar quebras de parágrafo, keep estrutura
    - Usar SentenceTransformers para identificar boundaries naturais
    """
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=chunk_size * 4,  # 512 tokens * ~4 chars/token
        chunk_overlap=overlap * 4,
        separators=["\n\n", "\n", ". ", " ", ""]  # Prioridade
    )
    chunks = splitter.split_text(text)
    return chunks

chunks = chunk_text(text)
print(f"Gerados {len(chunks)} chunks")
```

### 4. Gerar embeddings com SentenceTransformers

```python
from sentence_transformers import SentenceTransformer
import numpy as np

def embed_chunks(chunks: list[str], model_name="all-MiniLM-L6-v2") -> np.ndarray:
    """
    SentenceTransformers: rápido, pequeno (33MB), 384D
    Alternativa: "all-mpnet-base-v2" (429MB, 768D, mais denso)
    
    Tradeoff: velocidade vs densidade semântica
    - L6-v2: fast (50-100 chunks/sec), OK para intranets
    - mpnet: slow (10-20 chunks/sec), melhor recall
    """
    model = SentenceTransformer(model_name)
    embeddings = model.encode(
        chunks,
        convert_to_numpy=True,
        show_progress_bar=True,
        device='cuda'  # Troque 'cuda' → 'cpu' se sem GPU
    )
    return embeddings

embeddings = embed_chunks(chunks)
print(f"Embeddings shape: {embeddings.shape}")  # (n_chunks, 384)
```

### 5. Armazenar em ChromaDB

```python
import chromadb
from uuid import uuid4

def store_in_chromadb(
    chunks: list[str], 
    embeddings: np.ndarray,
    collection_name="ebook"
) -> chromadb.Collection:
    """
    ChromaDB: persistent storage em local SQLite
    Alternativa: HTTPClient para servidor remoto
    """
    client = chromadb.Client()
    
    # Criar collection (se não existir)
    collection = client.get_or_create_collection(
        name=collection_name,
        metadata={"hnsw:space": "cosine"}  # Cosine distance
    )
    
    # Adicionar documents com embeddings
    ids = [str(uuid4()) for _ in range(len(chunks))]
    collection.add(
        ids=ids,
        embeddings=embeddings.tolist(),
        documents=chunks,
        metadatas=[{"chunk_id": i, "source": "ebook"} for i in range(len(chunks))]
    )
    
    print(f"Armazenados {len(chunks)} chunks em ChromaDB")
    return collection

collection = store_in_chromadb(chunks, embeddings)
```

### 6. Busca semântica

```python
def semantic_search(
    query: str,
    collection: chromadb.Collection,
    n_results=5,
    model_name="all-MiniLM-L6-v2"
) -> list[tuple[str, float]]:
    """
    Query → embedding → kNN em ChromaDB
    Retorna top-5 chunks + distância (cosine)
    """
    model = SentenceTransformer(model_name)
    query_embedding = model.encode([query], convert_to_numpy=True)[0]
    
    results = collection.query(
        query_embeddings=[query_embedding.tolist()],
        n_results=n_results,
        include=["documents", "distances", "metadatas"]
    )
    
    # Formatar saída
    output = []
    for i, (doc, dist) in enumerate(zip(results['documents'][0], results['distances'][0])):
        relevance = 1 - dist  # Cosine distance → relevance (0-1)
        output.append((doc, relevance))
    
    return output

# Exemplo: buscas em "Designing Data-Intensive Applications"
queries = [
    "como funciona cache invalidation",
    "qual a diferença entre sharding e replicação",
    "como escalar banco de dados para 1 bilhão users"
]

for query in queries:
    print(f"\nQuery: {query}")
    results = semantic_search(query, collection)
    for i, (chunk, relevance) in enumerate(results):
        print(f"{i+1}. [{relevance:.3f}] {chunk[:100]}...")
```

### 7. RAG Opcional: Responder pergunta com LLM

```python
from anthropic import Anthropic

def query_with_llm(
    query: str,
    collection: chromadb.Collection,
    api_key: str
) -> str:
    """
    1. Buscar chunks relevantes (semantic search)
    2. Passar como contexto para Claude
    3. Claude responde baseado em contexto + knowledge
    """
    # Semantic search
    results = semantic_search(query, collection, n_results=5)
    context = "\n\n".join([chunk for chunk, _ in results])
    
    # Chamar Claude
    client = Anthropic(api_key=api_key)
    message = client.messages.create(
        model="claude-3-5-sonnet-20241022",
        max_tokens=1024,
        messages=[
            {
                "role": "user",
                "content": f"""Baseado neste contexto do livro:

{context}

Responda a pergunta: {query}

Se o contexto não tiver informação suficiente, diga "Não encontrei resposta no livro sobre isso"."""
            }
        ]
    )
    return message.content[0].text

# Uso
resposta = query_with_llm(
    "Como escalar para 1B users?",
    collection,
    api_key="sk-ant-..."
)
print(resposta)
```

### 8. Pipeline completo (script executável)

```python
#!/usr/bin/env python3
"""
Usage: python ebook_search.py --file "livro.epub" --query "sua pergunta"
"""
import argparse
from pathlib import Path
from sentence_transformers import SentenceTransformer
import chromadb

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--file", required=True, help="Caminho EPUB/PDF")
    parser.add_argument("--query", required=True, help="Pergunta semântica")
    parser.add_argument("--n-results", type=int, default=5)
    parser.add_argument("--model", default="all-MiniLM-L6-v2")
    
    args = parser.parse_args()
    
    # 1. Carregar
    loader = EbookLoader()
    text = loader.load(args.file)
    
    # 2. Chunk
    chunks = chunk_text(text)
    
    # 3. Embed
    embeddings = embed_chunks(chunks, args.model)
    
    # 4. Armazenar
    collection = store_in_chromadb(chunks, embeddings)
    
    # 5. Buscar
    results = semantic_search(args.query, collection, args.n_results, args.model)
    
    # 6. Mostrar
    print(f"\n=== Resultados para: '{args.query}' ===")
    for i, (chunk, relevance) in enumerate(results):
        print(f"\n{i+1}. Relevância: {relevance:.2%}")
        print(f"Chunk: {chunk[:200]}...")

if __name__ == "__main__":
    main()
```

## Stack e requisitos

### Hardware
- **CPU**: 2+ cores (OK em laptop)
- **RAM**: 8GB mínimo (16GB recomendado para books > 500 págs)
- **GPU**: Opcional (CUDA 11.8+, RTX 3060+ para batch embedding rápido)
- **Disco**: 10-50GB (ChromaDB SQLite + embeddings)

### Software
- **Python**: 3.10+
- **Dependencies**: sentence-transformers (33-400MB), chromadb (50MB), langchain (100MB)
- **Model**: all-MiniLM-L6-v2 (33MB) ou all-mpnet-base-v2 (429MB)
- **API** (opcional): Anthropic/OpenAI key para RAG com Claude/GPT

### Custo
- **Embeddings local**: zero (open-source)
- **ChromaDB**: zero (open-source, self-hosted)
- **LLM reranking**: $0.003-0.01 por query (Claude Haiku)

### Tempo de setup
- Instalação: 5min
- Embed livro 500 págs: 2-5 min (CPU), 30s (GPU)
- Primeira busca: 0.5-2s

## Armadilhas e limitacoes

### Armadilha 1: Chunks muito pequenos/grandes
Sintoma: busca retorna "O" (1 palavra) ou 10 páginas sem contexto
Root cause: chunk_size incomum
Fix: teste com chunk_size 256-1024 tokens. Maior = mais contexto, menos granularidade. Menor = inverso.

```python
# Testar 3 tamanhos
for size in [256, 512, 1024]:
    chunks = chunk_text(text, chunk_size=size)
    print(f"Size {size}: {len(chunks)} chunks, média {np.mean([len(c) for c in chunks]):.0f} chars")
```

### Armadilha 2: Embedding model errado para idioma
Sintoma: busca em português retorna chunks em inglês (ou vice-versa)
Root cause: modelo "all-MiniLM-L6-v2" é multilíngue mas enviesado para inglês
Fix: 
- Português: usar "sentence-transformers/distiluse-base-multilingual-cased-v2"
- Ou usar modelo específico português: "neuralmind/bert-base-portuguese-cased"

```python
# Verificar modelo
model = SentenceTransformer("distiluse-base-multilingual-cased-v2")
# Mais lento mas melhor para PT-BR
```

### Armadilha 3: Overlap insuficiente = contexto perdido
Sintoma: busca encontra chunk, mas frase começa no meio ("...blá blá")
Root cause: chunk_overlap muito pequeno (<20 tokens)
Fix: usar overlap 50-100 tokens (chunk_overlap × 4 chars/token = 200-400 caracteres)

### Armadilha 4: ChromaDB persistência perdida
Sintoma: indexa livro, fecha script, reimicia—ChromaDB está vazio
Root cause: cliente efêmero `Client()` não persiste
Fix: usar PersistentClient:

```python
# ❌ Errado
client = chromadb.Client()  # Memória

# ✅ Correto
client = chromadb.PersistentClient(path="./chromadb_data")
```

### Armadilha 5: Busca lenta com muitos chunks
Sintoma: 10k chunks (livro grande), busca leva 5s
Root cause: kNN em 10k embeddings é Θ(k × log n) sem índices
Fix: ChromaDB usa HNSW (Hierarchical Navigable Small World) por padrão, OK até 1M. Se muito lento, considerar Pinecone (cloud) ou usar batch search

### Armadilha 6: Relevance scores enganosos
Sintoma: busca retorna relevance 0.95 mas chunk é não-relacionado
Root cause: embeddings são por similaridade cosseno, não "corretude"
Fix: sempre revisar top-5 resultados, desconfiar de 0.99+, usar reranking com LLM para filtrar

```python
# Exemplo: filtrar só relevance > threshold
results = semantic_search(query, collection, n_results=10)
filtered = [(chunk, rel) for chunk, rel in results if rel > 0.6]
```

### Armadilha 7: Multilingue sem handling
Sintoma: livro mistura português/inglês, embeddings buscam só português
Root cause: modelos multilíngues não são perfeitos em mistura
Fix: detectar idioma por chunk, guardar em metadata, filtrar na busca

## Conexoes

[[explicabilidade-como-medida-de-compreensao|Explicabilidade (embedding como representação semântica)]]
[[rag-sistemas-autonomos|RAG para sistemas autônomos]]
[[chromadb-producao|ChromaDB em produção (escalá para n users)]]

## Historico
- 2026-04-11: Nota reescrita com 8 implementações code, stack moderno (Sentence-Transformers 2.2.2, ChromaDB 0.4.21), armadilhas práticas
- 2026-04-02: Nota original criada
