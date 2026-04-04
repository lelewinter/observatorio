---
tags: [conceito, tiktok, api, automacao, publicacao, social-media]
date: 2026-04-02
tipo: conceito
aliases: [TikTok Creator API, Automated Publishing, TikTok Shop API]
---
# TikTok Creator API e Publicação Automatizada

## O que é

Conjunto de endpoints REST fornecidos pelo TikTok que permite publicar vídeos, agendar postagens, ler analytics e gerenciar conteúdo programaticamente — sem interface web. Complementado pela TikTok Shop API para vincular produto a vídeo e rastrear conversão. Pré-requisito: conta TikTok Creator ou Business, aprovação do acesso à API.

## Como funciona

**Fluxo de autorização OAuth:**

1. Sua app redireciona usuário para TikTok login (`https://open-api.tiktok.com/oauth/authorize?...`)
2. Usuário autoriza permissões (postar vídeos, ler analytics)
3. TikTok redireciona pra sua app com `authorization_code`
4. Sua app troca code por `access_token` (válido ~1 hora) e `refresh_token` (válido ~1 ano)
5. Armazene tokens em DB seguro (nunca em plaintext)

```python
# Exemplo com requests
def get_access_token(auth_code):
    response = requests.post(
        "https://open-api.tiktok.com/v1/oauth/token",
        json={
            "client_id": TIKTOK_CLIENT_ID,
            "client_secret": TIKTOK_CLIENT_SECRET,
            "code": auth_code,
            "grant_type": "authorization_code"
        }
    )
    return response.json()["access_token"]
```

**Publicação de vídeo:**

Passo 1: Upload de vídeo em chunks (TikTok requer uploads em múltiplas partes pra vídeos grandes):

```python
def upload_video(file_path, access_token):
    with open(file_path, 'rb') as f:
        files = {'video': f}
        headers = {"Authorization": f"Bearer {access_token}"}
        response = requests.post(
            "https://open-api.tiktok.com/v1/post/publish/action/upload",
            files=files,
            headers=headers
        )
    return response.json()["upload_id"]
```

Passo 2: Publicar (iniciar processamento) com metadata:

```python
def publish_video(upload_id, caption, access_token, product_link=None):
    payload = {
        "upload_id": upload_id,
        "caption": caption,  # max 2200 caracteres
        "post_mode": "FEED_POST",  # ou "SCHEDULE" pra agendar
        "disable_duet": False,
        "disable_stitch": False,
        "allow_comment": True
    }

    if product_link:
        payload["poi_ids"] = [get_tiktok_shop_product_id(product_link)]

    headers = {"Authorization": f"Bearer {access_token}"}
    response = requests.post(
        "https://open-api.tiktok.com/v1/post/publish/action/publish",
        json=payload,
        headers=headers
    )
    post_id = response.json()["post_id"]
    return post_id
```

**Agendamento (schedule):**

Em vez de `"post_mode": "FEED_POST"`, use `"post_mode": "SCHEDULE"` e adicione:

```python
{
    "publish_time": int(datetime(2026, 4, 3, 14, 0, 0).timestamp())  # Unix timestamp
}
```

**Analytics (read):**

Após publicação, aguarde ~1h para dados aparecerem:

```python
def get_video_analytics(post_id, access_token):
    response = requests.get(
        f"https://open-api.tiktok.com/v1/post/{post_id}/analytics",
        headers={"Authorization": f"Bearer {access_token}"}
    )
    analytics = response.json()["data"]
    return {
        "views": analytics["views"],
        "likes": analytics["likes"],
        "comments": analytics["comments"],
        "shares": analytics["shares"],
        "clicks": analytics.get("clicks", 0),  # clicks pra link no bio/shop
    }
```

**TikTok Shop Product Link:**

Para vincular vídeo a produto específico no TikTok Shop:

```python
# Passo 1: Buscar product_id no TikTok Shop
def get_shop_product(sku, access_token):
    response = requests.get(
        "https://open-api.tiktok.com/v1/shop/products/search",
        params={"sku": sku},
        headers={"Authorization": f"Bearer {access_token}"}
    )
    return response.json()["products"][0]["product_id"]

# Passo 2: Usar product_id na publicação
publish_video(upload_id, caption, access_token, product_id=product_id)
```

## Pra que serve

**Automação de publicação:**
Publica automaticamente vídeos em sequência (ex: 1 a cada 6h) sem intervencão manual. Com 60 vídeos/semana, economiza ~3h de clicking.

**Agendamento inteligente:**
Analisa quando audiência é mais ativa (TikTok analytics histórico) e publica em horários otimizados automaticamente.

**Feedback loop em tempo real:**
Lê views/likes/clicks a cada 6-12h e ajusta próximas publicações baseado em performance (ex: próximo vídeo usa hook similar ao vencedor).

**Monetização:**
Integra produto direto no vídeo (TikTok Shop), rastreia clique → compra via API, calcula CVR precise.

**Trade-offs e limitações:**

1. **Rate limiting:**
   - TikTok permite ~300 requests/15 min por app
   - Publicação: ~10-50 vídeos/dia (depende de conta)
   - Se ultrapassar: IP é throttled
   - **Mitigação:** implementar retry exponencial, delay entre requests

2. **Lag de dados:**
   Analytics de views/likes leva 1-2h para aparecer. CVR (cliques) ainda mais lento. Não é tempo-real.

3. **Detecção de automação:**
   Se publica 50 vídeos em 1 hora (spacing muito regular), TikTok pode flagar conta como bot. Recomendação: espaçar com jitter (ex: 6h ± 30min).

4. **Política de conteúdo:**
   Mesmo publicando via API, vídeo está sujeito a review de moderação. Pode ser deletado/shadowbanned se violar política.

5. **Acesso à API pode ser revogado:**
   TikTok pode negar ou revogar acesso sem aviso. Sempre ter plano de fallback (manual ou outra plataforma).

## Exemplo prático

**Cenário:** E-commerce de cosméticos, 30 vídeos UGC prontos, quer publicar 5/dia em sequência com 6h de espaçamento, começando 2 de abril.

**Step 1 — Autenticar:**
```python
access_token = get_access_token(auth_code_from_user)
```

**Step 2 — Preparar schedule:**
```python
videos = [
    {"file": "ugc_001.mp4", "caption": "Hook 1", "product_id": "123"},
    {"file": "ugc_002.mp4", "caption": "Hook 2", "product_id": "123"},
    # ... 28 mais
]

base_time = datetime(2026, 4, 2, 12, 0, 0)  # 12h de 2 de abril

schedule = []
for i, video in enumerate(videos):
    publish_time = base_time + timedelta(hours=6*i)
    schedule.append({
        **video,
        "publish_time": int(publish_time.timestamp())
    })
```

**Step 3 — Publicar tudo:**
```python
for item in schedule:
    upload_id = upload_video(item["file"], access_token)
    publish_video(
        upload_id,
        caption=item["caption"],
        access_token=access_token,
        product_id=item["product_id"],
        publish_time=item["publish_time"]
    )
    time.sleep(2)  # Rate limiting: 2s entre requests
```

**Step 4 — Monitorar (job assíncrono a cada 6h):**
```python
while True:
    for video_id in published_videos:
        analytics = get_video_analytics(video_id, access_token)
        store_metrics_in_db(video_id, analytics)
    time.sleep(6 * 3600)  # Poll a cada 6 horas
```

Resultado: 30 vídeos publicados automaticamente em 5 dias, dados de performance coletados, próxima rodada otimizada baseado em vencedores.

## Aparece em
- [[producao-de-ugc-em-escala-com-ia]] — camada 3 (publicação)
- [[metricas-de-engagement-ecommerce]] — leitura de analytics via API

---
*Conceito extraído em 2026-04-02*
