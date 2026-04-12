---
tags: [multi-agente, software-engineering, orchestration, swe-agent, openhands, devin, autonomous-coding]
source: https://localaimaster.com/blog/openhands-vs-swe-agent | https://arxiv.org/abs/2407.16741 | https://openreview.net/forum?id=mXpq6ut8J3
date: 2026-04-02
tipo: aplicacao
---

# Sistemas Multi-Agente para Engenharia de Software: SWE-Agent, OpenHands & Devin (2026)

## O que é

Sistemas multi-agente para engenharia de software são arquiteturas onde **múltiplos agentes especializados** colaboram em um pipeline de desenvolvimento. Em vez de um único LLM genérico atacando problema completo, cada agente tem responsabilidade circunscrita:

- **Planner**: Break down feature em subtarefas
- **Coder**: Implementa código
- **Reviewer**: Valida lógica, segurança, estilo
- **Tester**: Escreve e roda testes
- **Security Auditor**: Busca vulnerabilidades
- **Documenter**: Gera docs + comentários

Arquiteturas abertas (**OpenHands**) e pesquisa (**SWE-Agent**) dominam 2026; a abordagem comercial proprietary (Devin da Cognition) é closed-source.

## Por que importa agora

1. **Redução de custo de tokens**: Delegação eficiente reduz re-prompting. Estudo: **60% economia de tokens** comparado a prompting genérico.

2. **Qualidade & segurança**: Especialização melhora resultado. Agente de segurança detecta vulnerabilidades **no código escrito**, não pós-deploy.

3. **Automation de rotina**: Feature planning, refactoring, testes podem ser automatizados completamente. Desenvolvedores focam em criatividade.

4. **Escalabilidade**: Arquitetura multi-agente escala em N agentes paralelos. Grandes repos processados via delegação de módulos.

Leticia está em mestrado; automação de boilerplate (testes, docs) acelera projeto.

## Como implementar

### 1. Arquitetura Base: Planejador → Executor → Revisor

```python
from typing import List, Dict
from dataclasses import dataclass
import json

@dataclass
class Task:
    id: str
    description: str
    assigned_to: str
    status: str  # pending, in_progress, completed, failed
    output: str = ""
    dependencies: List[str] = None

class SoftwareEngineeringOrchestrator:
    """Orquestrador de agentes especializados."""
    
    def __init__(self, llm_client):
        self.llm = llm_client
        self.tasks: Dict[str, Task] = {}
        self.agents = {
            "planner": PlanningAgent(llm_client),
            "coder": CodingAgent(llm_client),
            "reviewer": ReviewAgent(llm_client),
            "tester": TestingAgent(llm_client),
            "security": SecurityAgent(llm_client),
        }
    
    def plan_feature(self, feature_description: str) -> List[Task]:
        """Etapa 1: Planejador quebra feature em subtarefas."""
        
        plan_prompt = f"""
        Você é um planejador de software. Dado uma feature, quebre em subtarefas atômicas.
        
        Feature: {feature_description}
        
        Retorne JSON com array de tasks:
        {{
            "tasks": [
                {{"id": "plan_1", "type": "design", "description": "...", "assigned_to": "coder"}},
                {{"id": "plan_2", "type": "implement", "description": "...", "assigned_to": "coder"}},
                ...
            ]
        }}
        """
        
        response = self.llm.generate(plan_prompt)
        parsed = json.loads(response)
        
        # Criar Tasks
        for task_data in parsed['tasks']:
            task = Task(
                id=task_data['id'],
                description=task_data['description'],
                assigned_to=task_data.get('assigned_to', 'coder'),
                status='pending'
            )
            self.tasks[task.id] = task
        
        return list(self.tasks.values())
    
    def execute_task(self, task: Task) -> Task:
        """Executar tarefa com agente apropriado."""
        
        agent = self.agents.get(task.assigned_to)
        if not agent:
            raise ValueError(f"Agent {task.assigned_to} not found")
        
        task.status = "in_progress"
        try:
            output = agent.execute(task.description)
            task.output = output
            task.status = "completed"
        except Exception as e:
            task.status = "failed"
            task.output = str(e)
        
        return task
    
    def run_pipeline(self, feature_description: str) -> Dict:
        """Rodar pipeline completo."""
        
        # 1. Planejar
        print("[PLANNING] Quebrando feature em subtarefas...")
        tasks = self.plan_feature(feature_description)
        
        # 2. Executar tarefas (respeitando dependências)
        for task in tasks:
            print(f"[{task.assigned_to.upper()}] {task.description}")
            self.execute_task(task)
        
        # 3. Revisar código e segurança
        code_output = self.tasks.get('plan_2', Task('', '', '', '')).output
        
        print("[REVIEW] Revisando código...")
        review_feedback = self.agents['reviewer'].execute(code_output)
        
        print("[SECURITY] Auditando segurança...")
        security_issues = self.agents['security'].execute(code_output)
        
        # 4. Corrigir se necessário
        if security_issues:
            print("[CODER] Corrigindo vulnerabilidades...")
            code_output = self.agents['coder'].fix_security(code_output, security_issues)
        
        return {
            'tasks': self.tasks,
            'final_code': code_output,
            'review_feedback': review_feedback,
            'security_issues': security_issues
        }

# Agentes especializados (stubs)
class PlanningAgent:
    def __init__(self, llm):
        self.llm = llm
    
    def execute(self, description: str):
        # Planejar quebra feature
        return "Plan: [task list]"

class CodingAgent:
    def __init__(self, llm):
        self.llm = llm
    
    def execute(self, description: str):
        # Implementar código
        return "def my_function():\n    pass"
    
    def fix_security(self, code: str, issues: List[str]):
        # Corrigir vulnerabilidades
        return code

class ReviewAgent:
    def __init__(self, llm):
        self.llm = llm
    
    def execute(self, code: str):
        # Revisar código
        return "Feedback: [...]"

class TestingAgent:
    def __init__(self, llm):
        self.llm = llm
    
    def execute(self, code: str):
        # Escrever testes
        return "def test_my_function(): assert ..."

class SecurityAgent:
    def __init__(self, llm):
        self.llm = llm
    
    def execute(self, code: str):
        # Auditoria de segurança
        return ["SQLi in line 45", "XSS in line 67"]
```

### 2. Integração Real: OpenHands (2026)

OpenHands (fork de OpenDevin) é a solução open-source mais madura. Arquitetura:

```
┌─────────────────┐
│   User Input    │
│   (Chat/Code)   │
└────────┬────────┘
         │
    ┌────▼─────────────────┐
    │  AgentOrchestrator    │
    │  (LangGraph)          │
    └────┬──────────────────┘
         │
    ┌────┴─────────────────────────────────┐
    │                                        │
┌───▼───┐  ┌────────┐  ┌───────┐  ┌────────▼──┐
│CodeAct│  │Browser │  │Shell  │  │FileSystem │
│Agent  │  │Agent   │  │Agent  │  │Agent      │
└───┬───┘  └───┬────┘  └──┬────┘  └────┬──────┘
    │          │          │            │
    └──────────┴──────────┴────────────┘
              │
      ┌───────▼────────┐
      │  Tool Layer    │
      │ (Git, Docker)  │
      └────────────────┘
```

**Instalação & Setup**:

```bash
# Clonar repositório
git clone https://github.com/All-Hands-AI/OpenHands.git
cd OpenHands

# Instalar dependências
pip install -e ".[core]"

# Configurar LLM (suporta Claude, GPT-4, Gemini, Ollama, etc.)
export LLM_MODEL=claude-opus-4.6
export ANTHROPIC_API_KEY=sk-ant-...

# Rodar interface web
python -m openhands.server
```

**Uso programático**:

```python
from openhands.core.main import AgentFactory
from openhands.events.action import CmdRunAction, FileReadAction

# Criar agente
agent = AgentFactory.create_agent(
    agent_cls="CodeActAgent",
    llm_config={
        "model": "claude-opus-4.6",
        "api_key": "sk-ant-...",
    }
)

# Dar tarefa
response = agent.execute(
    task="Implement a function that converts CSV to JSON, then write tests for it."
)

# Agente executa automaticamente:
# 1. Escreve função
# 2. Salva em arquivo
# 3. Escreve testes
# 4. Roda testes
# 5. Itera se falhar
```

### 3. SWE-Agent vs OpenHands: Diferenças

| Aspecto | SWE-Agent | OpenHands |
|---------|-----------|-----------|
| **Tipo** | Research (benchmark) | Production-ready |
| **Licença** | MIT | MIT |
| **Agent-Computer Interface** | Novel (inovador) | LangGraph standard |
| **Suporte multi-modelo** | Claude, GPT-4 | 20+ modelos |
| **Multi-agente** | Não (single CodeActAgent) | Sim (delegação) |
| **Performance (SWE-Bench)** | 48% (Sonnet) | 72% (Claude 4.6) |
| **Deploy** | Local/Linux | Local/Docker/Cloud |

**SWE-Agent Interface** (sua inovação):

```python
# SWE-Agent: abstração de "agent-computer interface"
# Permite LLM executar:
# - bash: run any shell command
# - grep: search files
# - find: locate files
# - edit: modify code
# Tudo através de "actions" estruturadas, não texto livre

from swe_agent import AgentInterface

interface = AgentInterface()

# Agente vê output estruturado de cada ação
actions = [
    "find . -name '*.py' -type f",  # Encontrar arquivos Python
    "grep -n 'def get_user' src/",  # Procurar função
    "cat src/user.py",              # Ler arquivo
]

for action in actions:
    output = interface.execute(action)
    print(f"Output: {output}")
```

### 4. Orquestração com LangGraph (OpenHands style)

```python
from langgraph.graph import StateGraph
from typing import TypedDict

class AgentState(TypedDict):
    feature_description: str
    plan: str
    code: str
    tests: str
    review: str
    security_audit: str

def planning_node(state: AgentState):
    """Nó de planejamento."""
    plan = planner_llm(state['feature_description'])
    return {"plan": plan}

def coding_node(state: AgentState):
    """Nó de codificação."""
    code = coder_llm(state['plan'])
    return {"code": code}

def testing_node(state: AgentState):
    """Nó de testes."""
    tests = tester_llm(state['code'])
    return {"tests": tests}

def review_node(state: AgentState):
    """Nó de revisão."""
    review = reviewer_llm(state['code'])
    return {"review": review}

def security_node(state: AgentState):
    """Nó de segurança."""
    audit = security_llm(state['code'])
    return {"security_audit": audit}

# Construir grafo
graph = StateGraph(AgentState)
graph.add_node("plan", planning_node)
graph.add_node("code", coding_node)
graph.add_node("test", testing_node)
graph.add_node("review", review_node)
graph.add_node("security", security_node)

# Conectar nós
graph.add_edge("plan", "code")
graph.add_edge("code", "test")
graph.add_edge("code", "review")
graph.add_edge("code", "security")

# Security pode levar a retry do coder
def route_after_security(state):
    if "critical" in state['security_audit']:
        return "code"  # Voltar ao coder
    return "END"

graph.add_conditional_edges("security", route_after_security)

# Compilar e rodar
runnable = graph.compile()
result = runnable.invoke({
    'feature_description': 'Implement user authentication with JWT'
})

print(result['code'])
print(result['security_audit'])
```

## Stack e requisitos

### Ferramentas essenciais

- **Claude API** (recomendado) ou **GPT-4**: LLM base para agentes.
- **OpenHands**: Framework (https://github.com/All-Hands-AI/OpenHands)
- **LangGraph**: Orquestração (pip install langgraph)
- **LangChain**: Base de ferramentas (pip install langchain)
- **Docker**: Isolamento de execução (recomendado)
- **Git**: Versionamento (assume repositório git)

### Infraestrutura

```bash
# Minimal setup: local no laptop
pip install openhands langgraph langchain anthropic

# Production: Docker container
docker run -e ANTHROPIC_API_KEY=sk-ant-... \
           -e LLM_MODEL=claude-opus-4.6 \
           -p 3000:3000 \
           openhands:latest

# Scale: Kubernetes (para 10+ agentes paralelos)
kubectl apply -f openhands-deployment.yaml
```

### Modelo & contexto

| Modelo | Janela de contexto | Custo/token | Suporte multi-agente |
|--------|-----|------|---|
| Claude 3.5 Sonnet | 200k | €0.003 | Bom |
| Claude 4 | 100k | €0.03 | Excelente |
| GPT-4 Turbo | 128k | €0.01 | Razoável |
| Gemini 2.0 Pro | 1M | €0.001 | Razoável |
| Ollama (local) | Config | $0 | Pobre (modelos pequenos) |

## Armadilhas e limitações

### Técnicas

1. **Token window overflow**: Agentes grandes saturamente contexto. Solução: carregar apenas módulos relevantes, usar "attention masks" para ignorar imports irrelevantes.

2. **Hallucination em planos**: Planejador pode gerar subtarefas impossíveis (ex: "call endpoint that doesn't exist"). Mitigar com validação de plano contra codebase real.

3. **Infinite loops**: Agente pode ficar retentando mesma ação. Implementar "max_retries" + timeout:

```python
max_retries = 3
timeout_seconds = 30

for attempt in range(max_retries):
    try:
        result = agent.execute(task, timeout=timeout_seconds)
        break
    except TimeoutError:
        print(f"Attempt {attempt} timed out")
```

4. **Test brittleness**: Testes gerados por LLM tendem a ser frágeis (mock excessivo, ignore edge cases). Requer human review.

### Práticas

5. **Contexto negativo**: Explicitamente listar o que agente NÃO deve fazer. Ex: "Não adicione logging em loops críticos", "Não use global variables".

6. **Exemplars em prompt**: Mostrar exemplos de "boa" implementação acelera agentes.

```python
prompt = """
You are a coding agent. Follow these examples:

GOOD:
def process_users(users):
    return [u for u in users if u.active]

BAD:
def process_users(users):
    result = []
    for u in users:
        if u.active:
            result.append(u)
    return result
"""
```

7. **Review humano obrigatório**: Qualquer código enviado em production deve passar por human review, mesmo se agente tiver alta confiança. Não remover human do loop.

### Conceituais

8. **Diferença entre "SWE agent" e "agente de coding"**: SWE agent resolve issues (requer entender contexto, testar, validar); agente de coding só escreve código. OpenHands + SWE-Agent resolvem issues; LLMs simples só geram código.

9. **Replicabilidade**: Agentes com temperature=0 (determinístico) são replicáveis; temperature>0 pode produzir saídas diferentes. Para CI/CD, usar determinístico.

10. **Custo escalável**: Cada agente consome tokens. Se 5 agentes rodam em paralelo por 10 minutos, são ~500k tokens gastos. Monitorar custo; implementar rate-limiting se necessário.

## Conexões

- [[prompting-avancado-chain-of-thought|Prompting Avançado: Chain-of-Thought, Persona]] — técnicas de prompt para agentes
- [[langchain-agents-tools|LangChain: Agents & Tools Framework]] — base de orquestração
- [[ci-cd-automation-com-ai|CI/CD Automation com IA]] — integração com pipelines de desenvolvimento

## Histórico

- 2026-04-02: Nota criada (conceitual)
- 2026-04-11: Expansão profunda com arquitetura, código Python, OpenHands vs SWE-Agent, LangGraph orquestração
