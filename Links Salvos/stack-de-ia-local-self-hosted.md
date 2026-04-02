---
tags: [IA-local, LLM, self-hosted, RAG, ferramentas]
source: https://x.com/0xCVYH/status/2034752820159635746?s=20
date: 2026-04-02
---
# Stack de IA Local Self-Hosted

## Resumo
É possível montar um ambiente completo de IA local — com gerenciamento de modelos, interface, transcrição, voz e RAG — com custo zero de software, usando apenas hardware acessível.

## Explicação
Uma stack de IA local self-hosted permite rodar Large Language Models e ferramentas auxiliares inteiramente na própria máquina, sem depender de APIs pagas ou enviar dados para servidores externos. Isso oferece privacidade total, custo recorrente zero e controle completo sobre os modelos utilizados.

A stack recomendada combina cinco camadas funcionais: **Ollama** gerencia o download e a execução dos modelos (equivalente a um gerenciador de pacotes para LLMs); **Open WebUI** fornece uma interface gráfica no browser similar ao ChatGPT; **whisper.cpp** realiza transcrição de áudio localmente (implementação otimizada do Whisper da OpenAI em C++); **edge-tts** converte texto em fala sintética; e **AnythingLLM** implementa RAG (Retrieval-Augmented Generation), permitindo que o modelo consulte documentos próprios antes de responder.

O requisito mínimo de hardware — 16GB de RAM e 8GB de VRAM — é o gargalo real desta abordagem. A VRAM determina quais modelos podem ser executados com aceleração GPU; com 8GB é possível rodar modelos de 7B parâmetros quantizados (ex: Llama 3, Mistral, Gemma). Sem GPU suficiente, a inferência cai para CPU, tornando o uso prático muito mais lento.

A camada de RAG (AnythingLLM) é especialmente relevante para casos de uso profissional: ela cria embeddings dos documentos locais e os injeta como contexto nas queries ao modelo, superando a limitação de conhecimento estático dos LLMs base sem necessidade de fine-tuning.

## Exemplos
1. **Assistente de documentação privado**: Carregar manuais técnicos ou contratos no AnythingLLM e fazer perguntas via Open WebUI sem que os dados saiam da máquina.
2. **Transcrição + sumarização local**: Usar whisper.cpp para transcrever reuniões gravadas e passar o texto ao Ollama para gerar resumos.
3. **Pipeline de voz bidirecional**: Combinar whisper.cpp (entrada de voz) + Ollama (processamento) + edge-tts (resposta em áudio) para criar um assistente de voz totalmente local.

## Relacionado
*(Nenhuma nota existente no vault para conectar no momento.)*

## Perguntas de Revisão
1. Qual é o componente da stack responsável por permitir que o modelo responda com base em documentos próprios, e como ele funciona tecnicamente?
2. Por que a VRAM é o recurso limitante mais crítico nessa stack, e o que acontece quando ela é insuficiente?

## Histórico de Atualizações
- 2026-04-02: Nota criada a partir de Telegram