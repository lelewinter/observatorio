---
tags: []
source: https://x.com/sawyerhood/status/2036842374933180660?s=20
date: 2026-04-02
tipo: aplicacao
---
# Usar Browser CLI para Agentes Executarem em Browser

## O que é
Ferramenta (dev-browser) que permite agentes escreverem JavaScript/TypeScript executado diretamente no browser, em vez de emitir cliques sequenciais. Elimina overhead de turnos de interação; aproveita capacidade de geração de código dos LLMs.

## Como implementar
**1. Conceito fundamental**:

Abordagem tradicional:
```
Agent → "Click button" → Wait → Observe → "Type text" → Wait → Observe → ...
Latência: 100ms * N turnos = lenta
```

Abordagem dev-browser:
```
Agent → Write JavaScript → Execute → Result
Latência: 1 turno = rápido
```

**2. Instalação e setup**:

```bash
# Instalar dev-browser
npm install -g dev-browser

# Ou em seu projeto
npm install dev-browser

# Iniciar browser controller
dev-browser start --port 3000
```

**3. Integração com agentes de IA**:

```python
from anthropic import Anthropic

class BrowserAgent:
    def __init__(self, browser_url: str = "http://localhost:3000"):
        self.client = Anthropic()
        self.browser_url = browser_url

    def automate_task(self, task: str) -> str:
        """Agente escreve JavaScript para completar tarefa."""

        system_prompt = """Você é um agente de automação de browser.

Para tarefas no browser, escreva JavaScript que:
1. Navega a página
2. Encontra elementos
3. Executa ações
4. Retorna resultado

Use this JavaScript template:
```javascript
async function main() {
  // Navigate, find, click, type, extract
  return {success: true, result: "..."}
}
```

A função é executada no contexto do browser. Tem acesso a DOM, fetch, etc."""

        messages = [{
            "role": "user",
            "content": f"Complete this browser task: {task}"
        }]

        response = self.client.messages.create(
            model="claude-3-5-sonnet-20241022",
            max_tokens=2000,
            system=system_prompt,
            messages=messages
        )

        javascript_code = self._extract_javascript(response.content[0].text)

        # Executar no browser
        result = self._execute_in_browser(javascript_code)

        return result

    def _extract_javascript(self, response: str) -> str:
        """Extrai bloco JavaScript do response."""
        import re
        match = re.search(r'```javascript\n(.*?)\n```', response, re.DOTALL)
        return match.group(1) if match else ""

    def _execute_in_browser(self, javascript: str) -> str:
        """Executa JavaScript no browser via dev-browser."""
        import requests

        response = requests.post(
            f"{self.browser_url}/execute",
            json={"code": javascript}
        )

        return response.json().get("result", "")
```

**4. Exemplos de automação**:

```python
class BrowserAutomationExamples:
    def __init__(self, browser_agent: BrowserAgent):
        self.agent = browser_agent

    def scrape_adaptive(self):
        """Scraping que se adapta a mudanças de layout."""
        task = """
        Navigate to https://example.com
        Find all products with price > $50
        Extract name, price, link
        Return as JSON array"""

        result = self.agent.automate_task(task)
        return result

    def fill_complex_form(self):
        """Preenche formulário dinamicamente (não estático)."""
        task = """
        1. Go to /checkout
        2. Fill shipping address (123 Main St, City, State)
        3. Wait for address validation (may take 1-2s)
        4. Select first suggested address
        5. Continue to payment"""

        result = self.agent.automate_task(task)
        return result

    def test_ui_responsiveness(self):
        """Testa UI sem Playwright (direto em JS)."""
        task = """
        Test responsiveness:
        1. Resize window to 320px (mobile)
        2. Check if menu is hamburger
        3. Resize to 1920px (desktop)
        4. Check if menu is horizontal
        Report: {mobile_ok: bool, desktop_ok: bool}"""

        result = self.agent.automate_task(task)
        return result

    def handle_pagination(self):
        """Paginação automática e coleta de dados."""
        task = """
        Collect all products from paginated list:
        1. Extract products from current page
        2. Click next page
        3. Wait for load
        4. Repeat until no more pages
        Return: array of all products"""

        result = self.agent.automate_task(task)
        return result
```

**5. Comparação dev-browser vs Playwright**:

```
Métrica               | dev-browser  | Playwright
---------------------|--------------|----------
Turnos de interação   | 1            | 5-10+
Latência total        | 500ms-2s     | 2-5s
Complexidade de JS    | Gerenciável  | Complexa
Debugging             | Stack traces | Screenshots
Custo de API          | Menos chamadas| Mais chamadas (mais turnos)

Quando usar dev-browser:
- Automação linear (navega sequencialmente)
- Scraping estruturado
- Formulários complexos
- Performance crítica

Quando usar Playwright:
- Testes de regressão visual
- Interações complexas (modal chains)
- Validação de performance (timing)
```

**6. Integração com agentes LLM via tool use**:

```python
def create_browser_tool() -> dict:
    """Cria tool que agentes podem chamar."""
    return {
        "name": "execute_javascript",
        "description": "Execute JavaScript no browser e retorna resultado",
        "input_schema": {
            "type": "object",
            "properties": {
                "javascript": {
                    "type": "string",
                    "description": "Código JavaScript para executar"
                },
                "timeout_ms": {
                    "type": "integer",
                    "description": "Timeout em ms (default: 30000)"
                }
            },
            "required": ["javascript"]
        }
    }

class AgentWithBrowserTool:
    def __init__(self):
        self.client = Anthropic()

    def run_with_browser_access(self, task: str):
        """Agente tem acesso a browser como ferramenta."""

        tools = [create_browser_tool()]

        messages = [{"role": "user", "content": task}]

        while True:
            response = self.client.messages.create(
                model="claude-3-5-sonnet-20241022",
                max_tokens=2000,
                tools=tools,
                messages=messages
            )

            # Processar tool use
            for block in response.content:
                if hasattr(block, 'type') and block.type == "tool_use":
                    result = self._execute_browser_tool(block.input["javascript"])

                    messages.append({"role": "assistant", "content": response.content})
                    messages.append({
                        "role": "user",
                        "content": [{
                            "type": "tool_result",
                            "tool_use_id": block.id,
                            "content": result
                        }]
                    })
                    break
            else:
                # Sem tool use, tarefa completa
                return response.content[0].text

    def _execute_browser_tool(self, javascript: str) -> str:
        """Executa JavaScript no browser."""
        import requests
        response = requests.post(
            "http://localhost:3000/execute",
            json={"code": javascript},
            timeout=30
        )
        return str(response.json())
```

## Stack e requisitos
- **dev-browser**: npm package ou standalone binary
- **JavaScript/TypeScript**: browser compatibility (ES6+)
- **Dependências**: fetch, setTimeout, DOM API
- **Latência**: ~500ms-2s por execução (vs. 5-30s Playwright)
- **Custo**: ~1 chamada API/tarefa (vs. 10+ com Playwright)

## Armadilhas e limitações
- **Segurança**: executar código arbitrário no browser é risco. Apenas em browsers controlados.
- **Complexidade de async**: lidar com promessas e timeouts em JavaScript é delicado.
- **Cross-origin**: não pode acessar APIs externas por CORS.
- **Screenshot/visual**: dev-browser não tira screenshots. Use Playwright se precisa validar visuais.

## Conexões
[[Playwright Testing]], [[Tool Use com LLMs]], [[Browser Automation]], [[Agentes Web]]

## Histórico
- 2026-04-02: Nota criada
- 2026-04-02: Reescrita em padrão aplicação
