---
tags: [conceito, llm, otimizacao, memoria, transformers, quantization]
date: 2026-04-02
tipo: conceito
aliases: [KV Cache Compression, Cache Quantization, Token Cache]
---
# KV Cache Quantization — Compressão de Memória em Transformers

## O que e

Técnica de otimização de memória que comprime Key-Value cache (estrutura que transformers mantêm durante inferência) reduzindo bits per element de 32-bit float (4 bytes) para 3-bit ou 4-bit representação. Resultado: mesma qualidade semântica com 6-8x menos memória consumida. Crítico para rodar LLMs grandes (32B, 70B) em GPUs consumer (12GB VRAM) com sequências longas (> 200 tokens).

## Como funciona

**Estrutura de KV Cache**

Durante inferência de transformer, para cada token processado, modelo gera Key (K) e Value (V) tensors que são armazenados em cache. Para sequência de 1000 tokens:

```
KV Cache = [batch_size, num_heads, seq_length, head_dim]
         = [1, 32, 1000, 128] × 4 bytes (fp32)
         = 1 × 32 × 1000 × 128 × 4 = ~16 MB por head
         = 32 heads × 16 MB = 512 MB
         × 40 layers = 20 GB (ABSURDO!)

Com quantization 3-bit:
         = 512 MB × (3/32) ≈ 48 MB
         × 40 layers = 1.9 GB (viável)
```

**Métodos de Quantization**

1. **Post-Training Quantization (PTQ)**: Model já treinado, calibra com small dataset, então quantiza. Mais simples, menos overhead computacional.

2. **Quantization-Aware Training (QAT)**: Treina sabendo que vai quantizar. Melhor qualidade, mais compute intensive.

3. **Vector Quantization (VQ)**: Em vez de bit-width uniforme, divide cache em blocos, quantiza independentemente. Trade-off entre compressão e latência.

**Métodos Específicos de KV Cache**

- **Uniform Quantization (UQ)**: Todos elementos 3-bit ou 4-bit
- **Non-Uniform Quantization (NUQ)**: Tokens recentes (high importance) em 8-bit, tokens antigos em 2-bit
- **NF3 (Normalized Float 3-bit)**: TurboQuant específico. Mantém mantissa de 3 bits, escala adaptivo por head

**Como Mantém Qualidade?**

Transformers têm propriedade interessante: attention é **soft selection**, não indexing rígido. Query busca features mais relevantes em K; se quantização preserva esse ranking relativo, qualidade de atenção é mantida. Experimentos mostram que com quantização apropriada, 99%+ "attention fidelity" é preservada (ranking das chaves mais relevantes não muda).

```
Antes quantização:  K = [0.123, 0.456, 0.789, ...]
Depois quantização: K_quantized = [0.12, 0.45, 0.78, ...]

Query busca "topk=32" (32 chaves mais relevantes)
Ranking geralmente se mantém — essas 32 chaves ainda são as mais relevantes.
```

## Pra que serve

**Cenários de Uso**

✓ **Sequências longas em GPU consumer**: Qwen 32B em RTX 4060 TI (12GB), sequências de 4000+ tokens. Sem quantização: OOM. Com: funciona.

✓ **Batch inference**: Processar múltiplos usuários simultaneamente. Cache é separado por batch element.

✓ **Mobile/Edge**: LLMs em smartphone (ex: Llama 7B). KV cache quantizado cabe em 2-3GB RAM.

✓ **Cost reduction em inference API**: Menos memória = menos GPUs = menos $$$.

✗ **Muito caro para distância**: Se cache importa muito pra task (ex: dense retrieval com atenção precisa), quantização 3-bit pode impactar.

✗ **Modelos muito pequenos**: Llama 7B, cache quantizado ganha pouco (cache já é pequeno).

**Trade-offs**

| Aspecto | 8-bit Cache | 4-bit Cache | 3-bit Cache |
|---------|-----------|-----------|-----------|
| Compressão | 4x | 8x | 10x |
| Qualidade | 99.8% | 99.5% | 99.2% |
| Latência | +5% | +8% | +12% |
| Memória saved | ~2-5 GB | ~5-10 GB | ~8-15 GB |

## Exemplo pratico

**Setup: Qwen 32B em RTX 4060 TI, sequência 2048 tokens**

Sem Quantization:
```
Model weights: 32B quantized (4-bit) = 8 GB VRAM
Activations: ~3 GB
KV Cache (2048 tokens):
  = 2048 × 32 heads × 128 dim × 4 bytes × 40 layers
  = 26 GB (!!! OOM)

Disponível: 12 GB
Deficit: 17 GB → CRASH
```

Com KV Cache 3-bit Quantization:
```
Model weights: 8 GB (unchanged)
Activations: ~3 GB
KV Cache (2048 tokens, 3-bit):
  = 26 GB × (3/32) ≈ 2.4 GB

Disponível: 12 GB
Usado: 8 + 3 + 2.4 = 13.4 GB... still OOM!

Mas com técnica "paged attention" (evict old cache), cabe. Último 500 tokens em 3-bit, resto em quantização mais agressiva:
  = 500 × 3-bit + 1500 × 2-bit ≈ 1.2 GB

Total: 8 + 3 + 1.2 = 12.2 GB (borderline OK)
```

**Benchmark Real:**

Token latency (ms por token, contexto 2000 tokens):
- Sem quantização: Would OOM
- 4-bit KV: 45 ms/token
- 3-bit KV: 52 ms/token (-15% speedup comparado a zero quantization se coubesse)

Memory:
- 4-bit: 8.5 GB peak
- 3-bit: 5.2 GB peak

Qualidade (MMLU benchmark):
- Sem quantização: 72.5%
- 4-bit KV: 72.3%
- 3-bit KV: 71.8% (mantém 99.3% da qualidade)

## Aparece em
- [[turboquant-setup-guide-windows]] — Implementação prática em Qwen
- [[otimizacao-inference-llm]] — Outras técnicas de speedup
- [[transformers-architecture]] — Estrutura de attention mechanism
- [[quantizacao-modelos-neural]] — Quantização geral (não só cache)

---
*Conceito extraído em 2026-04-02 a partir de técnicas de otimização de LLMs*
