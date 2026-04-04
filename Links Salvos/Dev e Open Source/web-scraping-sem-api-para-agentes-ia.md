---
tags: [web-scraping, ia, agentes, automacao, dados]
date: 2026-04-02
tipo: aplicacao
---
# Fazer Web Scraping Inteligente para Agentes de IA

## O que é
Quando não há API, scrapar página dinamicamente com navegador headless + LLM para extrair dados estruturados.

## Como implementar
```python
from playwright.async_api import async_playwright
from anthropic import Anthropic

async def scrape_with_ai(url):
    async with async_playwright() as p:
        browser = await p.chromium.launch()
        page = await browser.new_page()
        await page.goto(url)
        html = await page.content()
    
    client = Anthropic()
    response = client.messages.create(
        model="claude-opus-4",
        max_tokens=1024,
        messages=[{
            "role": "user",
            "content": f"Extraia produtos e preços em JSON de:
{html}"
        }]
    )
    
    return response.content[0].text

import asyncio
data = asyncio.run(scrape_with_ai("https://shop.example.com"))
```

## Stack e requisitos
- Playwright/Puppeteer: navegação
- Claude API: extração estruturada
- Parsing: BeautifulSoup (fallback)

## Histórico
- 2026-04-02: Reescrita
