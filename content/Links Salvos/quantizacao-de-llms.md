---
tags: [llm, quantização, otimização, inferência, machine-learning]
source: https://x.com/ngrokHQ/status/2036844409145512255?s=20
date: 2026-04-02
---
# Quantização de LLMs

## Resumo
Quantização é uma técnica de compressão que reduz a precisão numérica dos pesos de um LLM, tornando o modelo até 4x menor e 2x mais rápido com perda mínima de qualidade.

## Explicação
Modelos de linguagem armazenam seus pesos (parâmetros) como números de ponto flutuante de 32 ou 16 bits. Quantização é o processo de representar esses mesmos pesos com menos bits — tipicamente 8, 4 ou até 2 bits — reduzindo drasticamente o espaço em memória e o custo computacional. Em termos práticos, um modelo que exigiria 16 GB de VRAM pode passar a caber em 4 GB, viabilizando execução local em hardware comum.

O princípio fundamental é que a maioria dos pesos em uma rede neural treinada se concentra em faixas de valores relativamente estreitas. É possível mapear esses valores contínuos para um conjunto discreto menor de representações sem perder a capacidade expressiva do modelo de forma significativa. A perda de qualidade existe, mas é geralmente marginal quando técnicas como calibração do range de quantização e quantização por camada são aplicadas corretamente.

A relevância prática da quantização é enorme para o deployment de LLMs fora de data centers: ela é a principal razão pela qual modelos como LLaMA e Mistral conseguem rodar em laptops e até smartphones. Ferramentas como `llama.cpp` e formatos como GGUF popularizaram quantização a 4 bits como padrão de fato para inferência local, democratizando o acesso a modelos poderosos sem dependência de cloud.

Do ponto de vista de engenharia, quantização opera majoritariamente em tempo de inferência (post-training quantization — PTQ), sem necessidade de retreinar o modelo, o que a torna acessível a qualquer desenvolvedor que tenha acesso ao modelo base já treinado.

## Exemplos
1. **Inferência local com llama.cpp**: Um modelo LLaMA 3 de 8B parâmetros em float16 ocupa ~16 GB; quantizado a Q4_K_M via GGUF, cabe em ~5 GB e roda em CPUs modernas.
2. **Deployment em dispositivos móveis**: Modelos quantizados a 4 bits permitem rodar LLMs diretamente em iPhones e chips Apple Silicon sem chamadas de API externas.
3. **Redução de custo de hosting**: Em servidores, modelos quantizados aumentam o throughput de tokens por segundo e reduzem custo por requisição, viabilizando startups com orçamento limitado de GPU.

## Relacionado
*(Nenhuma nota relacionada disponível no vault no momento da criação.)*

## Perguntas de Revisão
1. Qual é o trade-off fundamental da quantização e como ele é minimizado em técnicas modernas como Q4_K_M?
2. Por que a quantização post-training (PTQ) é preferível à quantization-aware training (QAT) do ponto de vista prático para desenvolvedores?

## Histórico de Atualizações
- 2026-04-02: Nota criada a partir de Telegram