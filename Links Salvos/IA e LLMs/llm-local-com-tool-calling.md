---
tags: []
source: https://x.com/0xCVYH/status/2036517180410384680?s=20
date: 2026-04-02
tipo: aplicacao
---
# Configurar LLM 4B Local com Tool Calling para Agência Ativa

## O que é

Modelo de linguagem compacto (4B parâmetros, 4GB RAM) com capacidade de **tool calling** nativo — capacidade de executar pesquisas web, APIs e ferramentas locais durante o raciocínio, funcionando como agente autônomo offline sem dependência de cloud.

## Como implementar

### Fase 1: Instalação do Modelo

**Via Ollama (Mais Simples):**

```bash
# Instale Ollama
curl https://ollama.ai/install.sh | sh

# Puxe modelo Qwen 4B com tool-calling
ollama pull qwen2.5-4b-instruct

# Teste
ollama run qwen2.5-4b-instruct "Pesquise o preço de Bitcoin hoje"
```

**Via Hugging Face Transformers:**

```bash
pip install transformers torch unsloth

# Download
huggingface-cli download Qwen/Qwen2.5-4B-Instruct \
  --local-dir ./models/qwen4b
```

### Fase 2: Configurar Tool Calling

Crie arquivo `tools.json`:

```json
{
  "tools": [
    {
      "name": "web_search",
      "description": "Pesquisa na web em tempo real",
      "parameters": {
        "query": "string - termo de busca",
        "max_results": "integer - máximo de resultados (padrão 5)"
      }
    },
    {
      "name": "get_current_weather",
      "description": "Obter temperatura atual de uma cidade",
      "parameters": {
        "city": "string - nome da cidade",
        "units": "string - 'celsius' ou 'fahrenheit'"
      }
    },
    {
      "name": "fetch_url",
      "description": "Baixar conteúdo de uma URL",
      "parameters": {
        "url": "string - URL completa"
      }
    },
    {
      "name": "run_python",
      "description": "Executar código Python",
      "parameters": {
        "code": "string - código Python a executar"
      }
    }
  ]
}
```

### Fase 3: Implementar Handler de Tools

```python
# tools_handler.py
import subprocess
import requests
from duckduckgo_search import DDGS
import json

def execute_tool(tool_name: str, **kwargs) -> str:
    """Executa ferramenta solicitada pelo modelo"""

    if tool_name == "web_search":
        return web_search(kwargs["query"], kwargs.get("max_results", 5))

    elif tool_name == "get_current_weather":
        return get_weather(kwargs["city"], kwargs.get("units", "celsius"))

    elif tool_name == "fetch_url":
        return fetch_url(kwargs["url"])

    elif tool_name == "run_python":
        return run_python(kwargs["code"])

    else:
        return f"Tool '{tool_name}' not found"

def web_search(query: str, max_results: int = 5) -> str:
    """Pesquisa web via DuckDuckGo (sem API key)"""
    try:
        results = DDGS().text(query, max_results=max_results)
        return json.dumps(results, ensure_ascii=False)
    except Exception as e:
        return f"Erro na pesquisa: {str(e)}"

def get_weather(city: str, units: str = "celsius") -> str:
    """Obtém clima via OpenWeatherMap"""
    try:
        # Você pode usar API gratuita como wttr.in (sem chave)
        response = requests.get(f"https://wttr.in/{city}?format=j1")
        return response.json()["current_condition"][0]["description"]
    except:
        return "Não consegui obter clima"

def fetch_url(url: str) -> str:
    """Baixa conteúdo de URL"""
    try:
        response = requests.get(url, timeout=5)
        return response.text[:2000]  # Limita a 2000 chars
    except Exception as e:
        return f"Erro ao buscar URL: {str(e)}"

def run_python(code: str) -> str:
    """Executa código Python com segurança limitada"""
    try:
        result = subprocess.run(
            ["python3", "-c", code],
            capture_output=True,
            text=True,
            timeout=5
        )
        return result.stdout[:1000]  # Limita output
    except Exception as e:
        return f"Erro ao executar: {str(e)}"
```

### Fase 4: Loop ReAct (Reasoning + Acting)

```python
# react_agent.py
from transformers import AutoTokenizer, AutoModelForCausalLM
from tools_handler import execute_tool
import json
import re

class LocalAgent:
    def __init__(self, model_name="Qwen/Qwen2.5-4B-Instruct"):
        self.tokenizer = AutoTokenizer.from_pretrained(model_name)
        self.model = AutoModelForCausalLM.from_pretrained(model_name)
        self.max_iterations = 5

    def run(self, user_query: str) -> str:
        """Executa loop ReAct"""
        thoughts = []
        messages = [
            {"role": "system", "content": "Você é um agente inteligente com acesso a ferramentas."},
            {"role": "user", "content": user_query}
        ]

        for iteration in range(self.max_iterations):
            # Gerar resposta do modelo
            response = self._generate(messages)
            thoughts.append(response)

            # Parser resposta para detectar tool calls
            tool_calls = self._parse_tool_calls(response)

            if not tool_calls:
                # Nenhuma ferramenta, retorna resposta final
                return response

            # Executar ferramentas
            tool_results = []
            for tool_name, tool_args in tool_calls:
                result = execute_tool(tool_name, **tool_args)
                tool_results.append({
                    "tool": tool_name,
                    "result": result
                })

            # Adicionar resultado ao histórico
            messages.append({"role": "assistant", "content": response})
            messages.append({
                "role": "user",
                "content": f"Resultados das ferramentas: {json.dumps(tool_results)}"
            })

        return "\n".join(thoughts)

    def _generate(self, messages: list) -> str:
        """Gera texto do modelo"""
        prompt = self.tokenizer.apply_chat_template(
            messages,
            tokenize=False,
            add_generation_prompt=True
        )
        inputs = self.tokenizer(prompt, return_tensors="pt")
        outputs = self.model.generate(
            **inputs,
            max_new_tokens=256,
            temperature=0.7,
            do_sample=True
        )
        return self.tokenizer.decode(outputs[0], skip_special_tokens=True)

    def _parse_tool_calls(self, text: str) -> list:
        """Extrai chamadas de ferramentas do formato especial"""
        pattern = r"<tool_call>(\w+)\((.*?)\)</tool_call>"
        matches = re.findall(pattern, text)

        tool_calls = []
        for tool_name, args_str in matches:
            try:
                # Parse args como JSON
                args = json.loads("{" + args_str + "}")
                tool_calls.append((tool_name, args))
            except:
                pass

        return tool_calls

# Use
agent = LocalAgent()
result = agent.run("Qual é o preço do Bitcoin agora?")
print(result)
```

### Fase 5: Via CLI com Ollama

Ou use integração mais simples com Ollama:

```bash
# Modelo Qwen4B já suporta JSON mode para tool calling
ollama run qwen2.5-4b-instruct \
  --format json \
  "Pesquise o clima em São Paulo e me diga se está chovendo"
```

## Stack e requisitos

- **Modelo**: Qwen2.5-4B-Instruct (ou similar)
- **RAM**: 4GB mínimo, 8GB confortável
- **CPU**: Qualquer CPU moderno (I5+ ou equivalente)
- **Storage**: 5-8GB para modelo quantizado
- **Bibliotecas**:
  - `transformers`
  - `torch`
  - `requests`
  - `duckduckgo-search`
- **Latência**: ~1-3 segundos por token
- **Custo**: $0 (completamente local)

## Armadilhas e limitações

1. **Tool calling não é nativo**: Qwen 4B não tem fine-tuning oficial para tool calling. Você precisa fazer parse manual (veja exemplo acima).

2. **Qualidade em PT-BR**: Modelo foi treinado principalmente em inglês. Performance em português é aceitável mas não perfeita.

3. **Sem acesso Real-time**: A menos que implemente APIs (veja `tools_handler.py`), "pesquisa" é offline. Integre com APIs reais para dados atualizados.

4. **Alucinação de ferramentas**: Modelo pode inventar chamadas de tool que não existem. Valide sempre.

5. **Segurança**: `run_python` executa código arbitrário. Em produção, use sandbox (ex: RestrictedPython).

## Conexões

- [[inferencia-local-de-llms-gigantes]] — modelos ainda maiores localmente
- [[llms-como-tutores-de-idiomas]] — uso de LLMs pequenos para educação
- [[memory-stack-para-agentes-de-codigo]] — agentes com memória persistente

## Histórico

- 2026-04-02: Nota criada
- 2026-04-02: Guia prático com implementação

## Exemplos
1. **Pesquisa acadêmica assistida localmente**: um estudante usa o modelo no notebook para pesquisar artigos e sintetizar referências sem enviar dados sensíveis para servidores externos.
2. **Monitoramento de informações offline-first**: um desenvolvedor configura o agente para rastrear e resumir notícias de fontes específicas, rodando em hardware próprio sem custos de API.
3. **Assistente técnico com busca contextual**: um engenheiro usa o modelo para pesquisar documentação técnica em tempo real durante uma sessão de debug, integrando resultados diretamente no raciocínio do agente.

## Relacionado
*(Nenhuma nota existente no vault para linkar neste momento.)*

## Perguntas de Revisão
1. Qual é a diferença fundamental entre um LLM respondendo da memória paramétrica e um LLM executando *tool calls* durante o raciocínio? Por que isso importa para a qualidade das respostas?
2. Quais técnicas de otimização (quantização, destilação, etc.) tornam possível rodar um modelo com capacidade de agência em hardware consumer com apenas 4GB de RAM?

## Histórico de Atualizações
- 2026-04-02: Nota criada a partir de Telegram