---
tags: [vibecoding, desenvolvimento, ia, cursor, claude-code, comunidade, code-review, testing]
source: https://medium.com/@addyosmani/vibe-coding-is-not-the-same-as-ai-assisted-engineering-3f81088d5b98
date: 2026-04-11
tipo: aplicacao
---

# Vibecoding: Discussão da Comunidade Reddit e Melhores Práticas

## O que é

Vibecoding é uma metodologia de desenvolvimento onde você "se rende às vibes" e deixa IA escrever o código enquanto você focam em intenção de alto nível. Você descreve o que quer em linguagem natural, um modelo de IA (Claude, Cursor, GitHub Copilot) gera o código-fonte, e você valida, testa e itera. O termo foi popularizado por Andrej Karpathy (co-founder OpenAI) em fevereiro de 2025 e, em 2026, evoluiu de um buzz em social media para uma mudança fundamental em como software é construído — 92% dos desenvolvedores dos EUA já adotaram alguma forma de vibecoding.

A comunidade Reddit (r/vibecoding, 89K membros) discute intensamente dois tópicos: (1) quando vibecoding funciona bem e (2) seus perigos reais — segurança, qualidade, manutenibilidade. Não é "escrever código em português e esperar magic", é um workflow estruturado com code review, testes, e responsabilidade humana no final.

## Como implementar

### Entendendo o Workflow Correto de Vibecoding

Vibecoding **não é** bater um prompt e usar código gerado direto em produção. É um ciclo estruturado:

```
1. PRD (Product Requirements Doc) → Define claro what/why/edge-cases
    ↓
2. Prompt Detalhado → Seja específico com contexto
    ↓
3. Geração de Código (Claude/Cursor)
    ↓
4. Code Review (sua responsabilidade!) → Ler cada linha
    ↓
5. Testes → Happy path + unhappy path
    ↓
6. Deploy com Monitoramento → Watch error rates
```

### Passo 1: Escrever um PRD Antes

Isso é a chave que a comunidade Reddit subvaloriza. Um PRD claro é o "mapa" que seu AI segue:

```markdown
# PRD: Sistema de Carrinho de Compras

## O que
API REST para gerenciar carrinho de compras de e-commerce.

## Casos de Uso
- Usuário adiciona produto (verifica stock antes)
- Usuário remove produto
- Usuário aplica cupom desconto (validar cupom)
- Usuário checkout (charge stripe)

## Edge Cases
- Stock = 0: returnar erro específico, não silenciar
- Cupom expirado: rejeitar com mensagem clara
- Falha de pagamento: não remover itens do carrinho
- Usuário anônimo: não permitir, redirecionar para login

## Dados
- Product: {id, name, price, stock}
- Cart: {user_id, items: [{product_id, quantity, price_snapshot}], created_at}

## Erro Handling
- 400: Bad request (missing fields)
- 401: Not authenticated
- 409: Stock conflict (item out of stock)
- 500: Server error (log to Sentry)
```

Agora prompta seu AI:

```
Implementa API Cart seguindo este PRD:
[colar PRD acima]

Tech stack: Python FastAPI, PostgreSQL, Stripe SDK.

Validações críticas:
- Toda rota validar autenticação (JWT)
- Stock check antes de adicionar
- Cupom expiration no apply_coupon
```

### Passo 2: Usar Ferramentas Apropriadas

A comunidade debata qual tool é melhor. Consenso 2026:

**Para prototyping rápido:**
- Claude Code (artifacts online, grátis)
- Cursor (integrado no editor, $20/mês)
- v0 (Vercel, UI components)

**Para code review integrado:**
- Cursor + `.cursorrules` file

**Para geração batch (pipeline):**
- Claude API direct (mais barato, mais controle)

**Para múltiplos prompts em sequência:**
- Chatbot UI (Claude web) com artifacts iterativos

### Passo 3: Implementar Code Review Obsessivo

A crítica #1 da comunidade: devs ignoram o código gerado. **Leia todo o código.**

```python
# Exemplo ruim (do Reddit):
# "Cursor gerou isto, parece OK, mergeei direto"

async def process_payment(user_id, amount, stripe_token):
    # PROBLEMA: nenhuma validação de token
    # PROBLEMA: nenhum try-catch para Stripe API timeout
    # PROBLEMA: nenhum log de transação
    charge = stripe.Charge.create(
        amount=int(amount * 100),
        currency="usd",
        source=stripe_token
    )
    return {"status": "success"}

# Exemplo bom (como a comunidade recommenda):
async def process_payment(user_id: int, amount: float, stripe_token: str):
    # Validar token existe
    if not stripe_token or len(stripe_token) < 10:
        raise ValueError("Invalid Stripe token")
    
    # Validar amount > 0
    if amount <= 0:
        raise ValueError("Amount must be positive")
    
    try:
        charge = stripe.Charge.create(
            amount=int(amount * 100),
            currency="usd",
            source=stripe_token,
            idempotency_key=f"{user_id}-{int(time.time())}"  # Evita charges duplicate
        )
        
        # Log para auditoria
        logger.info(f"Payment processed: user={user_id}, amount={amount}, charge_id={charge.id}")
        
        return {"status": "success", "charge_id": charge.id}
    
    except stripe.error.CardError as e:
        logger.error(f"Card declined: {e.user_message}")
        raise HTTPException(status_code=402, detail="Card declined")
    
    except stripe.error.APIError as e:
        logger.error(f"Stripe API error: {e}", exc_info=True)
        raise HTTPException(status_code=503, detail="Payment service temporarily unavailable")
```

**Checklist de Code Review (da comunidade):**

- [ ] Todas as funções têm type hints?
- [ ] Existem try-catch em chamadas externas (APIs, DB)?
- [ ] Validação de input em toda rota?
- [ ] Auth check em todos endpoints?
- [ ] SQL queries usam prepared statements (nunca string concat)?
- [ ] Erro messages são legíveis (não stack traces expostos)?
- [ ] Logging em pontos críticos (payment, auth, errors)?
- [ ] Edge cases cobertos (empty list, null, 0, negative)?
- [ ] Rate limiting em rotas públicas?
- [ ] Nenhuma hardcoded secrets (API keys, tokens)?

### Passo 4: Testes Sistemáticos (Happy + Unhappy Path)

Vibecoding pitfall #1: devs testam happy path, não edge cases.

```python
import pytest
from app import create_cart, add_item, apply_coupon

# HAPPY PATH
def test_add_item_success():
    cart = create_cart(user_id=1)
    add_item(cart, product_id=10, quantity=2)
    assert len(cart.items) == 1
    assert cart.items[0].quantity == 2

# UNHAPPY PATHS (frequentemente ignorados no vibecoding!)

def test_add_item_stock_zero():
    """Produto fora de estoque deve falhar, não silenciar."""
    cart = create_cart(user_id=1)
    with pytest.raises(ValueError, match="Out of stock"):
        add_item(cart, product_id=999, quantity=1)  # product_id 999 tem stock=0

def test_add_item_negative_quantity():
    """Quantity negativa é inválida."""
    cart = create_cart(user_id=1)
    with pytest.raises(ValueError, match="Quantity must be positive"):
        add_item(cart, product_id=10, quantity=-5)

def test_apply_expired_coupon():
    """Cupom expirado deve ser rejeitado."""
    cart = create_cart(user_id=1)
    add_item(cart, product_id=10, quantity=1)
    with pytest.raises(ValueError, match="Coupon expired"):
        apply_coupon(cart, coupon_code="EXPIRED2025")

def test_apply_coupon_to_empty_cart():
    """Cupom em carrinho vazio não faz sentido."""
    cart = create_cart(user_id=1)
    with pytest.raises(ValueError, match="Cart is empty"):
        apply_coupon(cart, coupon_code="VALID10")

def test_concurrent_stock_decrement():
    """Dois usuários pegam último item simultaneamente?"""
    # Simula race condition
    from concurrent.futures import ThreadPoolExecutor
    cart1 = create_cart(user_id=1)
    cart2 = create_cart(user_id=2)
    
    def try_add():
        try:
            add_item(cart1, product_id=lastitem, quantity=1)
            return True
        except ValueError:
            return False
    
    with ThreadPoolExecutor(max_workers=2) as executor:
        results = list(executor.map(lambda _: try_add(), range(2)))
    
    # Exatamente 1 deve ter sucesso
    assert sum(results) == 1
```

**Comandos para rodar:**
```bash
# Rodar todos testes
pytest tests/

# Rodar com cobertura
pytest --cov=app tests/

# Mostrar quais linhas NÃO foram testadas
pytest --cov=app --cov-report=html tests/
# Abre htmlcov/index.html para ver gaps
```

### Passo 5: Configurar .cursorrules para Orientação Automática

Se usando Cursor, crie `.cursorrules` na raiz do projeto:

```
# .cursorrules
You are an expert Python/FastAPI developer.

## Security Rules
- ALWAYS validate all user inputs
- NEVER hardcode secrets (use .env)
- ALWAYS use parameterized queries (no SQL injection)
- For payment APIs: use idempotency keys to prevent double-charge

## Code Quality
- Type hints on every function
- Docstrings on public functions
- Error handling with specific exceptions (not generic Exception)
- Logging: INFO for important events, ERROR for failures

## Testing
- Write tests BEFORE implementation if possible
- Happy path + 3 unhappy paths minimum
- Test concurrent scenarios if applicable

## When generating code
- Ask clarifying questions if requirements are unclear
- Suggest edge cases I might have missed
- Recommend libraries (requests, sqlalchemy, pydantic)
- Include example usage in docstrings
```

Agora, quando você pede a Cursor para gerar código, ele segue estas regras.

### Passo 6: Monitoramento em Produção

Vibecoding não termina no deploy. Reddit stories: "código rodava bem em teste, quebrou em produção com volume real."

```python
# Instrumentar código gerado com observabilidade

from sentry_sdk import capture_exception
import logging

logger = logging.getLogger(__name__)

async def checkout(cart_id: int):
    try:
        # Seu código...
        charge = stripe.Charge.create(...)
        
        # IMPORTANTE: monitore erro rates
        logger.info(f"checkout_success", extra={
            "cart_id": cart_id,
            "amount": cart.total,
            "timestamp": datetime.now().isoformat()
        })
        
        return {"status": "success"}
    
    except Exception as e:
        # Capture para Sentry
        capture_exception(e)
        
        # Log estruturado
        logger.error("checkout_failed", extra={
            "cart_id": cart_id,
            "error_type": type(e).__name__,
            "timestamp": datetime.now().isoformat()
        })
        
        raise
```

Depois, configurar alertas no Sentry/Datadog para anomalias.

## Stack e requisitos

### Ferramentas Principais (2026)

| Tool | Custo | Quando Usar | Sintaxe |
|------|-------|------------|---------|
| Claude Code (web) | Grátis | Prototipagem rápida | Python/JS/Any |
| Cursor | $20/mês | Coding diário, review integrado | Multi-language |
| GitHub Copilot | $10/mês | VS Code integrado | Python/JS/Go |
| Claude API direct | Pay-per-token | Automação, batch generation | Python SDK |
| v0 (Vercel) | Free tier | React components | JSX/Tailwind |

### Linguagens Recomendadas (por comunidade)

**Bem-estabelecido em vibecoding:**
- Python (fastapi, django, flask)
- JavaScript/TypeScript (nextjs, react)
- Go (simple syntax, menos alucinações)

**Experimental (mais erros):**
- Rust (ownership rules, AI acha confuso)
- C++ (memory management, geração ruim)

### Dependências Python Típicas

```bash
# Para web API + testes
pip install fastapi uvicorn sqlalchemy pydantic pytest pytest-cov

# Para payment processing
pip install stripe

# Para logging/monitoring
pip install python-json-logger sentry-sdk

# Para validation
pip install pydantic-validator

# Para async code
pip install asyncio httpx
```

### Hardware
- Qualquer máquina com IDE: Cursor/VS Code roda em laptop básico
- Se rodando modelos locais: ver nota anterior (Ollama lab)
- Internet obrigatória: Cursor e Claude Code precisam conexão

## Armadilhas e limitações

### 1. Vibecoding Não Substitui Code Review

**Armadilha (#1 no Reddit):**
```python
# Dev pede: "Gere um login system"
# Cursor gera 500 linhas
# Dev: "Parece OK" (nunca leu)
# Resultado: SQL injection vulnerability encontrada em produção
```

**Realidade:** Você PRECISA ler código gerado. Não é "human-less". É "human-directed".

**Mitigação:** 
- PR review com peer adicional
- Ferramentas de análise estática (Bandit para segurança Python)
- Testes de penetração básicos

### 2. IA Alucina Dependências e APIs

```python
# Prompt: "Use biblioteca XYZ para gerar QR codes"
# Claude gera:
import qrcode_xyz  # Não existe!
qrcode_xyz.generate(data)

# Real:
import qrcode  # Biblioteca correta
qr = qrcode.QRCode()
qr.add_data(data)
```

**Comunidade Reddit recomenda:**
- Verificar `pip search` / PyPI antes de usar lib gerada
- Manter `requirements.txt` limpo (auditável)
- Setups não-padrão falham mais (ex: ARM64 architecture)

### 3. Testes Gerados São Incompletos

IA gera happy path, ignora edge cases críticos.

```python
# IA gera:
def test_payment():
    assert process_payment(100) == True  # Only happy path!

# Deveria ter:
def test_payment():
    assert process_payment(100) == True
    assert process_payment(-50) raises ValueError
    assert process_payment(None) raises TypeError
    assert process_payment(huge_number) handles rate limit
```

**Solução:** Sempre revise testes gerados, adicione seus próprios.

### 4. Quantização de Conhecimento

Modelos "esquecem" coisas em prompts longos. Se seu PRD tem 2000 palavras, a geração pode violar reqs do meio do documento.

```python
# Prompt tem: "Validar CPF antes de processar"
# Mas depois no PRD, há 1000 linhas de contexto
# Código gerado: ignora validação CPF!
```

**Workaround:**
- PRDs concisos (máximo 500 palavras)
- Repetir reqs críticas ("CRITICAL: Always validate CPF")
- Dividir em múltiplos prompts se precisa muita coisa

### 5. Segurança Negligenciada

Maior crítica da comunidade: vibecoding pode levar a vulnerabilidades sistemáticas.

```python
# Perigo 1: SQL Injection
query = f"SELECT * FROM users WHERE id = {user_input}"  # Gerado por IA
# Correto:
query = "SELECT * FROM users WHERE id = ?"
conn.execute(query, (user_input,))

# Perigo 2: CORS aberto
app.add_middleware(CORSMiddleware, allow_origins=["*"])  # Generado por IA
# Correto:
app.add_middleware(CORSMiddleware, allow_origins=["https://seu-dominio.com"])

# Perigo 3: Secrets em logs
logger.info(f"User authenticated with password: {password}")  # IA gerou!
```

**Community safeguards:**
- `.cursorrules` explícito sobre segurança
- SAST (Static Analysis Security Testing) no CI/CD
- Rodas SonarQube ou similar

### 6. Performance Desconhecida

Código gerado pode ser ineficiente:

```python
# IA gera (N+1 query):
def get_user_posts(user_id):
    user = db.query(User).filter(User.id == user_id).first()
    for post in user.posts:  # Query por cada post!
        print(post.title)

# Correto (eager loading):
def get_user_posts(user_id):
    user = db.query(User).options(
        joinedload(User.posts)
    ).filter(User.id == user_id).first()
```

**Solução:** Profiling com `cProfile` ou APM tools.

## Conexões

[[entender-arquitetura-agents-ia|Como entender e construir agents IA com Claude]]
[[python-testing-pytest-tdd|Test-Driven Development com pytest e boas práticas]]
[[seguranca-owasp-top10|OWASP Top 10 e segurança em APIs web]]

## Historico

- 2026-04-11: Nota criada com pesquisa profunda de comunidade Reddit, best practices de code review, e armadilhas reais
- Fontes: Medium (Addy Osmani), DEV Community, Reddit r/vibecoding (89K membros), múltiplos blogs de best practices
