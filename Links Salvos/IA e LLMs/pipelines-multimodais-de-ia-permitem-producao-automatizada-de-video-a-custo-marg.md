---
tags: [ia-generativa, automacao, pipeline, video, open-source, llm, multimodal]
source: https://x.com/aiwithmayank/status/2039288878180520032?s=20
date: 2026-04-01
tipo: aplicacao
---

# Pipeline YouTube Shorts Multimodal com Custo Marginal ~$0.10

## O que é

Sistema open-source que encadeia Claude (roteiro), Gemini Imagen (imagens), ElevenLabs TTS (voz), Whisper (legendas) para converter texto em vídeo YouTube Shorts publicado automaticamente. Custo total por vídeo: $0.08-0.12.

## Como implementar

**Pré-requisito:** Git, Python 3.9+, FFmpeg instalado. Clone repositório: `git clone https://github.com/YouTubeShortsPipeline/yt-shorts-pipeline && cd yt-shorts-pipeline`.

**Etapa 1: Setup de credenciais.** Crie arquivo `.env`:
```
ANTHROPIC_API_KEY=sk-...
GEMINI_API_KEY=...
ELEVENLABS_API_KEY=...
YOUTUBE_CREDENTIALS_PATH=./credentials.json
```

Configure Google OAuth2 para upload automático em YouTube. ElevenLabs: obtenha voice ID via API.

**Etapa 2: Geração de roteiro.** Script `generate_script.py` recebe prompt em texto simples:
```bash
python scripts/generate_script.py \
  --topic "A história do Bitcoin" \
  --length short \
  --language pt-BR
```

Claude gera roteiro estruturado em JSON:
```json
{
  "title": "Bitcoin: A Revolução Digital",
  "scenes": [
    {"duration": 3, "narration": "...", "visual_prompt": "..."},
    ...
  ],
  "music_style": "uplifting"
}
```

**Etapa 3: Síntese de imagens.** Para cada cena, Gemini Imagen gera imagem baseada em `visual_prompt`. Salva em `assets/images/scene_N.png`. Resolução: 1080x1920 (vertical para shorts).

**Etapa 4: Síntese de voz.** ElevenLabs TTS converte `narration` em MP3 com voice ID consistente. Opcionalmente, customize inflexão com SSML: `<prosody rate="0.9" pitch="1.2">texto</prosody>`.

**Etapa 5: Composição de vídeo.** [[ffmpeg-montagem-video|FFmpeg]] encadeia: background music (looping) + narração sobreposta + imagens sincronizadas com duração + legendas geradas via Whisper. Saída: `output/video.mp4` (H.264, 30fps).

**Etapa 6: Upload e publicação.** Script `publish.py` envia MP4 para YouTube com título, descrição, tags e privacidade configuráveis:
```bash
python scripts/publish.py \
  --video output/video.mp4 \
  --title "Bitcoin: A Revolução Digital" \
  --description "Aprenda sobre Bitcoin em 60 segundos" \
  --tags "bitcoin,cripto,educacao"
```

**Modo dry-run.** Para validar sem gastar créditos: `--dry-run` gera storyboard em HTML com imagens e roteiro sincronizados.

**Automação periódica.** Schedule via cron (Linux) ou Task Scheduler (Windows):
```bash
0 9 * * * cd ~/yt-shorts && python scripts/publish.py --topic "noticia_do_dia" --schedule-publish
```

## Stack e requisitos

- Claude API (Sonnet 3.5 recomendado): ~$0.03/vídeo
- Gemini Imagen: ~$0.04/vídeo
- ElevenLabs TTS: ~$0.03/vídeo (50K caracteres/mês gratuitos em free tier)
- YouTube Data API (grátis)
- FFmpeg (open-source)
- Python 3.9+, pip
- Hardware: CPU qualquer (processamento é cloud-based)

## Armadilhas e limitações

Gemini Imagen pode gerar imagens com estética repetitiva sem prompt bem estruturado. Sincronização áudio-visual depende de duração estimada — se narração é mais longa que esperado, vídeo fica fora de sincro. ElevenLabs rate-limits em free tier (quota diária). YouTube demora 15-30 min para processar vídeo antes de publicar — não é instantâneo. Português do Brasil em TTS é inferior ao inglês em qualidade. Whisper pode errar legendas em ambiente com ruído de fundo (música alta).

## Conexões

[[Produção de Vídeo Programática com IA]], [[Pipelines de IA Local Self-Hosted]], [[Automação de Conteúdo com Agentes]], [[ffmpeg-montagem-video|FFmpeg: Montagem e Transcodificação]], [[text-to-speech-apis|Text-to-Speech APIs]]

## Histórico

- 2026-04-01: Nota criada
- 2026-04-02: Reescrita como guia de implementação prática