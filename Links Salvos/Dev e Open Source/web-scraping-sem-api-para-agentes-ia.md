---
tags: [web-scraping, ia, agentes, automacao, dados, playwright, llm-extraction, mcp]
date: 2026-04-02
tipo: aplicacao
source: https://medium.com/@sal_50154/building-an-agentic-web-scraper-with-the-claude-agent-sdk-playwright-mcp-tips-tricks-and-06238776abc0
---
# Web Scraping Inteligente para Agentes IA: Playwright + Claude

## O que é
**Problema:** Website sem API. Você precisa dos dados. Solução tradicional? Parser CSS gigante que quebra quando o site atualiza.

**Solução melhor:** Navegador headless (Playwright) renderiza página completa, Claude lê HTML bruto e extrai estrutura via LLM. Resiliente a mudanças de layout porque Claude entende *semântica*, não CSS.

Workflow:
```
Playwright visita URL
    ↓ (JavaScript renderizado)
HTML completo (com conteúdo dinâmico)
    ↓
Claude API lê HTML
    ↓ (LLM parsing)
Dados estruturados (JSON)
```

## Por que importa agora
- **Resilience:** Layout muda? Claude adapta. CSS selectors quebram? Claude não.
- **Dinâmico:** Playwright renderiza JS, captcha não é bloqueador (ainda é problema, mas aí agende humano)
- **Escalável:** Uma LLM + Playwright consegue scrapar 100 tipos de sites diferentes
- **Sem manutenção:** Vs parser CSS que precisa de updates constantes
- **MCP native:** Playwright agora é Model Context Protocol (Claude Code/Agents já integrado)

## Como funciona / Como implementar

### 1. Architecture: Browser Automation + LLM Extraction

```
Arquitetura baseada em MCP:

┌─ Claude Agent
├─ Tool: playwright_navigate (URL)
├─ Tool: playwright_click (selector)
├─ Tool: playwright_type (text)
├─ Tool: playwright_get_visible_text (extrair texto)
└─ Tool: claude_extraction (parse texto com LLM)

Workflow:
1. Agent navega a URL
2. Agent vê HTML ou screenshot
3. Agent identifica o que scrapar
4. Agent extrai em JSON estruturado
```

### 2. Setup básico: Playwright + Claude API

```python
from playwright.async_api import async_playwright
from anthropic import Anthropic
import json

client = Anthropic()

async def scrape_products(url: str) -> list[dict]:
    """
    Scrape products from ecommerce site
    Returns: [{"name": str, "price": float, "url": str}, ...]
    """
    
    async with async_playwright() as p:
        # 1. Launch browser
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()
        
        # 2. Navigate
        await page.goto(url, wait_until='networkidle')
        
        # 3. Extract visible text (better than raw HTML)
        content = await page.get_by_role("main").inner_text()
        
        # 4. Ask Claude to parse
        response = client.messages.create(
            model="claude-opus-4",
            max_tokens=2048,
            messages=[{
                "role": "user",
                "content": f"""Extract all products from this page.
Return as JSON array.

Format:
[
  {{
    "name": "Product Name",
    "price": 99.99,
    "currency": "USD",
    "availability": "in stock" | "out of stock"
  }},
  ...
]

Page content:
{content}

Return ONLY valid JSON, no explanations."""
            }]
        )
        
        # 5. Parse and return
        try:
            products = json.loads(response.content[0].text)
        except json.JSONDecodeError:
            print("Claude returned invalid JSON, fallback parsing...")
            products = []
        
        await browser.close()
        return products

# Run
import asyncio
products = asyncio.run(scrape_products("https://example-shop.com"))
print(json.dumps(products, indent=2))
```

### 3. Advanced: Agentic scraping com múltiplas páginas

```python
async def scrape_paginated(base_url: str, max_pages: int = 5):
    """Scrape multiple pages automatically"""
    
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()
        
        all_products = []
        current_page = 1
        
        while current_page <= max_pages:
            # Navigate to page
            url = f"{base_url}?page={current_page}"
            await page.goto(url)
            
            # Extract
            content = await page.get_by_role("main").inner_text()
            
            # Ask Claude
            response = client.messages.create(
                model="claude-opus-4",
                max_tokens=2048,
                messages=[{
                    "role": "user",
                    "content": f"""Extract products and check if "Next page" button exists.

Return JSON:
{{
  "products": [...],
  "has_next": true | false
}}

Content:
{content}"""
                }]
            )
            
            try:
                data = json.loads(response.content[0].text)
                all_products.extend(data.get("products", []))
                
                if not data.get("has_next"):
                    break
            except:
                break
            
            current_page += 1
        
        await browser.close()
        return all_products
```

### 4. Usando Playwright MCP (native em Claude Code)

```python
# Se você está em Claude Code/Desktop
# Playwright MCP já disponível, pode usar direto

# Comando do Claude Code:
# /browser navigate https://example.com
# /browser click "button:has-text('Next')"
# /browser get-visible-text

# Retorna HTML cleaned
# Claude então extrai dados
```

### 5. Error handling + retries

```python
async def scrape_with_retry(
    url: str, 
    max_retries: int = 3,
    timeout: int = 30000
) -> dict:
    """Resilient scraping com retry logic"""
    
    for attempt in range(max_retries):
        try:
            async with async_playwright() as p:
                browser = await p.chromium.launch(headless=True)
                page = await browser.new_page(
                    viewport={'width': 1280, 'height': 720}
                )
                
                # Set timeout
                page.set_default_timeout(timeout)
                
                try:
                    await page.goto(url)
                    
                    # Wait for content to load
                    await page.wait_for_selector('[data-product]', timeout=5000)
                    
                    content = await page.content()
                    
                    # Extract
                    response = client.messages.create(
                        model="claude-opus-4",
                        max_tokens=2048,
                        messages=[{
                            "role": "user",
                            "content": f"Parse: {content}"
                        }]
                    )
                    
                    return json.loads(response.content[0].text)
                    
                finally:
                    await browser.close()
                    
        except Exception as e:
            print(f"Attempt {attempt+1} failed: {e}")
            if attempt < max_retries - 1:
                await asyncio.sleep(2 ** attempt)  # exponential backoff
            else:
                raise
```

## Stack técnico
- **Browser:** Playwright (suporte Python, JS, .NET)
- **LLM:** Claude API (claude-opus-4 melhor para parsing)
- **MCP:** Playwright MCP integrado em Claude Code
- **Async:** asyncio (Python), Promise (JS)
- **JSON parsing:** json (Python), JSON.parse (JS)
- **Storage:** Arquivo JSON, database, ou webhook
- **Rate limiting:** Respectar robots.txt, añade delays

## Código prático: Scraper completo com logging

```python
import asyncio
import json
import logging
from datetime import datetime
from typing import Optional
from playwright.async_api import async_playwright
from anthropic import Anthropic

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class SmartScraper:
    def __init__(self, api_key: Optional[str] = None):
        self.client = Anthropic(api_key=api_key)
    
    async def scrape(
        self,
        url: str,
        selector: str = "main",
        schema: dict = None
    ) -> list[dict]:
        """
        Smart scrape with LLM extraction
        
        Args:
            url: Website URL
            selector: CSS selector for content area
            schema: JSON schema for extraction
        """
        
        logger.info(f"Scraping {url}")
        
        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=True)
            page = await browser.new_page(
                user_agent='Mozilla/5.0 (compatible; SmartBot/1.0)'
            )
            
            try:
                # Navigate
                await page.goto(url, wait_until='networkidle', timeout=30000)
                logger.info(f"Loaded {url}")
                
                # Extract text
                element = page.locator(selector)
                if await element.is_visible():
                    content = await element.inner_text()
                else:
                    content = await page.content()
                
                # Use LLM to parse
                prompt = f"""Extract structured data from this content.

Schema:
{json.dumps(schema or {"items": []}, indent=2)}

Content:
{content[:3000]}

Return valid JSON matching schema."""
                
                response = self.client.messages.create(
                    model="claude-opus-4",
                    max_tokens=2048,
                    messages=[{"role": "user", "content": prompt}]
                )
                
                data = json.loads(response.content[0].text)
                logger.info(f"Extracted {len(data)} items")
                
                return data
                
            finally:
                await browser.close()

# Usage
async def main():
    scraper = SmartScraper()
    data = await scraper.scrape(
        url="https://example-shop.com/products",
        selector="[role='main']",
        schema={
            "products": [
                {"name": "string", "price": "number", "in_stock": "boolean"}
            ]
        }
    )
    
    # Save results
    with open("scraped_data.json", "w") as f:
        json.dump(data, f, indent=2)
    
    logger.info(f"Saved to scraped_data.json")

if __name__ == "__main__":
    asyncio.run(main())
```

## Armadilhas e limitações

### 1. **LLM hallucina dados que não existem**
Claude consegue inventar produtos que "parecia estar lá mas não estava".

```python
# ❌ RUIM
"Extract all products"  # Claude pode alucinar

# ✓ BOM
"Extract ONLY products you can see on the page.
If no products, return empty array.
Do not invent."
```

### 2. **Context window explode com muitos dados**
Se página tem 100K caracteres de HTML, isso consome tokens massivamente.

**Solução:** Extract `inner_text()` (visual apenas) em vez de `content()` (HTML bruto). Reduz 80%.

### 3. **Websites mudam rapidamente**
Estrutura muda, LLM extrai "wrong". Sem feedback loop, erro propagate silenciosamente.

**Solução:** Validação e schema enforcement. Se Claude retorna `{"price": "abc"}` (string), erro.

### 4. **Rate limiting e blocks**
Fazer 1K requisições Playwright + Claude = IP ban rápido.

**Solução:** 
- Delay entre requisições (random.uniform(1, 3) segundos)
- Respeitar robots.txt
- Rodar em VPS em locais diferentes
- User agents variados

### 5. **Capcha e autenticação não são triviais**
Se site precisa login ou tem capcha, Playwright sozinho não resolve. Precisa de humano ou Anti-Capcha API.

**Solução:** Detectar quando está bloqueado, alertar human, pausar.

### 6. **MCP Playwright é read-only para LLM**
Você não pode fazer Claude clicar em botoesautomaticamente via MCP padrão (security). Precisa de implementação customizada.

**Solução:** Rodar Playwright localmente via Python, passar HTML ao Claude.

## Conexões
- [[Playwright Documentation]]
- [[Anthropic API Data Extraction]]
- [[Browser Automation com Python]]
- [[Agentic Systems Architecture]]
- [[MCP Servers e Extensions]]
- [[Rate Limiting Strategies]]

## Histórico
- 2026-04-02: Nota original
- 2026-04-11: Reescrita com MCP integration, agentic patterns, classe SmartScraper completa, e 6 armadilhas
