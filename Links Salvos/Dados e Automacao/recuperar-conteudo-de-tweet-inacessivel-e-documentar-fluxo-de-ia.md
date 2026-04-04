---
tags: []
source: https://x.com/i/status/2027074800431370564
date: 2026-04-03
tipo: aplicacao
---
# Recuperar Conteudo de Tweet Inacessivel e Documentar Fluxo de IA

## O que e

Este link aponta para um tweet/post no X (ex-Twitter) que estava inacessível no momento da captura, pois o JavaScript estava desabilitado ou o conteúdo não pôde ser renderizado. O desafio prático aqui é duplo: recuperar o conteúdo original do post e construir um fluxo robusto para capturar, arquivar e processar conteúdo de redes sociais antes que ele se torne inacessível. Isso importa porque posts técnicos no X costumam desaparecer, serem deletados ou ficarem atrás de bloqueios — e um sistema de arquivamento ativo é a única defesa real.

## Como implementar

**1. Tentativa de recuperação do conteúdo original**

O primeiro passo é tentar recuperar o tweet original usando ferramentas de cache e arquivamento público. Acesse o Wayback Machine em `https://web.archive.org/web/*/https://x.com/i/status/2027074800431370564` para verificar se houve snapshot. Paralelamente, consulte o Google Cache digitando `cache:x.com/i/status/2027074800431370564` na busca — embora o Google raramente indexe posts individuais do X, vale tentar. Outra opção é o `nitter.net` (ou instâncias alternativas como `nitter.privacydev.net`), que renderiza tweets sem JavaScript: acesse `https://nitter.privacydev.net/i/status/2027074800431370564`. Se o ID do tweet for válido, o Nitter frequentemente consegue exibir o conteúdo mesmo quando o X nativo falha.

**2. Usar a API do X (Twitter API v2) para buscar o tweet diretamente**

Se você tiver acesso à Twitter API v2 (nível Basic ou acima), pode buscar o tweet pelo ID programaticamente:

```bash
curl -X GET "https://api.twitter.com/2/tweets/2027074800431370564?tweet.fields=text,author_id,created_at,entities" \
  -H "Authorization: Bearer SEU_BEARER_TOKEN"
```

Isso retorna o conteúdo bruto em JSON, independente de JavaScript no browser. Para configurar: crie um app em `developer.twitter.com`, gere o Bearer Token, e use o endpoint `GET /2/tweets/:id`. O plano gratuito (Free tier) permite leitura limitada; o plano Basic (U$100/mês) oferece acesso mais amplo. Guarde o JSON retornado em arquivo local imediatamente.

**3. Construir um pipeline de arquivamento preventivo com Python**

Para evitar este problema no futuro, implemente um arquivador automático. Instale as dependências:

```bash
pip install tweepy requests playwright python-dotenv
playwright install chromium
```

Crie um script `archiver.py` que, ao receber uma URL de tweet, faz três coisas em paralelo: (a) busca via API com `tweepy.Client`, (b) tira screenshot com `playwright` renderizando a página completa, e (c) envia para o Wayback Machine via `requests.post("https://web.archive.org/save/URL")`. Use variáveis de ambiente via `python-dotenv` para gerenciar tokens. Estruture o output em pastas organizadas por data: `archive/2026-04-03/tweet_ID/` contendo `data.json`, `screenshot.png` e `metadata.txt`.

**4. Alternativa sem API: scraping com Playwright (modo headed)**

Se não tiver acesso à API, use Playwright com Chromium em modo autenticado:

```python
from playwright.sync_api import sync_playwright

with sync_playwright() as p:
    browser = p.chromium.launch(headless=False)
    context = browser.new_context(storage_state="auth.json")
    page = context.new_page()
    page.goto("https://x.com/i/status/2027074800431370564")
    page.wait_for_selector("article[data-testid='tweet']", timeout=10000)
    content = page.inner_text("article[data-testid='tweet']")
    page.screenshot(path="tweet_screenshot.png", full_page=True)
    print(content)
    browser.close()
```

Para gerar o `auth.json`, execute `playwright codegen x.com` e faça login manualmente — o Playwright salva os cookies de sessão. Isso contorna o bloqueio de JavaScript pois o browser real executa tudo normalmente.

**5. Processar e estruturar o conteúdo recuperado com LLM**

Uma vez recuperado o texto bruto (seja via API, Nitter ou Playwright), passe pelo pipeline de processamento: use um LLM local (ex: Ollama com `llama3.2` ou `qwen2.5`) para extrair estrutura — ferramentas mencionadas, comandos, links, conceitos-chave. Prompt sugerido:

```
Dado este conteúdo de tweet técnico: [CONTEÚDO]
Extraia em JSON:
- ferramentas_mencionadas: []
- comandos: []
- conceitos_chave: []
- resumo_tecnico: ""
- links_externos: []
```

Integre isso ao seu vault do Obsidian via script Python que escreve automaticamente o arquivo `.md` com frontmatter preenchido.

**6. Criar um fluxo de entrada via Telegram Bot para captura imediata**

Como a fonte original é o Telegram, configure um bot que receba URLs de tweets colados no chat e dispare o pipeline automaticamente. Use `python-telegram-bot`:

```python
from telegram.ext import ApplicationBuilder, MessageHandler, filters

async def handle_url(update, context):
    url = update.message.text
    if "x.com" in url or "twitter.com" in url:
        tweet_id = url.split("/")[-1]
        result = archive_tweet(tweet_id)  # sua função de arquivamento
        await update.message.reply_text(f"Arquivado: {result}")

app = ApplicationBuilder().token("SEU_BOT_TOKEN").build()
app.add_handler(MessageHandler(filters.TEXT, handle_url))
app.run_polling()
```

Assim, qualquer tweet interessante enviado para o bot é arquivado automaticamente antes que desapareça.

## Stack e requisitos

- **Linguagem:** Python 3.11+
- **Libs principais:** `tweepy>=4.14`, `playwright>=1.42`, `python-telegram-bot>=21.0`, `requests>=2.31`, `python-dotenv>=1.0`
- **API do X:** Bearer Token (plano Free para leitura básica; plano Basic U$100/mês para volume maior)
- **Telegram Bot API:** gratuita via @BotFather
- **Alternativas sem API:** Nitter (instâncias públicas, sem custo), Wayback Machine (gratuito, save API)
- **LLM local para processamento:** Ollama com `llama3.2:3b` (mínimo 4GB RAM) ou `qwen2.5:7b` (mínimo 8GB RAM, recomendado 6GB VRAM para GPU)
- **Hardware mínimo:** qualquer máquina com 8GB RAM para rodar sem GPU; com GPU NVIDIA 6GB+ para inferência rápida
- **Armazenamento:** ~500KB por tweet arquivado (JSON + screenshot PNG comprimido)
- **Custo estimado:** U$0 a U$100/mês dependendo do volume e nível de API

## Armadilhas e limitacoes

**Instâncias Nitter instáveis:** A maioria das instâncias públicas do Nitter cai ou é bloqueada regularmente pelo X. Mantenha uma lista atualizada de instâncias em `https://status.d420.de/` e implemente fallback automático entre elas no seu código.

**Rate limiting severo da API do X:** O plano gratuito permite apenas 1 requisição de leitura de tweet a cada 15 minutos no endpoint de busca por ID. Para volume real, o plano Basic é necessário — considere se o custo vale para o seu caso de uso.

**Bloqueio de scraping com Playwright:** O X implementa detecção anti-bot progressiva. Sessions autenticadas duram mais, mas eventualmente são detectadas. Não use headless puro sem stealth patches em produção; considere `playwright-stealth` ou `undetected-playwright`.

**Tweet ID inválido ou conteúdo deletado:** Se o tweet foi deletado antes do arquivamento, nenhuma das técnicas acima recupera o conteúdo — apenas o Wayback Machine (se houve snapshot anterior) pode ajudar. O arquivamento preventivo, disparado no momento do salvamento da URL, é a única solução real.

**Contexto perdido:** Tweets que são replies perdem contexto sem os tweets pais. Implemente busca recursiva de `conversation_id` via API para reconstruir a thread completa.

**Conteúdo de mídia (vídeo/imagem):** O pipeline descrito arquiva apenas texto. Para mídias, integre `yt-dlp` para vídeos e download direto de imagens via URLs extraídas do JSON da API.

**Não usar esta abordagem quando:** o volume é muito alto (centenas de tweets/dia) sem API paga — o scraping será bloqueado rapidamente e os custos de API escalarão; prefira soluções especializadas como Apify Twitter Scraper nesse cenário.

## Conexoes

Nenhuma nota relacionada encontrada no