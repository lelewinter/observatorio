---
tags: [IA-local, LLM, self-hosted, RAG, ferramentas, privacidade]
source: https://x.com/0xCVYH/status/2034752820159635746?s=20
date: 2026-04-02
tipo: aplicacao
---

# Montar Stack Completo de IA Local (Ollama + WebUI + Whisper + EdgeTTS + AnythingLLM RAG)

## O que é

Um ambiente completo de IA local self-hosted — com gerenciamento de modelos, interface web, transcrição de áudio, síntese de voz e RAG (Retrieval-Augmented Generation) — rodando inteiramente na máquina do usuário, sem APIs pagas ou transmissão de dados externos.

## Por que importa

**Privacidade**: Dados nunca saem da sua rede — contratos, documentos sensíveis, conversas ficam on-premise.

**Custo**: Zero recorrente. Uma vez instalado, não há billing por query (diferente de Claude API, GPT-4, etc).

**Controle**: Você escolhe qual modelo rodar, quando fazer updates, que dados indexar. Sem vendor lock-in.

**Latência**: Inferência local é ~500ms-2s dependendo do modelo e hardware, vs. 1-5s com API cloud + rede.

**Casos de uso práticos**:
- Empresa: Documentação privada + RAG = "Chat com seus manuais"
- Pesquisador: Rodar múltiplos modelos em paralelo para comparação
- Privacy-first: Processamento de dados sensíveis (saúde, financeiro)
- Offline-first: Laptop sem internet = IA funcionando normalmente

## Como funciona / Como implementar

### Arquitetura da Stack

```
┌─────────────────────────────────────────────────────────┐
│                 User Interface Layer                     │
├─────────────────────────────────────────────────────────┤
│ Open WebUI (browser)     AnythingLLM Desktop App        │
│ • Chat familiar (ChatGPT-like)  • Drag-drop files      │
│ • Model selection         • Visual RAG setup            │
│ • Settings                • Chat + knowledge base       │
└──────────┬──────────────────────────┬──────────────────┘
           │                          │
           ↓                          ↓
┌──────────────────┐    ┌───────────────────────┐
│ LLM Inference    │    │ RAG Processing        │
├──────────────────┤    ├───────────────────────┤
│ Ollama           │    │ AnythingLLM           │
│ • Model manager  │    │ • Embedding           │
│ • API REST       │    │ • Vector DB (local)   │
│ • Quantization   │    │ • Document indexing   │
│ • GPU accel      │    │ • Context injection   │
└──────────┬───────┘    └──────────┬────────────┘
           │                       │
           └───────────┬───────────┘
                       ↓
        ┌──────────────────────────────┐
        │   Local Model Storage        │
        ├──────────────────────────────┤
        │ ~/.ollama/models/            │
        │  ├── llama2:7b-q4            │
        │  ├── mistral:7b-q4           │
        │  ├── neural-chat:7b          │
        │  └── nomic-embed-text        │
        └──────────────────────────────┘
```

### Camada 1: Ollama (Model Management)

Ollama é um gerenciador de modelos LLM — equivalente a `apt` para Linux, mas para Large Language Models.

**Instalação**:

```bash
# macOS
brew install ollama

# Linux
curl https://ollama.ai/install.sh | sh

# Windows (WSL2 recomendado)
# Download: https://ollama.ai/download/windows

# Iniciar servidor
ollama serve  # Escuta em http://localhost:11434
```

**Baixar modelos**:

```bash
# 7B = 7 bilhões de parâmetros (fast, ~4GB VRAM)
ollama pull llama2:7b-q4       # Meta Llama 2, quantizado INT4 (3.5GB)
ollama pull mistral:7b         # Mistral 7B (rápido, bom reasoning)
ollama pull neural-chat:7b     # Otimizado para chat (recomendado para novo user)

# Embeddings (para RAG)
ollama pull nomic-embed-text   # 768-dimensional embeddings (384MB)

# Listar modelos instalados
ollama ls
```

**API REST** (usado por Open WebUI, AnythingLLM):

```bash
# Fazer request direto (debugging)
curl -X POST http://localhost:11434/api/generate -d '{
  "model": "mistral:7b",
  "prompt": "Why is the sky blue?",
  "stream": false
}'

# Response
{
  "model": "mistral:7b",
  "created_at": "2026-04-11T10:30:00Z",
  "response": "The sky appears blue due to Rayleigh scattering...",
  "done": true
}
```

### Camada 2: Open WebUI (Interface)

Interface web similar ao ChatGPT para interagir com modelos locais.

**Instalação**:

```bash
# Docker (recomendado, mais fácil)
docker run -d \
  -p 3000:8080 \
  -e OLLAMA_API_BASE_URL=http://host.docker.internal:11434 \
  --name open-webui \
  ghcr.io/open-webui/open-webui:latest

# Ou standalone Python
git clone https://github.com/open-webui/open-webui
cd open-webui
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
python -m open_webui.main

# Abrir: http://localhost:3000
```

**Features**:
- Chat multi-modelo (trocar entre Mistral, Llama no meio da conversa)
- Histórico persistente em SQLite local
- Share conversations (gera link público opcionalmente)
- Markdown + code highlighting

### Camada 3: Whisper (Speech-to-Text)

Transcrição de áudio local usando Whisper (OpenAI), implementado em C++ para velocidade.

**Setup**:

```bash
# whisper.cpp (implementação C++ otimizada)
git clone https://github.com/ggerganov/whisper.cpp
cd whisper.cpp
make

# Download modelo
bash ./models/download-ggml-model.sh base

# Transcrever
./main -f audio.wav -m models/ggml-base.bin

# Output
[00:00:00.000 --> 00:00:05.000]  The quick brown fox jumps over the lazy dog
```

**Via Python (mais simples)**:

```python
from faster_whisper import WhisperModel

model = WhisperModel("base", device="cuda", compute_type="int8")
segments, info = model.transcribe("audio.mp3", language="pt")

for segment in segments:
    print(f"{segment.start:.2f}s - {segment.end:.2f}s: {segment.text}")
```

**Performance**:
- Base model (77M params): ~10s para 1 min de áudio (com GPU)
- Tiny model (39M): ~2s (CPU, menos preciso)
- Large model (1.5B): ~60s (mais preciso, muita memória)

### Camada 4: Edge-TTS (Text-to-Speech)

Síntese de voz sem API (usa vozes corporativas offline).

**Instalação**:

```bash
pip install edge-tts

# Listar vozes disponíveis
edge-tts --list-voices | grep pt  # Português

# Gerar áudio
edge-tts --text "Olá, como você está?" \
         --voice pt-BR-AntonioNeural \
         --write-media output.mp3
```

**Via Python**:

```python
import asyncio
import edge_tts

async def text_to_speech(text: str, output_file: str):
    communicate = edge_tts.Communicate(
        text=text,
        voice="pt-BR-AntonioNeural",  # ou "pt-BR-FranciscaNeural"
        rate="+10%"  # 10% mais rápido
    )
    await communicate.save(output_file)

asyncio.run(text_to_speech(
    "Bem-vindo ao seu assistente local",
    "welcome.mp3"
))
```

### Camada 5: AnythingLLM (RAG)

Retrieval-Augmented Generation: permite que o modelo consulte seus documentos antes de responder.

**Instalação**:

```bash
# Desktop App (mais simples)
# Download: https://anythingllm.com/

# Ou Docker
docker run -d \
  -p 3001:3001 \
  -v anythingllm_storage:/app/storage \
  --name anythingllm \
  mintplexlabs/anythingllm:latest

# Abrir: http://localhost:3001
```

**Workflow**:

1. **Criar workspace** (ex: "TechDocs")
2. **Upload documentos** (PDF, DOCX, TXT, MD)
3. **Indexar** (AnythingLLM cria embeddings via `nomic-embed-text` local)
4. **Configurar LLM** (apontar para Ollama)
5. **Chat com memória** (modelo lê documentos + contexto histórico)

**Exemplo: Chat com Documentação**

```
User: "Como configurar autenticação OAuth?"

AnythingLLM:
1. Procura em embeddings: docs/oauth-setup.md
2. Injeta contexto: "Baseado em oauth-setup.md, seção 'Configuration'..."
3. Passa para Ollama (Mistral 7B): "User asked about OAuth. Here's relevant docs: [...]"
4. Mistral responde baseado em docs + seu conhecimento base

Response: "Para configurar OAuth... [referência ao documento]"
```

### Exemplo Completo: Pipeline de Voz Bidirecional

```python
# voice_assistant.py - Assistente de voz completamente local

import asyncio
from faster_whisper import WhisperModel
import edge_tts
import httpx
import json

class LocalVoiceAssistant:
    def __init__(self):
        self.whisper = WhisperModel("base", device="cuda")
        self.ollama_url = "http://localhost:11434/api/generate"
        self.ollama_model = "mistral:7b"
    
    async def transcribe(self, audio_file: str) -> str:
        """Áudio → Texto via Whisper"""
        segments, _ = self.whisper.transcribe(audio_file, language="pt")
        return " ".join([s.text for s in segments])
    
    async def generate_response(self, prompt: str) -> str:
        """Texto → Resposta via Ollama"""
        async with httpx.AsyncClient() as client:
            response = await client.post(
                self.ollama_url,
                json={
                    "model": self.ollama_model,
                    "prompt": prompt,
                    "stream": False,
                    "temperature": 0.7,
                }
            )
            return response.json()["response"]
    
    async def synthesize(self, text: str, output_file: str) -> None:
        """Texto → Áudio via Edge-TTS"""
        communicate = edge_tts.Communicate(
            text=text,
            voice="pt-BR-AntonioNeural"
        )
        await communicate.save(output_file)
    
    async def chat_with_voice(self, audio_input: str) -> str:
        """Pipeline completo: Áudio → Transcrição → Resposta → Áudio"""
        print(f"🎤 Transcrevendo {audio_input}...")
        user_text = await self.transcribe(audio_input)
        print(f"📝 Você: {user_text}")
        
        print("🧠 Processando...")
        response = await self.generate_response(user_text)
        print(f"🤖 Assistente: {response}")
        
        print("🔊 Sintetizando voz...")
        await self.synthesize(response, "response.mp3")
        print("✓ Resposta em: response.mp3\n")
        
        return response

# Uso
async def main():
    assistant = LocalVoiceAssistant()
    await assistant.chat_with_voice("question.wav")

asyncio.run(main())
```

**Executar**:
```bash
# Gravar áudio
ffmpeg -f alsa -i default -t 5 question.wav  # Linux
# ou usar app de gravação

python voice_assistant.py
```

## Stack técnico

| Camada | Ferramenta | VRAM Min | Disk | Latência | Propósito |
|--------|-----------|---------|------|----------|----------|
| **LLM** | Ollama | 8GB | 3-5GB/modelo | 500ms-2s | Inference |
| **Interface** | Open WebUI | 1GB | 100MB | N/A | Browser UI |
| **Speech-to-Text** | whisper.cpp | 2GB | 140MB | 1-10s/min | Audio input |
| **Text-to-Speech** | edge-tts | 500MB | 50MB | 100-500ms | Audio output |
| **RAG** | AnythingLLM | 2GB | 1GB+ docs | +200ms | Knowledge base |
| **Embeddings** | nomic-embed-text | 1GB | 274MB | 10-50ms | RAG indexing |

**Hardware Recomendado (Desktop)**:
- CPU: 6+ cores (Ryzen 5, i7 ou melhor)
- RAM: 32GB (16GB mínimo, será lento)
- GPU: 8GB+ VRAM (NVIDIA RTX 3060+, AMD RX 6700+ ou melhor)
- SSD: 256GB+ (instalar modelos)

## Código prático

### Montar Stack em Docker Compose

```yaml
# docker-compose.yml

version: '3.8'
services:
  
  ollama:
    image: ollama/ollama:latest
    ports:
      - "11434:11434"
    volumes:
      - ollama-storage:/root/.ollama
    environment:
      - CUDA_VISIBLE_DEVICES=0  # GPU 0
    command: ollama serve
  
  open-webui:
    image: ghcr.io/open-webui/open-webui:latest
    ports:
      - "3000:8080"
    environment:
      - OLLAMA_API_BASE_URL=http://ollama:11434
    depends_on:
      - ollama
  
  anythingllm:
    image: mintplexlabs/anythingllm:latest
    ports:
      - "3001:3001"
    volumes:
      - anythingllm-storage:/app/storage
    environment:
      - LLM_PROVIDER=ollama
      - OLLAMA_API_BASE=http://ollama:11434
    depends_on:
      - ollama

volumes:
  ollama-storage:
  anythingllm-storage:
```

**Deploy**:
```bash
docker-compose up -d

# Verificar saúde
docker-compose ps

# Acessar
# Open WebUI: http://localhost:3000
# AnythingLLM: http://localhost:3001
```

### Comparar Performance de Modelos

```python
import time
import httpx
import json

async def benchmark_models():
    prompt = "Explique o que é Machine Learning em 3 frases"
    models = ["mistral:7b", "neural-chat:7b", "llama2:7b"]
    
    results = {}
    for model in models:
        start = time.time()
        response = httpx.post(
            "http://localhost:11434/api/generate",
            json={"model": model, "prompt": prompt, "stream": False}
        ).json()
        latency = time.time() - start
        
        results[model] = {
            "latency_ms": int(latency * 1000),
            "tokens_per_sec": len(response["response"].split()) / latency,
            "response_length": len(response["response"])
        }
    
    # Exibir resultados
    for model, metrics in results.items():
        print(f"\n{model}:")
        print(f"  Latência: {metrics['latency_ms']}ms")
        print(f"  Velocidade: {metrics['tokens_per_sec']:.1f} tok/s")
```

## Armadilhas e Limitações

### 1. Quantização vs. Qualidade
**Problema**: Modelos quantizados INT4 (4-bit) são 4x menores e 4x mais rápidos, mas perdem qualidade. Teste mostra que Mistral 7B INT4 erra em tasks complexas que Mistral 7B FP16 acerta.

**Solução**:
```bash
# Testar múltiplos quantization levels
ollama pull mistral:7b       # Padrão (Q4_K_M)
ollama pull mistral:7b-fp16  # Full precision (maior qualidade)

# Usar por task
# Tasks simples: INT4 (rápido)
# Tasks complexas: FP16 (preciso)
```

### 2. VRAM Overflow
**Problema**: Você roda Ollama (7B = 4GB) + Open WebUI + AnythingLLM (2GB) + seu programa Python. Total = 8GB+. Seu laptop tem 8GB. Sistema fica muito lento (swap thrashing).

**Solução**:
```bash
# Monitorar VRAM em tempo real
nvidia-smi --query-gpu=memory.used --format=csv -l 1

# Desabilitar auto-load de modelo
ollama set KEEP_ALIVE=0  # Descarrega modelo após uso

# Ou usar modelo menor
ollama pull tinyllama:1.1b  # 700MB, ~200ms latência
```

### 3. Embedding Dimensionality
**Problema**: AnythingLLM usa `nomic-embed-text` (768 dims). Se você muda para `all-minilm-l6-v2` (384 dims), seus embeddings antigos não são compatíveis. RAG quebra.

**Solução**:
```python
# Manter embedding model fixo em config
# anythingllm-config.json
{
  "embedding_model": "nomic-embed-text",
  "embedding_version": "v1.0",
  "do_not_change": true
}

# Se PRECISA mudar:
# 1. Backup antigos embeddings
# 2. Re-indexar TODOS documentos
# 3. Testar antes de usar em produção
```

### 4. GPU vs. CPU Fallback
**Problema**: Você treina em GPU (RTX 4090), depois roda em CPU-only laptop. Inferência fica 50x mais lenta — inutilizável.

**Solução**:
```bash
# Testar em target hardware desde o início
# Se vai rodar em CPU, teste em CPU

# Usar modelos CPU-optimized (MobileNet, TinyLLM)
ollama pull tinyllama:1.1b-chat  # Feito para CPU

# Ou use quantização agressiva
# INT4 + small model = aceitável mesmo em CPU
```

### 5. Privacy Assumptions
**Problema**: "Local" não significa 100% privado se você:
- Usa OpenAI Whisper (se não for whisper.cpp)
- Indexa no Pinecone (cloud)
- Logs enviados para Ollama analytics

**Solução**:
```bash
# Garantir privacidade real
# 1. Usar whisper.cpp (não OpenAI)
# 2. AnythingLLM com vector DB local (Qdrant self-hosted)
# 3. Desabilitar telemetry

# .env para AnythingLLM
ANONYMOUS_API_KEY=null
DISABLE_TELEMETRY=true
```

## Conexões

- [[quantizacao-de-llms|Quantização de LLMs]] — INT4 vs FP16
- [[retrieval-augmented-generation|Retrieval-Augmented Generation (Conceito)]] — RAG teoria
- [[embeddings-search-semantica|Embeddings & Search Semântica]] — Como embeddings funcionam
- [[privacidade-dados-llm|Privacidade & Dados em LLMs (Conceito)]] — Considerações legais
- [[fine-tuning-local|Fine-tuning Local (Conceito)]] — Treinar modelos locais
- [[text-to-speech-apis|Text-to-Speech APIs (Conceito)]] — Síntese de voz

## Perguntas de Revisão

1. Qual é o componente da stack responsável por permitir que o modelo responda com base em documentos próprios, e como ele funciona tecnicamente? (Resposta: AnythingLLM + embeddings. Documentos são convertidos em vetores (nomic-embed-text), armazenados localmente. Ao chat, query é também embedida, similar vectors são recuperados, injetados como contexto ao LLM)

2. Por que VRAM é o recurso limitante mais crítico nessa stack? (Resposta: VRAM determina tamanho máximo do modelo que pode rodar com GPU acelerado. Sem GPU suficiente, fallback para CPU = 10-50x mais lento, às vezes inutilizável)

3. Qual a diferença prática entre Ollama + Open WebUI vs. AnythingLLM? (Resposta: Ollama é LLM manager, WebUI é chat simples. AnythingLLM inclui RAG built-in — você pode indexar docs e fazer chat com knowledge base automático)

## Histórico de Atualizações

- 2026-04-02: Nota criada a partir de Telegram
- 2026-04-11: Expandida com 5 camadas completas (Ollama, WebUI, Whisper, Edge-TTS, AnythingLLM), pipeline voice bidirecional, docker-compose, armadilhas de VRAM e embedding versioning
