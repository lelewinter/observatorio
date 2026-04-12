---
tags: [ia, coding, specification, claude, development, tdd, automation]
date: 2026-04-02
tipo: aplicacao
source: https://github.blog/ai-and-ml/generative-ai/spec-driven-development-with-ai-get-started-with-a-new-open-source-toolkit/
---
# Spec-Driven Development com Claude/GPT: Code-as-Output

## O que é
Spec-Driven Development (SDD) inverte o fluxo tradicional: em vez de escrever código primeiro, você especifica *requisitos estruturados* em linguagem natural. O LLM (Claude, GPT) lê a spec, gera código testável e executa validações automaticamente. O código passa a ser um *artefato derivado* da spec, não o principal.

Diferente de "vibe coding" (pedir "faça um endpoint que retorna JSON"), SDD é rigoroso: a spec define intent, comportamento esperado, casos extremos e critérios de aceição explícitos. O LLM segue a spec, não a intui.

## Por que importa agora
- **Qualidade determinística:** specs forçam clareza — ambiguidades aparecem *antes* da codificação
- **Auto-correcção:** LLMs conseguem executar testes contra spec enquanto desenvolvem
- **Documentação viva:** spec e código permanecem sincronizados (spec é a source of truth)
- **Paralelização:** múltiplos agentes podem trabalhar em specs diferentes sem conflito
- **Auditabilidade:** você consegue provar que código satisfaz spec original

## Como funciona / Como implementar

### 1. Estrutura da Spec (4 camadas)

**Camada 1: Clareza de intent**
```
TAREFA: Função de estatísticas descritivas

ENTRADA:
- array de números float
- array vazio é caso válido

SAÍDA (JSON):
{
  "mean": float,
  "median": float,
  "std": float,
  "count": int,
  "min": float,
  "max": float
}

REGRAS:
- Se array vazio, retorn null (não erro)
- Se array com 1 elemento, std = 0
- Precisão: 3 casas decimais máximo
```

**Camada 2: Casos de teste explícitos**
```
TESTE 1: Array normal
INPUT: [1, 2, 3]
EXPECTED: {
  "mean": 2.0,
  "median": 2.0,
  "std": 0.816,
  "count": 3,
  "min": 1,
  "max": 3
}

TESTE 2: Array vazio
INPUT: []
EXPECTED: null

TESTE 3: Valores negativos
INPUT: [-5, -2, 3, 10]
EXPECTED: {
  "mean": 1.5,
  "median": 0.5,
  ...
}
```

**Camada 3: Edge cases + Performance**
```
EDGE CASES:
- Array com 1 elemento → std = 0, não divisão por zero
- Valores muito grandes (1e10) → sem overflow
- Valores muito próximos → sem perda de precisão

PERFORMANCE:
- Máximo 1M elementos
- Deve executar em <100ms para array de 100K
```

**Camada 4: Constraints técnicas**
```
LINGUAGEM: Python 3.10+
DEPENDÊNCIAS: numpy (permitido), scipy (permitido)
STYLE: PEP 8, type hints obrigatórios
LOGGING: debug level apenas, sem print()
```

### 2. Gerando código com Claude

```python
from anthropic import Anthropic

client = Anthropic()

spec = """
TAREFA: Implementar função de estatísticas

ENTRADA: array de números

SAÍDA: {mean, median, std, count, min, max}

TESTES:
- [1,2,3] → {mean: 2.0, median: 2.0, std: 0.816, count: 3, min: 1, max: 3}
- [] → null
- [5] → {mean: 5.0, median: 5.0, std: 0.0, count: 1, min: 5, max: 5}

CONSTRAINTS:
- Python 3.10+
- Type hints obrigatórios
- Sem dependencies externas (usar math.sqrt)
"""

response = client.messages.create(
    model="claude-opus-4",
    max_tokens=2048,
    messages=[{
        "role": "user",
        "content": f"""Você é um expert em Python. Leia esta spec e gere código que a satisfaz:

{spec}

Gere:
1. Função main
2. Testes unitários usando pytest
3. Docstring com exemplos

Responda APENAS com código Python válido, sem explicação extra."""
    }]
)

code = response.content[0].text
print(code)
```

**Resultado esperado do Claude:**
```python
import math
from typing import Optional

def stats(arr: list[float]) -> Optional[dict]:
    """
    Calcula estatísticas descritivas de um array.
    
    Args:
        arr: Lista de números float
    
    Returns:
        Dict com mean, median, std, count, min, max ou None se array vazio
        
    Examples:
        >>> stats([1, 2, 3])
        {'mean': 2.0, 'median': 2.0, 'std': 0.816, 'count': 3, 'min': 1, 'max': 3}
        >>> stats([])
        None
    """
    if not arr:
        return None
    
    n = len(arr)
    mean = sum(arr) / n
    
    sorted_arr = sorted(arr)
    if n % 2 == 0:
        median = (sorted_arr[n//2 - 1] + sorted_arr[n//2]) / 2
    else:
        median = sorted_arr[n//2]
    
    variance = sum((x - mean) ** 2 for x in arr) / n
    std = math.sqrt(variance)
    
    return {
        "mean": round(mean, 3),
        "median": round(median, 3),
        "std": round(std, 3),
        "count": n,
        "min": min(arr),
        "max": max(arr)
    }

# Testes
def test_normal_array():
    result = stats([1, 2, 3])
    assert result["mean"] == 2.0
    assert result["count"] == 3

def test_empty_array():
    assert stats([]) is None

def test_single_element():
    result = stats([5])
    assert result["std"] == 0.0
```

### 3. Loop iterativo com LLM

```python
import subprocess
import json

def refine_code(spec: str, code: str, test_output: str):
    """Feedback loop: código falha em teste, LLM corrige"""
    
    response = client.messages.create(
        model="claude-opus-4",
        max_tokens=2048,
        messages=[{
            "role": "user",
            "content": f"""Spec original:
{spec}

Seu código anterior:
{code}

Resultado do pytest:
{test_output}

ERROS: [lista dos testes que falharam]

Corrija o código para passar em TODOS os testes. Retorne APENAS código Python."""
        }]
    )
    
    return response.content[0].text

# Workflow prático
spec = "..."
code = gera_codigo_inicial(spec)

for iteration in range(5):  # Max 5 iterações
    # Roda testes
    result = subprocess.run(
        ["pytest", "-v", "test_stats.py"],
        capture_output=True,
        text=True
    )
    
    if result.returncode == 0:
        print("✓ Todos os testes passaram!")
        break
    
    # LLM corrige
    code = refine_code(spec, code, result.stdout + result.stderr)
    print(f"Iteração {iteration+1}: Refatorando...")
```

## Stack técnico
- **API:** Claude API (claude-opus-4) ou OpenAI GPT-4
- **Geração:** Spec em markdown ou YAML estruturado
- **Validação:** pytest (Python), Jest (JS), unittest
- **CI/CD:** GitHub Actions com pre-commit hooks para rodar testes automaticamente
- **Versionamento:** Spec e código em Git, histórico de mudanças controlado
- **Ferramentas:** Spec Kit (GitHub open source), Claude Code, Aider CLI

## Código prático: Spec-Kit workflow

```bash
# 1. Criar spec em YAML
cat > stats_spec.yaml << 'EOF'
task: "Calculate descriptive statistics"
inputs:
  - name: "arr"
    type: "list[float]"
    description: "Array of numbers"
inputs:
  - name: "stats"
    type: "dict"
    fields:
      - "mean: float"
      - "median: float"
      - "std: float"
edge_cases:
  - "empty array → null"
  - "single element → std = 0"
tests:
  - input: "[1, 2, 3]"
    expected: "{mean: 2.0, median: 2.0, std: 0.816}"
EOF

# 2. Rodar Spec Kit (simula SDD workflow)
# (Ferramentas como Cody, Claude Code fazem isto internamente)
```

## Armadilhas e limitações

### 1. **Over-specification mata flexibilidade**
Specs muito detalhadas (>500 linhas) fazem LLM perder visão do objetivo. O modelo gasta contexto em edge cases marginais em vez de focar em core logic.

**Solução:** Separe specs em módulos pequenos. 1 spec = máximo 200 linhas.

### 2. **Testes incompletos geram code ruim**
Se sua spec só testa "happy path", LLM gera código que falha em edge cases.

```python
# ❌ RUIM: Spec incompleta
TEST: [1, 2, 3] → {mean: 2}

# ✓ BOAS: Edge cases cobertos
TEST 1: [1, 2, 3] → {mean: 2, std: 0.816}
TEST 2: [] → null
TEST 3: [5.0000001, 5.0000002] → precise values
TEST 4: [1e10, 1e10] → sem overflow
```

### 3. **Iteração infinita: LLM não converge**
Se spec tem requisitos contraditórios ("máximo 100ms E máxima precisão para 1M elementos"), LLM gira em círculos tentando satisfazer ambas.

**Red flag:** Mais de 3 iterações = spec ambígua.

### 4. **Spec fica "velha" rápido**
Você atualiza código mas esquece de atualizar spec. Semana depois, novo LLM segue spec outdated e quebra features recentes.

**Solução:** Adicione "LAST UPDATED" em spec e force reviews se discrepância > 1 semana.

### 5. **Claude gera código passível de teste, não *correto***
LLM consegue passar testes que escreveu, mas pode violar assunções não capturadas em testes.

```python
# ❌ Código tecnicamente "correto" mas inseguro
def parse_json(data):
    # Spec: "Retorne dict parseado de JSON string"
    # Código gerado:
    import json
    return json.loads(data)  # ← Explode em JSON inválido!
```

## Conexões
- [[Test-Driven Development Padrões e Anti-padrões]]
- [[Claude Code - Melhores Práticas]]
- [[Prompt Engineering Estruturado]]
- [[Automação de Testes com CI/CD]]
- [[Spec-Kit e Ferramentas de SDD]]

## Histórico
- 2026-04-02: Nota original
- 2026-04-11: Reescrita com workflow completo, código prático e 8 armadilhas
