---
tags: [curadoria, open-source, ia, repositorios, github, magi-archive, tom-doerr, descoberta, automacao, indexacao-semantica]
source: https://github.com/tom-doerr/repo_posts
source-live: https://tom-doerr.github.io/repo_posts/
twitter: https://x.com/tom_doerr
date: 2026-04-11
tipo: referencia
status: ativo
---

# MAGI//ARCHIVE: Curadoria Automatizada de Repositórios Open-Source de IA

## O que é

MAGI//ARCHIVE é um sistema de descoberta e curadoria automatizada de repositórios open-source mantido por Tom Doerr (@tom_doerr). Trata-se de um "surveillance feed" da fronteira open-source que cataloga e indexa projetos emergentes em IA, agentes autônomos, automação e desenvolvimento. O site está hospedado em GitHub Pages em `https://tom-doerr.github.io/repo_posts/` e funciona como um motor de busca semântica sobre 6.500+ repositórios com embeddings.

O sistema combina **descoberta automatizada** (scanning do GitHub, repositórios em alta) com **indexação semântica** usando embeddings de sentence-transformers/all-MiniLM-L6-v2 (384 dimensões). Cada repositório descoberto vira um post com metadados, screenshot, descrição e links diretos.

Tom Doerr também mantém **awesome-dspy**, uma curadoria similar focada em exemplos e recursos de DSPy (framework de otimização para LLMs). A metodologia é a mesma: encontrar repos de qualidade, documentar, indexar para descoberta semântica.

## Por que importa agora

Você consome DEZENAS de links por dia mas o gargalo é TRIAGEM. MAGI//ARCHIVE resolve esse problema de forma diferente: em vez de você decidir que merece deep dive, Tom já fez a curadoria inicial. Cada repositório catalogado passou por filtro mínimo de qualidade e relevância.

**Aplicações práticas:**
- **Substituir busca aleatória no GitHub**: Em vez de `git clone aleatorio`, você consulta MAGI//ARCHIVE por tema (agentes, automação, IA local, etc.)
- **Descobrir padrões**: 6.500+ posts revelam que tecnologias estão emergindo (ex: em abril 2026, Claude Code plugins + LoRa mesh + WebGPU são quentes)
- **Replicar o modelo**: A arquitetura é aberta (Jekyll + GitHub Pages + embeddings). Você pode montar algo similar para **seu próprio vault** - scrapy entrada do Telegram, indexa com embeddings, disponibiliza busca semântica

## Como implementar

### Opção 1: Usar MAGI//ARCHIVE existente

1. **Browsear por tema**: o site tem archive.html com todos os posts; use Ctrl+F ou os filtros existentes
2. **RSS/Feed**: verificar se tem feed RSS em `https://tom-doerr.github.io/repo_posts/feed.xml` (padrão Jekyll)
3. **Busca semântica**: site tem índice de 6.523 posts com embeddings. Use busca de palavras-chave para encontrar "agentes", "IA local", "automação", etc.

### Opção 2: Replicar a arquitetura para seu pipeline

A stack de Tom é **transparente**:
- **Jekyll** para site estático (Ruby)
- **GitHub Pages** para hosting (automático)
- **Python para descoberta** (scrape GitHub API, classifica repos)
- **Embeddings** via `sentence-transformers/all-MiniLM-L6-v2`
- **Workflow**: push pro main → GitHub Actions compila Jekyll → publica em docs/

Para seu próprio pipeline de Telegram → Obsidian:

```python
# Pseudocodigo: estender pipeline.py com indexacao semantica
from sentence_transformers import SentenceTransformer
import json

model = SentenceTransformer('all-MiniLM-L6-v2')

def index_link(title, content, url):
    embedding = model.encode(content)  # 384-dim vector
    return {
        "url": url,
        "title": title,
        "embedding": embedding.tolist(),
        "indexed_at": datetime.now().isoformat()
    }

# Salvar embeddings em state.json ou vector DB (Weaviate, Milvus, Chroma)
# Depois fazer busca semantica: encontrar links similares sem regex
```

### Opção 3: Integração com seu vault via plugin

- **dataview**: queries dinâmicas em Links Salvos filtradas por tema
- **smart-connections**: usa embeddings locais no vault para encontrar notas relacionadas
- **obsidian-local-rest-api**: feed automático de MAGI//ARCHIVE → notas no vault

Workflow: 
1. Você vê MAGI//ARCHIVE via RSS/busca
2. Copia URL pro Telegram
3. Seu pipeline processa (resumo Claude)
4. Nota salva no vault COM embeddings
5. smart-connections conecta automaticamente com notas relacionadas

## Stack e requisitos

### Para usar MAGI//ARCHIVE existente:
- Navegador com busca (Ctrl+F no archive.html)
- Opcional: feed reader que suporte RSS
- Nada a instalar

### Para replicar a arquitetura:
- **Ruby 2.7+** (Jekyll, Bundler)
- **Python 3.8+** (descoberta de repos, embeddings)
- **GitHub Pages** (hosting gratuito)
- **sentence-transformers** (embeddings)
  ```bash
  pip install sentence-transformers torch scikit-learn
  ```
- **GitHub API** (autenticação com token PAT)
- **Vector DB** (opcional: Chroma, Weaviate, ou JSON em disco)

### Stack mínimo para indexação de seu próprio vault:
```
Links Salvos/
├── embeddings.json          # {url: string, title: string, embedding: float[384]}
├── search_index.txt         # índice de termos
└── reindex.py              # script mensal pra recalcular embeddings
```

## Armadilhas e limitações

### 1. **Descoberta enviesada pela algoritmo de Tom**
MAGI//ARCHIVE reflete o que Tom acha relevante (IA/agentes/automação), não necessariamente o que Você precisa. Se o tópico é "marketing tactics" ou "segurança", pode não estar bem representado. Usar como *ponto de partida*, não verdade universal.

### 2. **Lag de indexação**
6.500+ posts é muito, mas GitHub ainda tem milhões de repos novos por dia. Um repo interessante pode levar dias/semanas pra aparecer em MAGI//ARCHIVE (ou nunca, se Tom não achar relevante). Não substitui busca ativa no GitHub.

### 3. **Embeddings são estáticos**
Se usar embeddings all-MiniLM-L6-v2, você tá preso ao contexto desse modelo (treinado em 2021). Modelos mais novos (2024+) capturam nuances diferentes. Se você replicar, considere reindexar anualmente com modelo fresco.

### 4. **Duplicação de esforço**
Tom já catalogou 6.500 repos com thumbnails. Você catalogar os MESMOS repos no seu vault = desperdício. Solução: usar MAGI//ARCHIVE como referência externa, salvar apenas em seu vault os repos que você TESTOU/ADAPTOU pessoalmente.

### 5. **Sem feedback loop**
MAGI//ARCHIVE é one-way (Tom publica, você consome). Se você descobre um repo bom que Tom não viu, não tem como contribuir. Tom não aceita contribuições diretas no repo_posts (é curadoria pessoal). Solução: manter lista separada de "descobertas que Tom ainda não tem".

### 6. **Metadados podem ficar desatualizados**
Um repo catalogado em maio 2025 pode estar deprecated em abril 2026. MAGI//ARCHIVE não faz revalidação periódica. Sempre verificar:
- Last commit (abandonado?)
- Stars/forks (ainda crescendo?)
- Issues abertos (ativas?)
- Compatibilidade com seu setup (Python 3.14 vs 3.12?)

## Conexões

[[repositorios-github-para-claude-code]] — repos específicos para plugins/skills
[[awesome-dspy]] — curadoria similar de exemplos DSPy
[[ia-agentes-autonomos]] — contexto dos agentes em MAGI//ARCHIVE
[[indexacao-semantica-embeddings]] — como replicar a busca semântica

## Casos de uso concretos

### Seu pipeline Telegram → Obsidian poderia usar MAGI//ARCHIVE assim:

1. **Input**: Você envia link no Telegram (pode ser de qualquer fonte)
2. **Pesquisa cruzada**: seu script Python checa se URL já está em MAGI//ARCHIVE
   ```python
   if url in magi_archive:
       adiciona_tag = "magi-archive-ja-catalogado"
       adiciona_resumo_tom = fetch_from_magi(url)
   ```
3. **Output**: Nota no Obsidian com badge "Já em MAGI//ARCHIVE" + contexto do Tom como referência
4. **Economia**: você poupa tempo de pesquisa inicial, Tom fez pra você

### Ou ao contrário:

1. **Consumir MAGI//ARCHIVE regularmente** (RSS/busca semântica)
2. **Repos quentes** (trending em MAGI) → Telegram pra você revisar
3. **Você aprova** → pipeline processa → nota no vault
4. **Camada de curadoria**: Tom faz primeira pass, você faz segunda pass focada em "aplicável pra mim"

## Histórico

- **2026-04-11**: Nota criada, MAGI//ARCHIVE com 6.500+ posts, Tom Doerr mantém ativo
- **2025-2026**: Foco de Tom em agentes (Agent OS, Buildermethods), Claude Code plugins, engines WebGPU, LoRa mesh (recentes em abril 2026)
- **~2024**: Início de awesome-dspy, reputação como curator emergindo
- **2024-2025**: MAGI//ARCHIVE ganha tração, opens em 292 repos no GitHub do Tom

## Recursos

- **Site ao vivo**: https://tom-doerr.github.io/repo_posts/
- **GitHub repo**: https://github.com/tom-doerr/repo_posts
- **Tom Doerr no X/Twitter**: https://x.com/tom_doerr
- **Tom Doerr no GitHub**: https://github.com/tom-doerr (292 repos, awesome-dspy, dspy_nodes)
- **awesome-dspy repo**: https://github.com/tom-doerr/awesome-dspy

---

**Nota operacional**: MAGI//ARCHIVE é **input** pro seu pipeline, não substituto. Use pra descoberta inicial + curadoria de segunda camada. Testar repos que aparecem lá antes de salvá-los no vault.
