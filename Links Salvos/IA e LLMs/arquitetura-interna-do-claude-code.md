---
tags: [claude-code, engenharia-de-software, llm, anthropic, ferramentas-ia]
source: https://x.com/ocodista/status/2039429796694814799?s=20
date: 2026-04-02
tipo: aplicacao
---
# Reverse-Engineer Agent Loops Aprendendo do Claude Code

## O que é
Documentação visível da arquitetura interna do Claude Code: como estrutura contexto, executa agent loop, usa tool calling, toma decisões. Permite otimizar prompts de sistema, construir agentes compatíveis, entender limites reais.

## Como implementar
**1. Estrutura observável do agent loop**:

Baseado em ccunpacked.dev e análise de outputs, Claude Code segue:

```
[Input: user prompt]
  ↓
[Prompt de sistema contextualizador]
  ↓
[Planning stage: break into subtasks]
  ↓
[Iteration loop]:
  - Decide next action (file read/write, shell run, etc)
  - Execute action
  - Observe result
  - Update context window
  - Check if done
  ↓
[Output: final result]
```

**2. Replicar estrutura em código**:

```python
class ClaudeCodeLike:
    def __init__(self):
        self.client = Anthropic()
        self.messages_history = []
        self.system_prompt = self.build_system_prompt()

    def build_system_prompt(self) -> str:
        """Claude Code usa prompt de sistema refinado."""
        return """Você é Claude Code, um agente de codificação autônomo.

Responsabilidades:
1. Receber uma tarefa de engenharia de software
2. Decomposição em sub-tarefas manageable
3. Executar iterativamente: planejar → escrever → testar → refinar
4. Usar ferramentas (file I/O, shell, git) eficientemente
5. Manter contexto de arquivo do projeto
6. Reconhecer quando tarefa está completa

Padrões observados:
- Nunca enviar arquivo inteiro se puder trabalhar por seções
- Sempre testar mudanças imediatamente
- Perguntar ao usuário antes de mudanças destrutivas
- Manter histórico de alterações para rollback

Ferramentas disponíveis:
- read_file(path, start_line=None, end_line=None)
- write_file(path, content)
- create_file(path, content)
- run_shell(command)
- list_files(path)
- search_files(pattern)"""

    def plan_task(self, task: str) -> dict:
        """Primeirafase: planejamento."""
        self.messages_history.append({
            "role": "user",
            "content": f"Tarefa: {task}\n\nCrie um plano estruturado (JSON)."
        })

        response = self.client.messages.create(
            model="claude-3-5-sonnet-20241022",
            max_tokens=2000,
            system=self.system_prompt,
            messages=self.messages_history
        )

        plan_text = response.content[0].text
        self.messages_history.append({
            "role": "assistant",
            "content": plan_text
        })

        return json.loads(self.extract_json(plan_text))

    def execute_iteration(self, current_plan: dict, iteration: int) -> dict:
        """Iteração do loop."""
        context = self.build_context_for_iteration(current_plan, iteration)

        self.messages_history.append({
            "role": "user",
            "content": context
        })

        response = self.client.messages.create(
            model="claude-3-5-sonnet-20241022",
            max_tokens=2000,
            system=self.system_prompt,
            messages=self.messages_history,
            tools=[
                {
                    "name": "read_file",
                    "description": "Lê arquivo",
                    "input_schema": {
                        "type": "object",
                        "properties": {
                            "path": {"type": "string"},
                            "start_line": {"type": "integer"},
                            "end_line": {"type": "integer"}
                        },
                        "required": ["path"]
                    }
                },
                {
                    "name": "write_file",
                    "description": "Escreve arquivo",
                    "input_schema": {
                        "type": "object",
                        "properties": {
                            "path": {"type": "string"},
                            "content": {"type": "string"}
                        },
                        "required": ["path", "content"]
                    }
                },
                {
                    "name": "run_shell",
                    "description": "Executa comando shell",
                    "input_schema": {
                        "type": "object",
                        "properties": {
                            "command": {"type": "string"}
                        },
                        "required": ["command"]
                    }
                }
            ]
        )

        # Processar tool_use
        actions = []
        for content_block in response.content:
            if hasattr(content_block, 'type') and content_block.type == "tool_use":
                result = self.execute_tool(content_block.name, content_block.input)
                actions.append({
                    "tool": content_block.name,
                    "input": content_block.input,
                    "result": result
                })

        return {
            "iteration": iteration,
            "actions": actions,
            "done": len(actions) == 0  # Heurística simplificada
        }

    def build_context_for_iteration(self, plan: dict, iteration: int) -> str:
        """Injeta contexto atual no prompt."""
        return f"""Progresso da tarefa:
Iteração {iteration} de 10

Plano:
{json.dumps(plan['steps'], indent=2)}

Próximo passo: executar step {iteration}

Qual ação tomar?"""

    def execute_tool(self, tool_name: str, tool_input: dict) -> str:
        """Executa ferramenta e retorna resultado."""
        if tool_name == "read_file":
            # Implementar...
            pass
        elif tool_name == "write_file":
            # Implementar...
            pass
        elif tool_name == "run_shell":
            # Implementar...
            pass

        return "Success"

    def extract_json(self, text: str) -> str:
        """Extrai JSON do texto."""
        import re
        match = re.search(r'\{.*\}', text, re.DOTALL)
        return match.group() if match else ""
```

**3. Otimizar prompts baseado na arquitetura**:

```python
def optimize_prompt_for_claude_code(user_task: str) -> str:
    """Formata prompt para melhor compatibilidade com agent loop."""

    # Padrão observado: Claude Code prefere requisitos estruturados
    optimized = f"""Tarefa de engenharia de software:

**Objetivo**: {user_task}

**Critérios de sucesso**:
1. [Listar métricas mensuráveis]
2. [Testes que devem passar]
3. [Requisitos não-funcionais]

**Contexto**:
- Projeto: [tipo/stack]
- Padrões existentes: [exemplos]
- Constraints: [limites técnicos]

**Entregáveis esperados**:
- [Arquivos/mudanças específicas]
- [Testes]
- [Documentação]

Proceda de forma iterativa e teste após cada mudança."""

    return optimized
```

**4. Debugging de comportamento de agente**:

```python
class AgentDebugger:
    def analyze_decision_quality(self, action_sequence: list) -> dict:
        """Analisa qualidade das decisões do agente."""
        metrics = {
            "tool_efficiency": self.calc_tool_efficiency(action_sequence),
            "iteration_count": len(action_sequence),
            "error_recovery": self.count_error_recoveries(action_sequence),
            "file_churn": self.count_file_changes(action_sequence)
        }

        # Padrão: bom agente tem alta eficiência, baixo churn
        if metrics["tool_efficiency"] > 0.8 and metrics["file_churn"] < 3:
            print("✓ Agent loop healthy")
        else:
            print("⚠ Agent loop subótimo - revisar prompts")

        return metrics

    def trace_context_growth(self, history: list) -> list:
        """Rastreia crescimento de contexto ao longo de iterações."""
        sizes = []
        for msg in history:
            size = len(str(msg))
            sizes.append(size)
        return sizes
```

## Stack e requisitos
- **Ferramentas de análise**: ccunpacked.dev, instrumentação de logs
- **Modelo**: Claude 3.5 Sonnet (recomendado para arquitetura mais estável)
- **Entendimento**: concepts de tool use, agentic reasoning, prompt engineering
- **Iteração**: 5-10 experimentos para calibrar prompts

## Armadilhas e limitações
- **Especulação**: ccunpacked.dev é reverse-engineered, não documentação oficial. Comportamentos podem divergir.
- **Versioning**: Anthropic pode mudar implementação sem aviso. Sempre validar suposições.
- **Black box**: alguns aspectos permanecem opacos. Não é 100% reproducível.
- **Over-fitting**: otimizar demais para Claude Code específico reduz portabilidade para outros LLMs.

## Conexões
[[Claude Code - Melhores Práticas]], [[Tool Use com LLMs]], [[Agent Loops]], [[Prompt Engineering Avançado]]

## Histórico
- 2026-04-02: Nota criada
- 2026-04-02: Reescrita em padrão aplicação
