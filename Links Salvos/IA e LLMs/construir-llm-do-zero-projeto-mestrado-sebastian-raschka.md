---
tags: [llm, treinamento, deep-learning, sebastian-raschka, mestrado, hands-on]
source: https://www.linkedin.com/feed/update/urn:li:activity:7324180712985624578/
date: 2026-03-28
tipo: aplicacao
autor: "Victor Hugo Germano"
---
# Build LLM from Scratch: 2 Semanas com Sebastian Raschka + 3Blue1Brown

## O que e
Livro prático "Build a Large Language Model From Scratch" de Sebastian Raschka estrutura a construção de um LLM funcional em projeto de 2 semanas. Complementado com série visual Deep Learning do 3Blue1Brown para intuição geométrica dos transformers. Demonstra que compreensão profunda de LLMs não exige infraestrutura corporativa — apenas tempo, Python e disciplina de aprendizado.

## Como implementar
**Pré-requisitos: Python, álgebra linear básica (multiplicação de matrizes, vetores).** O livro progride em ciclos hands-on: cada capítulo = teoria + implementação de código funcional que você executa. Fluxo: ler explicação, digitar código (não copiar), rodar em Colab, validar output, anotar dúvidas. 3Blue1Brown fornece visualização geométrica — quando Raschka menciona "produto escalar em atenção", o vídeo mostra a operação em 2D, tornando concreto. Semana 1 cobre tokenização, embeddings, arquitetura básica (bloco transformer simples). Semana 2 integra tudo em treinamento end-to-end em dataset pequeno (Shakespeare, ou similar), validando em holdout set. Usar Google Colab garante acesso GPU gratuita (T4 ~15 TFLOPS). Documentação do livro está no repositório oficial (github.com/rasbt/LLMs-from-scratch).

Padrão de estudo recomendado: 1-2h diárias, capítulo por dia. Não pule implementações — código escrito à mão cristaliza compreensão muito melhor que ler. Projetos auxiliares: visualizar attention weights em heatmaps, comparar modelo treinado com pré-treinado, fine-tuning em domínio específico (médico, legal).

## Stack e requisitos
Python 3.9+, PyTorch 2.0+, Jupyter Notebook. Google Colab T4 GPU (livre, 15h/dia). Modelo padrão do livro: 12 transformer blocks, 768 hidden dimensions, 12 attention heads. Requisitos: 4-6GB VRAM. Pré-treinamento em Shakespeare (~40MB): ~1h em T4. Computador pessoal com RTX 3060 reduz a ~30min. Sem GPU (CPU only): viável mas ~10x mais lento.

## Armadilhas e limitacoes
Tentação de pular capítulos — não faça, cada um introduz conceito que etapas posteriores exigem. Colab desconecta após 12h inatividade; salve checkpoints via Google Drive. Learning rate inicial muito alta causa divergência; começa em 1e-4, ajusta observando loss. Dataset pequeno (~1M tokens) vai overfit rapidamente em training — normal, valide em set holdout separado. Não tente "entender tudo profundamente" na primeira passada; acumula compreensão em reler notas.

## Conexoes
[[construcao-de-llm-do-zero|LLM do zero etapas]]
[[embeddings-multimodais-em-espaco-vetorial-unificado|Embeddings]]
[[fine-tuning-de-llms-sem-codigo|Fine-tuning prático]]
[[aprendizado-acelerado-com-ia|Técnicas de aprendizado]]

## Historico
- 2026-03-28: Referência original
- 2026-04-02: Reescrita pelo pipeline
