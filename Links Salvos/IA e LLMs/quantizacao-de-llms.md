---
tags: [llm, quantização, otimização, inferência, machine-learning]
source: https://x.com/ngrokHQ/status/2036844409145512255?s=20
date: 2026-04-02
tipo: aplicacao
---

# Implementar Quantização de LLMs com GGUF e Q4_K_M para Inferência Local

## Resumo
Quantização é compressão de pesos neural por redução de bit-depth: float32/float16 → int8/int4/int2. Resultado: modelos 4-8x menores, 2x mais rápidos, com degradação de qualidade <2% em casos bem calibrados. A técnica é **post-training** (sem retreinamento) e é o pilar técnico que democratizou LLMs locais.

## O que é

Quantização é o mapeamento de valores contínuos de alta precisão para um espaço discreto de baixa precisão. Em LLMs:

- **Original (FP32)**: 32 bits por peso → ~31 GB para LLaMA-7B
- **Quantizado (Q4)**: 4 bits por peso → ~4 GB para LLaMA-7B (7.75x compressão)

A ideia central: redes neurais treinadas têm **redundância estatística** nos pesos. A maioria dos valores se concentra em faixas estreitas de magnitudes. É possível "discretizar" essa faixa contínua em níveis quantizados (ex: 16 níveis com Q4) sem perder significativamente a capacidade do modelo de representar as computações aprendidas.

**Quantização uniforme** mapeia a faixa [min, max] dos pesos em n bins igualmente espaçados:
```
valor_quantizado = round((valor_original - min) / (max - min) * (2^bits - 1))
```

**Quantização por grupo (group quantization, usado em Q4_K_M)**: ao invés de quantizar todo o tensor com um min/max, divide-se em grupos menores (~32-128 valores) com calibração independente. Isso reduz erro de quantização dramáticamente.

## Por que importa

**1. Viabilidade de execução local**
- LLaMA-70B em FP16 requer ~140 GB VRAM (impossível em consumer hardware). Quantizado a Q4, cabe em ~20 GB, rodando em 2x RTX 4090 ou até GPUs mais modestas.

**2. Redução de latência**
- Menos memória = menos latência de carregamento. Mais importante: menos bytes por operação = operações mais rápidas em hardware otimizado para INT8/INT4.

**3. Custo zero de retreat**
- PTQ (post-training quantization) não requer retreinamento. Economiza semanas de GPU compute e dados de treinamento. Qualquer desenvolvedor com acesso ao checkpoint pode quantizar em minutos.

**4. Acesso democratizado a modelos capazes**
- Modelosr que antes exigiam data centers (A100, H100) agora rodam em gaming laptops, RPi clusters, ou até celulares.

**5. Trade-off controlado qualidade × tamanho**
- Q4_K_M é o "sweet spot" comunitário: 75% redução de tamanho, 92-98% retenção de qualidade original. Para tarefas de código, Q4_K_M ≈ FP16 em muitos benchmarks.

## Como funciona / Como implementar

### Fluxo geral de quantização

```
[Modelo FP32 treinado] 
  ↓ (PTQ - nenhum dado de treinamento)
[Calibração: scan dos pesos para min/max, estatísticas por grupo]
  ↓
[Quantização: map FP32 → INT4 com escala/offset]
  ↓
[Artefato GGUF quantizado]
  ↓ (Inferência)
[Dequantização em tempo real: INT4 → FP32 before GEMM ops]
  ↓
[Output]
```

O modelo original permanece FP32 em disco. A quantização cria um novo arquivo (ex: `model-Q4_K_M.gguf`) que armazena INT4 + metadata (scales, offsets por grupo).

### Técnicas principais

**1. Q4_K_M (GGUF format)**
- K = K-quant, usa escala de grupo
- M = medium, usa 6 bits para magnitude e escala (bom custo-benefício)
- Padrão de facto para llama.cpp

**2. Q8_0**
- 8 bits por peso, mais rápido de desquantizar, menos compressão
- Útil se memory não é gargalo, quer minimizar latência de desquantização

**3. AWQ (Activation-Aware Quantization)**
- Observa distribuição de activations durante calibração, não só pesos
- Melhor qualidade que quantização uniforme, mas calibração é mais cara
- Bom para fine-tuning posterior

**4. GPTQ (Gradient-based Post-Training Quantization)**
- Usa Hessian para encontrar melhor ponto de quantização (mais sofisticado que Q4_K_M)
- Calibração cara, mas qualidade ainda melhor
- Usado para modelos proprietários de alta performance

### Implementação prática com `llama-cpp-python`

```python
from llama_cpp import Llama

# Carregar modelo quantizado (automatic int4 dequantization)
model = Llama(
    model_path="/path/to/model-Q4_K_M.gguf",
    n_ctx=2048,
    n_gpu_layers=35,  # Offload para GPU
    verbose=False
)

# Inferência normal, desquantização acontece internamente
response = model(
    "Q: O que é quantização? A:",
    max_tokens=200,
    temperature=0.7
)

print(response['choices'][0]['text'])
```

### Quantizar modelo FP32 para GGUF usando `llama.cpp`

```bash
# 1. Clonar llama.cpp
git clone https://github.com/ggml-org/llama.cpp.git
cd llama.cpp

# 2. Compilar
make

# 3. Converter HuggingFace para GGUF (se ainda não está)
python convert.py /path/to/huggingface/model --outfile model.gguf

# 4. Quantizar para Q4_K_M
./quantize model.gguf model-Q4_K_M.gguf Q4_K_M

# Resultado: ~75% redução de tamanho, pronto para inferência
```

### Verificar qualidade pós-quantização

```python
from llama_cpp import Llama
import time

model_fp16 = Llama(model_path="model-fp16.gguf")
model_q4 = Llama(model_path="model-Q4_K_M.gguf")

prompt = "Implemente um quicksort em Rust:"

# Gerar resposta de ambas
start = time.time()
resp_fp16 = model_fp16(prompt, max_tokens=300)
time_fp16 = time.time() - start

start = time.time()
resp_q4 = model_q4(prompt, max_tokens=300)
time_q4 = time.time() - start

print(f"FP16: {time_fp16:.2f}s")
print(f"Q4_K_M: {time_q4:.2f}s")
print(f"Speed-up: {time_fp16/time_q4:.2f}x")

# Output (texto): geralmente idêntico ou muito similar
print("\nFP16 output:", resp_fp16['choices'][0]['text'][:200])
print("\nQ4 output:", resp_q4['choices'][0]['text'][:200])
```

### Setup com Ollama (automatizado)

Ollama baixa automaticamente modelos pré-quantizados em Q4_K_M:

```bash
ollama pull llama2:7b-chat-q4_k_m
ollama run llama2:7b-chat-q4_k_m
```

## Stack técnico

**Formatos e Runtimes:**
- **GGUF** — formato de facto (llama.cpp, Ollama, LM Studio)
- **GPTQ** — alternativa, melhor qualidade mas menos tooling
- **AWQ** — meio termo qualidade/calibração

**Ferramentas de Quantização:**
- **llama.cpp** (`./quantize`) — padrão, multi-plataforma, sem GPUs
- **AutoGPTQ** — se quer GPTQ, UI mais amigável
- **bitsandbytes** — para fine-tuning + quantização (mais complexo)

**Suporte em Runtime:**
- **llama-cpp-python** — binding Python oficial
- **Ollama** — simplificado, sem linha de comando
- **LM Studio** — GUI, para usuários não técnicos
- **vLLM** — inference server otimizado para APIs

**Benchmarking:**
- **lm-evaluation-harness** — suite de avaliação padrão (MMLU, GSM8K, etc.)
- **llama.cpp benchmark** — tokens/sec, latência de primeira token

## Código prático

### Comparação de precisão pré e pós-quantização

```python
import torch
from transformers import AutoModelForCausalLM, AutoTokenizer

model_name = "meta-llama/Llama-2-7b"
tokenizer = AutoTokenizer.from_pretrained(model_name)

# Carregar em FP32
model = AutoModelForCausalLM.from_pretrained(
    model_name,
    torch_dtype=torch.float32,
    device_map="auto"
)

# Extrair pesos de uma camada para análise
layer_weights = model.model.layers[0].self_attn.q_proj.weight.data

print(f"Pesos originais (FP32):")
print(f"  Min: {layer_weights.min():.6f}")
print(f"  Max: {layer_weights.max():.6f}")
print(f"  Std: {layer_weights.std():.6f}")

# Simular quantização Q4 (4 bits = 16 níveis)
num_levels = 2 ** 4
min_val = layer_weights.min()
max_val = layer_weights.max()

# Quantizar
quantized = torch.round(
    (layer_weights - min_val) / (max_val - min_val) * (num_levels - 1)
)

# Dequantizar (o que runtimes fazem)
dequantized = (quantized / (num_levels - 1)) * (max_val - min_val) + min_val

# Calcular erro de quantização
quantization_error = torch.abs(layer_weights - dequantized).mean()
print(f"\nErro médio de quantização Q4: {quantization_error:.6f}")
print(f"Erro relativo: {(quantization_error / layer_weights.abs().mean() * 100):.2f}%")
```

### Script de automação: quantizar e testar multiple formatos

```python
import os
from llama_cpp import Llama
import time

def quantize_and_benchmark(model_path, test_prompt):
    """Quantiza modelo e compara tempos."""
    
    formats = [
        ("Q4_K_M", "model-Q4_K_M.gguf"),
        ("Q8_0", "model-Q8_0.gguf"),
        ("Q6_K", "model-Q6_K.gguf"),
    ]
    
    results = {}
    
    for fmt_name, output_file in formats:
        print(f"\n=== Quantizando para {fmt_name} ===")
        os.system(f"./quantize {model_path} {output_file} {fmt_name}")
        
        # Benchmark
        model = Llama(model_path=output_file, n_gpu_layers=35)
        
        start = time.time()
        response = model(test_prompt, max_tokens=100)
        elapsed = time.time() - start
        
        file_size = os.path.getsize(output_file) / (1024**3)  # GB
        
        results[fmt_name] = {
            "time": elapsed,
            "size_gb": file_size,
            "tokens_per_sec": 100 / elapsed,
            "output_snippet": response['choices'][0]['text'][:100]
        }
    
    # Comparação
    print("\n=== RESULTADOS ===")
    for fmt, metrics in results.items():
        print(f"{fmt}:")
        print(f"  Tempo: {metrics['time']:.2f}s")
        print(f"  Tamanho: {metrics['size_gb']:.2f} GB")
        print(f"  Throughput: {metrics['tokens_per_sec']:.1f} tokens/sec")

test_prompt = "O que é machine learning?"
quantize_and_benchmark("model-fp32.gguf", test_prompt)
```

## Armadilhas e Limitações

**1. Degradação silenciosa em edge cases**
- Q4_K_M é ~92-98% de qualidade FP16 em média, mas há "hot spots" onde a perda é maior. Ex: raciocínio matemático complexo, código altamente técnico, tarefas de contagem exata.
- Solução: testar em tarefas específicas do seu caso de uso (não confiar em benchmarks genéricos). Usar Q6_K se precisão for crítica, mesmo que seja 1.5x mais lento.

**2. Dequantização causa overhead de latência**
- O modelo quantizado ocupa 4 GB, mas em tempo de inferência precisa dequantizar (INT4 → FP32) para cada operação GEMM. Isso adiciona latência (~10-15% mais lento que FP16 puro em GPUs modernas).
- Solução: usar GPUs com INT4 GEMM nativo (Ampere+, Ada, hopper), ou aceitar que Q4 é trade-off: tamanho < latência pura.

**3. Incompatibilidade de formato entre runtimes**
- Um modelo em GGUF Q4_K_M funciona em llama.cpp mas não em vLLM (que quer GPTQ ou FP16). Ao escolher quantizar, você se prende a um ecossistema.
- Solução: manter checkpoint original (FP32) e re-quantizar se for mudar runtime no futuro.

**4. Calibração em PTQ é "blind"**
- PTQ quantiza sem dados, apenas olha histogramas de pesos. Não sabe quais pesos são críticos para sua tarefa específica.
- Solução: usar AWQ ou GPTQ se performance for crítica (calibração usa dados de verdade, leva mais tempo mas resultado é melhor).

**5. Custo de desenvolvimento com quantização**
- Equipes que quantizam modelos internos precisam manter pipeline próprio (converter, quantizar, testar). Não é "one-click", especialmente para modelos customizados.
- Solução: usar Ollama ou modelos pré-quantizados da comunidade (HuggingFace tem centenas).

## Conexões

- [[quantizacao-dinamica-de-llms|Quantização Dinâmica de LLMs]] — técnicas mais sofisticadas (EOQ, bitpacking)
- [[Stack de IA Local Self-Hosted|stack-de-ia-local-self-hosted]] — deployment completo com quantização
- [[KV Cache Quantization|kv-cache-quantization]] — quantizar cache de atenção (orthogonal, melhora ainda mais)
- [[LLaMA e Mistral em Hardware Consumer|inferencia-local]] — implementação prática
- [[Compressão de Modelos e Destilação|model-compression]] — outras técnicas além quantização

## Histórico de Atualizações
- 2026-04-11: Expandida com técnicas Q4_K_M vs Q8_0, implementação llama.cpp, benchmarking, armadilhas específicas
- 2026-04-02: Nota criada a partir de Telegram