---
tags: []
source: https://x.com/i/status/2039805659525644595
date: 2026-04-03
tipo: aplicacao
---
# Construir Base de Conhecimento Pessoal com LLM, Obsidian e Markdown

## O que e

Andrej Karpathy descreve um sistema pessoal onde LLMs constroem e mantêm automaticamente uma wiki em markdown a partir de documentos brutos (papers, artigos, repositórios), permitindo consultas em linguagem natural sobre o corpus acumulado. A ideia central é deslocar o esforço humano da manipulação de código e infraestrutura para a curadoria de conhecimento estruturado. O resultado prático é um segundo cérebro consultável que cresce incrementalmente sem exigir RAG clássico em escala pequena/média.

## Como implementar

**1. Estrutura de diretórios base**

Crie um vault no Obsidian com a seguinte estrutura mínima:

```
vault/
├── raw/           ← documentos fonte originais (.md, .pdf, imagens)
├── wiki/          ← arquivos gerados e mantidos pelo LLM
│   ├── conceitos/ ← uma nota por conceito técnico identificado
│   ├── papers/    ← resumos estruturados de cada paper/artigo
│   └── index.md   ← índice mestre gerado pelo LLM
├── outputs/       ← slides Marp, gráficos matplotlib, relatórios
└── prompts/       ← seus prompts reutilizáveis para o LLM
```

Todo documento novo entra em `raw/`. O LLM nunca toca em `raw/`; apenas lê. Toda escrita do LLM vai para `wiki/` e `outputs/`. Essa separação é crítica para rastreabilidade.

**2. Ingestão de documentos brutos**

Instale o [Obsidian Web Clipper](https://obsidian.md/clipper) no navegador. Configure-o para salvar diretamente em `raw/` do seu vault local. Para artigos acadêmicos, use ferramentas como `arxiv-downloader` ou o próprio curl para baixar PDFs e converta para markdown com `marker` (biblioteca Python) ou `pandoc`:

```bash
pip install marker-pdf
marker_single paper.pdf output_dir/ --langs English
```

Para repositórios GitHub relevantes, gere um dump textual com ferramentas como `gitingest` ou `repo2txt`, que concatenam todos os arquivos relevantes em um único `.md` ou `.txt` depositado em `raw/`.

**3. Pipeline de compilação da wiki (o coração do sistema)**

Este é o passo principal. Você vai criar um prompt de sistema que instrui o LLM a agir como "editor da wiki". O fluxo é:

- Você aponta novos arquivos em `raw/` para o LLM (via contexto ou tool use)
- O LLM gera/atualiza arquivos em `wiki/papers/` com resumo estruturado, links para conceitos relacionados e backlinks
- O LLM atualiza `wiki/conceitos/` adicionando o novo paper como referência em conceitos já existentes ou criando novos arquivos de conceito
- O LLM atualiza `wiki/index.md`

Prompt base reutilizável para a etapa de ingestão:

```
Você é o editor desta wiki técnica. Dado o documento em <raw>, execute:
1. Crie wiki/papers/<slug>.md com: título, autores, data, problema,
   método, resultados, limitações, conexões com outros papers já na wiki.
2. Para cada conceito técnico central identificado, atualize ou crie
   wiki/conceitos/<conceito>.md adicionando este paper como referência.
3. Adicione entrada em wiki/index.md.
4. Use [[wikilinks]] internos em todos os arquivos gerados.
Formato de saída: um bloco de código por arquivo, com o caminho como header.
```

Execute isso com qualquer LLM de janela de contexto longa (Claude 3.5/3.7, GPT-4o, Gemini 1.5/2.0 Pro) que consiga receber o documento bruto + a wiki atual como contexto.

**4. Automação incremental com script Python**

Para não fazer isso manualmente toda vez, construa um script simples de orquestração:

```python
import os
import anthropic  # ou openai, google.generativeai

VAULT = "/caminho/para/vault"
RAW_DIR = f"{VAULT}/raw"
WIKI_DIR = f"{VAULT}/wiki"

client = anthropic.Anthropic()

def get_wiki_context():
    """Lê todos os .md da wiki para passar como contexto."""
    context = ""
    for root, _, files in os.walk(WIKI_DIR):
        for f in files:
            if f.endswith(".md"):
                path = os.path.join(root, f)
                rel = os.path.relpath(path, VAULT)
                with open(path) as fh:
                    context += f"\n\n--- FILE: {rel} ---\n{fh.read()}"
    return context

def ingest_document(raw_path: str):
    with open(raw_path) as fh:
        doc = fh.read()
    wiki_ctx = get_wiki_context()
    prompt = f"""...(seu prompt de ingestão aqui)...
    
<wiki_atual>
{wiki_ctx}
</wiki_atual>

<raw>
{doc}
</raw>"""
    
    response = client.messages.create(
        model="claude-opus-4-5",
        max_tokens=8096,
        messages=[{"role": "user", "content": prompt}]
    )
    # Parse e salve os arquivos gerados
    parse_and_write(response.content[0].text)
```

Adicione parsing do output para extrair cada bloco de arquivo e salvá-lo no caminho correto. Uma abordagem robusta é pedir ao LLM que retorne JSON com `{"caminho": "...", "conteudo": "..."}` para cada arquivo a criar/atualizar.

**5. Sistema de Q&A sobre a wiki**

Quando a wiki atingir massa crítica (~50-100 artigos), você pode fazer perguntas complexas diretamente. A abordagem do Karpathy evita RAG clássico: em vez de embeddings + vector store, o LLM recebe a wiki inteira (ou os arquivos de índice + conceitos) e raciocina sobre ela. Isso funciona bem até ~400k palavras, que cabe confortavelmente em modelos com janela de 1M tokens (Gemini 2.0 Pro, Claude 3.7 com extended context).

Prompt de Q&A:

```
Você é um assistente especializado nesta base de conhecimento técnica.
Abaixo está a wiki completa. Responda a pergunta com:
- Resposta direta e técnica
- Fontes: quais papers/conceitos da wiki embasam a resposta
- Lacunas: o que a wiki não cobre e que seria relevante pesquisar

<wiki>
{wiki_context}
</wiki>

Pergunta: {user_question}
```

**6. Health checks e linting da wiki**

Periodicamente (semanal ou quinzenal), rode um "lint" da wiki com um prompt dedicado:

```
Analise esta wiki e retorne:
1. Conceitos mencionados sem nota própria em wiki/conceitos/ (links quebrados)
2. Papers sem backlinks de nenhum conceito (órfãos)
3. Contradições ou inconsistências entre notas
4. 5 conexões não óbvias entre papers que merecem uma nota nova
5. 3 tópicos que a wiki deveria cobrir mas não cobre ainda
```

Use a saída para alimentar sua lista de curadoria: novos artigos para buscar, notas para enriquecer.

**7. Geração de outputs derivados**

Para slides: use o plugin [Marp for VS Code](https://marketplace.visualstudio.com/items?itemName=marp-team.marp-vscode) ou o Marp CLI. Peça ao LLM para gerar um arquivo `.md` com frontmatter Marp a partir de uma seção da wiki:

```bash
npm install -g @marp-team/marp-cli
marp wiki/outputs/apresentacao.md --pdf
```

Para visualizações: instrua o LLM a gerar scripts matplotlib salvos em `outputs/`, que você executa localmente. Archive os `.png` resultantes de volta em `wiki/` para que apareçam nas notas via `![[imagem.png]]`.

## Stack e requisitos

**LLMs recomendados (por caso de uso):**
- Ingestão e compilação de wiki: Claude 3.7 Sonnet/Opus, GPT-4o, Gemini 2.0 Pro
- Q&A com contexto longo (>200k tokens): Gemini 2.0 Pro (1M tokens), Claude 3.7 com extended thinking
- Health checks (tarefa mais simples): Claude 3.5 Haiku ou GPT-4o-mini para reduzir custo

**Ferramentas e bibliotecas:**
- Python 3.10+
- `anthropic` >= 0.25, `openai` >= 1.30 ou `google-generativeai` >= 0.5
- `marker-pdf` para conversão de PDF → markdown
- `pandoc` para conversões gerais de formato
- Obsidian (gratuito) + Obsidian Web Clipper (extensão de browser, gratuita)
- Plugin Marp para Obsidian ou Marp CLI (`npm`)
- `matplotlib` para geração de gráficos via LLM