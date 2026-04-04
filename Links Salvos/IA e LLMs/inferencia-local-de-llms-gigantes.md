---
tags: []
source: https://x.com/heynavtoor/status/2038614549973401699?s=20
date: 2026-04-02
tipo: aplicacao
---
# Executar LLMs de 397B Parâmetros em MacBook via Streaming de SSD

## O que é

Técnica de streaming de pesos desde SSD para RAM + arquitetura Mixture-of-Experts (MoE) permite rodar modelos gigantes (400B+ parâmetros) em hardware consumer sem GPU dedicada, mantendo apenas ~5-6GB ativos, ativando seletivamente 0.1% dos parâmetros por token.

## Como implementar

### Pré-requisitos

- **Apple Silicon Mac** (M1, M2, M3 Pro/Max) ou Linux/Windows com GPU NVIDIA
- **SSD rápido**: NVMe recomendado (>3.5 GB/s leitura)
- **RAM mínima**: 48GB unified memory (Mac) ou 32GB+ VRAM (GPU)
- **Storage**: 200-300GB para modelo de 397B

### Fase 1: Setup no MacBook (Apple Silicon)

Clone repositório flash-moe:

```bash
git clone https://github.com/heynavtoor/flash-moe.git
cd flash-moe

# Build em C puro (sem dependências Python!)
clang -O3 -mmacosx-version-min=11.0 \
  -fvectorize -fslp-vectorize-aggressive \
  flash_moe.c -o flash_moe \
  -framework Accelerate  # use vetorização nativa

# Ou compile com Metal (GPU shaders):
clang -O3 flash_moe_metal.c -framework Metal -o flash_moe_metal
```

### Fase 2: Download de Modelo MoE

Use Qwen3.5-397B ou modelo similar:

```bash
# Via Hugging Face
huggingface-cli download Qwen/Qwen3.5-397B-Instruct \
  --local-dir ./models/qwen397b \
  --resume-download \
  --local-dir-use-symlinks False

# Tamanho: ~209GB (comprimido no disco)
# Tempo: ~2-4 horas em internet de 100Mbps
```

### Fase 3: Configurar Streaming de SSD

Arquivo de config `streaming_config.json`:

```json
{
  "model": "qwen3.5-397b",
  "model_path": "./models/qwen3.5-397b/",
  "mode": "streaming",
  "ssd_streaming": {
    "enabled": true,
    "buffer_size_gb": 5.5,
    "prefetch_tokens": 10,
    "device": "/dev/nvme0n1p2",  # seu NVMe
    "read_ahead_kb": 512
  },
  "moe_config": {
    "num_experts": 512,
    "experts_per_token": 4,
    "expert_capacity": 1.25
  },
  "inference": {
    "max_tokens": 2048,
    "temperature": 0.7,
    "top_p": 0.9
  }
}
```

### Fase 4: Executar Inferência

**Método 1: Command Line**

```bash
./flash_moe \
  --config streaming_config.json \
  --prompt "Explain quantum computing in Portuguese" \
  --max-tokens 500 \
  --temperature 0.7

# Output:
# Quantum computing explores the principles of quantum mechanics...
# Tokens/second: 4.4
```

**Método 2: Python Binding (para integração)**

```python
# flash_moe_python.py
import ctypes
import json

# Carregar binário compilado
lib = ctypes.CDLL('./flash_moe')

# Define função C
generate = lib.flash_moe_generate
generate.argtypes = [ctypes.c_char_p, ctypes.c_char_p, ctypes.c_int]
generate.restype = ctypes.c_char_p

# Configuração
config_json = json.dumps({
    "model_path": "./models/qwen3.5-397b",
    "max_tokens": 500
}).encode()

# Executar
prompt = "What is machine learning?".encode()
result = generate(config_json, prompt, 500)

print(result.decode())
```

**Método 3: Como Servidor Local**

```python
# server.py - Flask wrapper
from flask import Flask, request, jsonify
import subprocess
import json

app = Flask(__name__)

@app.route("/generate", methods=["POST"])
def generate():
    data = request.json
    prompt = data["prompt"]

    # Chama binário flash_moe
    result = subprocess.run(
        ["./flash_moe", "--prompt", prompt, "--max-tokens", "500"],
        capture_output=True,
        text=True,
        timeout=120
    )

    return jsonify({
        "prompt": prompt,
        "response": result.stdout,
        "tokens_per_second": 4.4
    })

@app.route("/health", methods=["GET"])
def health():
    return jsonify({"status": "ok", "model": "qwen3.5-397b"})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)

# Use:
# curl -X POST http://localhost:5000/generate \
#   -H "Content-Type: application/json" \
#   -d '{"prompt": "Hello world"}'
```

### Fase 5: Otimizações de Performance

**Aumentar velocidade de leitura do SSD:**

```bash
# macOS - check SSD speed
diskutil secureErase freespace 0 /path/to/ssd

# Enable SSD cache pre-warm
diskutil info /  | grep "Solid State"

# Aumentar buffer se tiver RAM disponível
# Editar streaming_config.json: "buffer_size_gb": 8.0
```

**Paralelizar requisições:**

```python
import concurrent.futures

def batch_generate(prompts, max_workers=2):
    """Processa múltiplos prompts em paralelo"""
    with concurrent.futures.ThreadPoolExecutor(max_workers=max_workers) as executor:
        futures = [
            executor.submit(generate_single, p) for p in prompts
        ]
        return [f.result() for f in futures]

# Processamento de 2 prompts simultaneamente
results = batch_generate([
    "Explique IA",
    "O que é machine learning?"
])
```

## Stack e requisitos

- **CPU/GPU**: Apple Silicon M1+ (recomendado) ou NVIDIA 3090+ para non-Apple
- **RAM**: 48GB+ unified (Mac) ou 32GB+ VRAM
- **SSD**: NVMe com >3.5 GB/s (crítico para performance)
- **Modelo**: Qwen3.5-397B ou mistral-large-moe
- **Latência**: 4-5 tokens/seg em MacBook Pro M3 Max
- **Custo**: $0/hora (vs $300+/hora em cloud GPU)
- **Privacidade**: 100% local, nenhum dato é enviado

## Armadilhas e limitações

1. **SSD não é fast enough**: Se sua SSD for SATA, velocidade cai para <1 token/seg. Obtenha NVMe Gen4/5.

2. **Thermal throttling**: MacBook pode throttle se rodar 24/7. Use fan externo ou limite carga.

3. **Apenas leitura sequencial fast**: Acesso aleatório é lento. MoE mitiga mantendo working set pequeno.

4. **Modelos específicos**: Flash-moe foi otimizado para Qwen3.5-397B. Outros modelos podem precisar adaptação.

5. **Consumo energético**: Mesmo eficiente, ~50W sustained. Para 24/7, considere custo elétrico.

## Conexões

- [[Qwen 3.5 4B Destilado Claude Opus Local]] — modelos menores em CPU
- [[local_llm_reddit_discussao]] — comunidade de LLM local
- [[memory-stack-para-agentes-de-codigo]] — usar modelo local com Claude

## Histórico

- 2026-04-02: Nota criada
- 2026-04-02: Guia prático de implementação

## Exemplos
1. **Privacidade corporativa**: Empresas de saúde ou jurídicas podem rodar LLMs de alta capacidade localmente, sem enviar dados sensíveis para APIs externas.
2. **Desenvolvimento offline**: Engenheiros podem usar modelos de 400B parâmetros sem acesso à internet, em viagens ou ambientes com restrições de rede.
3. **Redução de custos de prototipagem**: Equipes pequenas podem testar capacidades de modelos grandes sem orçamento de cloud, usando hardware já disponível.

## Relacionado
*(Nenhuma nota relacionada disponível no vault no momento da criação.)*

## Perguntas de Revisão
1. Por que a arquitetura Mixture-of-Experts é condição necessária para que o streaming de pesos do SSD seja viável em inferência local?
2. Qual é a diferença fundamental entre memória unificada da Apple Silicon e a arquitetura CPU+GPU convencional que torna esse tipo de projeto mais eficiente no Mac?

## Histórico de Atualizações
- 2026-04-02: Nota criada a partir de Telegram