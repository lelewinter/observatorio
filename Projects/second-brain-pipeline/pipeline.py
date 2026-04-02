#!/usr/bin/env python3
"""
Second Brain Pipeline v2 — Leticia Winter
Dois canais de entrada (RSS passivo + Telegram ativo), processamento unificado.
Extrai conteudo, detecta duplicatas, gera/atualiza notas Zettelkasten,
classifica em subpastas por tema, notifica no Telegram.

Uso:
  python pipeline.py                        # roda tudo (Telegram + RSS)
  python pipeline.py --mode telegram        # so Telegram (1x)
  python pipeline.py --mode rss             # so RSS
  python pipeline.py --mode telegram-daemon # Telegram em loop (a cada 2min)
  python pipeline.py --digest               # digest semanal
  python pipeline.py --dry-run              # simula sem salvar
"""

import json
import re
import time
import shutil
import hashlib
import argparse
import logging
from datetime import datetime, timezone, timedelta
from logging.handlers import RotatingFileHandler
from pathlib import Path
from urllib.parse import quote

import feedparser
import requests
import trafilatura
from anthropic import Anthropic

# ── Logging ──────────────────────────────────────────────────────────────────
LOG_DIR = Path(__file__).parent / "logs"
LOG_DIR.mkdir(exist_ok=True)

log = logging.getLogger("pipeline")
log.setLevel(logging.INFO)

# Console
_console = logging.StreamHandler()
_console.setFormatter(logging.Formatter("%(asctime)s [%(levelname)s] %(message)s", datefmt="%H:%M:%S"))
log.addHandler(_console)

# Arquivo rotativo: 3 arquivos de 2MB cada (~6MB max)
_file = RotatingFileHandler(
    LOG_DIR / "pipeline.log", maxBytes=2_000_000, backupCount=3, encoding="utf-8"
)
_file.setFormatter(logging.Formatter("%(asctime)s [%(levelname)s] %(message)s", datefmt="%Y-%m-%d %H:%M:%S"))
log.addHandler(_file)

# ── Paths ────────────────────────────────────────────────────────────────────
BASE_DIR = Path(__file__).parent
CONFIG_FILE = BASE_DIR / "config.json"
STATE_FILE = BASE_DIR / "state.json"


# =============================================================================
# CONFIG & STATE
# =============================================================================

def load_config() -> dict:
    if not CONFIG_FILE.exists():
        raise FileNotFoundError("config.json nao encontrado")
    with open(CONFIG_FILE, encoding="utf-8") as f:
        return json.load(f)


def load_state() -> dict:
    if STATE_FILE.exists():
        with open(STATE_FILE, encoding="utf-8") as f:
            return json.load(f)
    return {"processed": [], "last_update_id": 0, "last_run": None}


def save_state(state: dict):
    state["processed"] = list(state["processed"])[-2000:]
    with open(STATE_FILE, "w", encoding="utf-8") as f:
        json.dump(state, f, indent=2)


# =============================================================================
# UTILITIES
# =============================================================================

def make_id(url: str, title: str = "") -> str:
    raw = (url + title).encode()
    return hashlib.md5(raw).hexdigest()


def to_kebab(text: str) -> str:
    text = text.lower()
    for a, b in [
        ('a\u0301','a'),('a\u0303','a'),('a\u0302','a'),('a\u0300','a'),
        ('\u00e1','a'),('\u00e3','a'),('\u00e2','a'),('\u00e0','a'),
        ('\u00e9','e'),('\u00ea','e'),('\u00e8','e'),
        ('\u00ed','i'),('\u00ee','i'),('\u00f3','o'),('\u00f5','o'),('\u00f4','o'),
        ('\u00fa','u'),('\u00fb','u'),('\u00fc','u'),('\u00e7','c'),('\u00f1','n'),
    ]:
        text = text.replace(a, b)
    text = re.sub(r'[^a-z0-9\s-]', '', text)
    text = re.sub(r'\s+', '-', text.strip())
    return text[:80]


def extract_filename(note: str) -> str:
    for line in note.splitlines():
        if line.startswith("# "):
            return to_kebab(line[2:].strip()) + ".md"
    return f"nota-{datetime.now().strftime('%Y%m%d-%H%M%S')}.md"


def extract_urls(text: str) -> list[str]:
    """Extrai URLs de uma mensagem de texto."""
    url_pattern = re.compile(r'https?://[^\s<>"{}|\\^`\[\]]+', re.IGNORECASE)
    return url_pattern.findall(text)


def extract_text_from_response(response) -> str:
    """Extrai texto de response da API Anthropic (incluindo server-side tools)."""
    texts = []
    for block in response.content:
        if hasattr(block, 'text'):
            texts.append(block.text)
    return "\n".join(texts)


def api_call_with_retry(client: Anthropic, model: str, max_tokens: int,
                        messages: list, max_retries: int = 3):
    """Wrapper para chamadas da API com retry e exponential backoff."""
    for attempt in range(max_retries):
        try:
            resp = client.messages.create(
                model=model, max_tokens=max_tokens, messages=messages,
            )
            cost_tracker.track(resp, model)
            return resp
        except Exception as ex:
            err_str = str(ex)
            is_retryable = any(k in err_str.lower() for k in
                ["rate_limit", "overloaded", "timeout", "529", "529", "500", "503"])

            if is_retryable and attempt < max_retries - 1:
                wait = (2 ** attempt) * 2  # 2s, 4s, 8s
                log.warning(f"  API retry {attempt + 1}/{max_retries} em {wait}s: {err_str[:80]}")
                time.sleep(wait)
            else:
                raise
    raise RuntimeError("max retries exceeded")


# ── Cost Tracker ────────────────────────────────────────────────────────────

# Precos por 1M tokens (USD) — abril 2026
PRICING = {
    "claude-haiku-4-5-20251001": {"input": 0.80, "output": 4.00},
    "claude-sonnet-4-6":        {"input": 3.00, "output": 15.00},
}

class CostTracker:
    def __init__(self):
        self.total_input = 0
        self.total_output = 0
        self.total_cost = 0.0
        self.calls = 0
        self.by_model = {}

    def track(self, response, model: str):
        """Registra tokens e custo de uma chamada da API."""
        usage = getattr(response, 'usage', None)
        if not usage:
            return

        inp = getattr(usage, 'input_tokens', 0)
        out = getattr(usage, 'output_tokens', 0)
        prices = PRICING.get(model, {"input": 3.0, "output": 15.0})
        cost = (inp * prices["input"] + out * prices["output"]) / 1_000_000

        self.total_input += inp
        self.total_output += out
        self.total_cost += cost
        self.calls += 1

        if model not in self.by_model:
            self.by_model[model] = {"input": 0, "output": 0, "cost": 0.0, "calls": 0}
        self.by_model[model]["input"] += inp
        self.by_model[model]["output"] += out
        self.by_model[model]["cost"] += cost
        self.by_model[model]["calls"] += 1

    def summary(self) -> str:
        """Retorna resumo de custo da rodada."""
        if not self.calls:
            return "Nenhuma chamada API."
        lines = [f"💰 Custo da rodada: ${self.total_cost:.4f}"]
        lines.append(f"   {self.calls} chamadas | {self.total_input:,} input + {self.total_output:,} output tokens")
        for model, data in self.by_model.items():
            short = model.split("-")[1] if "-" in model else model
            lines.append(f"   {short}: {data['calls']}x | ${data['cost']:.4f}")
        return "\n".join(lines)


# Instancia global por rodada
cost_tracker = CostTracker()


# =============================================================================
# ENTRADA: TELEGRAM
# =============================================================================

def download_telegram_file(cfg: dict, file_id: str, dest_dir: Path) -> Path | None:
    """Baixa arquivo do Telegram e salva localmente."""
    token = cfg.get("telegram_bot_token", "")
    try:
        # Obter file_path do Telegram
        resp = requests.get(
            f"https://api.telegram.org/bot{token}/getFile",
            params={"file_id": file_id}, timeout=15
        )
        file_info = resp.json()
        if not file_info.get("ok"):
            return None

        file_path = file_info["result"]["file_path"]
        file_url = f"https://api.telegram.org/file/bot{token}/{file_path}"

        # Baixar
        dl = requests.get(file_url, timeout=30)
        ext = Path(file_path).suffix or ".jpg"
        dest = dest_dir / f"telegram-{file_id[:12]}{ext}"
        dest.parent.mkdir(parents=True, exist_ok=True)
        dest.write_bytes(dl.content)
        log.info(f"  Foto baixada: {dest.name}")
        return dest

    except Exception as ex:
        log.warning(f"Download foto falhou: {ex}")
        return None


def fetch_telegram_items(cfg: dict, state: dict) -> tuple[list[dict], int]:
    """Busca mensagens novas no Telegram: links, texto e fotos."""
    token = cfg.get("telegram_bot_token", "")
    if not token:
        return [], state.get("last_update_id", 0)

    last_id = state.get("last_update_id", 0)
    url = f"https://api.telegram.org/bot{token}/getUpdates"
    params = {"offset": last_id + 1, "timeout": 0}

    try:
        resp = requests.get(url, params=params, timeout=15)
        data = resp.json()
    except Exception as ex:
        log.warning(f"Telegram getUpdates falhou: {ex}")
        return [], last_id

    if not data.get("ok"):
        log.warning(f"Telegram API error: {data}")
        return [], last_id

    items = []
    max_id = last_id

    for update in data.get("result", []):
        update_id = update["update_id"]
        max_id = max(max_id, update_id)

        message = update.get("message") or update.get("channel_post") or {}
        text = message.get("text", "") or message.get("caption", "") or ""
        chat_id = message.get("chat", {}).get("id")
        photos = message.get("photo", [])

        urls = extract_urls(text)

        if urls:
            # Mensagem com link(s)
            for link in urls:
                items.append({
                    "link": link,
                    "title": "",
                    "summary": "",
                    "source": "Telegram",
                    "chat_id": chat_id,
                    "skip_scoring": True,
                    "msg_type": "link",
                })
        elif photos:
            # Foto (pode ter caption)
            biggest = max(photos, key=lambda p: p.get("file_size", 0))
            items.append({
                "link": "",
                "title": text[:100] if text else "Foto do Telegram",
                "summary": text,
                "source": "Telegram (foto)",
                "chat_id": chat_id,
                "skip_scoring": True,
                "msg_type": "photo",
                "file_id": biggest.get("file_id", ""),
            })
        elif text.strip() and len(text.strip()) > 10:
            # Mensagem de texto puro (pensamento/ideia)
            items.append({
                "link": "",
                "title": text[:80],
                "summary": text,
                "source": "Telegram (texto)",
                "chat_id": chat_id,
                "skip_scoring": True,
                "msg_type": "text",
            })

    if items:
        log.info(f"Telegram: {len(items)} item(ns) novo(s)")

    return items, max_id


# =============================================================================
# ENTRADA: RSS FEEDS
# =============================================================================

def fetch_reddit(subreddits: list[str]) -> list[dict]:
    items = []
    for sub in subreddits:
        try:
            feed = feedparser.parse(
                f"https://www.reddit.com/r/{sub}/hot.rss?limit=20",
                request_headers={"User-Agent": "SecondBrainPipeline/2.0"}
            )
            for e in feed.entries[:20]:
                items.append({
                    "title": e.get("title", ""),
                    "link": e.get("link", ""),
                    "summary": e.get("summary", "")[:600],
                    "source": f"Reddit r/{sub}",
                })
        except Exception as ex:
            log.warning(f"Reddit r/{sub}: {ex}")
    return items


def fetch_hackernews(keywords: list[str]) -> list[dict]:
    items = []
    for kw in keywords:
        try:
            feed = feedparser.parse(f"https://hnrss.org/newest?q={kw}&points=15")
            for e in feed.entries[:8]:
                items.append({
                    "title": e.get("title", ""),
                    "link": e.get("link", ""),
                    "summary": e.get("summary", "")[:600],
                    "source": "Hacker News",
                })
        except Exception as ex:
            log.warning(f"HN '{kw}': {ex}")
    return items


def fetch_google_news(queries: list[str]) -> list[dict]:
    items = []
    for query in queries:
        encoded = query.replace(' ', '+')
        url = f"https://news.google.com/rss/search?q={encoded}&hl=pt-BR&gl=BR&ceid=BR:pt-419"
        try:
            feed = feedparser.parse(url)
            for e in feed.entries[:8]:
                items.append({
                    "title": e.get("title", ""),
                    "link": e.get("link", ""),
                    "summary": e.get("summary", "")[:600],
                    "source": f"Google News: {query}",
                })
        except Exception as ex:
            log.warning(f"Google News '{query}': {ex}")
    return items


def fetch_arxiv(categories: list[str], keywords: list[str]) -> list[dict]:
    items = []
    kw_lower = [k.lower() for k in keywords]
    for cat in categories:
        try:
            feed = feedparser.parse(f"http://export.arxiv.org/rss/{cat}")
            for e in feed.entries[:30]:
                title = e.get("title", "")
                summary = e.get("summary", "")
                if any(kw in (title + summary).lower() for kw in kw_lower):
                    items.append({
                        "title": title,
                        "link": e.get("link", ""),
                        "summary": summary[:600],
                        "source": f"ArXiv {cat}",
                    })
        except Exception as ex:
            log.warning(f"ArXiv {cat}: {ex}")
    return items


def fetch_nitter(accounts: list[str], instances: list[str]) -> list[dict]:
    """Tenta buscar tweets via Nitter (instancias publicas instáveis)."""
    items = []
    working = False
    for account in accounts:
        for instance in instances:
            try:
                feed = feedparser.parse(
                    f"https://{instance}/{account}/rss",
                    request_headers={"User-Agent": "SecondBrainPipeline/2.0"}
                )
                if not feed.entries:
                    continue
                working = True
                for e in feed.entries[:10]:
                    items.append({
                        "title": e.get("title", ""),
                        "link": e.get("link", "").replace(instance, "x.com"),
                        "summary": e.get("summary", "")[:600],
                        "source": f"X @{account}",
                    })
                break
            except Exception:
                continue
    if not working and accounts:
        log.warning("  Nitter: nenhuma instancia respondeu (provavelmente bloqueadas)")
    return items


def fetch_lobsters(tags: list[str]) -> list[dict]:
    """Busca posts do Lobsters (lobste.rs) por tag."""
    items = []
    for tag in tags:
        try:
            feed = feedparser.parse(f"https://lobste.rs/t/{tag}.rss")
            for e in feed.entries[:10]:
                items.append({
                    "title": e.get("title", ""),
                    "link": e.get("link", ""),
                    "summary": e.get("summary", "")[:600],
                    "source": f"Lobsters #{tag}",
                })
        except Exception as ex:
            log.warning(f"Lobsters #{tag}: {ex}")
    return items


def fetch_devto(tags: list[str]) -> list[dict]:
    """Busca posts do Dev.to por tag via RSS."""
    items = []
    for tag in tags:
        try:
            feed = feedparser.parse(f"https://dev.to/feed/tag/{tag}")
            for e in feed.entries[:8]:
                items.append({
                    "title": e.get("title", ""),
                    "link": e.get("link", ""),
                    "summary": e.get("summary", "")[:600],
                    "source": f"Dev.to #{tag}",
                })
        except Exception as ex:
            log.warning(f"Dev.to #{tag}: {ex}")
    return items


def fetch_producthunt() -> list[dict]:
    """Busca posts do dia do Product Hunt via RSS."""
    items = []
    try:
        feed = feedparser.parse("https://www.producthunt.com/feed")
        for e in feed.entries[:15]:
            items.append({
                "title": e.get("title", ""),
                "link": e.get("link", ""),
                "summary": e.get("summary", "")[:600],
                "source": "Product Hunt",
            })
    except Exception as ex:
        log.warning(f"Product Hunt: {ex}")
    return items


def fetch_github_trending(languages: list[str]) -> list[dict]:
    """Busca trending repos do GitHub via RSS mirror."""
    items = []
    for lang in languages:
        try:
            feed = feedparser.parse(
                f"https://mshibanami.github.io/GitHubTrendingRSS/daily/{lang}.xml"
            )
            for e in feed.entries[:8]:
                items.append({
                    "title": e.get("title", ""),
                    "link": e.get("link", ""),
                    "summary": e.get("summary", "")[:600],
                    "source": f"GitHub Trending ({lang})",
                })
        except Exception as ex:
            log.warning(f"GitHub Trending {lang}: {ex}")
    return items


def collect_rss_items(cfg: dict) -> list[dict]:
    """Coleta todos os itens de RSS configurados."""
    items = []

    subs = cfg.get("reddit_subreddits", [])
    if subs:
        log.info(f"  Reddit ({len(subs)} subreddits)")
        items += fetch_reddit(subs)

    hn_kw = cfg.get("hacker_news_keywords", [])
    if hn_kw:
        log.info(f"  HN ({len(hn_kw)} keywords)")
        items += fetch_hackernews(hn_kw)

    gn_queries = cfg.get("google_news_queries", [])
    if gn_queries:
        log.info(f"  Google News ({len(gn_queries)} queries)")
        items += fetch_google_news(gn_queries)

    arxiv_cats = cfg.get("arxiv_categories", [])
    if arxiv_cats:
        kws = cfg.get("arxiv_keywords", cfg.get("topics", [])[:12])
        log.info(f"  ArXiv ({len(arxiv_cats)} categorias)")
        items += fetch_arxiv(arxiv_cats, kws)

    tw_accounts = cfg.get("twitter_accounts", [])
    nitter_inst = cfg.get("nitter_instances", [])
    if tw_accounts and nitter_inst:
        log.info(f"  Nitter ({len(tw_accounts)} contas)")
        items += fetch_nitter(tw_accounts, nitter_inst)

    lobster_tags = cfg.get("lobsters_tags", [])
    if lobster_tags:
        log.info(f"  Lobsters ({len(lobster_tags)} tags)")
        items += fetch_lobsters(lobster_tags)

    devto_tags = cfg.get("devto_tags", [])
    if devto_tags:
        log.info(f"  Dev.to ({len(devto_tags)} tags)")
        items += fetch_devto(devto_tags)

    if cfg.get("producthunt_enabled", False):
        log.info("  Product Hunt")
        items += fetch_producthunt()

    gh_langs = cfg.get("github_trending_languages", [])
    if gh_langs:
        log.info(f"  GitHub Trending ({len(gh_langs)} langs)")
        items += fetch_github_trending(gh_langs)

    return items


# =============================================================================
# CORE: EXTRACAO DE CONTEUDO
# =============================================================================

def extract_tweet(url: str) -> dict | None:
    """Extrai conteudo de tweet via fxtwitter API (nao precisa de JS)."""
    # Normalizar URL: x.com ou twitter.com -> api.fxtwitter.com
    match = re.search(r'(?:x\.com|twitter\.com)/(\w+)/status/(\d+)', url)
    if not match:
        return None

    user, tweet_id = match.groups()
    api_url = f"https://api.fxtwitter.com/{user}/status/{tweet_id}"

    try:
        resp = requests.get(api_url, timeout=15)
        if resp.status_code != 200:
            return None

        data = resp.json()
        tweet = data.get("tweet", {})
        author = tweet.get("author", {})

        text = tweet.get("text", "")
        name = author.get("name", user)
        handle = author.get("screen_name", user)

        # Incluir quote tweet se existir
        quote = tweet.get("quote", {})
        if quote:
            quote_text = quote.get("text", "")
            quote_author = quote.get("author", {}).get("name", "")
            if quote_text:
                text += f"\n\n[Quote de {quote_author}]: {quote_text}"

        # Incluir media descriptions
        media = tweet.get("media", {})
        if media and media.get("all"):
            for m in media["all"]:
                alt = m.get("altText", "")
                if alt:
                    text += f"\n\n[Imagem: {alt}]"

        return {
            "title": f"{name} (@{handle}): {text[:100]}",
            "content": text,
            "url": url,
        }

    except Exception as ex:
        log.warning(f"fxtwitter falhou: {ex}")
        return None


def extract_content(url: str) -> dict:
    """Extrai titulo e conteudo principal de uma URL."""
    # Twitter/X: usar fxtwitter API
    if "x.com/" in url or "twitter.com/" in url:
        tweet = extract_tweet(url)
        if tweet and tweet["content"]:
            log.info(f"  Tweet extraido via fxtwitter")
            return tweet

    try:
        downloaded = trafilatura.fetch_url(url)
        if not downloaded:
            resp = requests.get(
                url, timeout=15,
                headers={"User-Agent": "SecondBrainPipeline/2.0"}
            )
            downloaded = resp.text

        content = trafilatura.extract(
            downloaded,
            include_comments=False,
            include_tables=True,
            output_format="txt",
        )

        # Extrair titulo do HTML
        title = ""
        if downloaded:
            title_match = re.search(r'<title[^>]*>([^<]+)</title>', downloaded, re.IGNORECASE)
            if title_match:
                title = title_match.group(1).strip()

        return {
            "title": title or "Sem titulo",
            "content": content or "",
            "url": url,
        }

    except Exception as ex:
        log.warning(f"Extracao falhou para {url}: {ex}")
        return {"title": "Sem titulo", "content": "", "url": url}


# =============================================================================
# CORE: MATCHING SEMANTICO (DEDUP)
# =============================================================================

def get_existing_notes(vault_path: str) -> list[dict]:
    """Lista notas existentes com titulo, tags e resumo (incluindo subpastas)."""
    salvos = Path(vault_path) / "Links Salvos"
    if not salvos.exists():
        return []

    notes = []
    for f in salvos.rglob("*.md"):
        if f.stem.startswith("digest-"):
            continue
        try:
            text = f.read_text(encoding="utf-8")
            title = ""
            tags = []
            resumo = ""

            lines = text.splitlines()
            for i, line in enumerate(lines):
                if line.startswith("# ") and not title:
                    title = line[2:].strip()
                if line.strip().startswith("tags:"):
                    tags = re.findall(r'[\w-]+', line)
                    tags = [t for t in tags if t != "tags"]
                if line.strip() == "## Resumo":
                    # Pega as proximas linhas ate a proxima secao
                    resumo_lines = []
                    for j in range(i + 1, min(i + 6, len(lines))):
                        if lines[j].startswith("## "):
                            break
                        if lines[j].strip():
                            resumo_lines.append(lines[j].strip())
                    resumo = " ".join(resumo_lines)

            notes.append({
                "filename": f.name,
                "filepath": str(f),
                "title": title or f.stem,
                "tags": tags,
                "resumo": resumo[:300],
            })
        except Exception:
            continue

    return notes


def find_notes_by_tags(existing_notes: list[dict], new_tags: list[str],
                       max_results: int = 10) -> list[dict]:
    """Filtra notas existentes que compartilham tags com o conteudo novo."""
    if not new_tags:
        return []

    new_tags_lower = {t.lower() for t in new_tags}
    scored = []

    for note in existing_notes:
        note_tags = {t.lower() for t in note.get("tags", [])}
        overlap = new_tags_lower & note_tags
        if overlap:
            scored.append((len(overlap), note))

    # Ordenar por numero de tags em comum (mais tags = mais relevante)
    scored.sort(key=lambda x: x[0], reverse=True)
    return [note for _, note in scored[:max_results]]


MATCH_PROMPT = """\
Voce e um assistente de deduplicacao de notas.

Conteudo novo:
Titulo: {new_title}
Resumo: {new_summary}

Notas existentes com tags similares:
{existing_notes}

Existe alguma nota que trata do MESMO assunto especifico?
Criterio: mesmo conceito, ferramenta, ou topico especifico (nao apenas mesmo tema geral).

Responda SOMENTE em JSON:
{{"match": true, "filename": "nome-do-arquivo.md", "reason": "uma frase"}}
ou
{{"match": false, "filename": null, "reason": "uma frase"}}"""


def find_matching_note(client: Anthropic, new_title: str, new_summary: str,
                       existing_notes: list[dict], new_tags: list[str]) -> dict | None:
    """Busca nota existente semanticamente similar, filtrando por tags primeiro."""
    # Filtro local por tags (zero tokens)
    candidates = find_notes_by_tags(existing_notes, new_tags, max_results=15)
    if not candidates:
        return None

    notes_text = "\n".join(
        f"- {n['filename']}: {n['title']} (tags: {', '.join(n['tags'][:5])})"
        for n in candidates
    )

    prompt = MATCH_PROMPT.format(
        new_title=new_title,
        new_summary=new_summary[:400],
        existing_notes=notes_text,
    )

    try:
        resp = api_call_with_retry(client, "claude-haiku-4-5-20251001", 200,
            [{"role": "user", "content": prompt}])
        raw = resp.content[0].text.strip()
        json_match = re.search(r'\{[^{}]+\}', raw)
        if not json_match:
            return None
        result = json.loads(json_match.group())
        if result.get("match") and result.get("filename"):
            log.info(f"  Match: {result['filename']} - {result.get('reason', '')}")
            return result
    except Exception as ex:
        log.warning(f"Matching falhou: {ex}")

    return None


# =============================================================================
# CORE: CONTEXTO DO VAULT
# =============================================================================

def build_vault_context(existing_notes: list[dict], new_tags: list[str],
                        vault_path: str, exclude_filename: str | None = None) -> str:
    """Busca notas relacionadas por tags e monta contexto do vault."""
    related = find_notes_by_tags(existing_notes, new_tags, max_results=8)

    if exclude_filename:
        related = [n for n in related if n["filename"] != exclude_filename]

    if not related:
        return "(nenhuma nota relacionada no vault)"

    context_parts = []

    for note in related[:6]:
        # Ler conteudo real da nota (titulo + resumo + explicacao parcial)
        note_path = Path(note.get("filepath", ""))
        if not note_path.exists():
            # Fallback: busca no Links Salvos
            note_path = Path(vault_path) / "Links Salvos" / note["filename"]
        fname = note["filename"].replace(".md", "")
        if not note_path.exists():
            context_parts.append(f"- [[{fname}|{note['title']}]]: {note['resumo']}")
            continue

        try:
            text = note_path.read_text(encoding="utf-8")
            # Extrair ate o fim da secao Explicacao (ou primeiros 800 chars)
            lines = text.splitlines()
            capture = False
            captured = []
            for line in lines:
                if line.startswith("# "):
                    captured.append(line)
                    capture = True
                    continue
                if line.startswith("## Resumo"):
                    capture = True
                    continue
                if line.startswith("## Explicacao"):
                    capture = True
                    continue
                if line.startswith("## Exemplos") or line.startswith("## Relacionado"):
                    break
                if capture and line.strip():
                    captured.append(line.strip())

            excerpt = "\n".join(captured)[:600]
            context_parts.append(
                f"### [[{fname}|{note['title']}]] (filename: {fname}) (tags: {', '.join(note['tags'][:4])})\n{excerpt}"
            )
        except Exception:
            context_parts.append(f"- [[{fname}|{note['title']}]]: {note['resumo']}")

    return "\n\n".join(context_parts)


# =============================================================================
# CORE: AVALIACAO DE RELEVANCIA (RSS)
# =============================================================================

EVAL_PROMPT = """\
Voce filtra conteudo para um second brain pessoal.

Topicos de interesse: {topics}

Item:
Titulo: {title}
Fonte:  {source}
Resumo: {summary}

Responda SOMENTE em JSON valido:
{{"score": <0-10>, "reason": "<uma frase>", "tags": ["tag1","tag2","tag3"]}}

Criterio:
8-10 = pratico, especifico, aplicavel, novidade real
5-7  = relacionado mas generico ou repetido
0-4  = irrelevante, spam, ou conteudo raso"""


def evaluate_relevance(client: Anthropic, item: dict, topics: list[str]) -> dict:
    """Avalia relevancia de um item RSS."""
    prompt = EVAL_PROMPT.format(
        topics=", ".join(topics[:25]),
        title=item.get("title", ""),
        source=item.get("source", ""),
        summary=item.get("summary", "")[:400],
    )

    try:
        resp = api_call_with_retry(client, "claude-haiku-4-5-20251001", 250,
            [{"role": "user", "content": prompt}])
        return json.loads(resp.content[0].text)
    except Exception:
        return {"score": 0, "reason": "parse error", "tags": []}


# =============================================================================
# CORE: GERACAO DE NOTAS
# =============================================================================

NOTE_PROMPT = """\
Sistema automatizado. NAO converse, NAO faca perguntas. Produza APENAS a nota no template.
Se o conteudo for curto (tweet, post), use as notas relacionadas do vault para dar contexto.

Crie nota Zettelkasten em PT-BR. Foco: conceito claro para estudo posterior.
IMPORTANTE: conecte este conteudo com o conhecimento existente no vault.
Explique como este conceito complementa, contradiz ou expande as notas relacionadas.

Fonte: {source}
URL: {url}
Titulo original: {title}
Conteudo: {content}
Tags: {tags}
Data: {date}

NOTAS RELACIONADAS DO VAULT (use para criar conexoes e enriquecer):
{vault_context}

REGRA CRITICA PARA O TITULO (#):
- O titulo DEVE ser o CONCEITO puro, curto e buscavel. 2-5 palavras.
- Pense como um termo de glossario ou verbete de enciclopedia.
- NUNCA usar nomes de usuarios, "@handles", numeros, ou detalhes.
- Os detalhes, numeros e contexto vao no corpo da nota (Resumo e Explicacao).
- BOM: "Destilacao de LLMs"
- BOM: "Hand Tracking via WebGPU"
- BOM: "Correcao de Erros Quanticos"
- BOM: "RAG com Embeddings Multimodais"
- RUIM: "Destilacao de Modelos Reduz LLMs a 4B Parametros Sem Perda Significativa" (longo demais)
- RUIM: "Thread do @karpathy sobre treinamento" (referencia fonte)
- RUIM: "Nova ferramenta de hand tracking no browser" (descritivo, nao conceitual)
- O titulo deve funcionar como nome de nota no Obsidian e ser facil de linkar com [[]].

Template EXATO:

---
tags: [{tags}]
source: {url}
date: {date}
---
# [Conceito central como afirmacao clara e especifica]

## Resumo
[1-2 frases. O conceito central.]

## Explicacao
[2-4 paragrafos em PT-BR. O que e, por que importa, como funciona.
Conecte com o conhecimento que ja existe no vault. Mencione como complementa
ou expande conceitos das notas relacionadas. Seja tecnico e especifico.]

## Exemplos
[2-3 aplicacoes praticas]

## Relacionado
[Links usando [[filename|Titulo]] para notas listadas acima. Use o filename (sem .md) como primeiro argumento e o titulo legivel depois do pipe. Explique a conexao em 1 frase.]

## Perguntas de Revisao
1. [Pergunta conceitual]
2. [Como isso se conecta com [[filename|titulo da nota]]?]

## Historico de Atualizacoes
- {date}: Nota criada a partir de {source}"""


EXTRACT_PROMPT = """\
Extraia os pontos-chave deste conteudo em PT-BR. Seja tecnico e especifico.
Foque em: o que e, como funciona, numeros/metricas, ferramentas mencionadas, aplicacoes praticas.
Max 800 palavras. NAO gere nota, apenas extraia os pontos.

Titulo: {title}
Conteudo:
{content}"""


def pre_extract(client: Anthropic, title: str, content: str) -> str:
    """Para conteudo longo (>3000 chars), extrai pontos-chave com Haiku primeiro."""
    if len(content) <= 3000:
        return content[:2500]

    log.info("  Conteudo longo, pre-extraindo pontos-chave com Haiku...")
    prompt = EXTRACT_PROMPT.format(title=title, content=content[:6000])

    try:
        resp = api_call_with_retry(client, "claude-haiku-4-5-20251001", 800,
            [{"role": "user", "content": prompt}])
        extracted = resp.content[0].text.strip()
        log.info(f"  Pre-extracao: {len(content)} -> {len(extracted)} chars")
        return extracted
    except Exception as ex:
        log.warning(f"  Pre-extracao falhou, usando truncado: {ex}")
        return content[:2500]


def generate_note(client: Anthropic, title: str, url: str, content: str,
                  vault_context: str, tags: list[str], source: str) -> str:
    """Gera nota Zettelkasten com contexto do vault."""
    processed_content = pre_extract(client, title, content)

    prompt = NOTE_PROMPT.format(
        source=source, url=url, title=title,
        content=processed_content,
        vault_context=vault_context[:2500],
        tags=", ".join(tags),
        date=datetime.now().strftime("%Y-%m-%d"),
    )

    resp = api_call_with_retry(client, "claude-sonnet-4-6", 2500,
        [{"role": "user", "content": prompt}])
    return extract_text_from_response(resp)


# =============================================================================
# CORE: MERGE DE NOTAS
# =============================================================================

MERGE_PROMPT = """\
Sistema automatizado. NAO converse. Produza a nota atualizada completa.

NOTA EXISTENTE:
{existing_note}

INFO NOVA:
Fonte: {source}
URL: {url}
Conteudo: {new_content}

OUTRAS NOTAS RELACIONADAS (para enriquecer conexoes):
{vault_context}

Regras:
1. Mantenha conteudo existente relevante
2. Incorpore info nova nas secoes apropriadas
3. Se houver contradicoes, priorize a info mais recente e mencione a mudanca
4. Atualize links [[]] em Relacionado usando as notas listadas acima
5. Adicione entrada no Historico de Atualizacoes:
   - {date}: Atualizado com informacoes de {source} ({url})

Retorne a nota COMPLETA atualizada."""


def merge_note(client: Anthropic, existing_note: str, new_content: str,
               vault_context: str, url: str, source: str) -> str:
    """Merge informacoes novas em nota existente, com contexto do vault."""
    processed_new = pre_extract(client, "", new_content) if len(new_content) > 3000 else new_content[:1500]

    prompt = MERGE_PROMPT.format(
        existing_note=existing_note[:2500],
        source=source, url=url,
        new_content=processed_new,
        vault_context=vault_context[:1500],
        date=datetime.now().strftime("%Y-%m-%d"),
    )

    resp = api_call_with_retry(client, "claude-sonnet-4-6", 2500,
        [{"role": "user", "content": prompt}])
    return extract_text_from_response(resp)


# =============================================================================
# SAIDA: OBSIDIAN
# =============================================================================

def classify_subfolder(tags: list[str], cfg: dict) -> str:
    """Classifica nota em subfolder por topic_folders do config."""
    topic_folders = cfg.get("topic_folders", {})
    if not topic_folders:
        return "Links Salvos"

    tags_lower = {t.lower() for t in tags}
    best_folder = "Links Salvos"
    best_overlap = 0

    for folder_name, folder_tags in topic_folders.items():
        overlap = len(tags_lower & {t.lower() for t in folder_tags})
        if overlap > best_overlap:
            best_overlap = overlap
            best_folder = f"Links Salvos/{folder_name}"

    return best_folder


def git_auto_commit(cfg: dict, filepath: str, message: str = ""):
    """Faz git add + commit + push automatico no vault (se git estiver configurado)."""
    vault = cfg.get("vault_path", "")
    if not vault:
        return
    git_dir = Path(vault) / ".git"
    if not git_dir.exists():
        return  # vault nao e um repo git, skip silencioso

    msg = message or f"auto: {Path(filepath).name}"
    try:
        import subprocess
        cwd = vault
        subprocess.run(["git", "add", filepath], cwd=cwd, capture_output=True, timeout=15)
        result = subprocess.run(
            ["git", "commit", "-m", msg],
            cwd=cwd, capture_output=True, timeout=15, text=True
        )
        if result.returncode == 0:
            subprocess.run(["git", "push"], cwd=cwd, capture_output=True, timeout=30)
            log.info(f"  Git: commit + push ({msg})")
        else:
            # Nada pra commitar (arquivo nao mudou)
            if "nothing to commit" in result.stdout:
                pass
            else:
                log.warning(f"  Git commit falhou: {result.stderr.strip()}")
    except Exception as ex:
        log.warning(f"  Git auto-commit falhou: {ex}")


def save_note_to_vault(cfg: dict, note: str, filename: str,
                       subfolder: str = "Links Salvos") -> bool:
    """Salva nota no vault. Tenta REST API primeiro, fallback para arquivo."""
    # Tentativa 1: Obsidian REST API
    try:
        encoded_path = f"{quote(subfolder)}/{quote(filename)}"
        api_url = f"{cfg['obsidian_api']}/vault/{encoded_path}"
        headers = {
            "Authorization": f"Bearer {cfg['obsidian_token']}",
            "Content-Type": "text/markdown",
        }
        r = requests.put(api_url, data=note.encode("utf-8"), headers=headers, timeout=5)
        if r.status_code in (200, 201, 204):
            log.info(f"  Salvo via API: {filename}")
            git_auto_commit(cfg, f"{subfolder}/{filename}")
            return True
    except Exception:
        pass

    # Tentativa 2: escrita direta no filesystem
    vault = cfg.get("vault_path")
    if vault:
        try:
            dest = Path(vault) / subfolder / filename
            dest.parent.mkdir(parents=True, exist_ok=True)
            dest.write_text(note, encoding="utf-8")
            log.info(f"  Salvo via arquivo: {filename}")
            git_auto_commit(cfg, f"{subfolder}/{filename}")
            return True
        except Exception as ex:
            log.error(f"  Fallback falhou: {ex}")

    return False


def read_note_from_vault(cfg: dict, filename: str,
                         subfolder: str = "Links Salvos") -> str | None:
    """Le conteudo de uma nota existente (busca em subpastas se necessario)."""
    vault = cfg.get("vault_path")
    if not vault:
        return None

    # Tenta caminho direto primeiro
    path = Path(vault) / subfolder / filename
    if path.exists():
        return path.read_text(encoding="utf-8")

    # Busca recursiva em Links Salvos
    salvos = Path(vault) / "Links Salvos"
    for f in salvos.rglob(filename):
        return f.read_text(encoding="utf-8")

    return None


# =============================================================================
# SAIDA: TELEGRAM NOTIFICACAO
# =============================================================================

TRIAGE_PROMPT = """\
Resumo TECNICO de triagem em PT-BR para Telegram (max 700 chars).
Seja especifico: nomes de tecnologias, numeros, comparacoes concretas. Zero frases genericas.

Titulo: {title}
Conteudo: {content}

Notas relacionadas ja no vault:
{vault_notes}

Formato:
📌 [Nome/conceito especifico, nao titulo generico]
🔧 [O que FAZ tecnicamente, em 2-3 frases. Stack, arquitetura, mecanismo.]
⚡ [Pra que serve na pratica. Caso de uso concreto.]
🔗 [Conexao com notas existentes: "complementa [[nota-x]] porque..."]
🏷️ {tags}"""


def generate_triage_summary(client: Anthropic, title: str, content: str,
                            vault_context: str, tags: list[str]) -> str:
    """Gera resumo curto para envio no Telegram."""
    # Extrair so titulos das notas relacionadas pro resumo
    related_titles = re.findall(r'\[\[([^\]]+)\]\]', vault_context)
    vault_notes = ", ".join(f"[[{t}]]" for t in related_titles[:5]) or "(nenhuma)"

    prompt = TRIAGE_PROMPT.format(
        title=title,
        content=content[:1000],
        vault_notes=vault_notes,
        tags=" ".join(f"#{t}" for t in tags[:5]),
    )

    try:
        resp = api_call_with_retry(client, "claude-haiku-4-5-20251001", 300,
            [{"role": "user", "content": prompt}])
        return resp.content[0].text.strip()
    except Exception:
        return f"📌 {title}"


def send_telegram_message(cfg: dict, text: str, chat_id: int | str | None = None,
                          parse_mode: str | None = "Markdown"):
    """Envia mensagem pro canal de saida do Telegram."""
    token = cfg.get("telegram_bot_token", "")
    target = chat_id or cfg.get("telegram_output_chat_id", "")
    if not token or not target:
        return

    url = f"https://api.telegram.org/bot{token}/sendMessage"
    payload = {
        "chat_id": target,
        "text": text,
        "disable_web_page_preview": True,
    }
    if parse_mode:
        payload["parse_mode"] = parse_mode

    try:
        resp = requests.post(url, json=payload, timeout=10)
        if not resp.json().get("ok") and parse_mode:
            # Retry sem parse_mode (Markdown pode falhar com chars especiais)
            payload.pop("parse_mode", None)
            requests.post(url, json=payload, timeout=10)
    except Exception as ex:
        log.warning(f"Telegram send falhou: {ex}")


def notify_telegram(cfg: dict, client: Anthropic, title: str, content: str,
                    vault_context: str, tags: list[str], filename: str,
                    subfolder: str = "Links Salvos",
                    is_update: bool = False):
    """Gera resumo e notifica no Telegram."""
    summary = generate_triage_summary(client, title, content, vault_context, tags)

    file_path = f"{subfolder}/{filename}"
    status = "🔄 Nota atualizada" if is_update else "✨ Nova nota"

    # Link web via Quartz/GitHub Pages
    quartz_base = cfg.get("quartz_base_url", "")
    if quartz_base:
        slug = file_path.replace(".md", "").replace(" ", "-").lower()
        web_url = f"{quartz_base.rstrip('/')}/{slug}"
        message = f"{summary}\n\n{status}\n🔗 {web_url}"
    else:
        message = f"{summary}\n\n{status}"

    send_telegram_message(cfg, message)


# =============================================================================
# PIPELINE PRINCIPAL
# =============================================================================

TEXT_NOTE_PROMPT = """\
Sistema automatizado. NAO converse. Produza APENAS a nota.

A usuario mandou um pensamento/observacao via Telegram. Crie nota Zettelkasten em PT-BR.
Trate como um insight pessoal para desenvolver depois.

Texto: {text}
Data: {date}

NOTAS RELACIONADAS DO VAULT (conecte se relevante):
{vault_context}

Template EXATO:

REGRA CRITICA PARA O TITULO (#):
- O titulo DEVE ser o CONCEITO puro, curto e buscavel. 2-5 palavras.
- BOM: "Busca Semantica por Tags"
- RUIM: "Pensamento sobre busca semantica"

---
tags: [{tags}]
source: Telegram (texto)
date: {date}
---
# [Conceito central como afirmacao clara]

## Resumo
[1-2 frases capturando a essencia do pensamento]

## Explicacao
[1-2 paragrafos desenvolvendo a ideia. Conecte com notas do vault se houver relacao.]

## Para Explorar
[2-3 direcoes de investigacao que este pensamento sugere]

## Relacionado
[Links usando [[filename|Titulo]] para notas listadas acima]

## Perguntas de Revisao
1. [Pergunta que force reflexao sobre este pensamento]

## Historico de Atualizacoes
- {date}: Nota criada a partir de mensagem no Telegram"""


def process_item(cfg: dict, client: Anthropic, item: dict,
                 existing_notes: list[dict], dry_run: bool = False) -> bool:
    """Processa um item: extrai -> tags -> match por tags -> vault context -> gera/merge -> salva -> notifica."""
    url = item.get("link", "")
    source = item.get("source", "Desconhecido")
    vault_path = cfg.get("vault_path", "")
    msg_type = item.get("msg_type", "link")

    # ── Foto do Telegram ────────────────────────────────────────────────
    if msg_type == "photo":
        file_id = item.get("file_id", "")
        caption = item.get("summary", "") or item.get("title", "")
        if file_id:
            attachments_dir = Path(vault_path) / "Links Salvos" / "_attachments"
            saved_path = download_telegram_file(cfg, file_id, attachments_dir)
            if saved_path:
                # Se tem caption, trata como texto + referencia a imagem
                if caption and len(caption) > 10:
                    item["summary"] = f"{caption}\n\n![[{saved_path.name}]]"
                    item["msg_type"] = "text"
                    msg_type = "text"
                else:
                    send_telegram_message(cfg, f"📷 Foto salva: {saved_path.name}")
                    return True
            else:
                log.warning("  Falha ao baixar foto")
                return False

    # ── Texto puro (pensamento/ideia) ───────────────────────────────────
    if msg_type == "text":
        text = item.get("summary", "") or item.get("title", "")
        log.info(f"Processando texto: {text[:60]}...")

        # Tags via Haiku
        try:
            ev = evaluate_relevance(client, {
                "title": text[:100], "source": source,
                "summary": text[:400]
            }, cfg.get("topics", []))
            tags = ev.get("tags", [])
        except Exception:
            tags = ["pensamento", "telegram"]

        # Matching
        match = find_matching_note(client, text[:100], text[:500], existing_notes, tags)
        context = build_vault_context(existing_notes, tags, vault_path,
                                      exclude_filename=match["filename"] if match else None)

        if dry_run:
            log.info(f"  [dry-run] TEXTO: {text[:60]}")
            return True

        if match:
            filename = match["filename"]
            existing_content = read_note_from_vault(cfg, filename)
            if existing_content:
                log.info(f"  Merge texto com: {filename}")
                note = merge_note(client, existing_content, text, context, "", source)
                is_update = True
            else:
                prompt = TEXT_NOTE_PROMPT.format(
                    text=text[:2000], vault_context=context[:2000],
                    tags=", ".join(tags),
                    date=datetime.now().strftime("%Y-%m-%d"),
                )
                resp = api_call_with_retry(client, "claude-sonnet-4-6", 1500,
                    [{"role": "user", "content": prompt}])
                note = extract_text_from_response(resp)
                filename = extract_filename(note)
                is_update = False
        else:
            prompt = TEXT_NOTE_PROMPT.format(
                text=text[:2000], vault_context=context[:2000],
                tags=", ".join(tags),
                date=datetime.now().strftime("%Y-%m-%d"),
            )
            resp = api_call_with_retry(client, "claude-sonnet-4-6", 1500,
                [{"role": "user", "content": prompt}])
            note = extract_text_from_response(resp)
            filename = extract_filename(note)
            is_update = False

        subfolder = classify_subfolder(tags, cfg)
        ok = save_note_to_vault(cfg, note, filename, subfolder=subfolder)
        if ok:
            notify_telegram(cfg, client, text[:100], text, context, tags,
                          filename, subfolder=subfolder, is_update=is_update)
            log.info(f"  {'Atualizada' if is_update else 'Criada'}: {subfolder}/{filename}")
        return ok

    # ── Link (fluxo original) ───────────────────────────────────────────
    if not url:
        return False

    # 1. Extracao de conteudo
    log.info(f"Extraindo: {url[:80]}")
    extracted = extract_content(url)
    title = extracted["title"] if extracted["title"] != "Sem titulo" else item.get("title", "")
    title = title or "Sem titulo"
    content = extracted["content"]

    if not content and item.get("summary"):
        content = item["summary"]

    if not content:
        log.warning(f"Sem conteudo extraido: {url}")
        return False

    # 2. Tags (precisamos antes do matching pra filtrar por tags)
    tags = item.get("tags", [])
    if not tags:
        try:
            ev = evaluate_relevance(client, {
                "title": title, "source": source,
                "summary": content[:400]
            }, cfg.get("topics", []))
            tags = ev.get("tags", [])
        except Exception:
            tags = []

    # 3. Matching semantico (filtrado por tags, zero tokens se nao tiver candidatos)
    log.info("  Checando duplicatas por tags...")
    match = find_matching_note(client, title, content[:500], existing_notes, tags)

    # 4. Contexto do vault (notas relacionadas por tags)
    log.info("  Buscando contexto no vault...")
    exclude = match["filename"] if match else None
    context = build_vault_context(existing_notes, tags, vault_path, exclude_filename=exclude)
    related_count = context.count("###")
    log.info(f"  {related_count} notas relacionadas encontradas")

    if dry_run:
        action = "MERGE" if match else "NOVA"
        log.info(f"  [dry-run] {action}: {title[:60]}")
        return True

    # 5. Gerar ou merge
    is_update = False
    if match:
        filename = match["filename"]
        existing_content = read_note_from_vault(cfg, filename)
        if existing_content:
            log.info(f"  Merge com: {filename}")
            note = merge_note(client, existing_content, content, context, url, source)
            is_update = True
        else:
            log.warning(f"  Match encontrado mas arquivo nao existe: {filename}")
            note = generate_note(client, title, url, content, context, tags, source)
            filename = extract_filename(note)
    else:
        note = generate_note(client, title, url, content, context, tags, source)
        filename = extract_filename(note)

    # 6. Classificar e salvar
    subfolder = classify_subfolder(tags, cfg)
    ok = save_note_to_vault(cfg, note, filename, subfolder=subfolder)
    if not ok:
        log.error(f"  Falha ao salvar: {filename}")
        return False

    # 7. Notificar
    notify_telegram(cfg, client, title, content, context, tags, filename,
                    subfolder=subfolder, is_update=is_update)

    action = "Atualizada" if is_update else "Criada"
    log.info(f"  {action}: {subfolder}/{filename}")
    return True


def run_pipeline(cfg: dict, mode: str = "all", dry_run: bool = False):
    """Executa o pipeline completo."""
    global cost_tracker
    cost_tracker = CostTracker()

    print(f"\n{'='*60}")
    print(f"  Second Brain Pipeline v2  {datetime.now().strftime('%d/%m/%Y %H:%M')}")
    print(f"  Modo: {mode}  {'[DRY RUN]' if dry_run else ''}")
    print(f"{'='*60}\n")

    client = Anthropic(api_key=cfg["anthropic_api_key"])
    state = load_state()
    seen = set(state["processed"])

    existing_notes = get_existing_notes(cfg.get("vault_path", ""))
    log.info(f"Vault: {len(existing_notes)} notas existentes em Links Salvos/")

    all_items: list[dict] = []
    new_update_id = state.get("last_update_id", 0)

    # ── Canal 1: Telegram (ativo) ────────────────────────────────────────
    if mode in ("all", "telegram"):
        log.info("--- Telegram ---")
        tg_items, new_update_id = fetch_telegram_items(cfg, state)
        all_items += tg_items

    # ── Canal 2: RSS (passivo) ───────────────────────────────────────────
    if mode in ("all", "rss"):
        log.info("--- RSS Feeds ---")
        rss_items = collect_rss_items(cfg)
        log.info(f"RSS total: {len(rss_items)} itens coletados")

        threshold = cfg.get("relevance_threshold", 7)
        max_rss = cfg.get("max_items_per_run", 15)
        scored_items = []

        log.info(f"Avaliando relevancia (threshold >= {threshold}/10)...")

        for item in rss_items:
            item_id = make_id(item["link"], item["title"])
            if item_id in seen:
                continue

            ev = evaluate_relevance(client, item, cfg.get("topics", []))
            score = ev.get("score", 0)

            if score >= threshold:
                item["tags"] = ev.get("tags", [])
                item["_score"] = score
                scored_items.append(item)
                log.info(f"  ✨ [{score}/10] {item['title'][:60]}")
            else:
                log.debug(f"  -  [{score}/10] {item['title'][:50]}")

            state["processed"].append(item_id)
            time.sleep(0.3)

            if len(scored_items) >= max_rss:
                break

        all_items += scored_items
        log.info(f"RSS: {len(scored_items)} passaram no filtro")

    # ── Processar todos ──────────────────────────────────────────────────
    if not all_items:
        log.info("Nada novo para processar.")
        state["last_update_id"] = new_update_id
        state["last_run"] = datetime.now(timezone.utc).isoformat()
        save_state(state)
        return

    notes_ok = 0

    for item in all_items:
        try:
            ok = process_item(cfg, client, item, existing_notes, dry_run)
            if ok:
                notes_ok += 1
                # Refresh notas existentes pro proximo item (dedup atualizado)
                existing_notes = get_existing_notes(cfg.get("vault_path", ""))
        except Exception as ex:
            log.error(f"Erro processando {item['link'][:60]}: {ex}")

        time.sleep(0.5)

    state["last_update_id"] = new_update_id
    state["last_run"] = datetime.now(timezone.utc).isoformat()
    save_state(state)

    print(f"\n{'='*60}")
    print(f"  {notes_ok} nota(s) processada(s)")
    print(f"\n{cost_tracker.summary()}")
    print(f"{'='*60}\n")


# =============================================================================
# DIGEST SEMANAL
# =============================================================================

DIGEST_PROMPT = """\
Sintetize o second brain semanal.

Notas criadas/atualizadas nos ultimos 7 dias:

{notes}

Crie um digest semanal em PT-BR:

---
tags: [digest, semanal, revisao]
date: {date}
---
# Digest Semana {week}/{year}: [Tema Principal]

## Os 3 Temas Dominantes
[Um paragrafo por tema. Cite notas e ferramentas reais.]

## Conexoes Nao Obvias
[2-3 conexoes entre notas distintas que merecem investigacao.]

## Para Agir Esta Semana
1. [Acao concreta]
2. [Acao concreta]
3. [Acao concreta]

## Sinais de Tendencia
[O que apareceu multiplas vezes? O que esta emergindo?]

## Notas da Semana
[Lista com titulos das notas]"""


def run_digest(cfg: dict):
    """Gera digest semanal."""
    print(f"\n{'='*60}")
    print(f"  Digest Semanal  {datetime.now().strftime('%d/%m/%Y')}")
    print(f"{'='*60}\n")

    client = Anthropic(api_key=cfg["anthropic_api_key"])
    vault = cfg.get("vault_path")
    if not vault:
        log.error("vault_path nao configurado")
        return

    salvos = Path(vault) / "Links Salvos"
    cutoff = datetime.now() - timedelta(days=7)
    recentes = [
        f for f in salvos.rglob("*.md")
        if f.stat().st_mtime > cutoff.timestamp()
        and not f.stem.startswith("digest-")
    ]

    if not recentes:
        log.info("Nenhuma nota nova nos ultimos 7 dias.")
        return

    log.info(f"{len(recentes)} notas dos ultimos 7 dias")

    notes_text = "\n\n---\n\n".join(
        f"## {f.stem}\n{f.read_text(encoding='utf-8')[:800]}"
        for f in sorted(recentes, key=lambda x: x.stat().st_mtime, reverse=True)[:25]
    )

    now = datetime.now()
    prompt = DIGEST_PROMPT.format(
        notes=notes_text,
        date=now.strftime("%Y-%m-%d"),
        week=now.strftime("%U"),
        year=now.year,
    )

    log.info("Gerando digest com Sonnet...")
    resp = api_call_with_retry(client, "claude-sonnet-4-6", 3000,
        [{"role": "user", "content": prompt}])

    digest = extract_text_from_response(resp)
    filename = f"digest-semana-{now.strftime('%Y-%W')}.md"
    ok = save_note_to_vault(cfg, digest, filename)

    if ok:
        # Gerar resumo formatado pro Telegram
        tg_prompt = f"""Resuma este digest semanal para uma mensagem de Telegram (max 1500 chars).
Formato:

📊 DIGEST SEMANAL — Semana {now.strftime('%U')}/{now.year}

🔥 Temas Dominantes
[3 temas, 1 linha cada com emoji relevante]

🔗 Conexoes
[2 conexoes nao obvias, 1 linha cada]

⚡ Para Agir
[2-3 acoes concretas, 1 linha cada]

📈 Tendencias
[2 sinais em 1 linha cada]

📝 {len(recentes)} notas processadas esta semana

Digest:
{digest[:2000]}"""

        try:
            tg_resp = api_call_with_retry(client, "claude-haiku-4-5-20251001", 600,
                [{"role": "user", "content": tg_prompt}])
            tg_message = tg_resp.content[0].text.strip()
        except Exception:
            tg_message = f"📊 Digest semanal pronto!\n📝 {len(recentes)} notas esta semana"

        quartz_base = cfg.get("quartz_base_url", "")
        if quartz_base:
            file_path = f"Links Salvos/{filename}"
            slug = file_path.replace(".md", "").replace(" ", "-").lower()
            tg_message += f"\n\n🔗 {quartz_base.rstrip('/')}/{slug}"

        send_telegram_message(cfg, tg_message)

    log.info(f"{'Digest salvo' if ok else 'Falha'}: {filename}")

    # ── Curadoria do vault: detectar novos temas e reorganizar ───────────
    curate_vault(cfg, client, vault)

    log.info(cost_tracker.summary())


# =============================================================================
# CURADORIA DO VAULT (roda dentro do digest semanal)
# =============================================================================

CURATE_PROMPT = """\
Voce e um curador de second brain / Zettelkasten.

PASTAS ATUAIS em Links Salvos/:
{current_folders}

TODAS AS NOTAS DO VAULT (titulo + tags + pasta atual):
{all_notes}

MOCs EXISTENTES na raiz do vault:
{existing_mocs}

Analise e responda SOMENTE em JSON valido:
{{
  "new_folders": [
    {{"name": "Nome da Pasta", "reason": "por que este tema merece pasta propria", "tags": ["tag1", "tag2"]}}
  ],
  "new_mocs": [
    {{"name": "MOC - Nome do Tema.md", "description": "descricao do MOC", "related_folders": ["Pasta1", "Pasta2"]}}
  ],
  "moves": [
    {{"filename": "nome-do-arquivo.md", "from": "Pasta Atual", "to": "Pasta Destino", "reason": "por que mover"}}
  ],
  "summary": "1-2 frases sobre o estado do vault e mudancas feitas"
}}

Regras:
- So crie pasta nova se tem 3+ notas que justifiquem (nao crie pasta pra 1 nota)
- So crie MOC novo se um tema tem 5+ notas espalhadas que merecem um mapa central
- So mova notas se estao claramente na pasta errada (nao mova por preferencia)
- Se nao tem nada pra mudar, retorne listas vazias
- Nomes de pasta em portugues sem acentos
- MOCs seguem formato "MOC - Nome do Tema.md"
- Seja conservador: menos mudancas eh melhor que muitas"""


MOC_TEMPLATE = """\
---
tags: [moc, {tags}]
date: {date}
---
# {title}

{description}

## Notas Relacionadas

{note_links}

## Conexoes e Padroes

[A ser preenchido conforme o vault cresce]

## Perguntas Abertas

- Quais sub-temas ainda nao foram explorados?
- Que conexoes com outros MOCs existem?
"""


def curate_vault(cfg: dict, client: Anthropic, vault: str):
    """Analisa vault e reorganiza se necessario: novas pastas, MOCs, moves."""
    log.info("\n--- Curadoria do Vault ---")

    salvos = Path(vault) / "Links Salvos"
    if not salvos.exists():
        return

    # Listar pastas atuais
    current_folders = []
    for d in sorted(salvos.iterdir()):
        if d.is_dir() and not d.name.startswith("_"):
            count = len(list(d.rglob("*.md")))
            current_folders.append(f"  {d.name}/ ({count} notas)")
    folders_text = "\n".join(current_folders) or "(nenhuma subpasta)"

    # Listar todas as notas com metadados
    all_notes = get_existing_notes(vault)
    notes_text_parts = []
    for n in all_notes:
        # Descobrir pasta atual
        fp = Path(n.get("filepath", ""))
        if fp.parent.name == "Links Salvos":
            folder = "(raiz)"
        else:
            folder = fp.parent.name
        notes_text_parts.append(
            f"- {n['filename']} | pasta: {folder} | tags: {', '.join(n['tags'][:6])} | titulo: {n['title'][:60]}"
        )
    notes_text = "\n".join(notes_text_parts[:120])

    # Listar MOCs existentes
    moc_files = sorted(Path(vault).glob("MOC -*.md"))
    mocs_text = "\n".join(f"  {m.name}" for m in moc_files) or "(nenhum MOC)"

    prompt = CURATE_PROMPT.format(
        current_folders=folders_text,
        all_notes=notes_text,
        existing_mocs=mocs_text,
    )

    try:
        resp = api_call_with_retry(client, "claude-sonnet-4-6", 1500,
            [{"role": "user", "content": prompt}])
        raw = extract_text_from_response(resp)

        # Extrair JSON
        json_match = re.search(r'\{[\s\S]+\}', raw)
        if not json_match:
            log.warning("  Curadoria: resposta sem JSON valido")
            return

        result = json.loads(json_match.group())

    except Exception as ex:
        log.warning(f"  Curadoria falhou: {ex}")
        return

    changes = 0

    # 1. Criar novas pastas
    for folder in result.get("new_folders", []):
        name = folder.get("name", "")
        if name:
            new_dir = salvos / name
            if not new_dir.exists():
                new_dir.mkdir(parents=True)
                log.info(f"  [NOVA PASTA] {name}/ - {folder.get('reason', '')}")
                changes += 1

                # Adicionar tags ao config.json (topic_folders)
                new_tags = folder.get("tags", [])
                if new_tags:
                    topic_folders = cfg.get("topic_folders", {})
                    if name not in topic_folders:
                        topic_folders[name] = new_tags
                        cfg["topic_folders"] = topic_folders
                        # Salvar config atualizado
                        with open(CONFIG_FILE, "w", encoding="utf-8") as f:
                            json.dump(cfg, f, indent=2, ensure_ascii=False)
                        log.info(f"  [CONFIG] topic_folders atualizado com {name}")

    # 2. Criar novos MOCs
    for moc in result.get("new_mocs", []):
        moc_name = moc.get("name", "")
        if not moc_name:
            continue
        moc_path = Path(vault) / moc_name
        if moc_path.exists():
            continue

        # Encontrar notas relacionadas
        related_folders = moc.get("related_folders", [])
        related_notes = []
        for n in all_notes:
            fp = Path(n.get("filepath", ""))
            if fp.parent.name in related_folders:
                related_notes.append(n)

        note_links = "\n".join(
            f"- [[{n['title']}]] — {n['resumo'][:80]}"
            for n in related_notes[:20]
        ) or "- (notas serao adicionadas automaticamente)"

        title = moc_name.replace("MOC - ", "").replace(".md", "")
        tags_str = ", ".join(related_folders[:3]).lower().replace(" ", "-")

        moc_content = MOC_TEMPLATE.format(
            tags=tags_str,
            date=datetime.now().strftime("%Y-%m-%d"),
            title=title,
            description=moc.get("description", "Mapa de conteudo para este tema."),
            note_links=note_links,
        )

        moc_path.write_text(moc_content, encoding="utf-8")
        log.info(f"  [NOVO MOC] {moc_name} ({len(related_notes)} notas linkadas)")
        changes += 1

    # 3. Mover notas mal classificadas
    for move in result.get("moves", []):
        fname = move.get("filename", "")
        from_folder = move.get("from", "")
        to_folder = move.get("to", "")

        if not fname or not to_folder:
            continue

        # Encontrar arquivo atual
        src = None
        for f in salvos.rglob(fname):
            src = f
            break

        if not src or not src.exists():
            continue

        dest_dir = salvos / to_folder
        dest_dir.mkdir(parents=True, exist_ok=True)
        dest = dest_dir / fname

        if dest.exists():
            continue

        shutil.move(str(src), str(dest))
        log.info(f"  [MOVE] {fname}: {from_folder} -> {to_folder} ({move.get('reason', '')})")
        changes += 1

    summary = result.get("summary", "")
    if changes:
        log.info(f"  Curadoria: {changes} mudanca(s). {summary}")
        # Notificar no Telegram
        send_telegram_message(cfg,
            f"🗂️ Curadoria semanal do vault:\n{summary}\n\n📊 {changes} mudanca(s) aplicadas"
        )
    else:
        log.info(f"  Curadoria: nenhuma mudanca necessaria. {summary}")


# =============================================================================
# DAILY REVIEW
# =============================================================================

DAILY_REVIEW_PROMPT = """\
Crie um resumo diario para Telegram (max 1200 chars) em PT-BR.

Notas criadas/atualizadas nas ultimas 24 horas:
{notes}

Custo API estimado: ~${cost}

Formato EXATO:

📋 REVIEW — {date}

📝 {count} nota(s) nas ultimas 24h

🧠 O que entrou
[Lista curta: 1 linha por nota com emoji relevante ao tema]

🔗 Fio condutor
[1-2 frases: qual o tema ou padrao que conecta essas notas?]

💰 Custo API: ~${cost}

Se nao tiver notas, diga apenas que foi um periodo tranquilo."""


def run_daily_review(cfg: dict):
    """Gera review diario e envia pro Telegram."""
    global cost_tracker
    cost_tracker = CostTracker()

    print(f"\n{'='*60}")
    print(f"  Daily Review  {datetime.now().strftime('%d/%m/%Y %H:%M')}")
    print(f"{'='*60}\n")

    client = Anthropic(api_key=cfg["anthropic_api_key"])
    vault = cfg.get("vault_path")
    if not vault:
        log.error("vault_path nao configurado")
        return

    salvos = Path(vault) / "Links Salvos"
    cutoff = (datetime.now() - timedelta(hours=24)).timestamp()

    recentes = [
        f for f in salvos.rglob("*.md")
        if f.stat().st_mtime > cutoff
        and not f.stem.startswith("digest-")
        and not f.stem.startswith("daily-")
    ]

    now = datetime.now()

    if not recentes:
        msg = f"📋 REVIEW — {now.strftime('%d/%m/%Y')}\n\n😌 Ultimas 24h tranquilas, nenhuma nota nova."
        send_telegram_message(cfg, msg)
        log.info("Nenhuma nota nova hoje.")
        return

    log.info(f"{len(recentes)} notas de hoje")

    # Ler resumo curto de cada nota
    notes_text = []
    for f in sorted(recentes, key=lambda x: x.stat().st_mtime):
        try:
            text = f.read_text(encoding="utf-8")
            title = ""
            resumo = ""
            for i, line in enumerate(text.splitlines()):
                if line.startswith("# ") and not title:
                    title = line[2:].strip()
                if line.strip() == "## Resumo":
                    for j in range(i + 1, min(i + 4, len(text.splitlines()))):
                        l = text.splitlines()[j].strip()
                        if l.startswith("## "):
                            break
                        if l:
                            resumo = l
                            break
            notes_text.append(f"- {title or f.stem}: {resumo[:150]}")
        except Exception:
            notes_text.append(f"- {f.stem}")

    # Estimar custo do dia via state.json (aproximado)
    # Usamos o custo das chamadas desta rodada como proxy minimo
    daily_cost = "0.00"
    state = load_state()
    last_run = state.get("last_run", "")

    prompt = DAILY_REVIEW_PROMPT.format(
        notes="\n".join(notes_text),
        cost=daily_cost,
        date=now.strftime("%d/%m/%Y"),
        count=len(recentes),
    )

    try:
        resp = api_call_with_retry(client, "claude-haiku-4-5-20251001", 500,
            [{"role": "user", "content": prompt}])
        message = resp.content[0].text.strip()
    except Exception as ex:
        log.error(f"Falha ao gerar daily review: {ex}")
        message = (
            f"📋 REVIEW DO DIA — {now.strftime('%d/%m/%Y')}\n\n"
            f"📝 {len(recentes)} nota(s) processada(s) hoje\n\n"
            + "\n".join(notes_text[:10])
        )

    send_telegram_message(cfg, message)
    log.info("Daily review enviado.")
    log.info(cost_tracker.summary())


# =============================================================================
# CLI
# =============================================================================

def run_telegram_daemon(cfg: dict):
    """Roda Telegram polling em loop continuo (daemon mode)."""
    interval = cfg.get("telegram_poll_interval", 120)
    print(f"\n{'='*60}")
    print(f"  Telegram Daemon  —  polling a cada {interval}s")
    print(f"  Ctrl+C para parar")
    print(f"{'='*60}\n")

    while True:
        try:
            run_pipeline(cfg, mode="telegram")
        except KeyboardInterrupt:
            log.info("Daemon interrompido pelo usuario.")
            break
        except Exception as ex:
            log.error(f"Erro no daemon loop: {ex}")

        try:
            time.sleep(interval)
        except KeyboardInterrupt:
            log.info("Daemon interrompido pelo usuario.")
            break


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Second Brain Pipeline v2")
    parser.add_argument(
        "--mode", choices=["all", "telegram", "rss", "telegram-daemon"],
        default="all",
        help="Canal de entrada: all, telegram, rss, ou telegram-daemon (loop continuo)"
    )
    parser.add_argument(
        "--dry-run", action="store_true",
        help="Simula sem salvar notas"
    )
    parser.add_argument(
        "--digest", action="store_true",
        help="Gera digest semanal"
    )
    parser.add_argument(
        "--daily", action="store_true",
        help="Gera review diario e envia no Telegram"
    )
    args = parser.parse_args()

    cfg = load_config()

    if args.digest:
        run_digest(cfg)
    elif args.daily:
        run_daily_review(cfg)
    elif args.mode == "telegram-daemon":
        run_telegram_daemon(cfg)
    else:
        run_pipeline(cfg, mode=args.mode, dry_run=args.dry_run)
