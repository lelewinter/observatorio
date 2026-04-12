---
tags: [spec-driven-development, metodologia, engenharia-de-software, ia, sdd, llm-code-gen]
source: https://x.com/SalazarRog35996/status/2038329759474520303?s=20
date: 2026-04-02
tipo: aplicacao
---

# Implementar Spec-Driven Development (SDD) com Agentes de IA para Codificação

## O que é

Spec-Driven Development (SDD) é uma metodologia que inverte a hierarquia tradicional de engenharia de software: em vez de código ser a fonte primária de verdade, **especificações formais e executáveis** assumem esse papel. Código, testes e documentação são derivados **automaticamente** ou **validados contra** a spec usando agentes de IA (LLMs).

Não é simplesmente "documentar bem": é tratar a spec como um **contrato estruturado e verificável** que tanto humanos quanto máquinas consumem como entrada de um pipeline de geração de código. GitHub Spec Kit (projeto open-source com 84.7k stars) fornece scaffolding Python para essa prática, suportando 14+ plataformas de agentes de IA.

## Por que importa agora

A maturidade dos LLMs em código criou um novo gargalo: **qualidade do input, não capacidade do modelo**. Estudos controlados mostram que especificações humanas bem-refinadas reduzem erros em código gerado por até 50%. A ascensão de agentes autônomos (Claude Code, Cursor, Copilot com MCP) torna a spec um artefato crítico — cada vez mais, engenheiros gastam tempo escrevendo especificações que IA executa, em vez de escrever código diretamente.

SDD também resolve um problema prático: com IA gerando código candidato, como controlar qualidade consistentemente? Resp: specs como critério objetivo. Qualquer desvio entre código e spec fica evidente, seja para um linter ou para outro agente de validação.

## Como funciona / Como implementar

### Estrutura de uma Spec SDD

Uma spec SDD efetiva cobre pelo menos:
- **Definição de comportamento**: entrada esperada, saída esperada, efeitos colaterais
- **Contrato de API**: tipagem, validações, exceções
- **Exemplos concretos**: casos de uso com dados reais
- **Fluxo de dados**: como informação se move entre componentes
- **Regras de negócio**: restrições, invariantes, limites

Não é prosa; é estruturado. OpenAPI/AsyncAPI para APIs, JSON Schema para dados, Gherkin para comportamento.

### Fluxo prático

```
1. Engenheiro escreve ou refina spec (usando template SDD)
2. Coloca spec no prompt ou passa para ferramenta de SDD
3. Agente LLM lê spec, gera código candidato
4. Agente validador testa código contra spec
5. Se houver divergência, agente corrige ou sinaliza para review
6. Spec fica viva: quando requisitos mudam, só a spec é atualizada
```

### Exemplo concreto: API REST com spec OpenAPI

Arquivo `api-spec.yml`:
```yaml
openapi: 3.0.0
info:
  title: Payment Service
  version: 1.0.0
paths:
  /transactions:
    post:
      summary: Create a new transaction
      requestBody:
        required: true
        content:
          application/json:
            schema:
              type: object
              required: [amount, currency, customer_id]
              properties:
                amount:
                  type: number
                  minimum: 0.01
                  maximum: 999999.99
                currency:
                  type: string
                  enum: [USD, EUR, BRL]
                customer_id:
                  type: string
                  pattern: '^cust_[a-zA-Z0-9]{12}$'
      responses:
        '201':
          description: Transaction created successfully
          content:
            application/json:
              schema:
                type: object
                properties:
                  id:
                    type: string
                    pattern: '^txn_[a-zA-Z0-9]{16}$'
                  status:
                    type: string
                    enum: [pending, completed, failed]
                  created_at:
                    type: string
                    format: date-time
        '400':
          description: Invalid input
          content:
            application/json:
              schema:
                type: object
                properties:
                  error:
                    type: string
                  details:
                    type: array
                    items:
                      type: object
                      properties:
                        field:
                          type: string
                        message:
                          type: string
        '409':
          description: Duplicate transaction within 30 seconds
```

Agora passa isso para um agente SDD:
```
Generate Python Flask implementation that matches this spec exactly.
Enforce all validations. Return only code that passes automated spec validation.
```

Agente gera:
```python
from flask import Flask, request, jsonify
from datetime import datetime
import uuid
import re

app = Flask(__name__)

VALID_CURRENCIES = {'USD', 'EUR', 'BRL'}

@app.route('/transactions', methods=['POST'])
def create_transaction():
    data = request.get_json()
    
    # Validação: campos obrigatórios
    if not all(k in data for k in ['amount', 'currency', 'customer_id']):
        return jsonify({
            'error': 'Missing required fields',
            'details': [{'field': k, 'message': f'{k} is required'} 
                       for k in ['amount', 'currency', 'customer_id'] 
                       if k not in data]
        }), 400
    
    # Validação: amount
    try:
        amount = float(data['amount'])
        if not (0.01 <= amount <= 999999.99):
            return jsonify({
                'error': 'Invalid amount',
                'details': [{'field': 'amount', 
                           'message': 'must be between 0.01 and 999999.99'}]
            }), 400
    except (ValueError, TypeError):
        return jsonify({
            'error': 'Invalid amount type',
            'details': [{'field': 'amount', 'message': 'must be a number'}]
        }), 400
    
    # Validação: currency
    if data['currency'] not in VALID_CURRENCIES:
        return jsonify({
            'error': 'Invalid currency',
            'details': [{'field': 'currency', 
                       'message': f'must be one of {VALID_CURRENCIES}'}]
        }), 400
    
    # Validação: customer_id pattern
    if not re.match(r'^cust_[a-zA-Z0-9]{12}$', data['customer_id']):
        return jsonify({
            'error': 'Invalid customer_id format',
            'details': [{'field': 'customer_id',
                       'message': 'must match pattern ^cust_[a-zA-Z0-9]{12}$'}]
        }), 400
    
    # Gerar resposta
    transaction_id = f"txn_{uuid.uuid4().hex[:16]}"
    
    return jsonify({
        'id': transaction_id,
        'status': 'pending',
        'created_at': datetime.utcnow().isoformat() + 'Z'
    }), 201
```

Validador automatizado verifica: todos os campos da spec presentes? Validações corretas? Tipos de retorno conformes?

## Stack técnico

- **Ferramentas de especificação**: OpenAPI (APIs REST), AsyncAPI (eventos), Protocol Buffers (RPC)
- **Plataformas SDD**: GitHub Spec Kit (Python CLI), Kiro, Tessl
- **Agentes LLM**: Claude Code, Cursor, GitHub Copilot, Google Antigravity (todos suportam MCP)
- **Validação**: OpenAPI validators, JSON Schema, testes automáticos contra spec
- **Versionamento**: Git + branches para spec evolution

## Código prático

### Template SDD em Python para documentar sua própria spec

```python
# sdd_spec.py - Template para escrever specs estruturadas

from dataclasses import dataclass
from typing import List, Dict, Any
from enum import Enum

class BehaviorLevel(Enum):
    REQUIREMENT = "requirement"
    CONSTRAINT = "constraint"
    INVARIANT = "invariant"

@dataclass
class SpecComponent:
    """Uma unidade da spec"""
    name: str
    description: str
    inputs: Dict[str, str]  # {param_name: type}
    outputs: Dict[str, str]  # {param_name: type}
    behavior: str  # Descrição do comportamento
    examples: List[Dict[str, Any]]  # Casos de teste
    constraints: List[str]  # Validações
    level: BehaviorLevel

# Exemplo: spec de um componente de pagamento
payment_spec = SpecComponent(
    name="ProcessPayment",
    description="Processa um pagamento com validação de fraude",
    inputs={
        "amount": "float",
        "currency": "string",
        "customer_id": "string",
        "card_token": "string"
    },
    outputs={
        "transaction_id": "string",
        "status": "string",
        "timestamp": "datetime"
    },
    behavior="Valida amount > 0, currency em [USD,EUR,BRL], "
             "verifica fraude com terceiro, retorna transaction_id ou erro",
    examples=[
        {
            "input": {"amount": 100.50, "currency": "USD", 
                     "customer_id": "cust_abc123", "card_token": "tok_xyz"},
            "expected_output": {"status": "completed", "transaction_id": "txn_..."}
        },
        {
            "input": {"amount": 0, "currency": "USD", 
                     "customer_id": "cust_abc123", "card_token": "tok_xyz"},
            "expected_output": None,  # erro esperado
            "error": "amount must be > 0"
        }
    ],
    constraints=[
        "amount deve estar entre 0.01 e 999999.99",
        "currency deve estar em ISO 4217",
        "timeout de 30 segundos para decisão de fraude"
    ],
    level=BehaviorLevel.REQUIREMENT
)

# Seu agente LLM lê isso e sabe exatamente o que fazer
```

### Integração com agente: usar spec como prompt estruturado

```python
# prompt_generator.py - Converte spec em prompt otimizado para LLM

def spec_to_llm_prompt(spec: SpecComponent) -> str:
    """Converte SpecComponent em prompt estruturado para Claude/Copilot"""
    
    examples_str = "\n".join([
        f"Input: {ex['input']}\nExpected: {ex.get('expected_output', 'error: ' + ex.get('error', ''))}"
        for ex in spec.examples
    ])
    
    constraints_str = "\n".join([f"- {c}" for c in spec.constraints])
    
    return f"""
# Implement: {spec.name}

## Description
{spec.description}

## Contract
### Inputs
{json.dumps(spec.inputs, indent=2)}

### Outputs
{json.dumps(spec.outputs, indent=2)}

## Expected Behavior
{spec.behavior}

## Constraints
{constraints_str}

## Test Cases (MUST all pass)
{examples_str}

## Requirements
- Validate all inputs according to spec
- Return output matching specified type signature
- Handle all examples correctly
- Do not exceed 30-second timeout
"""
```

## Armadilhas e Limitações

### 1. **Spec Drift**: A spec virou ficção
A maioria dos projetos que adota SDD sofre de uma verdade incômoda: a spec não é atualizada quando requisitos mudam. Resultado: a spec que o agente segue é desatualizada, e o código gerado fica defasado em relação ao que o produto precisa.

**Mitigação**: Tratar spec como "artefato vivo". Use git branches para spec proposals. Integre spec updates no mesmo PR que muda código. Use linters que forçam consistência spec-código (OpenAPI linters detectam desvios).

### 2. **Hallucination do Agente apesar da Spec**
Mesmo com uma spec crystal-clear, LLMs podem "alucinar" validações não pedidas, lógica extra, ou esquecer casos de borda documentados. A spec reduz mas não elimina esse problema.

**Mitigação**: Validação em duas camadas:
1. Agente validador automatizado (não o agente que gerou código) checa código contra spec
2. Testes parametrizados que cobrem 100% dos exemplos da spec

```python
# Teste parametrizado que força cobertura total da spec
import pytest

@pytest.mark.parametrize("example", payment_spec.examples)
def test_process_payment_matches_spec(example):
    result = process_payment(**example['input'])
    
    if 'error' in example:
        assert result is None or result.status == 'failed'
    else:
        assert result.status == example['expected_output']['status']
        assert result.transaction_id.startswith('txn_')
```

### 3. **Specs muito genéricas ou muito específicas**
Spec vaga demais: agente gera código que passa tecnicamente mas não resolve o problema real. Spec muito específica sobre implementação: engessa agente, elimina flexibilidade arquitetural, vira "pseudo-código em YAML".

**Mitigação**: Especificar **comportamento observável** (inputs → outputs), não implementação. Ex: "valida que o amount > 0" (bom) vs. "usa função `validate_amount()` do módulo X" (ruim).

### 4. **Custo cognitivo de manter specs em múltiplas linguagens**
Se você tem APIs em Python, TypeScript e Go, manter uma spec OpenAPI única é ótimo. Mas specs de comportamento (_Gherkin_, stories) podem divergir quando traduzidas para contextos linguagem-específicos.

**Mitigação**: Spec de contrato (OpenAPI) é agnóstica e única. Spec de comportamento complexo usa Gherkin centralizado, com exemplos executáveis (BDD tools como Cucumber).

### 5. **Difícil validar specs geradas automaticamente**
Se você usa um agente para **gerar** specs a partir de requisitos textuais (meta!), pode gerar specs contraditórias ou incompletas. Incluir ciclos de validação não-escaláveis.

**Mitigação**: Specs são escritas por humanos; agentes as consomem, não as criam. Se você quer automação upstream, use BDD (Behavior-Driven Development) que começa com cenários humanos (Gherkin) e depois traduz para spec.

## Conexões

- [[separacao-de-responsabilidades-em-workflow-de-ia|Separação de Responsabilidades em Workflow de IA]] — SDD é um padrão de separação: spec define "o quê", agente implementa "como"
- [[claude-code-opera-com-26-prompts-especializados-organizados-em-camadas-funcionai|Claude Code com 26 Prompts Especializados]] — Claude Code já usa especificações internas estruturadas
- [[unity-mcp-integracao-llm-com-game-engine|Unity MCP Integração LLM com Game Engine]] — MCP expõe "specs" de ferramentas que agentes consomem
- [[skill-workflow-composition|Skill-Workflow Composition]] — Skills são specs de comportamento que agentes orquestram
- TDD vs SDD: TDD começa com testes; SDD começa com spec declarativa

## Perguntas de Revisão
1. Por que a qualidade da spec é mais crítica para agentes LLM do que a capacidade bruta do modelo?
2. Como você detectaria se uma spec está "driftando" em relação ao código em produção?
3. Qual é a diferença entre uma spec genérica (OpenAPI) vs. uma spec muito ligada a detalhes de implementação?

## Histórico de Atualizações
- 2026-04-02: Nota criada a partir de Telegram
- 2026-04-11: Expandida com exemplos de código, stack técnico, armadilhas, integração prática com agentes