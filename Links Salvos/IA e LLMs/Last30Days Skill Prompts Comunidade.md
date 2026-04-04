---
date: 2026-03-24
tags: [claude-code, skill, prompts, reddit, x, community, open-source]
source: https://x.com/MillieMarconnni/status/2036363493478375797?s=20
autor: "@MillieMarconnni"
tipo: aplicacao
---

# Criar Skill Claude Code: Last30Days para Prompts Atualizados

## O que é

Skill customizável para [[Claude Code]] que monitora Reddit e X em tempo real (últimos 30 dias) para sintetizar prompts vencedores que a comunidade descobriu e testou, eliminando dependência de documentação estática ou guias desatualizados. Gera prompts pronto-para-use baseados em padrões empíricos atuais.

## Como implementar

### Pré-requisito: Credenciais de API

Configure acesso às APIs (veja [Reddit App Registration](https://www.reddit.com/prefs/apps) e [X API](https://developer.twitter.com/)):

```bash
# .env no seu projeto
REDDIT_CLIENT_ID=your_id
REDDIT_CLIENT_SECRET=your_secret
X_API_KEY=your_key
X_API_SECRET=your_secret
```

### Fase 1: Estrutura Básica da Skill

Crie arquivo `skills/last30days.py`:

```python
import anthropic
from datetime import datetime, timedelta
import praw  # Reddit API
import requests  # X API

client = anthropic.Anthropic()

def fetch_reddit_posts(query: str, days: int = 30) -> list:
    """Busca posts do Reddit dos últimos N dias"""
    reddit = praw.Reddit(
        client_id=os.getenv("REDDIT_CLIENT_ID"),
        client_secret=os.getenv("REDDIT_CLIENT_SECRET"),
        user_agent="last30days_skill"
    )

    cutoff = datetime.now() - timedelta(days=days)
    posts = []

    # Buscar em subreddits relevantes
    for subreddit in ["PromptEngineering", "ChatGPT", "LocalLLaMA"]:
        sub = reddit.subreddit(subreddit)
        for post in sub.search(query, time_filter="month"):
            if post.created_utc > cutoff.timestamp():
                posts.append({
                    "title": post.title,
                    "content": post.selftext,
                    "score": post.score,
                    "source": f"r/{post.subreddit}"
                })
    return posts

def fetch_x_posts(query: str, days: int = 30) -> list:
    """Busca tweets dos últimos N dias"""
    headers = {
        "Authorization": f"Bearer {os.getenv('X_API_KEY')}",
        "User-Agent": "last30days_skill"
    }

    cutoff = (datetime.now() - timedelta(days=days)).isoformat()

    response = requests.get(
        "https://api.twitter.com/2/tweets/search/recent",
        headers=headers,
        params={
            "query": query + " -is:retweet",
            "max_results": 100,
            "start_time": cutoff
        }
    )

    return response.json().get("data", [])

def synthesize_prompts(reddit_posts: list, x_posts: list, topic: str) -> str:
    """Usa Claude para sintetizar padrões em prompts prontos"""

    evidence = f"""
    Reddit posts (últimos 30 dias):
    {chr(10).join([f"- {p['title']} (score: {p['score']})" for p in reddit_posts[:5]])}

    X/Twitter posts:
    {chr(10).join([f"- {p['text'][:100]}..." for p in x_posts[:5]])}
    """

    message = client.messages.create(
        model="claude-opus-4-1",
        max_tokens=2000,
        messages=[{
            "role": "user",
            "content": f"""Você é especialista em prompt engineering.

Baseado em evidências reais de comunidades (Reddit, X) dos últimos 30 dias sobre "{topic}":

{evidence}

Gere 3 prompts PRONTOS PARA COPY-PASTE que funcionam AGORA em modelos recentes.
Cada prompt deve:
1. Estar testado pela comunidade (cite a fonte)
2. Ser específico e acionável
3. Incluir variáveis que o usuário pode customizar
4. Explicar brevemente por que funciona

Formato:
## Prompt [N]: [Título]
\`\`\`
[prompt completo aqui]
\`\`\`
**Por que funciona:** [explicação baseada em comunidade]
**Fonte:** [subreddit ou usuario X]
"""
        }]
    )

    return message.content[0].text
```

### Fase 2: Integração com Claude Code

Registre a skill no arquivo de configuração Claude (`~/.claude/skills.yaml`):

```yaml
skills:
  - name: last30days
    path: ./skills/last30days.py
    trigger: /last30days
    description: "Gera prompts vencedores baseados em comunidade (últimos 30 dias)"
    examples:
      - "/last30days prompting techniques for coding"
      - "/last30days Midjourney style keywords"
      - "/last30days Claude prompt patterns"
```

### Fase 3: Agendamento Periódico (Opcional)

Para manter cache quente, execute updates periódicos:

```python
# scheduled_update.py - rodar a cada 6 horas
from apscheduler.schedulers.background import BackgroundScheduler
import pickle

def cache_trending_topics():
    """Pré-calcula trends e armazena em cache"""
    trending_queries = [
        "prompting techniques",
        "model comparisons",
        "optimization tricks"
    ]

    cache = {}
    for query in trending_queries:
        posts_reddit = fetch_reddit_posts(query)
        posts_x = fetch_x_posts(query)
        cache[query] = {
            "reddit": posts_reddit,
            "x": posts_x,
            "timestamp": datetime.now()
        }

    with open("prompt_cache.pkl", "wb") as f:
        pickle.dump(cache, f)

scheduler = BackgroundScheduler()
scheduler.add_job(cache_trending_topics, 'interval', hours=6)
scheduler.start()
```

## Stack e requisitos

- **Python 3.10+**
- **praw**: `pip install praw` (Reddit API client)
- **requests**: `pip install requests` (HTTP library para X API)
- **anthropic**: `pip install anthropic` (Claude API)
- **apscheduler**: `pip install apscheduler` (scheduling, opcional)
- **API keys**: Reddit (free), X API (Basic ou higher), Anthropic (Pro ou Max para latência)
- **Custo**: ~$0.01-0.05 por query de síntese (Claude Haiku), gratuito se usar até 1M tokens/mês
- **Frequência de update**: em tempo real, ~5-10s de latência

## Armadilhas e limitações

1. **Rate limits**: Reddit permite ~60 requests/minuto; X API tem limites por tier. Implemente cache agressivo.

2. **Viés comunitário**: Padrões mais upvotados podem refletir preferência da comunidade, não necessariamente os *melhores* prompts. Diversifique fontes (subreddits, X followers).

3. **Prompts desatualizados rapidamente**: Um prompt que é trend agora pode ser "patched" pelo modelo em semanas. Adicione timestamp a cada prompt: "Validado em: 2026-04-02".

4. **Cobertura de idioma**: Reddit/X em inglês dominam. Para PT-BR, configure busca em comunidades locais ou discords brasileiros manualmente.

5. **Qualidade de síntese**: Claude pode "aluci nar" fontes. Sempre inclua links reais para verificação.

## Conexões

- [[Claude Code - Melhores Práticas]] — integração com setup ótimo
- [[Last30Days Skill Prompts Comunidade]] — skill relacionada
- [[otimizacao-de-tokens-em-llms]] — otimize síntese para menos tokens
- [[450_skills_workflows_claude]] — galeria de outras skills

## Histórico

- 2026-03-24: Conceito original do skill
- 2026-04-02: Guia de implementação prática com código

Casos de uso abrangem técnicas de prompting para qualquer modelo, Midjourney techniques, Suno Music prompts, Cursor rules, trending anything. Características técnicas: 100% Open Source com MIT License, implementado como Claude Code skill com integração de Reddit API e X API, processamento sintetiza dados brutos, identifica padrões, estrutura como prompts, otimiza para uso imediato.

Impacto representa mudança de paradigma: antes conhecimento estático desatualizado, depois inteligência comunitária em tempo real. Quando alguém descobre algo que funciona no Reddit ou X, você pode saber em dias (não meses), ter em formato pronto, executar imediatamente. Democratiza acesso: qualquer pessoa pode acessar técnicas top sem ser expert, sem tempo de research.

## Exemplos

Comparação de tempo e qualidade: pesquisa manual leva 30-60 minutos com qualidade inconsistente e atualização semanal se houver. Last30Days skill leva menos de 5 segundos com qualidade validada por comunidade e atualização contínua (30 dias rolling).

Exemplos de casos de uso: ChatGPT para questões legais, Claude para coding, qualquer modelo para qualquer tarefa, estilos Midjourney que estão gerando buzz, parâmetros que realmente funcionam, técnicas aprovadas pela comunidade, gêneros Suno em alta, prompts de sucesso recente, configurações Cursor ótimas agora, rules que a comunidade descobriu, best practices atualizadas, trending rap songs, qualquer tópico que você precisar.

## Relacionado

- [[450_skills_workflows_claude]]
- [[Claude Code - Melhores Práticas]]
- [[30_prompts_claude_fp_a_analise]]
- [[Resumo Links Adicionais Comunidade]]

## Perguntas de Revisão

1. Por que inteligência comunitária em tempo real é melhor que conhecimento estático?
2. Como Last30Days resolve o problema de prompts desatualizados?
3. Qual é o impacto de 30-segundo scan versus 30-minute manual research?
