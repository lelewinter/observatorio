---
tags: [conceito, agents, workflow, planning, decomposition]
date: 2026-04-02
tipo: conceito
aliases: [Multi-Agent Workflow, Agent Decomposition]
---

# Multi-Agent Decomposition

## O que é

Padrão arquitetural onde uma tarefa complexa é dividida entre múltiplos agentes especializados. Cada agente tem responsabilidade bem-definida (planning, research, writing, review) e interage via mensagens, não via código acoplado.

## Como funciona

Em vez de um único agent com N tools, cria-se N agentes, cada um otimizado para um stage:

1. **Planning Agent**: Recebe task, produz plano estruturado (outline, passos)
2. **Research Agent**: Dado plano, executa busca e coleta informação
3. **Execution Agent**: Usa pesquisa para produzir artefato (escrita, código)
4. **Review Agent**: Revisa qualidade, fatos, coesão; retorna feedback

Cada agent comunica com o próximo via output do anterior. Exemplo: Planning output (JSON) → input para Research.

```
User: "Escreva livro sobre IA em Saúde"
       ↓
[Planning Agent]
output: {"title": "...", "chapters": [{"title": "Cap 1", "topics": [...]}]}
       ↓
[Research Agent]  (para cada capítulo)
output: {"chapter_id": 1, "sources": [...], "notes": "..."}
       ↓
[Writing Agent]
output: "Capítulo 1 pronto com 600-800 palavras"
       ↓
[Review Agent]
output: "Versão refinada com melhorias de prosa"
       ↓
[Aggregator]
final output: Livro completo
```

## Pra que serve

- Decompor problemas grandes que excederiam token limit de um agent
- Paralelizar: múltiplos Writing Agents podem processar capítulos em paralelo
- Especialização: cada agent tem prompt otimizado para seu role
- Erro mitigation: Review step catch erros de estágios anteriores
- [[agentes-especializados-vs-generalistas]]
- [[arquitetura-multi-agente-com-avaliador-separado]]

## Exemplo prático

```python
import json
from concurrent.futures import ThreadPoolExecutor

def planning_agent(topic: str) -> dict:
    response = client.messages.create(
        model="claude-3-5-sonnet-20241022",
        max_tokens=2000,
        messages=[{
            "role": "user",
            "content": f"""Planejar livro: {topic}

Retorne JSON:
{{"title": "...", "chapters": [{{"title": "Cap X", "topics": ["t1", "t2"]}}]}}"""
        }]
    )
    return json.loads(response.content[0].text)

def research_agent(chapter_topics: list) -> str:
    # Pesquisa cada tópico
    research = ""
    for topic in chapter_topics:
        # MCP web_search ou vector_search
        results = vector_db.search(topic, top_k=3)
        research += f"## {topic}\n" + "\n".join([r["text"] for r in results])
    return research

def writing_agent(chapter: dict, research: str) -> str:
    response = client.messages.create(
        model="claude-3-5-sonnet-20241022",
        max_tokens=4000,
        messages=[{
            "role": "user",
            "content": f"""Escreva capítulo:
Título: {chapter['title']}
Tópicos: {', '.join(chapter['topics'])}

Pesquisa:
{research}

Requisitos: 600-800 palavras, prosa clara, cite fontes."""
        }]
    )
    return response.content[0].text

def review_agent(draft: str) -> str:
    response = client.messages.create(
        model="claude-3-5-sonnet-20241022",
        max_tokens=3000,
        messages=[{
            "role": "user",
            "content": f"""Revise e refine:

{draft}

Checklist: clareza, fatos, fluxo, tom.
Retorne versão melhorada."""
        }]
    )
    return response.content[0].text

# Orquestração
outline = planning_agent("Inteligência Artificial em Saúde")
chapters = []

# Pode paralelizar aqui
with ThreadPoolExecutor(max_workers=3) as executor:
    futures = []
    for chapter in outline["chapters"]:
        research = research_agent(chapter["topics"])
        future = executor.submit(writing_agent, chapter, research)
        futures.append(future)

    for future in futures:
        draft = future.result()
        final = review_agent(draft)
        chapters.append(final)

book = "\n\n---\n\n".join(chapters)
```

## Armadilhas

- Sem sincronização, agentes podem gerar outputs incompatíveis. Sempre defina schemas JSON.
- Prompt fatigue: cada agente precisa de prompt bem-escrito. Reutilize templates.
- Custo cresce linearmente: N agents = N API calls. Batch quando possível.

## Aparece em
- [[10-projetos-mcp-agents-rag-codigo]] - Book Writer workflow
- [[agentscope-framework-multi-agente]] - Framework para multi-agents
- [[sistemas-multi-agente-para-engenharia-de-software]]

---
*Conceito extraido em 2026-04-02*
