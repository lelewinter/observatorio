---
tags: []
source: https://x.com/GoogleResearch/status/2036533564158910740?s=20
date: 2026-04-02
---
# Compressão de KV Cache em LLMs

## Resumo
TurboQuant é um algoritmo de compressão do Google Research que reduz o consumo de memória do KV cache de LLMs em pelo menos 6x, com speedup de até 8x e sem perda de acurácia.

## Explicação
O KV cache (key-value cache) é uma estrutura de dados crítica na inferência de LLMs baseados em Transformers. Durante a geração de texto, o modelo armazena os vetores de chave (K) e valor (V) de cada token já processado para evitar recomputação. Em modelos grandes e contextos longos, esse cache se torna um dos principais gargalos de memória — podendo consumir dezenas de gigabytes por requisição, limitando o batch size e a escalabilidade do serviço.

TurboQuant aborda esse problema via quantização do KV cache, representando os valores numéricos com menor precisão (ex: de float16 para int4 ou menos bits), reduzindo o footprint de memória em ao menos 6x. O diferencial anunciado é que essa compressão agressiva é feita sem degradação de acurácia — o que historicamente era o principal trade-off de técnicas de quantização. O speedup de até 8x provavelmente deriva da combinação de menor uso de memória (menos pressão no bandwidth de memória HBM) e operações aritméticas mais rápidas com tipos de menor precisão.

A relevância prática é alta: reduzir o KV cache é um dos problemas mais diretos para viabilizar inferência com janelas de contexto longas (100k+ tokens) e aumentar o throughput em serviços de produção. Algoritmos como FlashAttention e PagedAttention (vLLM) já atacavam o problema de eficiência de atenção e gerenciamento de memória; TurboQuant complementa essa camada atuando diretamente na compressão dos dados armazenados.

Como não há notas relacionadas no vault ainda, este conceito pode servir de nó central para uma futura constelação de notas sobre eficiência de inferência em LLMs, conectando quantização, atenção eficiente e otimização de memória.

## Exemplos
1. **Contextos longos em produção**: com KV cache 6x menor, um servidor pode manter sessões de 600k tokens onde antes suportava 100k, sem adquirir hardware adicional.
2. **Aumento de batch size**: a memória liberada permite processar mais requisições simultâneas, reduzindo latência média em APIs de LLM em produção.
3. **Deploy em hardware restrito**: modelos grandes tornam-se viáveis em GPUs com menos VRAM (ex: A10G em vez de A100), reduzindo custo operacional.

## Relacionado
*(Nenhuma nota existente no vault para linkar neste momento.)*

## Perguntas de Revisão
1. Qual é o trade-off clássico da quantização e como o TurboQuant alega superá-lo sem perda de acurácia?
2. Como a compressão do KV cache se diferencia de outras técnicas de eficiência de Transformers, como FlashAttention ou sparse attention?

## Histórico de Atualizações
- 2026-04-02: Nota criada a partir de Telegram