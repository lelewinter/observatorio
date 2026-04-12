---
tags: [audio, transcricao, whisper, gpu, nlp, speech-to-text, local, faster-whisper]
source: https://github.com/SYSTRAN/faster-whisper | https://github.com/Vaibhavs10/insanely-fast-whisper | https://modal.com/blog/choosing-whisper-variants
date: 2026-04-02
tipo: aplicacao
---

# Transcrição de Áudio Local com GPU: Whisper, Faster-Whisper & Insanely-Fast-Whisper (2026)

## O que é

Whisper é o modelo open-source de speech-to-text do OpenAI que roda completamente local (sem cloud). Suporta 90+ idiomas, funciona offline, e em GPU alcança **30x real-time** (2.5 horas de áudio em 5 minutos em RTX 3060). Duas variantes otimizadas dominam 2026:

1. **Faster-Whisper**: 4x mais rápido que Whisper vanilla, usa CTranslate2 (engine inference otimizado).
2. **Insanely-Fast-Whisper**: Velocidade máxima em GPUs altas; troca-off entre precisão e throughput.

Ambas rodam local, não exigem API key, não enviam dados pra cloud. Privacidade total.

## Por que importa agora

1. **Privacidade**: Dados de áudio nunca saem da máquina. Crítico para Leticia se estiver transcrevendo notas pessoais, estudos sensíveis, ou conteúdo privado.

2. **Costo zero**: Sem limite de minutos/mês como APIs (Whisper API paga ~$0.36 por hora de áudio). 150h/ano em Whisper local = grátis; em cloud = ~$54/ano.

3. **Offline-first**: Estudar no trem, avião, ou lugar sem internet. Transcrição funciona completamente offline após download do modelo.

4. **Latência previsível**: Whisper API tem fila; local garante início imediato.

Leticia estuda à noite; pode gravar aulas, podcasts, ou notas de voz, e transcrever instantaneamente.

## Como implementar

### 1. Setup Básico com Faster-Whisper

```bash
# Instalar (escolha conforme GPU)
pip install faster-whisper

# Ou para Insanely-Fast-Whisper
pip install insanely-fast-whisper

# Ou Whisper vanilla (mais lento, mas simples)
pip install openai-whisper
```

### 2. Uso Vanilla (Whisper original)

```python
import whisper
import torch

# Detectar GPU
device = "cuda" if torch.cuda.is_available() else "cpu"
print(f"Usando: {device}")

# Carregar modelo (tamanhos: tiny, base, small, medium, large)
# tiny: 39M params, ~1GB VRAM, mais rápido, menos acurácia
# large: 1.5B params, 8GB VRAM, mais preciso
model = whisper.load_model("base", device=device)

# Transcrever arquivo
result = model.transcribe("audio.mp3", language="pt", verbose=True)

print(result["text"])
# Output: "Olá, meu nome é Leticia e estou estudando Whisper."

# Com timestamps
for segment in result["segments"]:
    print(f"[{segment['start']:.2f}s - {segment['end']:.2f}s] {segment['text']}")
```

**Performance esperada (Whisper large, RTX 3060)**:
- 1 minuto de áudio: ~2 segundos processamento (30x real-time)
- 1 hora de áudio: ~2 minutos processamento

### 3. Otimizado: Faster-Whisper

Usa CTranslate2, que reescreve internals com:
- Quantização (FP32 → INT8), reduz VRAM
- Kernel otimizado
- Batching

```python
from faster_whisper import WhisperModel

# device="cuda" se GPU disponível, "cpu" caso contrário
# compute_type="float16" (rápido, leve) ou "int8" (muito leve, menos preciso)
model = WhisperModel(
    "base",
    device="cuda",
    compute_type="float16"  # ou "int8" se VRAM limitada
)

# Transcrever
segments, info = model.transcribe("audio.mp3", language="pt")

for segment in segments:
    print(f"[{segment.start:.2f}s] {segment.text}")

# Velocidade: 8-10x faster que vanilla no mesmo modelo
```

**Comparação de velocidade (2026 benchmark, 1 hora de áudio)**:

| Implementação | Compute Type | GPU (RTX 3060) | VRAM | Acurácia (WER) |
|---------------|------------|---|---|---|
| Whisper vanilla | float32 | 6.5 min | 8GB | 5.4% |
| Faster-Whisper | float32 | 1.8 min | 4GB | 5.4% |
| Faster-Whisper | float16 | 1.2 min | 2GB | 5.5% |
| Faster-Whisper | int8 | 0.9 min | 1.5GB | 5.8% |
| Insanely-Fast | (otimizado) | 0.45 min | 1GB | 6.2% |

### 4. Insanely-Fast: Máxima Velocidade

```python
import torch
from transformers import AutoModelForSpeechSeq2Seq, AutoProcessor, pipeline

# Setup pipeline com BetterTransformer + Flash Attention 2
device = "cuda:0" if torch.cuda.is_available() else "cpu"
torch_dtype = torch.float16 if device != "cpu" else torch.float32

model_id = "openai/whisper-large-v3-turbo"

model = AutoModelForSpeechSeq2Seq.from_pretrained(
    model_id,
    torch_dtype=torch_dtype,
    low_cpu_mem_usage=True,
    use_safetensors=True
).to(device)

# Ativa BetterTransformer (não disponível em todas versões)
try:
    model.model.encoder = model.model.encoder.to_bettertransformer()
except:
    print("BetterTransformer não disponível; usando padrão")

processor = AutoProcessor.from_pretrained(model_id)

pipe = pipeline(
    "automatic-speech-recognition",
    model=model,
    tokenizer=processor.tokenizer,
    feature_extractor=processor.feature_extractor,
    torch_dtype=torch_dtype,
    device=device,
    chunk_length_s=30,  # processar em chunks de 30s
    batch_size=16       # paralelizar processamento
)

# Transcrever
result = pipe("audio.mp3", generate_kwargs={"language": "pt"})
print(result["text"])

# Velocidade esperada: 150 minutos de áudio em ~98 segundos
```

**Otimizações ativadas**:
- **Flash Attention 2**: Kernel CUDA customizado que reduz memória e acelera atenção.
- **BetterTransformer**: Loops de transformação compilados em C, bypass overhead Python.
- **Chunking**: Processa áudio em pedaços, não arquivo inteiro (evita memória pico).
- **Batching**: Múltiplos chunks em paralelo.

### 5. Caso Real: Transcrever Podcasts com Leticia

```python
import os
from pathlib import Path
from faster_whisper import WhisperModel
import json
from datetime import datetime

class PodcastTranscriber:
    def __init__(self, model_size="base", device="cuda"):
        self.model = WhisperModel(model_size, device=device, compute_type="float16")
        self.transcripts_dir = Path("~/Documentos/Transcriptions").expanduser()
        self.transcripts_dir.mkdir(exist_ok=True)
    
    def transcribe(self, audio_file, language="pt"):
        """Transcrever arquivo, salvar em JSON + Markdown."""
        
        print(f"Transcrevendo: {audio_file}")
        segments, info = self.model.transcribe(audio_file, language=language)
        
        # Converter para lista
        segments = list(segments)
        
        # Salvar JSON (estruturado)
        output_name = Path(audio_file).stem
        json_file = self.transcripts_dir / f"{output_name}.json"
        
        with open(json_file, 'w', encoding='utf-8') as f:
            json.dump({
                'file': audio_file,
                'language': language,
                'duration': info.duration,
                'timestamp': datetime.now().isoformat(),
                'segments': [
                    {
                        'start': s.start,
                        'end': s.end,
                        'text': s.text
                    } for s in segments
                ]
            }, f, ensure_ascii=False, indent=2)
        
        # Salvar Markdown (legível)
        md_file = self.transcripts_dir / f"{output_name}.md"
        with open(md_file, 'w', encoding='utf-8') as f:
            f.write(f"# {output_name}\n\n")
            f.write(f"**Data**: {datetime.now().strftime('%Y-%m-%d %H:%M')}\n")
            f.write(f"**Duração**: {info.duration:.1f}s\n\n")
            
            for segment in segments:
                minutes, seconds = divmod(segment.start, 60)
                f.write(f"[{int(minutes):02d}:{seconds:05.2f}] {segment.text}\n")
        
        print(f"✓ Salvo em {json_file} e {md_file}")
        return segments

# Usar
transcriber = PodcastTranscriber(model_size="base")
transcriber.transcribe("aula_ia_20260410.mp3", language="pt")
```

**Output JSON**:
```json
{
  "file": "aula_ia_20260410.mp3",
  "language": "pt",
  "duration": 3600,
  "timestamp": "2026-04-10T20:30:00",
  "segments": [
    {
      "start": 0.0,
      "end": 12.5,
      "text": "Olá, bem-vindo ao curso de Inteligência Artificial."
    },
    {
      "start": 12.5,
      "end": 28.3,
      "text": "Vamos começar com os fundamentos de redes neurais."
    }
  ]
}
```

## Stack e requisitos

### Hardware

| Modelo | VRAM | RTX 3060 | GTX 1070 | M1 MacBook | Tempo/1h áudio |
|--------|------|---------|---------|-----------|---|
| Whisper tiny | 0.5GB | ✓✓ | ✓ | ✓ | 8s |
| Whisper base | 1GB | ✓✓ | ✓ | ✓ | 20s |
| Whisper small | 2GB | ✓ | ✓ | ✓ | 40s |
| Whisper medium | 5GB | ✓ (tight) | marginal | ✓ | 1.5min |
| Whisper large | 10GB | ✓ (swap) | ✗ | ✓ | 2min |

**Recomendação para Leticia**:
- GPU: RTX 3060 8GB (via colab) ou local com "base" model.
- CPU-only: apenas "tiny" é aceitável (30s por minuto de áudio).

### Software

```bash
# Dependências
pip install librosa soundfile scipy  # manipulação de áudio

# Escolher uma:
pip install openai-whisper          # vanilla
pip install faster-whisper          # recomendado
pip install insanely-fast-whisper   # máxima velocidade

# Opcional: processamento em batch
pip install pydub ffmpeg-python     # converter formatos (mp4 → wav)
```

### Dados

Whisper requer download de modelo na primeira execução:
- **tiny**: 39M → 140MB disk
- **base**: 74M → 290MB disk
- **small**: 244M → 970MB disk
- **medium**: 769M → 3GB disk
- **large**: 1.5B → 6GB disk

Cache default: `~/.cache/huggingface/hub/` (pode ser 10GB+ se usar múltiplos modelos).

## Armadilhas e limitações

### Técnicas

1. **Accent/dialect mismatch**: Whisper treinado em data diversa, mas português (Portugal) vs português (Brasil) podem ter acurácia diferente. Testar em sample pessoal antes de processar 10h de áudio.

2. **Background noise**: Whisper é robusto, mas ruído forte (ventilador, tráfego) reduz acurácia. Denoising prévio com librosa ajuda:
```python
import librosa
import soundfile as sf

y, sr = librosa.load("audio_noisy.mp3")
y_denoised = librosa.effects.harmonic(y)  # remover ruído percussivo
sf.write("audio_clean.wav", y_denoised, sr)
```

3. **Memory leaks em loop**: Se transcrever 100 arquivos em loop, GPU memory pode não ser liberada. Usar:
```python
import gc
import torch

for audio_file in files:
    segments, _ = model.transcribe(audio_file)
    # ... processar
    
    # Limpar cache GPU a cada 10 arquivos
    if i % 10 == 0:
        gc.collect()
        torch.cuda.empty_cache()
```

4. **Whisper-large-v3-turbo vs large**: Em 2026, Turbo é ~5x mais rápido que large com acurácia quasi-equivalente. Preferir turbo se disponível.

### Práticas

5. **Batch processing com queue**: Transcrever muitos arquivos em paralelo pode sobrecarregar GPU. Usar fila:
```python
from queue import Queue
import threading

transcribe_queue = Queue()

def worker():
    while True:
        audio_file = transcribe_queue.get()
        transcriber.transcribe(audio_file)
        transcribe_queue.task_done()

# Iniciar 2 workers (CPU-bound preprocessing)
for _ in range(2):
    t = threading.Thread(target=worker, daemon=True)
    t.start()

# Enqueue arquivos
for audio_file in large_list:
    transcribe_queue.put(audio_file)

transcribe_queue.join()
```

6. **Fallback para CPU**: Se GPU encher, implementar fallback:
```python
try:
    model = WhisperModel("base", device="cuda", compute_type="float16")
    segments, _ = model.transcribe(audio_file)
except torch.cuda.OutOfMemoryError:
    print("GPU out of memory, falling back to CPU...")
    model = WhisperModel("tiny", device="cpu", compute_type="int8")
    segments, _ = model.transcribe(audio_file)
```

7. **Language detection falha**: Whisper consegue detectar idioma automaticamente, mas linguagem mista (português + inglês) pode ser detectada como errada. Especificar manualmente:
```python
# Em vez de language=None (auto-detect)
segments, _ = model.transcribe(audio_file, language="pt")  # força português
```

### Conceituais

8. **Diferença entre WER e qualidade prática**: WER (Word Error Rate) é métrica, mas Leticia pode achar transcrição perfeitamente legível com 5-10% WER se erros forem em palavras técnicas (nomes, jargão).

9. **Fine-tuning pessoal não funciona bem**: Tentar treinar Whisper em amostra pessoal (50-100 áudios) tipicamente piora performance. Whisper pré-treinado já é bom; melhor ajustar prompt (context) se erros sistêmicos.

10. **Streaming não é suportado nativamente**: Whisper processa arquivo inteiro. Se quiser transcrição em tempo real (ex: podcast ao vivo), exige arquitetura diferente (Yarp, distilled models).

## Conexões

- [[local-llm-inference-ollama-vllm|Local LLM Inference: Ollama, vLLM]] — executar LLMs localmente offline
- [[audio-processing-librosa-essentia|Audio Processing com librosa & Essentia]] — pré-processamento e análise de áudio
- [[pipeline-nlp-ponta-a-ponta|Pipeline NLP Ponta-a-Ponta]] — integrar transcrição em fluxo maior

## Histórico

- 2026-04-02: Nota criada (simplista)
- 2026-04-11: Expansão profunda com 3 variantes, benchmarks GPU 2026, código real, armadilhas técnicas
