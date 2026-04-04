---
tags: [browser, AI, agentes, interface, Opera]
source: https://x.com/aigleeson/status/2039029063122370857?s=20
date: 2026-04-02
tipo: aplicacao
---
# Arquitetar Browser como Container de Agente Autônomo

## O que é
Inversão de hierarquia: em vez de IA dentro do browser (extensão), o agente é orquestrador principal e browser é ferramenta que ele invoca. Agente autônomo controla navegação, preenche formulários, coleta dados; usuário aprova apenas decisões críticas.

## Como implementar
**1. Arquitetura: IA como orquestrador central**:

```
Tradicional:
User → Browser (IA como assistente dentro) → Toma ação

Invertido:
User → Agente Autônomo (decision maker) → Browser (efetuador)
                      ↓
                 Decide quando usar browser
                      ↓
              Browser executa, retorna resultado
```

**2. Estrutura base do agente container**:

```python
from enum import Enum
from typing import Optional

class BrowserAction(Enum):
    NAVIGATE = "navigate"
    CLICK = "click"
    TYPE = "type"
    EXTRACT = "extract"
    WAIT = "wait"

class AIBrowserContainer:
    def __init__(self, model: str = "claude-3-5-sonnet"):
        self.model = model
        self.client = Anthropic()
        self.browser_state = {}
        self.execution_log = []

    def run_autonomous_task(self, objective: str, user_supervision: bool = True):
        """Executa tarefa autonomamente, com aprovação opcional do usuário."""

        system_prompt = """Você é agente autônomo com acesso a um browser.

Seu objetivo: """ + objective + """

Você pode:
- navigate(url)
- click(selector)
- type(selector, text)
- extract(selector, attribute)
- wait(ms)

Para cada passo, decida qual ação tomar.
Se algo for crítico (logout, delete, money transfer), pedir aprovação."""

        messages = [{"role": "user", "content": objective}]
        iteration = 0
        max_iterations = 20

        while iteration < max_iterations:
            iteration += 1

            # LLM decide próxima ação
            response = self.client.messages.create(
                model=self.model,
                max_tokens=1000,
                system=system_prompt,
                messages=messages
            )

            action_text = response.content[0].text

            # Parse ação (simplified)
            action = self._parse_action(action_text)

            if action["type"] == "done":
                return action.get("result", "Task completed")

            # Verificar se precisa aprovação
            if user_supervision and self._requires_approval(action):
                approved = input(f"Approve action: {action}? (y/n): ")
                if approved.lower() != 'y':
                    messages.append({"role": "assistant", "content": action_text})
                    messages.append({
                        "role": "user",
                        "content": "Ação rejeitada pelo usuário. Tente alternativa."
                    })
                    continue

            # Executar ação no browser
            result = self._execute_browser_action(action)

            # Feedback ao agente
            self.execution_log.append({
                "iteration": iteration,
                "action": action,
                "result": result
            })

            messages.append({"role": "assistant", "content": action_text})
            messages.append({
                "role": "user",
                "content": f"Action executed. Result: {result}"
            })

        return "Max iterations reached"

    def _parse_action(self, response: str) -> dict:
        """Parse ação da resposta do LLM."""
        import re
        import json

        # Procura por JSON na resposta
        match = re.search(r'\{.*\}', response, re.DOTALL)
        if match:
            return json.loads(match.group())

        # Fallback: parse por keywords
        if "done" in response.lower():
            return {"type": "done", "result": response}
        elif "navigate" in response.lower():
            return {"type": "navigate"}
        else:
            return {"type": "unknown"}

    def _requires_approval(self, action: dict) -> bool:
        """Identifica ações que precisam aprovação humana."""
        risky_actions = [
            "delete", "logout", "submit_payment", "modify_critical",
            "send_email", "change_password"
        ]

        action_str = str(action).lower()
        return any(risky in action_str for risky in risky_actions)

    def _execute_browser_action(self, action: dict) -> str:
        """Executa ação no browser real."""
        # Integrar com Playwright, Selenium ou dev-browser
        action_type = action.get("type")

        if action_type == "navigate":
            url = action.get("url")
            # browser.goto(url)
            return f"Navigated to {url}"

        elif action_type == "click":
            selector = action.get("selector")
            # browser.click(selector)
            return f"Clicked {selector}"

        elif action_type == "extract":
            selector = action.get("selector")
            # content = browser.extract(selector)
            return "Extracted content"

        return "Action executed"
```

**3. Workflow de pesquisa autônoma**:

```python
class AutonomousResearchAgent(AIBrowserContainer):
    def research_topic(self, topic: str) -> dict:
        """Pesquisa um tópico autonomamente."""

        objective = f"""Pesquise: {topic}

Steps:
1. Navigate to Google
2. Search for "{topic}"
3. Visit top 3 results
4. Extract key information
5. Compile into report

Report format: {{'summary': '...', 'sources': [...], 'key_findings': [...]}}"""

        result = self.run_autonomous_task(objective, user_supervision=True)

        return {
            "topic": topic,
            "result": result,
            "execution_log": self.execution_log
        }
```

**4. Monitoramento de ações do agente**:

```python
class AgentMonitor:
    def __init__(self, container: AIBrowserContainer):
        self.container = container

    def display_execution_timeline(self):
        """Exibe timeline de ações executadas."""
        print("=== Execution Timeline ===\n")

        for log_entry in self.container.execution_log:
            iteration = log_entry["iteration"]
            action = log_entry["action"]
            result = log_entry["result"]

            print(f"[{iteration}] {action.get('type')}: {action}")
            print(f"     Result: {result[:100]}")

    def rollback_to_state(self, iteration: int):
        """Volta a um ponto anterior se algo deu errado."""
        # Limpar ações posteriores
        self.container.execution_log = self.container.execution_log[:iteration]
        print(f"Rolled back to iteration {iteration}")

    def export_automation_script(self):
        """Exporta sequência de ações como script reutilizável."""
        script = "# Auto-generated automation script\n\n"

        for log_entry in self.container.execution_log:
            action = log_entry["action"]
            action_type = action.get("type")

            if action_type == "navigate":
                script += f"browser.goto('{action.get('url')}')\n"
            elif action_type == "click":
                script += f"browser.click('{action.get('selector')}')\n"
            elif action_type == "type":
                script += f"browser.type('{action.get('selector')}', '{action.get('text')}')\n"

        return script
```

**5. Controle do usuário e transparência**:

```python
class UserControlledAgentBrowser:
    def __init__(self):
        self.agent = AIBrowserContainer()
        self.user_supervision_level = "medium"  # low, medium, high

    def set_supervision_level(self, level: str):
        """Define quanto o agente precisa pedir aprovação."""
        self.user_supervision_level = level
        # Low: agente é quase totalmente autônomo
        # Medium: aprova apenas ações críticas
        # High: aprova cada ação

    def run_with_supervision(self, task: str):
        """Executa com nível configurado de supervisão."""
        if self.user_supervision_level == "high":
            # Pedir aprovação a cada passo
            return self.agent.run_autonomous_task(task, user_supervision=True)
        elif self.user_supervision_level == "medium":
            # Pedir aprovação apenas para ações críticas
            return self.agent.run_autonomous_task(task, user_supervision=True)
        else:
            # Totalmente autônomo
            return self.agent.run_autonomous_task(task, user_supervision=False)
```

## Stack e requisitos
- **Browser automation**: Playwright, Selenium, ou custom via dev-browser
- **LLM**: Claude 3.5 Sonnet (ou melhor) para raciocínio complexo
- **Logging**: JSON para auditória
- **User interface**: CLI ou web dashboard para aprovações
- **Custo**: ~$1-5 por task complexa

## Armadilhas e limitações
- **Autonomia perigosa**: agente pode fazer coisas não intencionadas. Implementar guardrails rigorosos.
- **Accountability**: quem é responsável se agente fizer algo errado? Documentar aprovações.
- **Variabilidade de web**: mudanças de UI quebram automações. Implementar fallbacks.
- **Performance**: agentes são lentos. Tarefas que levam 5min manualmente podem levar 15min com agente.

## Conexões
[[Agentes Autônomos]], [[Browser Automation]], [[Tool Use com LLMs]], [[Agent Loops]], [[User Supervision]]

## Histórico
- 2026-04-02: Nota criada
- 2026-04-02: Reescrita em padrão aplicação
