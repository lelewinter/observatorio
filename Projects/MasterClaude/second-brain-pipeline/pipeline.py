#!/usr/bin/env python3
"""
Second Brain Pipeline — Leticia Winter
Monitora Reddit, Nitter, HN, Google News (concorrentes) e ArXiv.
Cria notas Zettelkasten no Obsidian. Gera digest semanal.
"""

import json
import re
import time
import hashlib
import argparse
from datetime import datetime, timezone, timedelta
from pathlib import Path

import feedparser
import requests
from anthropic import Anthropic

BASE_DIR    = Path(__file__).parent
CONFIG_FILE = BASE_DIR / "config.json"
STATE_FILE  = BASE_DIR / "state.json"


# ── Config & Estado ───────────────────────────────────────────────────────────
def load_config() -> dict:
    if not CONFIG_FILE.exists():
        raise FileNotFoundError("config.json não encontrado")
    with open(CONFIG_FILE, encoding="utf-8") as f:
        return json.load(f)

def load_state() -> dict:
    if STATE_FILE.exists():
        with open(STATE_FILE, encoding="utf-8") as f:
            return json.load(f)
    return {"processed": [], "last_run": None}

def save_state(state: dict):
    state["processed"] = list(state["processed"])[-1000:]
    with open(STATE_FILE, "w", encoding="utf-8") as f:
        json.dump(state, f, indent=2)


# ── Utilitários ───────────────────────────────────────────────────────────────
def make_id(item: dict) -> str:
    raw = (item.get("link", "") + item.get("title", "")).encode()
    return hashlib.md5(raw).hexdigest()

def to_kebab(text: str) -> str:
    text = text.lower()
    for a, b in [
        ('á','a'),('ã','a'),('â','a'),('à','a'),
        ('é','e'),('ê','e'),('è','e'),
        ('í','i'),('î','i'),('ó','o'),('õ','o'),('ô','o'),
        ('ú','u'),('û','u'),('ü','u'),('ç','c'),('ñ','n'),
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


# ── Fontes: Social ────────────────────────────────────────────────────────────
def fetch_reddit(subreddits: list[str]) -> list[dict]:
    items = []
    for sub in subreddits:
        try:
            feed = feedparser.parse(f"https://www.reddit.com/r/{sub}/hot.rss?limit=20")
            for e in feed.entries[:20]:
                items.append({"title": e.get("title",""), "link": e.get("link",""),
                               "summary": e.get("summary","")[:600], "source": f"Reddit r/{sub}"})
        except Exception as ex:
            print(f"  ⚠️  Reddit r/{sub}: {ex}")
    return items

def fetch_nitter(accounts: list[str], instances: list[str]) -> list[dict]:
    items = []
    for account in accounts:
        for instance in instances:
            try:
                feed = feedparser.parse(f"https://{instance}/{account}/rss")
                if not feed.entries:
                    continue
                for e in feed.entries[:10]:
                    items.append({"title": e.get("title",""),
                                  "link": e.get("link","").replace(instance, "x.com"),
                                  "summary": e.get("summary","")[:600], "source": f"X @{account}"})
                break
            except Exception:
                continue
    return items

def fetch_hackernews(keywords: list[str]) -> list[dict]:
    items = []
    for kw in keywords:
        try:
            feed = feedparser.parse(f"https://hnrss.org/newest?q={kw}&points=15")
            for e in feed.entries[:8]:
                items.append({"title": e.get("title",""), "link": e.get("link",""),
                               "summary": e.get("summary","")[:600], "source": "Hacker News"})
        except Exception as ex:
            print(f"  ⚠️  HN '{kw}': {ex}")
    return items


# ── Fontes: Concorrentes ──────────────────────────────────────────────────────
def fetch_google_news(queries: list[str]) -> list[dict]:
    """Notícias via Google News RSS — ideal para monitorar concorrentes em PT-BR."""
    items = []
    for query in queries:
        encoded = query.replace(' ', '+')
        url = f"https://news.google.com/rss/search?q={encoded}&hl=pt-BR&gl=BR&ceid=BR:pt-419"
        try:
            feed = feedparser.parse(url)
            for e in feed.entries[:8]:
                items.append({"title": e.get("title",""), "link": e.get("link",""),
                               "summary": e.get("summary","")[:600],
                               "source": f"Google News: {query}"})
        except Exception as ex:
            print(f"  ⚠️  Google News '{query}': {ex}")
    return items

def fetch_competitor_blogs(blogs: dict) -> list[dict]:
    """RSS dos blogs oficiais dos concorrentes."""
    items = []
    for name, rss_url in blogs.items():
        try:
            feed = feedparser.parse(rss_url)
            for e in feed.entries[:5]:
                items.append({"title": e.get("title",""), "link": e.get("link",""),
                               "summary": e.get("summary","")[:600],
                               "source": f"Blog {name}"})
        except Exception as ex:
            print(f"  ⚠️  Blog {name}: {ex}")
    return items


# ── Fontes: ArXiv ─────────────────────────────────────────────────────────────
def fetch_arxiv(categories: list[str], keywords: list[str]) -> list[dict]:
    """Papers do ArXiv filtrados por keywords de interesse."""
    items = []
    kw_lower = [k.lower() for k in keywords]
    for cat in categories:
        try:
            feed = feedparser.parse(f"http://export.arxiv.org/rss/{cat}")
            for e in feed.entries[:30]:
                title   = e.get("title", "")
                summary = e.get("summary", "")
                if any(kw in (title + summary).lower() for kw in kw_lower):
                    items.append({"title": title, "link": e.get("link",""),
                                  "summary": summary[:600], "source": f"ArXiv {cat}"})
        except Exception as ex:
            print(f"  ⚠️  ArXiv {cat}: {ex}")
    return items


# ── Claude: avaliação e geração ───────────────────────────────────────────────
EVAL_PROMPT = """\
Você filtra conteúdo para o second brain de uma Analytics Manager especialista em IA
que também acompanha o mercado de SaaS/fintech brasileiro (empresa: Superlógica).

Tópicos de interesse técnico: {topics}
Concorrentes a monitorar: Conta Azul, Omie, TOTVS, Vindi, Iugu

Item:
Título: {title}
Fonte:  {source}
Resumo: {summary}

Responda SOMENTE em JSON válido:
{{"score": <0-10>, "reason": "<uma frase>", "tags": ["tag1","tag2","tag3"]}}

Critério:
8-10 → conteúdo prático, específico, aplicável — ou movimento relevante de concorrente
5-7  → relacionado mas genérico
0-4  → irrelevante, repetido ou spam"""

NOTE_PROMPT = """\
Crie uma nota Zettelkasten em português PT-BR.

Fonte: {source}
URL: {link}
Título: {title}
Conteúdo: {summary}
Tags: {tags}
Data: {date}

Use EXATAMENTE este template:

---
tags: [{tags}]
source: {link}
date: {date}
---
# [Título como afirmação específica — o que este conteúdo PROVA ou ENSINA]

## Resumo
[Uma frase que capture a ideia central]

## Explicação
[3-5 parágrafos em PT-BR. Explique o "por quê" antes do "como". Use analogia simples.]

## Exemplos
[2-3 casos práticos concretos]

## Relacionado
- (deixar vazio)

## Perguntas de Revisão
1. [Pergunta que testa compreensão real]
2. [Como conecta com outro conceito?]
3. [Como aplicar na prática?]"""

DIGEST_PROMPT = """\
Você sintetiza o second brain semanal da Leticia Winter, Analytics Manager especialista em IA.

Notas criadas nos últimos 7 dias:

{notes}

Crie um digest semanal em PT-BR com este formato EXATO:

---
tags: [digest, semanal, revisao]
date: {date}
---
# Digest Semana {week}/{year}: [Tema Principal Identificado]

## Os 3 Temas Dominantes
[Um parágrafo por tema. Seja específico — cite as notas e ferramentas reais.]

## Conexões Não Óbvias
[2-3 conexões entre notas distintas que merecem investigação futura.]

## Para Agir Esta Semana
1. [Ação concreta e específica baseada no que foi aprendido]
2. [Ação concreta]
3. [Ação concreta]

## Sinais de Tendência
[O que apareceu múltiplas vezes? O que está emergindo nas fontes?]

## Notas Criadas
[Lista com os títulos das notas desta semana]"""


def evaluate(client: Anthropic, item: dict, topics: list[str]) -> dict:
    prompt = EVAL_PROMPT.format(
        topics=", ".join(topics[:20]),
        title=item["title"],
        source=item["source"],
        summary=item["summary"][:400],
    )
    resp = client.messages.create(
        model="claude-haiku-4-5-20251001", max_tokens=250,
        messages=[{"role": "user", "content": prompt}],
    )
    try:
        return json.loads(resp.content[0].text)
    except Exception:
        return {"score": 0, "reason": "parse error", "tags": []}

def generate_note(client: Anthropic, item: dict, tags: list[str]) -> str:
    prompt = NOTE_PROMPT.format(
        source=item["source"], link=item["link"], title=item["title"],
        summary=item["summary"][:800], tags=", ".join(tags),
        date=datetime.now().strftime("%Y-%m-%d"),
    )
    resp = client.messages.create(
        model="claude-sonnet-4-6", max_tokens=1800,
        messages=[{"role": "user", "content": prompt}],
    )
    return resp.content[0].text.strip()


# ── Salvar no Obsidian ────────────────────────────────────────────────────────
def save_note(cfg: dict, note: str, filename: str, subfolder: str = "Links Salvos") -> bool:
    encoded = subfolder.replace(" ", "%20")
    try:
        url = f"{cfg['obsidian_api']}/vault/{encoded}/{filename}"
        headers = {"Authorization": f"Bearer {cfg['obsidian_token']}",
                   "Content-Type": "text/markdown"}
        r = requests.put(url, data=note.encode("utf-8"), headers=headers, timeout=5)
        if r.status_code in (200, 201, 204):
            return True
    except Exception:
        pass
    vault = cfg.get("vault_path")
    if vault:
        try:
            dest = Path(vault) / subfolder / filename
            dest.write_text(note, encoding="utf-8")
            return True
        except Exception as ex:
            print(f"  Fallback falhou: {ex}")
    return False


# ── Digest Semanal ────────────────────────────────────────────────────────────
def run_weekly_digest(cfg: dict, client: Anthropic):
    print(f"\n{'━'*54}")
    print(f"  Digest Semanal  {datetime.now().strftime('%d/%m/%Y')}")
    print(f"{'━'*54}")

    vault = cfg.get("vault_path")
    if not vault:
        print("❌ vault_path não configurado")
        return

    salvos    = Path(vault) / "Links Salvos"
    cutoff    = datetime.now() - timedelta(days=7)
    recentes  = [
        f for f in salvos.glob("*.md")
        if f.stat().st_mtime > cutoff.timestamp()
           and not f.stem.startswith("digest-")
    ]

    if not recentes:
        print("  Nenhuma nota nova nos últimos 7 dias.")
        return

    print(f"\n  {len(recentes)} notas dos últimos 7 dias encontradas")

    notes_text = "\n\n---\n\n".join(
        f"## {f.stem}\n{f.read_text(encoding='utf-8')[:600]}"
        for f in sorted(recentes, key=lambda x: x.stat().st_mtime, reverse=True)[:20]
    )

    now    = datetime.now()
    prompt = DIGEST_PROMPT.format(
        notes=notes_text,
        date=now.strftime("%Y-%m-%d"),
        week=now.strftime("%U"),
        year=now.year,
    )

    print("  Gerando digest com Claude Sonnet...")
    resp = client.messages.create(
        model="claude-sonnet-4-6", max_tokens=2000,
        messages=[{"role": "user", "content": prompt}],
    )
    digest = resp.content[0].text.strip()
    filename = f"digest-semana-{now.strftime('%Y-%W')}.md"

    ok = save_note(cfg, digest, filename)
    print(f"\n  {'✅ Digest salvo' if ok else '❌ Falha ao salvar'}: {filename}")
    print(f"{'━'*54}\n")


# ── Pipeline de monitoramento ─────────────────────────────────────────────────
def run_monitor(cfg: dict, client: Anthropic, dry_run: bool = False):
    print(f"\n{'━'*54}")
    print(f"  Second Brain Monitor  {datetime.now().strftime('%d/%m/%Y %H:%M')}")
    print(f"{'━'*54}")

    state = load_state()
    seen  = set(state["processed"])

    print("\n📡 Coletando feeds...")
    all_items: list[dict] = []

    print(f"   Reddit  ({len(cfg['reddit_subreddits'])} subreddits)")
    all_items += fetch_reddit(cfg["reddit_subreddits"])

    print(f"   Nitter  ({len(cfg['twitter_accounts'])} contas)")
    all_items += fetch_nitter(cfg["twitter_accounts"], cfg["nitter_instances"])

    print(f"   HN      ({len(cfg['hacker_news_keywords'])} keywords)")
    all_items += fetch_hackernews(cfg["hacker_news_keywords"])

    if cfg.get("competitor_news_queries"):
        print(f"   Google News  ({len(cfg['competitor_news_queries'])} queries)")
        all_items += fetch_google_news(cfg["competitor_news_queries"])

    if cfg.get("competitor_blogs"):
        print(f"   Blogs concorrentes  ({len(cfg['competitor_blogs'])} feeds)")
        all_items += fetch_competitor_blogs(cfg["competitor_blogs"])

    if cfg.get("arxiv_categories"):
        kws = cfg.get("arxiv_keywords", cfg["topics"][:12])
        print(f"   ArXiv  ({len(cfg['arxiv_categories'])} categorias)")
        all_items += fetch_arxiv(cfg["arxiv_categories"], kws)

    new_items = [i for i in all_items if (iid := make_id(i)) not in seen]
    for i in new_items:
        i["_id"] = make_id(i)

    print(f"\n   {len(all_items)} coletados → {len(new_items)} novos")

    if not new_items:
        print("\n✅ Nada novo desde o último run.")
        state["last_run"] = datetime.now(timezone.utc).isoformat()
        save_state(state)
        return

    threshold  = cfg.get("relevance_threshold", 7)
    max_items  = cfg.get("max_items_per_run", 25)
    notes_done = 0

    print(f"\n🧠 Avaliando relevância (threshold >= {threshold}/10)...\n")

    for item in new_items[:max_items]:
        state["processed"].append(item["_id"])
        try:
            ev    = evaluate(client, item, cfg["topics"])
            score = ev.get("score", 0)
            tags  = ev.get("tags", [])

            if score >= threshold:
                print(f"  ✨ [{score}/10] {item['title'][:65]}")
                print(f"     {ev.get('reason','')}")
                if not dry_run:
                    note     = generate_note(client, item, tags)
                    filename = extract_filename(note)
                    ok       = save_note(cfg, note, filename)
                    print(f"     {'💾 ' + filename if ok else '❌ falha ao salvar'}")
                    if ok:
                        notes_done += 1
                else:
                    print(f"     [dry-run]")
                    notes_done += 1
            else:
                print(f"  ─  [{score}/10] {item['title'][:60]}")
        except Exception as ex:
            print(f"  ❌ {ex}")
        time.sleep(0.4)

    state["last_run"] = datetime.now(timezone.utc).isoformat()
    save_state(state)

    print(f"\n{'━'*54}")
    print(f"  ✅ {notes_done} nota(s) criada(s) no vault")
    print(f"{'━'*54}\n")


# ── Entrypoint ────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Second Brain Pipeline")
    parser.add_argument("--dry-run", action="store_true", help="Avalia sem gravar notas")
    parser.add_argument("--digest",  action="store_true", help="Gera digest semanal")
    args = parser.parse_args()

    cfg    = load_config()
    client = Anthropic(api_key=cfg["anthropic_api_key"])

    if args.digest:
        run_weekly_digest(cfg, client)
    else:
        run_monitor(cfg, client, dry_run=args.dry_run)
