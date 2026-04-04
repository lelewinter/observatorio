---
tags: [tts, audiobooks, conversao, documentos, audio, acessibilidade]
source: https://x.com/tom_doerr/status/2039381547166408950?s=20
date: 2026-04-02
tipo: aplicacao
---

# Converter Documentos para Audiobooks com TTS Moderno

## O que é

Pipeline automatizado que lê PDFs/markdown/docx e gera audiobooks com qualidade natural (48kHz). Modelos como Qwen TTS oferecem prosódia e ritmo superiores a TTS tradicionais.

## Como implementar

**Setup:**
```bash
pip install qwen-tts PyPDF2 pydub librosa soundfile
```

**Caso 1: PDF → Audiobook**
```python
import PyPDF2
from qwen_tts import QwenTTS
import soundfile as sf
import numpy as np

tts = QwenTTS(language="pt-BR")
reader = PyPDF2.PdfReader("livro.pdf")
text = "".join([page.extract_text() for page in reader.pages])

paragraphs = text.split("\n\n")
audios = []

for para in paragraphs:
    if len(para.strip()) < 10:
        continue
    audio = tts.synthesize(para)
    audios.append(audio.numpy())

combined = np.concatenate(audios)
sf.write("audiobook.wav", combined, 24000)
```

**Caso 2: Chapters com timestamps**
```python
import json
from datetime import timedelta

chapters = []
current_time = 0

for chapter_title, chapter_text in [(t, c) for t, c in chapter_data]:
    audio = tts.synthesize(chapter_text)
    duration = len(audio.numpy()) / 24000

    chapters.append({
        "title": chapter_title,
        "start": str(timedelta(seconds=int(current_time))),
        "duration": str(timedelta(seconds=int(duration)))
    })
    current_time += duration

with open("chapters.json", "w") as f:
    json.dump(chapters, f, indent=2)
```

**Caso 3: Vozes múltiplas**
```python
screenplay = [
    ("narrator", "Assim começou..."),
    ("char1", "Olá, quem é você?"),
    ("char2", "Sou um viajante.")
]

for speaker, text in screenplay:
    audio = tts.synthesize(text, speaker=speaker)
    audio.save(f"{speaker}.wav")
```

**Caso 4: Batch parallelizado**
```python
import multiprocessing

def worker(task_queue, result_queue):
    while True:
        task = task_queue.get()
        if task is None:
            break
        section_id, text = task
        audio = tts.synthesize(text)
        result_queue.put((section_id, audio))

# 4 workers
for _ in range(4):
    p = multiprocessing.Process(target=worker, args=(tasks, results))
    p.start()
```

## Stack e requisitos

- **TTS**: Qwen TTS / OpenVoice (48kHz, 16-bit)
- **Python**: 3.8+
- **Libraries**: PyPDF2, librosa, soundfile
- **GPU**: 4GB+ VRAM (recomendado)
- **Custo**: $0 (open-source)

## Armadilhas

1. **Limitação: prosódia**: Chunks > 500 palavras perdem naturalidade. Limitar tamanho.

2. **Armadilha: caracteres especiais**: Fórmulas LaTeX/símbolos não sintetizam bem. Converter para texto.

3. **Limitação: múltiplos idiomas**: Misturar PT/EN degrada qualidade. Separar por idioma.

4. **Armadilha: velocidade**: Speed > 1.2x compromete qualidade. Manter 0.9-1.1x.

5. **Limitação: contexto**: Max ~2000 tokens por chunk. Chunking mandatório.

## Conexões

- [[clonagem-de-voz-local-open-source]] - Clonar voz narrador
- [[tts-open-source-local]] - Alternativas de TTS
- [[transcricao-de-audio-local-com-gpu]] - Transcrever áudio

## Histórico

- 2026-04-02: Reescrita com implementação prática
