---
tags: [ia, cursos, huggingface, llm, agentes, visao-computacional, audio, open-source]
source: https://x.com/heynavtoor/status/2039326170421010855?s=20
date: 2026-04-02
tipo: aplicacao
---
# 9 Cursos Gratuitos HuggingFace: LLMs a Visão Computacional

## O que e
HuggingFace lançou suite de 9 cursos open-source cobrindo stack completo de IA moderna: LLMs, agentes, visão computacional, áudio, gamedev e 3D. Cada curso combina teoria concisa com notebooks executáveis em Colab, eliminando barreira de custo para aprendizado prático em IA. Modelos, datasets e código são open-source no hub da plataforma.

## Como implementar
Acessar cursos em https://huggingface.co/learn — cada um é autossuficiente. **Curso de LLMs**: cobre arquitetura, pré-treinamento, fine-tuning com [[transformers]] library. Exemplo: fazer fine-tuning de Llama-2 em dataset customizado usando UI na plataforma ou código Python. **Curso de Agentes**: construit agentes com [[smolagents]] ou [[langchain]], integrando tool calling, planejamento e iteração. **Visão Computacional**: fine-tuning [[ViT]] ou [[DINO]] em datasets próprios, detecção de objetos com YOLO. **Áudio**: treinar modelos de speech-to-text ([[Whisper]]), classificação de áudio, text-to-speech. Cada módulo: 30min leitura + 30min código hands-on em Colab. Fluxo recomendado: comeca com LLMs se novo em IA, depois agentes, depois multimodal conforme interesse.

Integração prática: modelos fine-tuned no curso podem ser salvos direto no HF Hub, compartilhados, ou deployados via [[spaces]] (hospedagem Gradio gratuita). Usar datasets públicos (ImageNet, Common Voice, LibriSpeech) ou uploads privados.

## Stack e requisitos
Conta Google (Colab), conta HuggingFace (grátis). T4 GPU via Colab suficiente para todos os cursos. Python 3.8+, bibliotecas instaláveis via pip: `transformers`, `datasets`, `huggingface-hub`. Pré-requisito de conhecimento: Python intermediário, conceitos básicos de redes neurais (backpropagation, loss, gradient). Tempo: 1-2h por módulo.

## Armadilhas e limitacoes
Colab memory reset se inativa >90min; salva checkpoints para Google Drive. Datasets grandes (ImageNet full) excedem limite Colab storage; usar shards ou samples. Fine-tuning completo em 24GB RAM é lento; usar LoRA para modelos > 7B parâmetros. Modelos multimodais (Llava, Gemini emulation) exigem GPUs melhor (A100 idealmente), consumer GPUs limitadas a inferência.

## Conexoes
[[construcao-de-llm-do-zero|LLM do zero]]
[[fine-tuning-de-llms-sem-codigo|Fine-tuning sem código]]
[[democratizacao-de-modelos-de-ia|Acesso a modelos]]
[[embeddings-multimodais-em-espaco-vetorial-unificado|Embeddings multimodais]]

## Historico
- 2026-04-02: Nota criada
- 2026-04-02: Reescrita pelo pipeline
