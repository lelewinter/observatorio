---
tags: [conceito, llm, rag, retrieval, generative-ai]
date: 2026-04-02
tipo: conceito
aliases: [RAG, Retrieval-Augmented Generation]
---

# RAG: Aumentar LLM com Documentos Externos (Retrieval-Augmented Generation)

## O que é

RAG combina um sistema de retrieval (busca) com LLM: primeiro encontra documentos relevantes, depois passa para LLM gerar resposta contextualizada. Melhora acurácia em dados específicos do usuário.

Pipeline típico:
1. **Indexar**: Converter documentos em embeddings, armazenar em vector DB
2. **Query**: Usuário faz pergunta
3. **Retrieve**: Buscar top-K documentos similares semanticamente
4. **Generate**: LLM responde usando documentos como contexto

## Como funciona

```python
from langchain.vectorstores import Chroma
from langchain.embeddings import OpenAIEmbeddings
from langchain.llms import OpenAI
from langchain.chains import RetrievalQA

# 1. Indexar documentos
embeddings = OpenAIEmbeddings()
vectorstore = Chroma.from_documents(
    documents=loaded_docs,
    embedding=embeddings
)

# 2. Criar retrieval QA chain
llm = OpenAI(temperature=0)
qa = RetrievalQA.from_chain_type(
    llm=llm,
    chain_type="stuff",
    retriever=vectorstore.as_retriever()
)

# 3. Fazer pergunta
response = qa.run("Qual é a política de retorno?")
# Busca documentos → passa contexto para LLM → gera resposta
```

## Para que serve

- **Conhecimento específico**: LLM treinado em internet, não em seus PDFs. RAG adiciona seu conhecimento sem treinar.
- **Atualização fácil**: Novo documento? Adicionar ao vector DB. Sem fine-tuning.
- **Reduzir alucinações**: LLM citando documentos é mais confiável que responder de memória.
- **Compliance**: Auditável (sabe qual documento gerou resposta).

Casos de uso:
- Suporte ao cliente (buscar em FAQ/knowledge base)
- Análise de documentos legais
- Assistente de documentação técnica

## Exemplo prático

```python
# Indexar documentação técnica
from langchain.document_loaders import DirectoryLoader

loader = DirectoryLoader("docs/", glob="*.md")
docs = loader.load()

# Dividir em chunks
from langchain.text_splitter import RecursiveCharacterTextSplitter
splitter = RecursiveCharacterTextSplitter(chunk_size=1000)
chunks = splitter.split_documents(docs)

# Criar vector store (local)
from langchain.vectorstores import FAISS
vectorstore = FAISS.from_documents(chunks, embeddings)

# Query
qa = RetrievalQA.from_chain_type(
    llm=OpenAI(),
    retriever=vectorstore.as_retriever(search_kwargs={"k": 5})
)

answer = qa.run("Como configuro autenticação OAuth?")
# Retorna resposta baseada em docs/authentication.md + docs/oauth.md
```

## Aparece em

- [[leitor-de-ebooks-com-busca-semantica]] - RAG para documentos
- [[web-scraping-sem-api-para-agentes-ia]] - Scraping + RAG para agentes
- [[16_github_repos_melhor_curso_ml]] - Conceito fundamental

---
*Conceito extraído em 2026-04-02*
