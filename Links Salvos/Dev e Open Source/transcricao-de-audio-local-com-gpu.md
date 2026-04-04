---
tags: [audio, transcricao, whisper, gpu, nlp]
date: 2026-04-02
tipo: aplicacao
---
# Transcrever Áudio Localmente com Whisper (GPU)

## O que é
OpenAI Whisper roda local, suporta 90+ idiomas, 30x mais rápido em GPU.

## Como implementar
```bash
pip install openai-whisper

# Transcrever
whisper audio.mp3 --model large --language pt
```

**Python:**
```python
import whisper

model = whisper.load_model("large", device="cuda")
result = model.transcribe("audio.mp3")
print(result["text"])
```

**Speed:**
- CPU: ~6x real-time
- GPU: ~30x real-time
- VRAM: 8GB para "large"

## Histórico
- 2026-04-02: Reescrita
