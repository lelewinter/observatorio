---
tags: []
source: https://x.com/RoundtableSpace/status/2036439229748666843?s=20
date: 2026-04-02
tipo: aplicacao
---
# Implementar Roteador de Complexidade para Orquestração de Agentes

## O que é
Um modelo treinado especificamente para classificar requisições de IA por complexidade e rotear para o executor mais apropriado: modelos locais leves para tarefas simples, modelos poderosos na nuvem para raciocínio complexo. Reduz custo operacional e latência em pipelines multi-agente.

## Como implementar
**1. Arquitetura básica**: implemente um router como camada intermediária entre usuário/agente coordenador e os executores finais. O router recebe uma requisição, a processa via um modelo especializado (pode ser um SLM de 2-7B parâmetros via Ollama ou LM Studio), e emite uma classificação em formato estruturado (JSON com score de complexidade + recomendação de modelo).

**2. Critérios de classificação**: treine ou configure o router para avaliar: (a) número de etapas lógicas necessárias, (b) interdependências entre partes do problema, (c) necessidade de raciocínio multi-modal, (d) volume de contexto disponível. Tarefas com score <0.3 rodam localmente; 0.3-0.7 em SLM híbrido; >0.7 escaladas para [[Claude]] ou GPT-4o na nuvem.

**3. Integração com LangChain/AutoGen**: estenda o router como ferramenta (tool) dentro do agente orquestrador. Ao receber um prompt, o agente invoca o router, obtém a classificação e automata a escolha de executor. Exemplo em Python com LangChain:

```python
from langchain.chat_models import ChatOllama
from langchain_core.tools import tool

router_model = ChatOllama(model="mistral:7b")

@tool
def classify_task(task_description: str) -> dict:
    """Classifica complexidade da tarefa e retorna executor recomendado."""
    prompt = f"""Analise esta tarefa e responda em JSON:
    {task_description}

    Responda com: {{"complexity_score": 0-1, "executor": "local|hybrid|cloud", "reasoning": "..."}}"""

    response = router_model.invoke(prompt)
    return json.loads(response.content)

# Usar no agent
agent.add_tool(classify_task)
```

**4. Persistência e feedback**: mantenha um log de decisões (`routing_log.jsonl`) para coletar dados sobre quais roteamentos foram bem-sucedidos. Use esse histórico para realocar thresholds ou reposar o router periodicamente — criar um loop de mejora contínua.

**5. Configuração local com Ollama**: baixe `mistral:7b` ou `qwen:7b` via Ollama (`ollama pull mistral`), exponha via API local (por padrão em `http://localhost:11434`), e configure o router para usar `base_url="http://localhost:11434"` em vez de APIs remotas.

## Stack e requisitos
- **Modelo router**: Mistral 7B, Qwen 7B ou similar (via Ollama, LM Studio, ou API)
- **Executores locais**: Ollama com modelos de 2-7B (Phi, Mistral, OpenHermes)
- **Executores cloud**: chave API Claude, OpenAI GPT-4o ou similar
- **Memória**: 8GB RAM mínimo para router + 1 executor local em paralelo
- **Frameworks**: LangChain 0.1+, AutoGen 0.2+, ou custom com `requests` + `httpx`
- **Latência esperada**: router ~100-500ms em CPU; decisão adiciona <1s total

## Armadilhas e limitações
- **Misclassificação**: modelo router pode errar em casos limítrofes (0.45-0.55 de score). Mitigue com intervalo de confiança e fallback manual.
- **Overhead de latência**: invocação do router adiciona latência; compensa apenas para pipelines com >10 requisições/hora ou tarefas de longa duração.
- **Escalabilidade de contexto**: router não vê contexto completo do agente; informações críticas podem ser perdidas na classificação. Use resumos estruturados como input.
- **Dependência do modelo**: qualidade da classificação depende completamente do modelo escolhido. Um router mal treinado prejudica todo o pipeline.

## Conexões
[[Claude Code - Melhores Práticas]], [[Arquitetura de Agentes de Código Open-Source]], [[Arquitetura Multi-Agente com Avaliador Separado]], [[LangChain]], [[Ollama]], [[Mistral 7B]], [[Orquestração de Agentes]]

## Histórico
- 2026-04-02: Nota criada
- 2026-04-02: Reescrita em padrão aplicação