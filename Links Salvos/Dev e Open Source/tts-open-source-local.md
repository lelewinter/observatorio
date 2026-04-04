---
tags: [tts, audio, sintetizacao, voz, open-source]
date: 2026-04-02
tipo: aplicacao
---
# Síntese de Voz Open-Source Localmente

## O que é
Gerar áudio de voz a partir de texto sem APIs externas. Alternativas: Piper, Glow-TTS, FastPitch.

## Como implementar
```bash
pip install piper-tts

piper --model pt_BR/zeferino_medium.onnx   < texto.txt > output.wav
```

**Programaticamente:**
```python
from piper import Piper

piper = Piper("pt_BR/zeferino_medium.onnx")
audio = piper.synthesize("Olá mundo")
audio.save("output.wav")
```

## Stack e requisitos
- Piper ou Glow-TTS
- ONNX runtime (CPU)
- Opcional GPU para speed

## Histórico
- 2026-04-02: Reescrita
