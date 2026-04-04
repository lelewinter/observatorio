---
tags: []
source: https://www.linkedin.com/posts/cristianvieira-oficial_passei-um-tempo-no-reposit%C3%B3rio-que-a-langchain-share-7439666264974716929-HstF?utm_source=social_share_send&utm_medium=android_app&rcm=ACoAAAgQrLIB4LHRfm8oNhRCsOv9i7wGJSYJXQs&utm_campaign=share_via
date: 2026-04-02
tipo: aplicacao
---
# Construir Agente de Código Model-Agnostic

## O que é
Arquitetura aberta de agente de código (DeepAgents/LangChain) que separa orquestração de modelo subjacente. Permite usar qualquer LLM (Claude, GPT, Ollama local) com mesma lógica: planning, file I/O, shell execution, sub-agentes, auto-sumarização.

## Como implementar
**1. Core loop do agente**:

```python
from typing import Optional, List
from dataclasses import dataclass

@dataclass
class AgentState:
    task: str
    plan: List[str]
    completed_steps: List[str]
    files_modified: List[str]
    current_context: str
    iteration: int = 0

class CodeAgent:
    def __init__(self, llm_provider: str = "claude", model: str = "claude-3-5-sonnet"):
        self.llm_provider = llm_provider
        self.model = model
        self.max_iterations = 15
        self.file_system = FileSystemManager()
        self.shell = ShellExecutor()
        self.state: Optional[AgentState] = None

    def run(self, task: str) -> str:
        """Executa tarefa com agent loop completo."""
        self.state = AgentState(task=task, plan=[], completed_steps=[], files_modified=[])

        # Fase 1: Planning
        self.state.plan = self.phase_planning()
        print(f"Plano: {self.state.plan}")

        # Fase 2-N: Execução iterativa
        for iteration in range(self.max_iterations):
            self.state.iteration = iteration

            # Decidir próxima ação
            action = self.decide_next_action()

            if action["type"] == "done":
                return action.get("result", "Task completed")

            # Executar ação
            result = self.execute_action(action)

            # Auto-sumarização se contexto cresceu
            if self.estimate_context_usage() > 0.7:
                self.summarize_context()

        return "Max iterations reached"

    def phase_planning(self) -> List[str]:
        """LLM quebra tarefa em sub-tarefas."""
        prompt = f"""Analise esta tarefa: {self.state.task}

Retorne um plano em JSON:
{{
  "steps": [
    {{"number": 1, "description": "...", "owner": "agent"}}
  ],
  "assumptions": [...],
  "risks": [...]
}}

Plano deve ser executável incrementalmente."""

        response = self.call_llm(prompt)
        plan_json = self.extract_json(response)
        return [step["description"] for step in plan_json["steps"]]

    def decide_next_action(self) -> dict:
        """Decide qual ação executar baseado em estado."""
        context = self.build_context_window()

        prompt = f"""Estado atual:
Task: {self.state.task}
Plano: {self.state.plan}
Completo: {self.state.completed_steps}
Iteração: {self.state.iteration}

{context}

Qual é a próxima ação? Responda em JSON:
{{
  "type": "file_read|file_write|shell_run|sub_agent|summarize|done",
  "target": "...",
  "params": {{...}},
  "reasoning": "..."
}}"""

        response = self.call_llm(prompt)
        return self.extract_json(response)

    def execute_action(self, action: dict) -> str:
        """Executa ação e retorna resultado."""
        action_type = action["type"]

        if action_type == "file_read":
            content = self.file_system.read(action["target"])
            self.state.current_context = content[:2000]  # Truncate se grande
            return f"Read {action['target']}"

        elif action_type == "file_write":
            self.file_system.write(action["target"], action["params"]["content"])
            self.state.files_modified.append(action["target"])
            return f"Wrote {action['target']}"

        elif action_type == "shell_run":
            result = self.shell.execute(action["target"], timeout=30)
            return result.stdout + result.stderr

        elif action_type == "sub_agent":
            # Delegar para sub-agente especializado
            sub_agent = CodeAgent(llm_provider=self.llm_provider)
            result = sub_agent.run(action["target"])
            return result

        elif action_type == "summarize":
            return self.summarize_context()

        return "Unknown action"

    def build_context_window(self) -> str:
        """Constrói resumo de estado para passar ao LLM."""
        parts = [
            f"## Arquivos modificados",
            "\n".join(self.state.files_modified[-5:]),  # Últimos 5
            f"## Última saída",
            self.state.current_context[:1000],
        ]
        return "\n".join(parts)

    def estimate_context_usage(self) -> float:
        """Estima uso de contexto (0-1)."""
        # Simplificado; em produção usar token counter
        context_size = len(self.state.current_context)
        max_context = 100000  # Assumir 100k chars
        return min(context_size / max_context, 1.0)

    def summarize_context(self) -> str:
        """Sumariza contexto para economizar tokens."""
        prompt = f"""Resuma o progresso até agora:

{self.build_context_window()}

Responda com:
- Progresso feito
- Problemas encontrados
- Próximos passos

Máx 500 caracteres."""

        summary = self.call_llm(prompt)
        self.state.current_context = summary
        return summary

    def call_llm(self, prompt: str) -> str:
        """Chama LLM (model-agnostic)."""
        if self.llm_provider == "claude":
            from anthropic import Anthropic
            client = Anthropic()
            response = client.messages.create(
                model=self.model,
                max_tokens=2000,
                messages=[{"role": "user", "content": prompt}]
            )
            return response.content[0].text

        elif self.llm_provider == "ollama":
            import ollama
            response = ollama.generate(
                model=self.model,
                prompt=prompt
            )
            return response["response"]

        # Adicionar mais providers conforme necessário
        raise NotImplementedError(f"Provider {self.llm_provider} not supported")
```

**2. File system manager (sandboxing)**:

```python
import os
from pathlib import Path
import shutil

class FileSystemManager:
    def __init__(self, work_dir: str = "/tmp/agent_work"):
        self.work_dir = Path(work_dir)
        self.work_dir.mkdir(exist_ok=True)

    def read(self, path: str) -> str:
        """Lê arquivo dentro do work_dir."""
        full_path = self.work_dir / path
        if not str(full_path).startswith(str(self.work_dir)):
            raise PermissionError("Cannot read outside work directory")
        return full_path.read_text()

    def write(self, path: str, content: str):
        """Escreve arquivo dentro do work_dir."""
        full_path = self.work_dir / path
        full_path.parent.mkdir(parents=True, exist_ok=True)
        full_path.write_text(content)

    def list(self, path: str = "") -> List[str]:
        """Lista arquivos."""
        directory = self.work_dir / path
        return [str(p.relative_to(self.work_dir)) for p in directory.rglob("*")]
```

**3. Shell executor com timeout**:

```python
import subprocess
from dataclasses import dataclass

@dataclass
class ShellResult:
    stdout: str
    stderr: str
    returncode: int

class ShellExecutor:
    ALLOWED_COMMANDS = ["python", "node", "bash", "git", "npm", "pip"]

    def execute(self, command: str, timeout: int = 30) -> ShellResult:
        """Executa comando com validação."""
        # Validar comando
        cmd_name = command.split()[0]
        if cmd_name not in self.ALLOWED_COMMANDS:
            return ShellResult("", f"Command {cmd_name} not allowed", 1)

        try:
            result = subprocess.run(
                command,
                shell=True,
                capture_output=True,
                timeout=timeout,
                text=True
            )
            return ShellResult(result.stdout, result.stderr, result.returncode)
        except subprocess.TimeoutExpired:
            return ShellResult("", "Timeout", -1)
        except Exception as e:
            return ShellResult("", str(e), -1)
```

**4. Sub-agentes para paralelização**:

```python
from concurrent.futures import ThreadPoolExecutor

class MultiAgentOrchestrator:
    def __init__(self, num_agents: int = 3):
        self.agents = [CodeAgent() for _ in range(num_agents)]
        self.executor = ThreadPoolExecutor(max_workers=num_agents)

    def run_parallel(self, tasks: List[str]) -> List[str]:
        """Executa múltiplas tarefas em paralelo."""
        futures = [
            self.executor.submit(agent.run, task)
            for agent, task in zip(self.agents, tasks)
        ]
        return [f.result() for f in futures]

    def run_sequential_with_deps(self, task_graph: dict):
        """Executa tarefas com dependências."""
        # task_graph: {"task_id": {"command": "...", "depends_on": ["..."]}}
        completed = {}

        def execute_task(task_id):
            task = task_graph[task_id]
            # Aguardar dependências
            for dep in task.get("depends_on", []):
                if dep not in completed:
                    execute_task(dep)

            agent = CodeAgent()
            completed[task_id] = agent.run(task["command"])

        for task_id in task_graph:
            if task_id not in completed:
                execute_task(task_id)

        return completed
```

## Stack e requisitos
- **Modelo**: qualquer LLM (Claude, GPT, local via Ollama)
- **Frameworks**: LangChain 0.1+, ou custom com `anthropic`, `openai`, `ollama`
- **Execução**: Python 3.9+, sandbox de arquivo, shell seguro
- **Memória**: 4GB minimum; mais se usar grandes modelos locais
- **Latência**: ~5-30s por iteração (deps. LLM)

## Armadilhas e limitações
- **Divergência do modelo**: mesma arquitetura, modelos diferentes podem ter comportamento divergente. Testar com cada LLM.
- **Infinitos loops**: se LLM não consegue decidir "done", fica em loop. Implementar max_iterations rigorosamente.
- **Custo de contexto**: auto-sumarização reduz mas não elimina crescimento de contexto.
- **Segurança de shell**: execute apenas comandos whitelisted. Sempre sandbox.

## Conexões
[[Claude Code]], [[DeepAgents]], [[LangChain]], [[Tool Use com LLMs]], [[Multi-Agente Orquestração]]

## Histórico
- 2026-04-02: Nota criada
- 2026-04-02: Reescrita em padrão aplicação
