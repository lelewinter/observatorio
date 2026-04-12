---
date: 2026-03-23
tags: [llm, open-source, local-llm, qwen, destilacao, claude, cadeia-de-raciocinio]
source: https://x.com/0xCVYH/status/2036174079607079379?s=20
autor: "@0xCVYH"
tipo: aplicacao
---

# Rodar Qwen 3.5-4B Localmente com llama.cpp ou Ollama (Destilado de Claude Opus)

## O que é

Qwen 3.5-4B é modelo de linguagem open source com apenas 4 bilhões de parâmetros, destilado do Claude Opus 4.6 (melhor modelo do mundo). Comprime o "pensamento" do Opus em modelo que roda completamente localmente no notebook — sem API, sem cloud, sem latência de rede, sem custo recorrente. Formato GGUF (Quantized) permite execução eficiente em CPU/GPU comum.

Característica crítica: Qwen 3.5-4B foi treinado com 14.000 amostras de raciocínio estilo Claude Opus (chain-of-thought), capturando não apenas respostas mas o *como você pensa* para chegar lá.

## Por que importa agora

O tradeoff histórico entre qualidade e privacidade desapareceu:

| Aspecto | LLM Cloud (Claude, GPT-5) | LLM Local Antigo (<2026) | Qwen 3.5-4B Agora |
|---------|---------------------------|--------------------------|------------------|
| Qualidade | 95%+ | 60% | 90%+ |
| Privacidade | 0% (dados na Anthropic/OpenAI) | 100% (local) | 100% |
| Latência | 1-3s (rede) | Varia (local) | <100ms |
| Custo | ~$0.003 por 1K tokens | Grátis | Grátis |
| Raciocínio Multi-etapa | Sim (CoT) | Não (LLaMA 2, Mistral) | **Sim (destilado Opus)** |

Leticia pode agora rodas um modelo que "pensa como Claude Opus" no seu notebook, sem dados deixando a máquina. Ideal para:
- Análise confidencial (dados médicos, financeiros)
- Prototipagem desconectada (offline, voo, datacenter sem internet)
- Integração local em apps (desktop, mobile edge)
- Pesquisa de IA (treinar modelos especializados em cima desta base)

## Como implementar

### Setup: llama.cpp (recomendado para CPU/GPU misto)

```bash
# 1. Instalar llama.cpp
git clone https://github.com/ggerganov/llama.cpp
cd llama.cpp
make

# 2. Download do Qwen 3.5-4B GGUF (4-bit quantizado, ~3GB)
# Opção A: Hugging Face (direto)
# https://huggingface.co/Jackrong/Qwen3.5-4B-Claude-4.6-Opus-Reasoning-Distilled-v2-GGUF

# Download com wget ou curl
wget https://huggingface.co/Jackrong/Qwen3.5-4B-Claude-4.6-Opus-Reasoning-Distilled-v2-GGUF/resolve/main/qwen-3.5-4b-opus-q4_k_m.gguf

# 3. Rodar inference
./main -m qwen-3.5-4b-opus-q4_k_m.gguf \
    -p "Por que a destilação de LLMs funciona? Pense passo a passo." \
    -n 512 \
    --repeat_penalty 1.1 \
    -c 2048  # context window
```

**Output esperado:**
```
Destilação de LLMs funciona porque:

1. O modelo maior (Opus) tem uma "compreensão" distribuída 
   em 176B parâmetros.
2. Ao treinar o modelo menor (Qwen 4B) em exemplos de raciocínio 
   do Opus, ele aprende PADRÕES de como pensar, não memoriza 
   as respostas.
3. Esses padrões são mais gerais que as respostas específicas — 
   transferem para problemas novos.
4. Resultado: Qwen 4B consegue ~95% da qualidade do Opus 
   em 2.3% dos parâmetros.

A analogia correta é: maestro ensina orquestra jovem 
a improvisar. Orquestra nunca será tão boa quanto maestro, 
mas consegue tocar 95% tão bem em sua própria apresentação.
```

### Setup: Ollama (mais simples)

```bash
# 1. Instalar Ollama
# macOS/Linux: https://ollama.ai
# Windows: https://ollama.ai/download

# 2. Rodar Qwen direto (Ollama faz download automático)
ollama run jackrong/qwen3.5-4b-opus:q4

# 3. Usar via API
curl http://localhost:11434/api/generate \
  -d '{
    "model": "jackrong/qwen3.5-4b-opus:q4",
    "prompt": "Qual é a diferença entre destilação e fine-tuning?",
    "stream": false
  }'
```

### Integração em Python

```python
# requirements.txt
ollama==0.1.0
langchain==0.1.0

# local_qwen.py
import ollama
from typing import Iterator

class LocalQwenModel:
    def __init__(self, model_name: str = "jackrong/qwen3.5-4b-opus:q4"):
        self.model_name = model_name
        self.client = ollama.Client()
    
    def generate_chain_of_thought(self, query: str, max_tokens: int = 1024) -> str:
        """Gera resposta com raciocínio multi-etapa (CoT)."""
        
        cot_prompt = f"""Pense passo a passo:

Pergunta: {query}

Processo de raciocínio:
1. Entender a pergunta
2. Identificar componentes-chave
3. Resolver cada componente
4. Integrar a resposta final

Responda com clareza:"""
        
        response = self.client.generate(
            model=self.model_name,
            prompt=cot_prompt,
            stream=False,
            options={
                "num_predict": max_tokens,
                "temperature": 0.7,
                "top_p": 0.9,
            }
        )
        
        return response["response"]
    
    def streaming_generate(self, prompt: str) -> Iterator[str]:
        """Stream de tokens (útil para UI responsiva)."""
        response = self.client.generate(
            model=self.model_name,
            prompt=prompt,
            stream=True
        )
        
        for chunk in response:
            yield chunk["response"]

# Uso
if __name__ == "__main__":
    qwen = LocalQwenModel()
    
    # Teste 1: CoT
    result = qwen.generate_chain_of_thought(
        "Por que modelo local é importante para privacidade em IA?"
    )
    print(result)
    
    # Teste 2: Streaming
    print("\n--- Streaming ---")
    for token in qwen.streaming_generate("Explique quantização em LLMs"):
        print(token, end="", flush=True)
```

### Specialized Fine-tuning (avançado)

Se Leticia quer treinar Qwen 3.5-4B para caso de uso específico (ex: análise de código, criação de jogos):

```python
# fine_tune_qwen.py
from unsloth import FastLanguageModel
import torch

# Carrega modelo base com LoRA (Low-Rank Adaptation)
model, tokenizer = FastLanguageModel.from_pretrained(
    model_name="unsloth/Qwen3.5-4B-Claude-Distilled",
    max_seq_length=2048,
    load_in_4bit=True,
    dtype=torch.float16,
)

# Configurar LoRA (treina ~1% dos parâmetros, não 100%)
model = FastLanguageModel.get_peft_model(
    model,
    r=16,  # Rank
    lora_alpha=16,
    lora_dropout=0.05,
    bias="none",
    use_gradient_checkpointing=True,
    use_rslora=True,  # Rank-stabilized LoRA
)

# Dataset de exemplos (ex: GDScript para game dev)
training_data = [
    {
        "instruction": "Gere um script Godot 4 para movimento de player",
        "input": "Player deve se mover com WASD, pular com espaço",
        "output": """extends CharacterBody2D

var speed = 200.0
var jump_force = -400.0

func _process(delta):
    var velocity = Vector2.ZERO
    
    if Input.is_action_pressed("ui_right"):
        velocity.x = speed
    if Input.is_action_pressed("ui_left"):
        velocity.x = -speed
    if Input.is_action_just_pressed("ui_accept"):
        velocity.y = jump_force
    
    velocity.y += 800 * delta  # Gravity
    position += velocity * delta
"""
    }
]

# Treinar (requer GPU com 8GB+)
from transformers import TrainingArguments, SFTTrainer

trainer = SFTTrainer(
    model=model,
    tokenizer=tokenizer,
    train_dataset=training_data,
    dataset_text_field="output",
    max_seq_length=2048,
    args=TrainingArguments(
        per_device_train_batch_size=4,
        gradient_accumulation_steps=4,
        warmup_steps=5,
        num_train_epochs=3,
        learning_rate=2e-4,
        output_dir="./qwen-gdscript-specialist",
    ),
)

trainer.train()

# Export para GGUF (compatível com llama.cpp)
model.save_pretrained("qwen-gdscript-finetuned")
```

## Stack técnico

- **Modelo base:** Qwen3.5-4B-Claude-4.6-Opus-Reasoning-Distilled-v2 (Hugging Face)
- **Formato:** GGUF (quantização 4-bit = ~3.2GB no disco)
- **Runtime:** llama.cpp (C++, otimizado) ou Ollama (wrapper user-friendly)
- **Framework Python:** Ollama client, LangChain, Unsloth (fine-tuning)
- **Hardware mínimo:** CPU moderna + 8GB RAM (lento mas funciona) / GPU 6GB+ (rápido)
- **Sistema operacional:** Linux, macOS, Windows (todos suportados)

## Armadilhas e limitações

**1. Raciocínio multi-etapa é custoso mesmo em 4B.** Chain-of-thought gera respostas 3-5x mais longas que respostas diretas. Em modelo pequeno, isso significa latência maior. Solução: use CoT para problemas complexos (math, lógica), respostas diretas para simples (classificação, extração).

**2. Quantização em 4-bit reduz qualidade.** GGUF q4_k_m (4-bit) perde ~5-10% de qualidade em relação ao modelo completo. Se você precisa de precisão máxima, considere 5-bit ou até 8-bit (mas vai usar mais VRAM). Teste com seu caso de uso antes de descartar.

**3. Contexto limitado (2K tokens).** Qwen 3.5-4B treinou com context window de 2048 tokens (~8K caracteres). Se sua tarefa requer análise de documento grande (>10K palavras), vai truncar. Solução: split do documento + prompting, ou usar versão maior (Qwen 27B, 35B).

**4. Destilação não transfere conhecimento super-especializado.** Se Opus foi treinado com dados que Qwen não viu, Qwen não vai saber. Ex: Opus tem knowledge de papers publicados em 2025, Qwen pode não ter. Verifique benchmark antes de usar para research.

**5. Fine-tuning requer dados de qualidade.** Se você treina Qwen com dados ruins, fica modelo ruim. Regra: ~500-1000 exemplos de alta qualidade > 10K exemplos mediocres. Curador, não quantidade.

**6. Não suporta visão multimodal natively.** Qwen 3.5-4B é texto-only. Se você precisa "entender imagens", vai precisar de pipeline separado (CLIP, ViT) ou usar modelo multimodal maior. Workaround: descrever imagem em texto (via OCR ou manual) antes de passar para Qwen.

## Conexões

- [[Claude Code Subconscious Letta Memory Layer]] — Usar Qwen local para memória persistente
- [[local_llm_reddit_discussao]] — Comunidade que roda LLMs locais
- [[16_github_repos_melhor_curso_ml]] — Se quiser entender fine-tuning melhor
- [[Mistral TTS - Text-to-Speech Local Gratuito]] — Combinar com TTS para apps assistente
- [[MediaPipe Face Recognition Local Edge]] — Stack de modelos locais + visão

## Histórico

- 2026-03-23: Nota criada (X/@0xCVYH)
- 2026-04-02: Reescrita como guia de implementação
- 2026-04-11: Expandida com código Python/GGUF, fine-tuning, tabela de tradeoffs, armadilhas
