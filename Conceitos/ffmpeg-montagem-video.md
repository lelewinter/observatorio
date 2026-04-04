---
tags: [conceito, ffmpeg, video, automacao, montagem, transcoding]
date: 2026-04-02
tipo: conceito
aliases: [FFmpeg Automation, Video Encoding, Montagem Automatizada]
---
# FFmpeg: Montagem e Transcodificação Automatizada

## O que é

FFmpeg é utilitário de linha de comando (CLI) para processamento de áudio/vídeo: decodificação, filtros, codificação, multiplexing. Crítico para pipelines de automação porque: (1) zero custo, (2) controle fino (bitrate, codec, resolução), (3) infinitamente scriptável (CLI + stdin/stdout), (4) suporta centenas de formatos.

Diferencia-se de MoviePy (wrapper Python) por: performance (FFmpeg é C nativo), complexidade de filtros (FFmpeg filtergraph é Turing-complete), mas tem curva de aprendizado mais acentuada.

## Como funciona

**Arquitetura interna FFmpeg:**

```
Input → Demuxing → Decoding → Filtering → Encoding → Muxing → Output
```

- **Demuxing:** Parse de container (MP4, MKV, WebM) e extrai streams (video, audio, subtítulos).
- **Decoding:** Converte codec comprimido (H.264, VP9) em frames brutos (YUV).
- **Filtering:** Aplica transformações (scale, fps, overlay, fade, colorspace).
- **Encoding:** Recomprime frames com novo codec/bitrate.
- **Muxing:** Recombina streams comprimidos no container final.

**Sintaxe básica:**

```bash
ffmpeg -i input.mp4 -c:v libx264 -preset fast -crf 23 output.mp4
```

- `-i input.mp4`: arquivo de entrada
- `-c:v libx264`: codec de vídeo (H.264)
- `-preset fast`: speed/quality trade-off (ultrafast, superfast, veryfast, faster, fast, medium, slow, slower, veryslow)
- `-crf 23`: quality (0=lossless, 23=visually lossless, 51=worst)
- `-c:a aac`: codec de áudio
- `output.mp4`: arquivo de saída

**Operações Frequentes:**

**1. Montagem Multi-input (vídeo + áudio):**
```bash
ffmpeg -i video_base.mp4 -i audio_narrado.mp3 -i background_music.mp3 \
  -filter_complex "[0:v]scale=1080:1920[v];[1:a]volume=1[narrado];[2:a]volume=0.3[music];[narrado][music]amerge[a]" \
  -map "[v]" -map "[a]" \
  -c:v libx264 -preset fast -crf 23 \
  -c:a aac -b:a 128k \
  output.mp4
```

Breakdown:
- `[0:v]` = stream de vídeo do input 0
- `scale=1080:1920` = redimensiona para 1920×1080 (vertical)
- `[narrado][music]amerge` = mistura dois áudios
- `-map "[v]" -map "[a]"` = mapeia output de filtro para streams finais

**2. Transcodificação com Otimização de Plataforma:**

YouTube Shorts (vertical, H.264, AAC):
```bash
ffmpeg -i input.mp4 \
  -c:v libx264 -preset medium -crf 22 \
  -s 1080x1920 -r 30 \
  -c:a aac -b:a 128k \
  -movflags +faststart \
  shorts_output.mp4
```

TikTok (vertical, VP9 preferido):
```bash
ffmpeg -i input.mp4 \
  -c:v libvpx-vp9 -crf 30 -b:v 800k \
  -c:a libopus -b:a 96k \
  -s 1080x1920 -r 30 \
  tiktok_output.webm
```

**3. Overlay de Texto Dinâmico:**
```bash
ffmpeg -i video_base.mp4 \
  -vf "drawtext=textfile=subtitles.txt:fontsize=48:fontcolor=white:y=(h-text_h)/2" \
  output_com_texto.mp4
```

**4. Fade In/Out:**
```bash
ffmpeg -i input.mp4 \
  -vf "fade=t=in:st=0:d=1,fade=t=out:st=9:d=1" \
  -c:a copy \
  output_fade.mp4
```

**5. Concatenação de Múltiplos Clipes:**
```bash
# 1. Criar arquivo de lista
echo "file 'clip1.mp4'" > lista.txt
echo "file 'clip2.mp4'" >> lista.txt
echo "file 'clip3.mp4'" >> lista.txt

# 2. Concatenar
ffmpeg -f concat -safe 0 -i lista.txt -c copy output.mp4
```

**Performance & Otimização:**

- **GPU Encoding:** Se tem NVIDIA, usar `-c:v hevc_nvenc` em vez de libx264 (10x mais rápido, mesma qualidade).
- **Multithread:** FFmpeg automaticamente usa N cores; set explicitly: `-threads 8`.
- **Preset vs. Quality:** `-preset fast -crf 23` é sweet spot (qualidade alta, tempo aceitável). Não usar `veryfast` pra conteúdo profissional.
- **Bitrate Adaptativo:** Em vez de CRF (constant rate factor), usar `-b:v 800k` (constant bitrate) para previsibilidade de tamanho.

## Pra que serve

**Automação de montagem:** Gerar 100 vídeos Shorts/TikToks parametrizados (textos, áudios, overlays) via script.

**Otimização pra plataforma:** Convertendo MP4 genérico para formato nativo de cada rede (resolução, fps, codec).

**Processamento em lote:** Dividir vídeo longo em capítulos, aplicar watermark em 1000 vídeos, extrair keyframes.

**Streaming ao vivo:** FFmpeg integra com OBS/Streamlabs; pode usar filtergraph para efeitos em tempo real.

**Quando NÃO usar:**
- Interface gráfica necessária → use DaVinci Resolve, Adobe Premiere (melhor UX).
- Tempo real strict (<500ms) → FFmpeg tem latência de 1-3s (use GStreamer).
- Trabalho manual iterativo → CLI é lento pra experimentar (use Python + MoviePy).

## Exemplo prático

**Cenário:** Gerar 50 YouTube Shorts com padrão: base video (10s) + narração (TTS) + música fundo + texto com dica em 3 pontos da timeline.

**Setup Python + FFmpeg:**

```python
import subprocess
import json

DICAS = [
    {"titulo": "Dica 1", "texto": "Use pomodoro", "naracao": "Use a técnica..."},
    # ... 49 mais
]

TEMPLATE_FILTRO = """
[0:v] scale=1080:1920, fps=30 [v_scaled];
[1:a] volume=1 [narrado];
[2:a] volume=0.2 [music];
[narrado][music] amerge [audio_final];
[v_scaled] drawtext=text='{text_point1}':fontsize=48:fontcolor=white:y=h/4:x=(w-text_w)/2:enable='between(t,2,4)' [v1];
[v1] drawtext=text='{text_point2}':fontsize=48:fontcolor=white:y=h/2:x=(w-text_w)/2:enable='between(t,5,7)' [v2];
[v2] drawtext=text='{text_point3}':fontsize=48:fontcolor=white:y=3*h/4:x=(w-text_w)/2:enable='between(t,8,10)' [v_final]
"""

def gerar_shorts(dica_idx, dica):
    # Setup paths
    base_video = "base_10s.mp4"
    naracao_mp3 = f"narracoes/{dica_idx}.mp3"
    musica_mp3 = "background_music.mp3"
    output = f"shorts/{dica_idx}.mp4"

    # Montar filtro com textos dinâmicos
    filter_graph = TEMPLATE_FILTRO.format(
        text_point1=dica["titulo"],
        text_point2=dica["texto"].split()[0:5],  # primeira linha
        text_point3=dica["texto"].split()[5:10]  # segunda linha
    )

    # Comando FFmpeg
    cmd = [
        "ffmpeg",
        "-i", base_video,
        "-i", naracao_mp3,
        "-i", musica_mp3,
        "-filter_complex", filter_graph,
        "-map", "[v_final]",
        "-map", "[audio_final]",
        "-c:v", "libx264",
        "-preset", "fast",
        "-crf", "23",
        "-c:a", "aac",
        "-b:a", "128k",
        output
    ]

    # Executar
    subprocess.run(cmd, check=True)
    print(f"✓ Gerado: {output}")

# Gerar todos os 50 Shorts
for idx, dica in enumerate(DICAS):
    gerar_shorts(idx, dica)
```

**Resultado:** 50 vídeos montados em ~5 minutos (4 vídeos/min com `-preset fast` em CPU moderna).

## Conexões com Notas

- [[pipelines-multimodais-de-ia-permitem-producao-automatizada-de-video-a-custo-marg|Pipeline YouTube Shorts Multimodal]] — integra FFmpeg para composição final
- [[producao-de-video-programatica-com-ia|Produção de Vídeo Programática]] — usa FFmpeg para overlay de CTA e áudio
- [[Mistral TTS Text-to-Speech Local Gratuito]] — TTS que pode ser combinado com FFmpeg para montagem
- [[text-to-speech-apis|Text-to-Speech APIs]] — síntese de áudio para composição com FFmpeg

---
*Conceito extraído em 2026-04-02*
