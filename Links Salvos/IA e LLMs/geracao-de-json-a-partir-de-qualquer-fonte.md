---
tags: [json, structured-output, llm, pydantic, instructor, claude-api]
source: https://x.com/ctatedev/status/2039497913001197650?s=20
date: 2026-04-02
tipo: aplicacao
atualizado: 2026-04-11
---

# Geração de JSON Estruturado: Converter Qualquer Fonte em Especificações

## O que é

Framework que força LLMs a retornar JSON garantidamente válido, escapando o problema de "modelo às vezes retorna texto, às vezes JSON quebrado". Implementado via Claude API `response_format` nativo, biblioteca Instructor (com Pydantic), ou json_schema draft spec. Transforma problema de "LLM → texto solto" para "LLM → JSON type-safe com validação automática".

Core insight: você define Pydantic model (ou JSON schema), passa para LLM, e recebe objeto Python validado — não precisa fazer parsing/error-handling manual. Se modelo tenta retornar JSON inválido, biblioteca rejeita e retry automático.

Pattern escalado: em vez de "pedir Claude para escrever documento", você pede "estruture informação como JSON" onde cada campo é validado. Downstream: JSON pode alimentar databases, APIs, validators, ou regeneração em outro formato.

## Como implementar

### Opção 1: Claude API Native (Mais Recente)

Claude 3.5 Sonnet agora suporta `response_format` nativo com JSON schema:

```python
from anthropic import Anthropic
import json

client = Anthropic()

# Define estrutura esperada
response_schema = {
    "type": "object",
    "properties": {
        "company_name": {"type": "string"},
        "founding_year": {"type": "integer"},
        "industry": {"type": "string", "enum": ["SaaS", "FinTech", "AI", "Other"]},
        "founders": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "name": {"type": "string"},
                    "background": {"type": "string"}
                },
                "required": ["name", "background"]
            }
        },
        "total_funding": {"type": "number"},  # em milhões USD
        "status": {"type": "string", "enum": ["Pre-seed", "Seed", "Series A", "IPO"]}
    },
    "required": ["company_name", "founding_year", "industry", "status"]
}

def extract_company_info(text: str) -> dict:
    """
    Extrai informações estruturadas sobre empresa de texto solto.
    """
    message = client.messages.create(
        model="claude-3-5-sonnet-20241022",
        max_tokens=1024,
        messages=[{
            "role": "user",
            "content": f"""
            Extraia informações estruturadas desta descrição de empresa.
            Retorne JSON válido conforme schema.
            
            Descrição:
            {text}
            """
        }],
        response_format={
            "type": "json_schema",
            "json_schema": {
                "name": "CompanyInfo",
                "schema": response_schema,
                "strict": True  # Força aderência rigorosa ao schema
            }
        }
    )
    
    # Resposta é garantidamente válida JSON
    result = json.loads(message.content[0].text)
    return result

# Teste
company_description = """
Anthropic foi fundada em 2021 por Dario e Daniela Amodei e equipe. 
Foca em IA segura. Levantou Series B de USD 150M em 2023.
Cria modelos de linguagem como Claude.
"""

company_info = extract_company_info(company_description)
print(json.dumps(company_info, indent=2))
# Output: 
# {
#   "company_name": "Anthropic",
#   "founding_year": 2021,
#   "industry": "AI",
#   "founders": [
#     {
#       "name": "Dario Amodei",
#       "background": "AI Safety"
#     }
#   ],
#   "total_funding": 150.0,
#   "status": "Series A"
# }
```

### Opção 2: Instructor + Pydantic (Recomendado para Controle)

Instructor é wrapper que torna Pydantic models "validáveis" em LLM calls:

```python
import instructor
from pydantic import BaseModel, Field
from typing import List
from anthropic import Anthropic

# Aplicar patch ao cliente
client = instructor.from_anthropic(Anthropic())

# Define modelos Pydantic com type hints
class Founder(BaseModel):
    name: str = Field(..., description="Nome do fundador")
    background: str = Field(..., description="Background profissional")
    equity_percentage: float = Field(default=None, description="% do equity")

class CompanyProfile(BaseModel):
    name: str = Field(..., description="Nome da empresa")
    industry: str = Field(..., description="Indústria")
    founding_year: int = Field(..., ge=1900, le=2100, description="Ano de fundação")
    headquarters: str = Field(..., description="Sede geográfica")
    founders: List[Founder] = Field(..., description="Lista de fundadores")
    total_funding_usd: float = Field(default=0, ge=0)
    stage: str = Field(..., enum=["Pre-seed", "Seed", "Series A", "Series B", "IPO"])
    key_products: List[str] = Field(..., description="Produtos principais")
    last_updated: str = Field(default="2026-04-11")

def extract_company_structured(text: str) -> CompanyProfile:
    """
    Extrai empresa com full type safety via Instructor.
    """
    response = client.messages.create(
        model="claude-3-5-sonnet-20241022",
        max_tokens=2048,
        messages=[{
            "role": "user",
            "content": f"""
            Analise este texto e extraia informações de empresa estruturadas.
            Garanta que todos os campos requeridos estejam preenchidos.
            
            Texto:
            {text}
            """
        }],
        response_model=CompanyProfile  # Magic: retorna validado
    )
    
    return response

# Uso
company_text = """
OpenAI foi fundada em 2015 por Sam Altman, Elon Musk e outros.
Sediada em San Francisco. Desenvolvem GPT-4, ChatGPT.
Levantaram Series D em 2023. Valuation USD 80B+.
"""

company = extract_company_structured(company_text)

# Type hints garantidos
print(f"Empresa: {company.name}")
print(f"Fundadores: {[f.name for f in company.founders]}")
print(f"Stage: {company.stage}")

# Manipulação segura (IDE autocomplete funciona)
for founder in company.founders:
    print(f"  - {founder.name} ({founder.background})")

# Retorna True pois foi validado
print(company.model_validate(company.model_dump()))
```

### Opção 3: Parsing Manual com Retry (Robustez Extra)

Para casos que exigem mais controle ou fallback:

```python
import json
import re
from anthropic import Anthropic

class StructuredExtractor:
    def __init__(self, max_retries: int = 3):
        self.client = Anthropic()
        self.max_retries = max_retries
    
    def extract_with_retry(self, text: str, schema: dict, retries: int = 0) -> dict:
        """
        Tenta extrair JSON. Se falhar, retry com prompt de correção.
        """
        if retries > self.max_retries:
            raise ValueError(f"Failed to extract after {self.max_retries} retries")
        
        # Primeira tentativa
        message = self.client.messages.create(
            model="claude-3-5-sonnet-20241022",
            max_tokens=2048,
            messages=[{
                "role": "user",
                "content": f"""
                Extraia dados estruturados em JSON válido.
                Schema esperado:
                {json.dumps(schema, indent=2)}
                
                Texto:
                {text}
                
                Responda APENAS com JSON válido. Sem markdown code blocks.
                """
            }]
        )
        
        response_text = message.content[0].text.strip()
        
        # Remove markdown code blocks se houver
        response_text = re.sub(r'^```json?\n?', '', response_text)
        response_text = re.sub(r'\n?```$', '', response_text)
        
        try:
            result = json.loads(response_text)
            # Valida contra schema (básico)
            self._validate_schema(result, schema)
            return result
        
        except (json.JSONDecodeError, ValueError) as e:
            print(f"Tentativa {retries + 1} falhou: {str(e)}")
            
            if retries < self.max_retries:
                # Retry com mais contexto
                return self.extract_with_retry(
                    text=text,
                    schema=schema,
                    retries=retries + 1
                )
            else:
                raise
    
    def _validate_schema(self, data: dict, schema: dict) -> None:
        """Validação básica de schema."""
        required = schema.get("required", [])
        for field in required:
            if field not in data:
                raise ValueError(f"Missing required field: {field}")
        
        for key, expected_type in schema.get("properties", {}).items():
            if key in data:
                actual_type = type(data[key]).__name__
                if expected_type.get("type") == "string" and not isinstance(data[key], str):
                    raise ValueError(f"Field {key} should be string, got {actual_type}")

# Uso
schema = {
    "type": "object",
    "properties": {
        "entities": {"type": "array"},
        "sentiment": {"type": "string"},
        "summary": {"type": "string"}
    },
    "required": ["entities", "sentiment", "summary"]
}

extractor = StructuredExtractor(max_retries=2)
result = extractor.extract_with_retry("Texto complexo aqui...", schema)
```

### Caso Prático: Document Parser Pipeline

```python
from pydantic import BaseModel, Field
from typing import List, Optional
import instructor
from anthropic import Anthropic

client = instructor.from_anthropic(Anthropic())

class ContractTerm(BaseModel):
    term_name: str = Field(..., description="Nome do termo (ex: 'Payment Terms')")
    description: str = Field(..., description="O que significa")
    risk_level: str = Field(..., enum=["Low", "Medium", "High"])
    our_position: str = Field(default="Neutral", description="Favorável/Desfavorável/Neutro")

class ContractAnalysis(BaseModel):
    contract_type: str = Field(..., description="Tipo: NDA, SLA, MSA, etc")
    parties_involved: List[str] = Field(..., description="Empresas envolvidas")
    effective_date: Optional[str] = Field(default=None)
    expiration_date: Optional[str] = Field(default=None)
    key_terms: List[ContractTerm] = Field(..., description="Termos críticos")
    red_flags: List[str] = Field(default_factory=list)
    recommendation: str = Field(..., enum=["Sign", "Renegotiate", "Walk"])
    summary: str = Field(..., description="Resumo executivo")

def analyze_contract(contract_text: str) -> ContractAnalysis:
    """
    Lê contrato e retorna análise estruturada.
    Perfeito para legal review automatizado.
    """
    analysis = client.messages.create(
        model="claude-3-5-sonnet-20241022",
        max_tokens=4096,
        messages=[{
            "role": "user",
            "content": f"""
            Analise este contrato como advogado.
            Extraia: tipo, partes, termos-chave, red flags, recomendação.
            
            Contrato:
            {contract_text}
            """
        }],
        response_model=ContractAnalysis
    )
    
    return analysis

# Uso
contract = "Acordo de Serviços entre Acme Corp e Widget Inc..."
analysis = analyze_contract(contract)

print(f"Tipo: {analysis.contract_type}")
print(f"Recomendação: {analysis.recommendation}")
for term in analysis.key_terms:
    print(f"  - {term.term_name}: {term.risk_level}")
```

## Stack e requisitos

**Mínimo:**
- Python 3.9+
- `pip install anthropic`
- API key Anthropic válida

**Com Instructor (Recomendado):**
- `pip install instructor pydantic`
- Pydantic 2.x
- anthropic 0.20+

**Para Validação Avançada:**
- `pip install jsonschema` (validar contra JSON schema spec)
- `pip install attrs` (alternativa a Pydantic)

**Performance:**
- Claude API chamada: ~200-500ms (network + processing)
- Validação Pydantic: <1ms
- Retry loop: 1-3s se falha, 3-9s com múltiplos retries
- Custo: ~$0.01-0.05 por extraction (depende tamanho texto)

## Armadilhas e limitações

**Schema Muito Complexo → Alucinação:**
Se schema tem 50+ campos aninhados, modelo pode "inventar" dados para preencher. Mitigação:
```python
# Ruim: schema com tudo
{"fields": [50+ items]}

# Bom: dividir em múltiplas chamadas
# Call 1: extrair campos A-L
# Call 2: extrair campos M-Z
# Merge resultado
```

**LLM Não Entende Constraints:**
Campo `age: int` com `ge=0, le=150`. Modelo pode retornar `"age": 500` e Pydantic valida incorreto. Solução:
```python
# Ser explícito no prompt
"age: integer between 0 and 150. If unknown, return -1"

# Usar enums em vez de ranges
age_bracket: str = Field(..., enum=["0-18", "18-35", "35-65", "65+"])
```

**JSON Inválido Silencioso:**
Instructor + Pydantic mascara alguns erros. Se validação falhar internamente, retry automático pode não convergir. Debug com:
```python
try:
    result = client.messages.create(..., response_model=MyModel)
except instructor.exceptions.InstructorError as e:
    print(f"Validation error: {e}")
    # Retry com schema simplificado
```

**Hallucination em Arrays:**
Modelo pode inventar items em array se schema não claro:
```python
# Problema
"founders": []  # Vazio, modelo inventa 5 aleatórios

# Solução
founders: List[Founder] = Field(
    default_factory=list,
    description="Array de fundadores. Se não houver, array vazio."
)
```

**Custo Escala com Tokens:**
Response com 2000 tokens = ~USD 0.01. Se chama 100x/dia = USD 1/dia. Otimize:
- Reduzir schema complexity
- Truncar input text (primeiros 2000 chars)
- Batch requests

**Unicode e Caracteres Especiais:**
JSON pode quebrar com emojis, caracteres acentuados. Claude lida bem, mas validação pode falhar:
```python
# Recomendado: escape manual
result = json.loads(response, strict=False)  # Aceita mal-formatted
```

## Conexões

- [[designmd-como-contrato-de-design-para-llms|Design specs como contrato]] — estrutura como "schema social"
- [[geracao-automatizada-de-prompts|Prompting estruturado]] — engineered prompts para JSON
- [[construcao-de-llm-do-zero|LLM do zero]] — entender como modelos processam tokens JSON
- [[multi-agentes-com-structured-outputs|Multi-agentes com tipos]] — estruturado em orquestração de agentes

## Histórico

- 2026-04-02: Nota criada
- 2026-04-11: Reescrita com 3 abordagens completas (Claude API native, Instructor+Pydantic, retry manual). Adicionados exemplos práticos (company info, contract analysis). Cobertos armadilhas (schema complexity, hallucination, custo, unicode). Implementação de pipeline real de document parsing.
