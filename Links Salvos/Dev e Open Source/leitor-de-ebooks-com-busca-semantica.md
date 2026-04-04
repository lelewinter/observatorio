---
tags: [ebooks, busca, semantica, nlp, embeddings]
date: 2026-04-02
tipo: aplicacao
---
# Implementar Leitor de E-Books com Busca Semântica

## O que é
Aplicação que carrega EPUBs/PDFs e permite busca por significado (não keyword). Ex: "explicação de gravidade" encontra seções relevantes mesmo sem a palavra "gravidade".

## Como implementar
```bash
pip install sentence-transformers langchain chromadb epub

# Processar ebook
python load_ebook.py "livro.epub"

# Busca semântica
python search.py "Como funciona a física quântica?"
```

## Stack e requisitos
- SentenceTransformers: embeddings
- ChromaDB: vector storage
- Langchain: orquestração

## Histórico
- 2026-04-02: Reescrita
