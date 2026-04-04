---
tags: []
source: https://x.com/ihtesham2005/status/2035009684386771306?s=20
date: 2026-04-02
tipo: aplicacao
---
# Configurar Agente de Pesquisa Profunda 100% Local

## O que é
Agente que replica Perplexity Pro inteiramente off-line via Ollama, executando ciclos iterativos de geração de queries, web scraping, sumarização e auto-crítica até produzir relatório estruturado com citações rastreáveis. Custo zero pós-setup, privacidade total, executável em hardware local.

## Como implementar
**1. Setup de infraestrutura local**: instale Ollama e baixe modelo apropriado:

```bash
# Instalar Ollama (ollama.com)
curl -fsSL https://ollama.ai/install.sh | sh

# Baixar modelo (Mistral 7B é bom balanço qualidade/velocidade)
ollama pull mistral
# ou para melhor qualidade em análise: ollama pull neural-chat

# Expor API local
ollama serve  # Roda em http://localhost:11434
```

**2. Implementação do agent loop**: crie script Python com lógica iterativa:

```python
import requests
import json
from typing import List

class LocalDeepResearcher:
    def __init__(self, model: str = "mistral", max_iterations: int = 5):
        self.model = model
        self.base_url = "http://localhost:11434/api"
        self.max_iterations = max_iterations
        self.research_log = []

    def generate_search_queries(self, topic: str, iteration: int) -> List[str]:
        """LLM gera novas queries baseado no que foi achado até aqui."""
        prompt = f"""Você está pesquisando: "{topic}"

Iteração {iteration}. Até aqui coletamos:
{json.dumps(self.research_log[-2:], ensure_ascii=False)}

Gere 3 novas queries de busca para descobrir:
1. Aspecto que ainda não foi coberto
2. Fonte que contradiz ou complementa
3. Caso de uso prático não explorado

Retorne apenas as 3 queries, uma por linha, sem numeração."""

        response = requests.post(
            f"{self.base_url}/generate",
            json={"model": self.model, "prompt": prompt, "stream": False}
        )
        queries = response.json()["response"].strip().split("\n")
        return [q.strip() for q in queries if q.strip()]

    def scrape_search_results(self, queries: List[str]) -> dict:
        """Raspa resultados (mock aqui; integre Google via SerpAPI ou similar)."""
        # Usar BeautifulSoup + requests para web scraping
        results = {}
        for q in queries:
            # Aqui integraria com Google Search ou similar
            # Por simplicidade, usando mock
            results[q] = [
                {"url": f"https://example.com/{i}", "title": f"Result {i}", "snippet": "..."}
                for i in range(3)
            ]
        return results

    def summarize_findings(self, content: str) -> str:
        """Sumariza conteúdo raspado."""
        response = requests.post(
            f"{self.base_url}/generate",
            json={
                "model": self.model,
                "prompt": f"Resuma em bullet points (máx 5 items):\n{content}",
                "stream": False
            }
        )
        return response.json()["response"]

    def evaluate_completeness(self, accumulated: str) -> dict:
        """Auto-crítica: avalia se há gaps na pesquisa."""
        response = requests.post(
            f"{self.base_url}/generate",
            json={
                "model": self.model,
                "prompt": f"""Analise a pesquisa feita até agora:
{accumulated}

Responda em JSON:
{{"completeness_score": 0-1, "gaps": ["gap1", "gap2"], "should_continue": true/false}}""",
                "stream": False
            }
        )
        return json.loads(response.json()["response"])

    def run(self, topic: str) -> str:
        """Executa loop completo de pesquisa."""
        for iteration in range(self.max_iterations):
            print(f"\n=== Iteração {iteration + 1} ===")

            # Gerar queries
            queries = self.generate_search_queries(topic, iteration)
            print(f"Queries geradas: {queries}")

            # Scrape
            results = self.scrape_search_results(queries)

            # Sumarizar
            accumulated = "\n".join([
                self.summarize_findings(json.dumps(r))
                for r in results.values()
            ])

            # Avaliar completeness
            evaluation = self.evaluate_completeness(accumulated)
            self.research_log.append({
                "iteration": iteration,
                "completeness": evaluation["completeness_score"],
                "gaps": evaluation["gaps"]
            })

            print(f"Completeness: {evaluation['completeness_score']:.2%}")
            print(f"Gaps: {evaluation['gaps']}")

            if not evaluation["should_continue"] or iteration == self.max_iterations - 1:
                break

        # Gerar relatório final
        final_report = self.generate_final_report(accumulated, topic)
        return final_report

    def generate_final_report(self, content: str, topic: str) -> str:
        """Formata saída final em Markdown estruturado."""
        response = requests.post(
            f"{self.base_url}/generate",
            json={
                "model": self.model,
                "prompt": f"""Crie um relatório estruturado sobre: {topic}

Baseado em:
{content}

Formato Markdown com:
## O Que É
## Principais Achados
## Fontes Consultadas
## Contradições Encontradas
## Próximos Passos""",
                "stream": False
            }
        )
        return response.json()["response"]

# Uso
researcher = LocalDeepResearcher(model="mistral", max_iterations=5)
report = researcher.run("Quantização de modelos de IA")
print(report)
```

**3. Integração com web scraping**: use `requests` + `BeautifulSoup` para coletar dados:

```python
from bs4 import BeautifulSoup
import requests

def scrape_url(url: str) -> str:
    """Raspa e extrai texto de uma URL."""
    try:
        response = requests.get(url, timeout=10)
        soup = BeautifulSoup(response.content, 'html.parser')
        # Remove scripts e styles
        for script in soup(["script", "style"]):
            script.decompose()
        text = soup.get_text(separator="\n")
        return "\n".join(line.strip() for line in text.split("\n") if line.strip())
    except Exception as e:
        return f"Erro ao raspar {url}: {e}"
```

**4. Persistência de dados**: salve ciclos em SQLite para análise posterior:

```python
import sqlite3

def save_iteration(db_path: str, topic: str, iteration: int, findings: dict):
    conn = sqlite3.connect(db_path)
    conn.execute("""
        INSERT INTO research (topic, iteration, queries, findings, completeness, timestamp)
        VALUES (?, ?, ?, ?, ?, datetime('now'))
    """, (topic, iteration, json.dumps(findings["queries"]),
          json.dumps(findings["summary"]), findings["completeness"]))
    conn.commit()
    conn.close()
```

**5. Integração com Obsidian**: exporte em formato compatível:

```python
def export_to_obsidian(report: str, topic: str, vault_path: str):
    """Cria nota no Obsidian com o relatório gerado."""
    note_path = f"{vault_path}/Links Salvos/Research-{topic}-{date.today()}.md"
    with open(note_path, 'w', encoding='utf-8') as f:
        f.write(f"""---
tags: [pesquisa-automatizada, {topic.lower().replace(' ', '-')}]
date: {date.today()}
---

# Pesquisa: {topic}

{report}
""")
    print(f"Nota criada em {note_path}")
```

## Stack e requisitos
- **Modelo**: Mistral 7B, Neural-Chat, DeepSeek 7B via Ollama
- **RAM**: 8-16GB (Mistral precisa ~8GB)
- **GPU** (opcional): CUDA-compatible para 2-4x speedup
- **Dependências Python**: `requests`, `beautifulsoup4`, `sqlite3`, `ollama`
- **Tempo por ciclo**: 2-5 min local vs. 30s-1min na nuvem
- **Custo**: $0 (Ollama local) vs. $20/mês (Perplexity Pro)
- **Privacidade**: 100% offline, nenhum dado sai do computador

## Armadilhas e limitações
- **Qualidade web scraping**: `BeautifulSoup` pode falhar em sites com JavaScript pesado. Integre Selenium/Playwright se necessário.
- **Falta de acesso a artigos pagos**: sem conta institucional, muitos papers estão bloqueados. Use `sci-hub` com cuidado legal.
- **Modelagem de queries**: modelo local pode gerar queries redundantes. Configure prompt para evitar reiteração.
- **Velocidade iterativa**: em CPU, cada ciclo pode levar 5+ minutos. GPU reduz a ~1 min.
- **Hallucination de URLs**: modelo pode inventar URLs credíveis. Sempre validar antes de citar.

## Conexões
[[Ollama]], [[Mistral 7B]], [[BeautifulSoup]], [[RAG com LLMs]], [[Agente de Pesquisa Científica com LLM]], [[Busca de Código Sem Índice]]

## Histórico
- 2026-04-02: Nota criada
- 2026-04-02: Reescrita em padrão aplicação