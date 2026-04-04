---
tags: []
source: https://x.com/i/status/2039736220834480233
date: 2026-04-03
tipo: aplicacao
---
# Rodar Gemma 4 Localmente para Reasoning e Workflows Agentivos

## O que e

O Gemma 4 é a geração mais recente dos modelos open-weights do Google, derivado da mesma pesquisa que originou o Gemini 3. Ele foi lançado sob licença Apache 2.0, o que significa que você pode usar comercialmente, fazer fine-tuning e distribuir sem restrições de royalties. O foco principal é raciocínio avançado (advanced reasoning) e execução de workflows agentivos diretamente no seu hardware, eliminando dependência de APIs externas e custos de inferência.

## Como implementar

**1. Escolher a variante correta do Gemma 4**

O Gemma 4 foi lançado em múltiplos tamanhos. Com base no padrão da família Gemma anterior e nas informações disponíveis até o lançamento, esperam-se variantes de 1B, 4B, 12B e 27B parâmetros, além de versões multimodais (texto + imagem). Para uso local sem GPU de datacenter, o ponto de entrada mais equilibrado é o modelo de 12B em quantização Q4_K_M, que cabe em GPUs com 8–12 GB de VRAM. Para máquinas com apenas CPU, use a variante 4B em Q4_K_M ou Q5_K_S.

**2. Instalação via Ollama (caminho mais rápido)**

O Ollama é a forma mais direta de rodar Gemma 4 localmente sem configuração manual de pesos:

```bash
# Instalar Ollama (Linux/macOS)
curl -fsSL https://ollama.com/install.sh | sh

# Puxar e rodar Gemma 4 (ajuste o tag conforme disponibilidade)
ollama pull gemma4:12b
ollama run gemma4:12b

# Para a variante instrução/chat
ollama run gemma4:12b-instruct
```

Após o pull, o Ollama expõe automaticamente uma API REST compatível com OpenAI na porta `11434`. Isso permite integrar com qualquer ferramenta que já consuma endpoints OpenAI sem alterar o código.

**3. Instalação via Hugging Face + Transformers (maior controle)**

Para fine-tuning, experimentação ou integração em pipelines Python, use a biblioteca `transformers` diretamente:

```bash
pip install transformers accelerate bitsandbytes torch sentencepiece
```

```python
from transformers import AutoTokenizer, AutoModelForCausalLM
import torch

model_id = "google/gemma-4-12b-it"  # tag exato pode variar no HF

tokenizer = AutoTokenizer.from_pretrained(model_id)
model = AutoModelForCausalLM.from_pretrained(
    model_id,
    device_map="auto",
    torch_dtype=torch.bfloat16,
    load_in_4bit=True  # quantização via bitsandbytes para economizar VRAM
)

messages = [
    {"role": "user", "content": "Explique passo a passo como otimizar uma query SQL com índices compostos."}
]

input_ids = tokenizer.apply_chat_template(messages, return_tensors="pt").to(model.device)
output = model.generate(input_ids, max_new_tokens=512, do_sample=True, temperature=0.7)
print(tokenizer.decode(output[0], skip_special_tokens=True))
```

O parâmetro `device_map="auto"` distribui camadas automaticamente entre GPU e CPU se necessário (offloading), o que permite rodar o 27B mesmo em máquinas com 16 GB de VRAM se você tiver RAM suficiente.

**4. Servir o modelo com uma API compatível com OpenAI via LM Studio ou llama.cpp**

Para cenários de produção leve ou integração com ferramentas como LangChain e AutoGen, suba um servidor local:

```bash
# Via llama.cpp (compile antes ou use binário pré-compilado)
./llama-server \
  -m ./models/gemma-4-12b-q4_k_m.gguf \
  --host 0.0.0.0 \
  --port 8080 \
  -c 8192 \
  --n-gpu-layers 35
```

O parâmetro `--n-gpu-layers` controla quantas camadas ficam na GPU. Ajuste conforme sua VRAM: comece com 20 e aumente até saturar a memória. O flag `-c 8192` define o context window — o Gemma 4 suporta contextos longos (possivelmente até 128k tokens nas variantes maiores, verifique a config do modelo baixado).

**5. Construir um workflow agentivo simples com LangChain**

O ponto de diferencial do Gemma 4 anunciado é suporte a raciocínio e agentes. Para montar um agente com tools locais:

```python
from langchain_community.llms import Ollama
from langchain.agents import initialize_agent, AgentType
from langchain.tools import Tool
import subprocess

llm = Ollama(model="gemma4:12b-instruct", temperature=0)

def executar_shell(cmd: str) -> str:
    resultado = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=10)
    return resultado.stdout or resultado.stderr

tools = [
    Tool(
        name="ShellExecutor",
        func=executar_shell,
        description="Executa comandos shell no sistema local. Use para tarefas de sistema."
    )
]

agent = initialize_agent(
    tools=tools,
    llm=llm,
    agent=AgentType.ZERO_SHOT_REACT_DESCRIPTION,
    verbose=True
)

agent.run("Liste os 5 arquivos mais recentes na pasta /tmp e diga qual é o maior.")
```

Para workflows mais robustos com estado, substitua `initialize_agent` por LangGraph, que permite construir grafos de execução com loops, condicionais e memória persistente entre steps.

**6. Fine-tuning com QLoRA para domínio específico**

A licença Apache 2.0 permite fine-tuning e redistribuição do modelo ajustado. Para adaptar o Gemma 4 ao seu domínio:

```bash
pip install trl peft datasets
```

```python
from trl import SFTTrainer
from peft import LoraConfig
from transformers import TrainingArguments

lora_config = LoraConfig(
    r=16,
    lora_alpha=32,
    target_modules=["q_proj", "v_proj"],
    lora_dropout=0.05,
    bias="none",
    task_type="CAUSAL_LM"
)

training_args = TrainingArguments(
    output_dir="./gemma4-finetuned",
    per_device_train_batch_size=2,
    gradient_accumulation_steps=4,
    num_train_epochs=3,
    learning_rate=2e-4,
    fp16=True,
    save_strategy="epoch",
    logging_steps=10,
)

trainer = SFTTrainer(
    model=model,
    train_dataset=seu_dataset,  # Dataset Hugging Face com campo "text"
    peft_config=lora_config,
    dataset_text_field="text",
    max_seq_length=2048,
    args=training_args,
)

trainer.train()
```

Com QLoRA no modelo 12B, você precisa de aproximadamente 16 GB de VRAM para treinar com batch size 2. Para o modelo 4B, 8 GB já são suficientes.

## Stack e requisitos

**Hardware mínimo por variante:**
- Gemma 4 1B (Q4): CPU moderna com 8 GB RAM — sem GPU necessária
- Gemma 4 4B (Q4_K_M): GPU com 4 GB VRAM ou CPU com 16 GB RAM
- Gemma 4 12B (Q4_K_M): GPU com 8–10 GB VRAM (RTX 3080/4070 ou equivalente)
- Gemma 4 27B (Q4_K_M): GPU com 16–20 GB VRAM ou offloading GPU+CPU com 32 GB RAM

**Software:**
- Python 3.10+
- `transformers` >= 4.40, `torch` >= 2.2, `bitsandbytes` >= 0.43
- `ollama` >= 0.3 (para o caminho simplificado)
- `llama.cpp` compilado com suporte CUDA/Metal para máxima performance
- `trl` + `peft` para fine-tuning

**Licença:** Apache 2.0 — uso comercial permitido, sem restrição de redistribuição

**Custo:** Zero de API. Custo elétrico de inferência local + hardware existente. Para fine-tuning na nuvem, uma sessão de 3 horas em A100 no Google Colab Pro custa aproximadamente US$ 10–15.

**Acesso ao modelo:** Requer aceitação de termos no Hugging Face (google/gemma-4-*) — processo rápido e gratuito.

## Armadilhas e limitacoes

**Latência em hardware modesto:** Mesmo com quantização Q4, o modelo 12B em CPU pura produz tokens em velocidade frustrante (2–5 tokens/segundo). Para uso agentivo com múltiplos steps, isso