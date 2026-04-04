---
tags: []
source: https://x.com/paulogrego_/status/2036978185166844349?s=20
date: 2026-04-02
tipo: aplicacao
---

# Gerar Criativos de Vídeo em Escala com Renoise + Seedance 2.0

## O que é

Plataforma Renoise combina orquestrador de lógica (tipo Claude Code) com Seedance 2.0 (geração de vídeo) para converter especificação de criativo em centenas de variações de ad-video automaticamente.

## Como implementar

**Pré-requisito:** Conta Renoise, credenciais Seedance 2.0, arquivo de produto/marca.

**Etapa 1: Definir template de criativo.** Crie JSON de especificação:
```json
{
  "product": {
    "name": "Tênis XYZ",
    "category": "footwear",
    "image": "url_to_product_image.jpg"
  },
  "variations": [
    {
      "cta_text": ["Compre agora", "Desconto especial", "Visite a loja"],
      "music_style": ["uplifting", "energetic", "calm"],
      "duration": [15, 30, 60],
      "aspect_ratio": ["vertical", "square"]
    }
  ],
  "brand_guidelines": {
    "color_primary": "#FF6B35",
    "font": "Montserrat",
    "logo_placement": "top-right"
  }
}
```

**Etapa 2: Instruir Claude/orquestrador.** Passe template + briefing ao Claude:
```
Gere 200 variações de vídeo-ad para Tênis XYZ usando os templates abaixo.
Para cada variação:
1. Combine uma opção de CTA, música e duração
2. Mantenha brand guidelines (cores, logo placement)
3. Certifique que texto é legível em mobile
4. Crie um JSON config para cada variação

Saída desejada: array de 200 configs prontos para gerar
```

Claude Code gera matrix combinatória:
```json
[
  {
    "id": "variant_001",
    "cta_text": "Compre agora",
    "music_style": "uplifting",
    "duration": 15,
    "aspect_ratio": "vertical"
  },
  { "id": "variant_002", ... },
  ...
]
```

**Etapa 3: Gerar vídeos via Seedance 2.0.** Para cada config, chame Seedance:
```bash
for config in configs/*.json; do
  curl -X POST https://seedance-api.com/generate \
    -H "Authorization: Bearer TOKEN" \
    -d @$config \
    --output "videos/$(jq -r '.id' $config).mp4"
done
```

Seedance gera vídeo de ~3-6 segundos a partir de produto photo + instruções.

**Etapa 4: Adicionar CTA e áudio.** [[ffmpeg-montagem-video|FFmpeg]] sobrepõe elementos:
```bash
ffmpeg -i base_video.mp4 \
  -i music_track.mp3 \
  -filter_complex "[0:v]drawtext=text='Compre agora':fontfile=/path/to/font.ttf:fontsize=48[v1];[v1][1:a]concat=n=1:v=1:a=1[out]" \
  -map "[out]" \
  output_final.mp4
```

**Etapa 5: Upload para plataformas.** Renoise integra com Meta Ads, TikTok, YouTube:
```python
from renoise import RenovClient

client = RenovClient(api_key="...")

# Upload em batch para Meta Ads
campaign = client.create_campaign(
    name="TeniisXYZ_Escalada",
    videos=[f"videos/variant_{i:03d}.mp4" for i in range(200)],
    platform="meta",
    account_id="..."
)

# Renoise gerencia A/B testing automático
campaign.run_ab_test(metrics=["ctr", "conversion_rate"])
```

**Etapa 6: Monitor e otimização.** Renoise rastreia performance de cada variação:
```json
{
  "variant_001": {
    "ctr": 3.2,
    "conversion_rate": 0.8,
    "cost_per_result": 1.45
  }
}
```

Vencedores são escalados, perdedores pausados automaticamente.

## Stack e requisitos

- Renoise (SaaS): $500-2000/mês dependendo volume
- Seedance 2.0 API: ~$0.05-0.20 por vídeo
- Meta Ads/TikTok accounts com budget para testes
- Imagem de produto em alta resolução
- Briefing de marca + CTA options
- Tempo: 4-8 horas setup + coleta de assets

## Armadilhas e limitações

Seedance 2.0 pode gerar movimento visualmente artificial em alguns casos — requer validação humana. Homogeneização criativa é risco real: 200 variações geradas mecanicamente podem parecer "todas iguais" — adicione variação estética manual. CTA repetitivo em centenas de vídeos reduz recall — revise top performers e redesenhe outliers. Meta/TikTok algorithms não favorecem AI-generated content detectável (pode ter menor reach) — considere blending com conteúdo humano. Custo acumula rápido com 200 vídeos — validate com pequeno batch (20-30) antes de escalar.

## Conexões

[[Pipelines Multimodais de IA]], [[Vibe Coding para Desenvolvimento de Jogos]], [[Automação de Conteúdo]], [[ffmpeg-montagem-video|FFmpeg: Montagem e Transcodificação]], [[text-to-speech-apis|Text-to-Speech APIs]]

## Histórico

- 2026-04-02: Nota criada
- 2026-04-02: Reescrita como guia de implementação