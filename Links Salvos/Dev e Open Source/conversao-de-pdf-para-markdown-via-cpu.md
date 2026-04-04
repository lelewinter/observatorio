---
tags: [pdf, markdown, conversao, ocr, documentos, nlp]
source: https://x.com/oliviscusAI/status/2033860465760030923?s=20
date: 2026-04-02
tipo: aplicacao
---

# Converter PDFs para Markdown a 100 Páginas/Segundo em CPU

## O que é

Ferramenta open-source (provavelmente Nougat ou similar) que converte PDFs em Markdown estruturado em CPU puro, 100 páginas/segundo. Sem GPU, ideal para pipelines RAG e ingestão de documentos.

## Como implementar

```bash
pip install nougat-ocr
# ou
pip install pymupdf fitz

# Basic usage
nougat pdf_input.pdf -o output_markdown/
```

**Python pipeline:**
```python
import pymupdf
import os

def pdf_to_markdown(pdf_path, output_dir="./output"):
    doc = pymupdf.open(pdf_path)
    os.makedirs(output_dir, exist_ok=True)

    markdown_content = []

    for page_num in range(len(doc)):
        page = doc[page_num]
        text = page.get_text("markdown")
        markdown_content.append(f"## Page {page_num + 1}\n\n{text}")

    with open(f"{output_dir}/output.md", "w", encoding="utf-8") as f:
        f.write("\n\n".join(markdown_content))

    return f"{output_dir}/output.md"

pdf_to_markdown("documento.pdf")
```

**Com tabelas:**
```python
import pymupdf
import pandas as pd

doc = pymupdf.open("documento.pdf")
for page_num, page in enumerate(doc):
    # Extrair tabelas
    tables = page.find_tables()
    for table in tables:
        df = pd.DataFrame(table.extract())
        print(df.to_markdown())
```

**Para RAG pipeline:**
```python
from langchain.document_loaders import PDFLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter

loader = PDFLoader("doc.pdf")
pages = loader.load()

splitter = RecursiveCharacterTextSplitter(
    chunk_size=1000,
    chunk_overlap=200
)
docs = splitter.split_documents(pages)

# Embeddings + vector DB
# ...
```

## Stack e requisitos

- **Nougat**: OCR/layout (opcionalmente)
- **PyMuPDF**: extração de PDF
- **Pandas**: para tabelas
- **Python**: 3.8+
- **CPU**: 2+ cores

## Armadilhas

1. **Tabelas complexas**: Podem ser extraídas como texto. Validar manualmente.
2. **Imagens**: PDFs com imagens precisam OCR (Tesseract). Nougat faz isso mas é lento.
3. **Encoding**: PDFs antigos podem ter charset issues. Forçar UTF-8.

## Conexões

- [[web-scraping-sem-api-para-agentes-ia]] - Processamento de dados web
- [[leitor-de-ebooks-com-busca-semantica]] - Indexação de documentos

## Histórico

- 2026-04-02: Nota original
- 2026-04-02: Reescrita com implementação
