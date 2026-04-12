---
tags: []
source: https://x.com/0xCVYH/status/2038140278196916387?s=20
date: 2026-04-02
tipo: aplicacao
---

# Usar EOQ Dynamic BitPacking para Comprimir LLMs de 9B→5GB (3.6x)

## Resumo
Quantização dinâmica (EOQ + dynamic bitpacking) aloca bits **heterogeneamente**: camadas críticas recebem mais bits, redundantes recebem menos. Resultado: **3-4x compressão** com perda < 2%. LLaMA-9B vai de 18 GB → 5 GB, executável em GPUs consumer. Diferente de Q4_K_M uniforme (todos os pesos → 4 bits).

## O que é

Quantização dinâmica é uma estratégia adaptativa que **não** comprime todos os pesos igualmente. Em vez disso:

1. **Analisa importância**: qual camada/bloco contribui mais para a saída final?
2. **Aloca bits dinamicamente**: camadas críticas (atenção, projeções) → mais bits (5-8); camadas redundantes (MLPs em certos contextos) → menos bits (2-4)
3. **Empacota eficientemente**: usa codificação entrópica para armazenar numero variável de bits por parâmetro

**Exemplo concreto:**
```
Quantização Uniforme (Q4_K_M):
┌─ Camada de Atenção    → 4 bits
├─ Camada de FFN        → 4 bits
├─ Embeddings           → 4 bits
└─ Output Projection    → 4 bits
Total: ~5 GB

Quantização Dinâmica (EOQ BitPacking):
┌─ Camada de Atenção    → 6 bits (crítica para coerência)
├─ Camada de FFN        → 3 bits (mais redundante)
├─ Embeddings           → 4 bits (importância média)
└─ Output Projection    → 5 bits (sensível)
Total: ~4.9 GB (marginal) MAS qualidade ~5% melhor
```

### Técnicas principais

**1. EOQ (Entropy-Optimal Quantization)**
- Usa teoria da informação: encontra ponto de quantização que minimiza entropia dos pesos
- Walsh-Hadamard transform para normalizar distribuição (torna aproximadamente Gaussiana)
- Uniform quantization pós-transform é praticamente "ótima" em senso teórico

**2. Dynamic BitPacking**
- Armazena número variável de bits por parâmetro
- Usa escala e offset por camada (como K-quant), mas com número de bits adaptativo
- Kernels CUDA customizados para descompactar eficientemente em tempo de inferência

**3. Comparação com GPTQ e AWQ**
| Método | Bits por peso | Calibração | Tempo | Qualidade | Suporte Runtime |
|--------|---------------|------------|-------|-----------|-----------------|
| Q4_K_M | 4 (uniforme) | Nenhuma | 1-2 min | 92% | Excelente (llama.cpp) |
| GPTQ | 4 (uniforme) | Intensa (dados) | 30-60 min | 95-96% | Bom (AutoGPTQ) |
| AWQ | 4 (uniforme) | Moderada | 10-15 min | 93-94% | Emergente |
| EOQ BitPacking | 3-6 (dinâmico) | Nenhuma | 5-10 min | 96-98% | Nascente (poucos runtimes) |

## Por que importa

**1. Compressão radical sem sacrificar qualidade**
- 3.64x compressão (17.9 GB → 4.93 GB) com 92-98% da performance original é um salto contra Q4_K_M (~3x com perda 2-8%).
- A diferença vem de alocar mais bits onde importa: atenção (operação crítica) vs FFN (cálculos locais menos sensíveis).

**2. Desbloqueador para edge + on-device deployment**
- Modelo de 9B em 5 GB roda em RTX 4060 (8 GB VRAM), MacBook Air M2 (8 GB CPU RAM) com latência aceitável.
- Viabiliza offline-first applications: privacidade garantida, zero latência de rede.

**3. Paradoxo de economia: menos memória pode ser mais rápido**
- Menos bytes no cache L3/L2 = melhor hit rate em operações de multiplicação de matrizes (GEMM).
- GPU consegue paralelizar mais em tensores comprimidos vs armazenar tudo na DRAM lenta.

**4. Custo computacional de desenvolvimento baixo**
- EOQ é "data-free" (como Q4_K_M), não precisa de dados para calibração.
- Minutos de quantização vs horas de GPTQ/AWQ.

**5. Qualidade em tarefas sensíveis**
- Código, raciocínio matemático, tarefas de retrieval: EOQ > Q4_K_M em benchmarks internos.
- Potencialmente importante para fine-tuning posterior (quantização que preserva gradientes).

## Como funciona / Como implementar

### Arquitetura de EOQ Dynamic BitPacking

```
[Modelo FP32]
  ↓
[Análise de sensibilidade por camada]
  - Mede gradiente/Hessian de cada parâmetro
  - Atribui "score de importância" (higher = mais crítico)
  ↓
[Alocação de bits]
  - Camadas com score alto → 6-8 bits
  - Camadas com score baixo → 2-3 bits
  - Constraint: tamanho total < X GB
  ↓
[Quantização por camada]
  - Apply Hadamard transform (normaliza distribuição)
  - Uniform quantization com número de bits específico
  ↓
[Bitpacking]
  - Agrupa múltiplos pesos de baixa-precisão em palavras de 32 bits
  - Ex: 8 pesos de 4 bits = 1 palavra de 32 bits
  ↓
[Artefato comprimido]
  ↓ (Inference)
[Descompactar on-the-fly em CUDA kernel]
  ↓
[GEMM com FP32 dequantizado]
```

### Implementação referência (pseudocódigo)

```python
import torch
import torch.nn.functional as F

def hadamard_transform(matrix):
    """Aplica Walsh-Hadamard transform para normalizar pesos."""
    # Em prática, usa kernels CUDA otimizados
    return torch.linalg.matrix_power(2, -0.5) @ matrix  # Simplificação

def compute_weight_importance(model):
    """Calcula score de importância por parâmetro/camada."""
    importance = {}
    for name, param in model.named_parameters():
        # Heurística: magnitudes altas + sensibilidade a perturbações
        magnitude = torch.abs(param).mean().item()
        
        # Estimativa de Hessian diagonal (expensive, alternativa: use magnitude)
        hessian_approx = magnitude  # Simplifição para demo
        
        importance[name] = hessian_approx
    return importance

def allocate_bits_dynamic(importance, target_size_mb):
    """Aloca bits por camada para atingir tamanho alvo."""
    allocation = {}
    total_params = sum(imp for imp in importance.values())
    
    for name, imp in importance.items():
        # Camadas importantes recebem mais bits
        if imp > total_params * 0.3:  # Top 30%
            allocation[name] = 6  # 6 bits
        elif imp > total_params * 0.1:
            allocation[name] = 5
        else:
            allocation[name] = 3  # Menos crítico
    
    return allocation

def quantize_with_dynamic_bits(model, bit_allocation):
    """Quantiza modelo com alocação dinâmica."""
    quantized_state = {}
    
    for name, param in model.state_dict().items():
        bits = bit_allocation.get(name.replace('.weight', ''), 4)
        
        # Hadamard transform
        w = param.data
        w_transformed = hadamard_transform(w)
        
        # Quantizar
        num_levels = 2 ** bits
        w_min, w_max = w_transformed.min(), w_transformed.max()
        w_quantized = torch.round(
            (w_transformed - w_min) / (w_max - w_min) * (num_levels - 1)
        ).to(torch.int8 if bits <= 8 else torch.int16)
        
        # Armazenar scales/offsets para dequantização
        quantized_state[name] = {
            'data': w_quantized,
            'scale': (w_max - w_min) / (num_levels - 1),
            'offset': w_min,
            'bits': bits
        }
    
    return quantized_state

def bitpack_weights(quantized_state):
    """Empacota pesos quantizados em palavras de 32 bits."""
    packed = {}
    for name, q_info in quantized_state.items():
        w_quant = q_info['data'].flatten()
        bits = q_info['bits']
        
        # Empacota N pesos de 'bits' bits em palavras de 32 bits
        # Exemplo: 8 pesos de 4 bits = 1 palavra de 32 bits
        items_per_word = 32 // bits
        padded_len = ((len(w_quant) + items_per_word - 1) // items_per_word) * items_per_word
        w_quant_padded = torch.nn.functional.pad(w_quant, (0, padded_len - len(w_quant)))
        
        packed_words = []
        for i in range(0, len(w_quant_padded), items_per_word):
            word = 0
            for j, val in enumerate(w_quant_padded[i:i+items_per_word]):
                word |= (val.item() & ((1 << bits) - 1)) << (j * bits)
            packed_words.append(word)
        
        packed[name] = {
            'packed_data': torch.tensor(packed_words, dtype=torch.uint32),
            'bits': bits,
            'scale': q_info['scale'],
            'offset': q_info['offset'],
            'original_shape': q_info['data'].shape
        }
    
    return packed

# Uso
model = load_model("meta-llama/Llama-2-9b")
importance = compute_weight_importance(model)
bit_allocation = allocate_bits_dynamic(importance, target_size_mb=5000)
quantized = quantize_with_dynamic_bits(model, bit_allocation)
packed = bitpack_weights(quantized)

# Salvar artefato
torch.save(packed, "model-EOQ-BitPacked.pt")
```

### Kernel CUDA para descompactação eficiente

```cuda
// Em pseudocódigo (CUDA C++)
__global__ void bitpack_unpack_kernel(
    const uint32_t* packed_data,
    float* output,
    int bits,
    float scale,
    float offset,
    int size
) {
    int idx = blockIdx.x * blockDim.x + threadIdx.x;
    if (idx >= size) return;
    
    int items_per_word = 32 / bits;
    int word_idx = idx / items_per_word;
    int item_in_word = idx % items_per_word;
    
    uint32_t word = packed_data[word_idx];
    uint32_t mask = (1u << bits) - 1;
    int quantized_val = (word >> (item_in_word * bits)) & mask;
    
    // Dequantizar (inverse transform)
    float dequantized = quantized_val * scale + offset;
    output[idx] = dequantized;
}
```

## Stack técnico

**Quantização Dinâmica:**
- **PolarQuant** (PyPI) — implementação pública de EOQ + Hadamard
- **CalmOps** — toolkit de compressão que inclui bitpacking
- **TurboQuant (Google, 2026)** — alternativa: dinâmica para KV cache (6x reduction, 8x speedup)

**Runtimes suportados:**
- **llama.cpp** — suporte experimental (não padrão como Q4_K_M)
- **Custom CUDA kernels** — necessário para performance (runtimes genéricos não otimizam)
- **TensorRT** — suporte para quantização dinâmica com profiles de inferência

**Benchmarking:**
- **lm-evaluation-harness** — avalia drop de qualidade em MMLU, GSM8K, etc.
- **perplexity** — métrica simples de degradação

## Código prático

### Comparar Q4_K_M vs EOQ BitPacked

```python
import torch
from transformers import AutoModelForCausalLM, AutoTokenizer

tokenizer = AutoTokenizer.from_pretrained("mistralai/Mistral-7B")
model_q4 = AutoModelForCausalLM.from_pretrained("mistralai/Mistral-7B-Q4_K_M.gguf")
model_eoq = torch.load("mistralai/Mistral-7B-EOQ-BitPacked.pt")

prompt = "Escreva um programa Python que calcula fibonacci:"
tokens = tokenizer.encode(prompt, return_tensors="pt")

# Gerar com ambos
output_q4 = model_q4.generate(tokens, max_length=100)
output_eoq = model_eoq.generate(tokens, max_length=100)

print("Q4_K_M:", tokenizer.decode(output_q4[0]))
print("EOQ:", tokenizer.decode(output_eoq[0]))

# Comparar tamanhos
print(f"\nQ4_K_M size: 5.2 GB")
print(f"EOQ BitPacked size: 4.9 GB")
print(f"Savings: 5.8%")
```

### Estimar ganho de qualidade com teste de tarefas

```python
from lm_eval.tasks import get_task
import numpy as np

tasks = ["mmlu", "gsm8k", "arc_challenge"]
models = [model_q4, model_eoq]

for task_name in tasks:
    task = get_task(task_name)
    scores = {}
    
    for model_name, model in [("Q4_K_M", model_q4), ("EOQ", model_eoq)]:
        # Avaliar
        results = task.run(model)
        scores[model_name] = results['accuracy']
    
    diff_pct = (scores["EOQ"] - scores["Q4_K_M"]) / scores["Q4_K_M"] * 100
    print(f"{task_name}: Q4={scores['Q4_K_M']:.2%}, EOQ={scores['EOQ']:.2%}, diff={diff_pct:+.1f}%")
```

## Armadilhas e Limitações

**1. Suporte runtime muito limitado**
- EOQ + bitpacking é "nicely" teórico, mas runtimes como llama.cpp não têm kernels otimizados. Dequantização genérica é lenta (até 30% mais lento que Q4_K_M padrão).
- Solução: usar Custom CUDA kernels (requer expertise em GPU computing), ou esperar que comunidade amadureça suporte.

**2. Variabilidade entre modelos**
- A alocação ótima de bits é específica à arquitetura (LLaMA vs Mistral vs MPT diferem em importância de camadas).
- Re-calcular importance scores para cada modelo leva tempo e requer dados de calibração (contradiz "data-free").
- Solução: usar heurísticas transferíveis (ex: sempre dar 6 bits a atenção, 3 para FFN), aceitar suboptimalidade.

**3. Incompatibilidade com fine-tuning**
- Quantização dinâmica destrói simetria de gradientes. Fine-tuning posterior é muito mais difícil que com quantização uniforme.
- Solução: se planeja fine-tune, quantizar depois, não antes. Ou usar QAT (Quantization-Aware Training) que é muito mais caro.

**4. Overhead de análise de importância**
- Calcular Hessian ou sensibilidade para cada parâmetro em modelo de 7B é custoso (~1-2 horas em GPU).
- Pode anular economia de tempo vs GPTQ se fizer análise completa.
- Solução: usar heurísticas rápidas (magnitude apenas), ou comprar análise pré-computada (comunidade pode compartilhar scores).

**5. Comunicação/visibilidade comunitária baixa**
- Trabalhos em EOQ e bitpacking são principalmente papers acadêmicos. Ecossistema prático é imaturo (poucos templates, ferramentas, best practices).
- Solução: começar com Q4_K_M bem validado. EOQ é "nice to have" futurista se performance for muito crítica.

## Conexões

- [[quantizacao-de-llms|Quantização de LLMs]] — técnica base (uniforme)
- [[TurboQuant - Compressão de KV Cache|turboquant-kv-cache]] — quantização dinâmica aplicada a cache (Google, 2026)
- [[Stack de IA Local Self-Hosted|stack-de-ia-local-self-hosted]] — integração em pipeline
- [[Fine-tuning de LLMs Quantizados|fine-tuning-quantized]] — treinar com modelo quantizado
- [[Destilação de Modelos]] — alternativa: reduzir tamanho via knowledge distillation

## Histórico de Atualizações
- 2026-04-11: Expandida com EOQ teoria, Hadamard transform, bitpacking, kernels CUDA, armadilhas e comparação vs GPTQ/AWQ
- 2026-04-02: Nota criada a partir de Telegram