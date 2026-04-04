---
tags: [conceito, skills, workflows, composição, reutilização]
date: 2026-04-02
tipo: conceito
aliases: [Skill Composition, Workflow Chaining]
---

# Skill-Workflow Composition

## O que é

Padrão de encadear múltiplos skills estruturados em sequência, onde output de um skill vira input de outro. Permite construir pipelines complexos reutilizando componentes testados pela comunidade.

## Como funciona

Cada skill tem contrato bem-definido:
- Input schema: tipos, campos obrigatórios
- Output schema: format (JSON, markdown, CSV)
- Execução: determinística (mesmo input = mesmo output)

Composição conecta skills via interface:

```
[Código]
   ↓
[Skill 1: Code Review]
Output: JSON com achados
   ↓
[Skill 2: Generate Tests]
Input: Código + achados review
Output: Suite de testes
   ↓
[Skill 3: Documentation]
Input: Código + review + tests
Output: Documentação estruturada
```

**Variações:**
- **Pipeline linear**: A → B → C (sequencial)
- **Parallel**: A, B executam em paralelo, C espera ambas
- **Branching**: Se A return error, use skill alternativo B
- **Looping**: Até condição, refaz A

## Pra que serve

- Automatizar workflows repetitivos (code review → test generation → docs)
- Reutilizar componentes testados (não reescrever prompt)
- Escalar análises complexas (1 pessoa roda múltiplos skills)
- Reduzir erro humano (skill é determinístico)
- [[450_skills_workflows_claude]]
- [[code-review-checklist-3-fases-claude-code]]
- [[agentes-de-codigo-para-robotica]]

## Exemplo prático

```python
# Composição de skills: Research → Analysis → Report

class ResearchPipeline:
    def __init__(self, client):
        self.client = client

    def run(self, topic: str, depth: str = "medium"):
        # Skill 1: Gather sources
        sources = self.client.run_skill(
            "literature-search",
            inputs={"topic": topic, "depth": depth}
        )
        # Output: [{"title": "...", "url": "...", "abstract": "..."}]

        # Skill 2: Extract key points
        summaries = self.client.run_skill(
            "paper-summarizer",
            inputs={"papers": sources, "max_length": 500}
        )
        # Output: [{"paper_id": "...", "summary": "..."}]

        # Skill 3: Correlate findings
        correlations = self.client.run_skill(
            "find-contradictions-patterns",
            inputs={"summaries": summaries}
        )
        # Output: {"patterns": [...], "contradictions": [...]}

        # Skill 4: Generate report
        report = self.client.run_skill(
            "research-report-generator",
            inputs={
                "topic": topic,
                "sources": sources,
                "summaries": summaries,
                "correlations": correlations,
                "tone": "academic"
            }
        )
        # Output: Markdown documento com 5-10 páginas

        return report

# Uso
pipeline = ResearchPipeline(claude_client)
report = pipeline.run("LLM safety mechanisms", depth="deep")
print(report)
```

**Exemplo com error handling:**

```python
def pipeline_with_fallback(code, language):
    try:
        # Skill 1: Code Review
        review = client.run_skill("code-review", {"code": code})
    except SkillError:
        # Fallback: simple analysis
        review = client.run_skill("simple-lint", {"code": code})

    try:
        # Skill 2: Generate Tests
        tests = client.run_skill("test-gen", {"code": code, "review": review})
    except:
        # Fallback: manualmente pedir ao user
        tests = input("Provide tests manually: ")

    # Skill 3 sempre roda
    docs = client.run_skill("doc-gen", {"code": code, "tests": tests})

    return {"code": code, "tests": tests, "docs": docs}
```

## Armadilhas

- **Version mismatch**: Skill A atualiza output schema, Skill B quebraecer.
  Solução: use schema validation, semantic versioning
- **Latency**: Cada skill ~10s, pipeline de 5 skills = 50s.
  Solução: paralelizar quando possível
- **Cost explosion**: 5 skills × $0.10 = $0.50 por run.
  Solução: cache intermediários, batch processing
- **Context loss**: Output de A pode ser resumido demais para C usar.
  Solução: preservar contexto em objeto estruturado, não texto simples

## Aparece em
- [[450_skills_workflows_claude]] - Biblioteca de skills
- [[code-review-checklist-3-fases-claude-code]] - Skill de review em 3 fases
- [[agentes-de-codigo-para-robotica]] - Agentes usando skills

---
*Conceito extraido em 2026-04-02*
