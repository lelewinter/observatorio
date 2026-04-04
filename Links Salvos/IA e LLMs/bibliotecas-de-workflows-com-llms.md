---
tags: []
source: https://www.linkedin.com/posts/sairam-sundaresan_think-youve-mastered-claude-you-havent-share-7436968814027763713-XNeu?utm_source=social_share_send&utm_medium=android_app&rcm=ACoAAAgQrLIB4LHRfm8oNhRCsOv9i7wGJSYJXQs&utm_campaign=whatsapp
date: 2026-04-02
tipo: aplicacao
---
# Construir Biblioteca Reutilizável de Workflows com LLMs

## O que é
Coleção 450+ de workflows prontos (vs. simples prompts) que encapsulam lógica, encadeamento, integração com ferramentas. Exemplos: TDD assistido, pesquisa com auto-citação, análise de causa-raiz. Reduz custo cognitivo de orquestração; acelera adoção em produção.

## Como implementar
**1. Estrutura de workflow base**:

```python
from dataclasses import dataclass
from typing import Optional, List, Callable
from enum import Enum

class WorkflowStepType(Enum):
    LLM_CALL = "llm"
    TOOL_USE = "tool"
    DECISION = "decision"
    PARALLEL = "parallel"
    LOOP = "loop"

@dataclass
class WorkflowStep:
    id: str
    type: WorkflowStepType
    description: str
    input_schema: dict
    output_schema: dict
    next_step: Optional[str] = None
    conditions: Optional[List[tuple]] = None  # (condition, step_id_if_true)

class Workflow:
    def __init__(self, name: str, version: str):
        self.name = name
        self.version = version
        self.steps = {}
        self.start_step = None

    def add_step(self, step: WorkflowStep):
        """Registra um step no workflow."""
        self.steps[step.id] = step

    def set_start(self, step_id: str):
        """Define step inicial."""
        self.start_step = step_id

    def validate(self) -> bool:
        """Valida integridade do workflow."""
        if not self.start_step:
            raise ValueError("Start step não definido")

        visited = set()
        current = self.start_step

        while current:
            if current in visited:
                raise ValueError(f"Cycle detected at {current}")
            visited.add(current)

            if current not in self.steps:
                raise ValueError(f"Step {current} not found")

            current = self.steps[current].next_step

        return True

    def to_dict(self) -> dict:
        """Serializa para YAML/JSON."""
        return {
            "name": self.name,
            "version": self.version,
            "start": self.start_step,
            "steps": {sid: self._step_to_dict(s) for sid, s in self.steps.items()}
        }

    def _step_to_dict(self, step: WorkflowStep) -> dict:
        return {
            "type": step.type.value,
            "description": step.description,
            "input_schema": step.input_schema,
            "output_schema": step.output_schema,
            "next": step.next_step
        }
```

**2. Exemplo: TDD assistido**:

```python
def create_tdd_workflow() -> Workflow:
    """Workflow: Write test → Implement → Run test → Refine"""

    workflow = Workflow("TDD-Assisted", "1.0")

    # Step 1: Gerar test
    step_gen_test = WorkflowStep(
        id="gen_test",
        type=WorkflowStepType.LLM_CALL,
        description="Generate unit test from requirement",
        input_schema={
            "requirement": "str (what to test)",
            "language": "str (python, js, etc)"
        },
        output_schema={
            "test_code": "str",
            "test_description": "str"
        },
        next_step="save_test"
    )

    # Step 2: Salvar test
    step_save_test = WorkflowStep(
        id="save_test",
        type=WorkflowStepType.TOOL_USE,
        description="Save test file to disk",
        input_schema={"test_code": "str", "filepath": "str"},
        output_schema={"success": "bool"},
        next_step="run_test_first"
    )

    # Step 3: Rodar test (deve falhar)
    step_run_test_first = WorkflowStep(
        id="run_test_first",
        type=WorkflowStepType.TOOL_USE,
        description="Run test (expect failure)",
        input_schema={"filepath": "str"},
        output_schema={"passed": "bool", "output": "str"},
        next_step="decide_test_valid"
    )

    # Step 4: Decisão
    step_decide = WorkflowStep(
        id="decide_test_valid",
        type=WorkflowStepType.DECISION,
        description="Check if test is properly failing",
        input_schema={"passed": "bool"},
        output_schema={"valid_test": "bool"},
        conditions=[
            ("passed == False", "gen_implementation"),  # Teste falhando = bom
            ("passed == True", "gen_test")  # Teste passando = refazer
        ]
    )

    # Step 5: Implementar código
    step_impl = WorkflowStep(
        id="gen_implementation",
        type=WorkflowStepType.LLM_CALL,
        description="Generate implementation to pass test",
        input_schema={
            "test_code": "str",
            "language": "str"
        },
        output_schema={
            "implementation_code": "str"
        },
        next_step="save_implementation"
    )

    # ... mais steps ...

    workflow.add_step(step_gen_test)
    workflow.add_step(step_save_test)
    workflow.add_step(step_run_test_first)
    workflow.add_step(step_decide)
    workflow.add_step(step_impl)

    workflow.set_start("gen_test")
    workflow.validate()

    return workflow
```

**3. Executor de workflow**:

```python
from anthropic import Anthropic

class WorkflowExecutor:
    def __init__(self, workflow: Workflow):
        self.workflow = workflow
        self.client = Anthropic()
        self.context = {}

    def execute(self, initial_input: dict) -> dict:
        """Executa workflow do início até fim."""
        current_step_id = self.workflow.start_step
        self.context = initial_input

        while current_step_id:
            step = self.workflow.steps[current_step_id]
            print(f"Executing: {step.description}")

            if step.type == WorkflowStepType.LLM_CALL:
                result = self._execute_llm_step(step)
            elif step.type == WorkflowStepType.TOOL_USE:
                result = self._execute_tool_step(step)
            elif step.type == WorkflowStepType.DECISION:
                result, next_step_override = self._execute_decision_step(step)
                if next_step_override:
                    current_step_id = next_step_override
                    continue

            self.context.update(result)
            current_step_id = step.next_step

        return self.context

    def _execute_llm_step(self, step: WorkflowStep) -> dict:
        """Chama Claude para executar step."""
        prompt = f"{step.description}\n\nInput: {self.context}"

        response = self.client.messages.create(
            model="claude-3-5-sonnet-20241022",
            max_tokens=2000,
            messages=[{"role": "user", "content": prompt}]
        )

        return {step.id: response.content[0].text}

    def _execute_tool_step(self, step: WorkflowStep) -> dict:
        """Executa ferramenta (file I/O, shell, etc)."""
        # Implementar conforme ferramenta específica
        return {step.id: "tool_result"}

    def _execute_decision_step(self, step: WorkflowStep) -> tuple:
        """Avalia condição e retorna próximo step."""
        condition, value = step.conditions[0]

        # Evaluar condition
        if eval(condition.replace("passed", str(self.context.get("passed", False)))):
            return {step.id: True}, step.conditions[0][1]

        return {step.id: False}, step.next_step
```

**4. Biblioteca de 450+ workflows (exemplo)**:

```python
class WorkflowLibrary:
    def __init__(self):
        self.workflows = {}

    def register_workflow(self, workflow: Workflow):
        """Registra workflow na biblioteca."""
        key = f"{workflow.name}:{workflow.version}"
        self.workflows[key] = workflow

    def get_workflow(self, name: str, version: str = "latest") -> Workflow:
        """Recupera workflow."""
        if version == "latest":
            # Buscar versão mais recente
            matching = [k for k in self.workflows if k.startswith(name)]
            if not matching:
                raise ValueError(f"Workflow {name} not found")
            return self.workflows[max(matching)]

        return self.workflows[f"{name}:{version}"]

    def list_workflows_by_category(self, category: str) -> List[Workflow]:
        """Lista workflows por categoria."""
        # Implementar tagging...
        pass

# Usar
library = WorkflowLibrary()

# Registrar workflows conhecidos
library.register_workflow(create_tdd_workflow())
library.register_workflow(create_research_workflow())
library.register_workflow(create_root_cause_analysis_workflow())
# ... 450+ workflows total ...

# Executar
workflow = library.get_workflow("TDD-Assisted")
executor = WorkflowExecutor(workflow)
result = executor.execute({"requirement": "Write function to calculate fibonacci", "language": "python"})
```

**5. Padrões comuns encapsulados**:

```python
def create_research_with_self_citation_workflow() -> Workflow:
    """Workflow: Busca → Síntese → Citação automática → Formato final"""
    # ... implementação ...
    pass

def create_root_cause_analysis_workflow() -> Workflow:
    """Workflow: Analisar incidente → Identificar causa → Propor solução"""
    # ... implementação ...
    pass

def create_document_analysis_workflow() -> Workflow:
    """Workflow: Ler PDF → Extrai conceitos → Gera resumo → Salva em vault"""
    # ... implementação ...
    pass

def create_playwright_testing_workflow() -> Workflow:
    """Workflow: Escrever teste → Executar → Screenshot → Analisar """
    # ... implementação ...
    pass
```

## Stack e requisitos
- **YAML/JSON**: serializar workflows
- **Orchestration**: custom executor ou Temporal/Airflow
- **Versioning**: biblioteca com suporte a múltiplas versões
- **Documentação**: cada workflow com exemplos práticos
- **Custo**: típico $1-10 por workflow completo

## Armadilhas e limitações
- **Over-fitting**: cada workflow é muito específico. Reutilização limitada.
- **Manutenção**: 450 workflows = manutenção pesada quando APIs mudarem.
- **Latência**: workflows encadeados podem ser lentos (~5-30s cada passo).

## Conexões
[[Tool Use com LLMs]], [[Agente Loops]], [[Claude Code - Melhores Práticas]], [[Orquestração de Agentes]]

## Histórico
- 2026-04-02: Nota criada
- 2026-04-02: Reescrita em padrão aplicação
