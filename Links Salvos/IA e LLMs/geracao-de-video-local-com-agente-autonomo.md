---
tags: [ia-local, geração-de-video, agentes-autonomos, llm, hardware-acessivel]
source: https://x.com/0xCVYH/status/2036546677943746984?s=20
date: 2026-04-02
tipo: aplicacao
---
# WanGP: Geração de Vídeo Local com Agente LLM Nativo (8GB VRAM)

## O que e
WanGP integra agente LLM (Qwen 3.5VL) nativamente em interface de geração de vídeo local, permitindo descrever videos em linguagem natural e o agente orquestra todo pipeline: interpretação de intenção, preenchimento automático de parâmetros, execução de modelo diffusão. Roda 100% local em 8GB VRAM, eliminando dependência de APIs pagas.

## Como implementar
**Fluxo**: usuário digita "vídeo de céu ao pôr do sol em floresta, estilo anime, 5 segundos" no interface Gradio → agente LLM analisa prompt, extrai: (duração=5s, estilo=anime, prompt_refinado para diffusion), preenche form UI automaticamente, clica "generate". Backend roda diffusion model localmente (provavelmente ~4-8B parâmetros), output é MP4 pronto. **Agência**: agente não gera vídeo diretamente — orquestra, traduzindo intenção humana em config técnica. Isso é design pattern diferente de "LLM que gera vídeo": aqui LLM é maestro, diffusion é instrumento.

Setup: instalar WanGP, baixar modelo Qwen 3.5VL + video diffusion (ex: Stable Video, AnimateAnything), rodar `python app.py`. Acesso em http://localhost:7860.

## Stack e requisitos
GPU 8GB+: RTX 3060, RTX 4060, Apple Silicon M1/M2 Pro suficientes. Qwen 3.5VL (~7B params) + video diffusion (~2B) ≈ 15GB VRAM pico, offload parcial em RAM reduz a 8GB usável. Python 3.10+, Gradio, transformers, diffusers. Tempo: primeira execução ~5 minutos (model download), gerar vídeo 5seg ~2-3 minutos em RTX 3060. Custo: zero (open-source).

## Armadilhas e limitacoes
Qualidade de vídeo gerado é inferior a APIs cloud (Sora, Runway) — espera degradação em movimento, estilo pode ser genérico. Interpretação de prompt pelo agente pode falhar em intenções muito específicas ("cinematic, 24fps, anamorphic lens") — agente simplifica. Tempo de geração é lento comparado a cloud (3min vs 30seg em Runway Pro) — trade-off é privacidade total. Offloading entre GPU e RAM tem overhead; performance piora com modelo maior. Controlabilidade reduzida — não pode especificar keyframes intermediários ou máscaras de movimento.

## Conexoes
[[democratizacao-de-modelos-de-ia|IA local e descentralizada]]
[[geracao-de-cenas-multi-shot-por-ia|Geração cinematográfica]]
[[empresa-virtual-de-agentes-de-ia|Orquestração de agentes]]

## Historico
- 2026-04-02: Nota criada
- 2026-04-02: Reescrita pelo pipeline
