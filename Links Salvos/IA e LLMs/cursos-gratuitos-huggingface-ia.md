---
tags: [ia, cursos, huggingface, llm, agentes, visao-computacional, audio, open-source, transformers]
source: https://x.com/heynavtoor/status/2039326170421010855?s=20
date: 2026-04-11
tipo: aplicacao
---
# 9 Cursos Gratuitos HuggingFace: LLMs a Visão Computacional

## O que é

HuggingFace oferece suite completa de **9 cursos open-source** cobrindo stack moderno de IA, disponíveis em [https://huggingface.co/learn](https://huggingface.co/learn). Cada curso combina:

- Teoria concisa em markdown/videos (30min leitura)
- **Notebooks executáveis em Google Colab** (30-60min prático)
- Modelos, datasets e código reutilizáveis do HuggingFace Hub
- **Certificados de conclusão** após quiz final

A proposta é eliminar barreira de custo e acesso: não exige GPU cara própria, ambiente local complexo ou assinatura. Tudo roda em navegador com Colab T4 gratuito (35h/mês). Cursos cobrem: **LLMs, Agentes, Visão Computacional, Processamento de Áudio, Multimodal, Diffusion Models, Reinforcement Learning, e Open Source Stack**.

## Como implementar

### Caminho Recomendado (Ordem Progressiva)

**Fase 1: Foundation (Semanas 1-2)**

1. **LLM Course** ([https://huggingface.co/learn/llm-course](https://huggingface.co/learn/llm-course))
   - Cap 1: Arquitetura de Transformers (atenção, layer norm, feed-forward)
   - Cap 2: Pre-training (tokenização, causal language modeling, métricas)
   - Cap 3: Fine-tuning (SFT, DPO, QLora para modelos 7B+)

**Exemplo prático — Fine-tuning Llama-2-7B em dataset customizado:**

```python
from transformers import AutoModelForCausalLM, AutoTokenizer, TrainingArguments, Trainer
from datasets import load_dataset

# Carregar modelo e tokenizer
model_name = "meta-llama/Llama-2-7b"
model = AutoModelForCausalLM.from_pretrained(model_name, device_map="auto")
tokenizer = AutoTokenizer.from_pretrained(model_name)

# Preparar dataset customizado
dataset = load_dataset("json", data_files="meu_dataset.json")

def tokenize_function(examples):
    return tokenizer(
        examples["text"],
        padding="max_length",
        truncation=True,
        max_length=512
    )

tokenized = dataset.map(tokenize_function, batched=True)

# Configurar training
training_args = TrainingArguments(
    output_dir="./llama-finetuned",
    num_train_epochs=3,
    per_device_train_batch_size=4,  # Reduzido para 24GB VRAM
    gradient_accumulation_steps=4,
    learning_rate=2e-4,
    warmup_steps=100,
    logging_steps=10,
    save_steps=500,
)

trainer = Trainer(
    model=model,
    args=training_args,
    train_dataset=tokenized["train"],
)

trainer.train()
```

2. **Agents Course** ([https://huggingface.co/learn/agents-course](https://huggingface.co/learn/agents-course))
   - SmoLAgents: agentes leves com tool calling
   - LangChain integration: planning, memory, iteração
   - Exemplo: agente que busca paper no arXiv, resume e responde questões

**Código mínimo — Agente com tool calling:**

```python
from transformers import load_tool
from smolagents import CodeAgent, HfApiModel

# Carregar ferramentas disponíveis
web_search_tool = load_tool("huggingface-tools/web_search")
image_generation_tool = load_tool("huggingface-tools/text_to_image")

# Definir agente
model = HfApiModel(
    model_id="meta-llama/Llama-2-70b-chat-hf",
    token="hf_YOUR_TOKEN"
)

agent = CodeAgent(
    tools=[web_search_tool, image_generation_tool],
    model=model,
    max_iterations=5
)

# Executar tarefa
result = agent.run("Busque noticias sobre IA em 2026 e gere imagem conceitual")
```

**Fase 2: Especialização (Semanas 3-6)**

3. **Vision Course**
   - Fine-tuning ViT (Vision Transformer) em ImageNet custom
   - DINO para object detection zero-shot
   - Exemplo: treinar classificador de plantas em 500 imagens próprias

```python
from transformers import ViTImageProcessor, ViTForImageClassification
from PIL import Image
import torch

# Carregar modelo pré-treinado
processor = ViTImageProcessor.from_pretrained("google/vit-base-patch16-224")
model = ViTForImageClassification.from_pretrained(
    "google/vit-base-patch16-224",
    num_labels=10,  # Número de classes customizado
    id2label={i: str(i) for i in range(10)},
    label2id={str(i): i for i in range(10)}
)

# Inferência
image = Image.open("planta.jpg")
inputs = processor(images=image, return_tensors="pt")
outputs = model(**inputs)
logits = outputs.logits

predicted_class_idx = logits.argmax(-1).item()
print(f"Classe predita: {model.config.id2label[predicted_class_idx]}")
```

4. **Audio Course**
   - Whisper para speech-to-text multilíngue
   - Classificação de áudio (environmental sound)
   - Text-to-speech com Bark ou XTTS

```python
from transformers import AutoProcessor, AutoModelForCTC
import librosa
import numpy as np

# Speech-to-text com Wav2Vec2
processor = AutoProcessor.from_pretrained("facebook/wav2vec2-base-960h")
model = AutoModelForCTC.from_pretrained("facebook/wav2vec2-base-960h")

# Carregar áudio
audio, sr = librosa.load("audio.wav", sr=16000)

# Processar
input_values = processor(audio, sampling_rate=sr, return_tensors="pt").input_values
logits = model(input_values).logits
predicted_ids = torch.argmax(logits, dim=-1)

# Decodificar
transcription = processor.batch_decode(predicted_ids)[0]
print(f"Transcrição: {transcription}")
```

5. **Multimodal Course**
   - LLaVA: vision + language
   - CLIP para zero-shot image classification
   - Cross-modal retrieval (texto → imagens similares)

**Fase 3: Advanced (Semanas 7+)**

6. **Diffusion Models** — Geração de imagens, inpainting, controlnet
7. **RL Course** — Fine-tuning com reward models, PPO
8. **Open Source Stack** — Production-grade LLM serving (vLLM, TGI)

### Integração com Obsidian

Cada curso completado pode gerar nota no vault:
- Salvar checkpoints de modelo no HF Hub (privado ou público)
- Link direto: `huggingface.co/seu-usuario/seu-modelo`
- Compartilhar via HuggingFace Spaces (Gradio app gratuita)

```python
# Após fine-tuning, fazer push para Hub
from huggingface_hub import Repository

model.push_to_hub("seu-usuario/seu-modelo-customizado")
tokenizer.push_to_hub("seu-usuario/seu-modelo-customizado")
```

## Stack e requisitos

**Mínimo para começar:**
- Conta Google (grátis, acesso Colab)
- Conta HuggingFace (grátis)
- Python 3.10+
- Conhecimento prévio: Python intermediário, noções de redes neurais (backprop, loss)

**Hardware:**
- GPU: T4 Colab (15GB VRAM) suficiente para todos os cursos
- Para rodar localmente: RTX 3060+ (12GB) ou Apple Silicon 16GB+

**Bibliotecas (instaladas automaticamente em Colab):**
```bash
pip install transformers datasets huggingface_hub accelerate torch
pip install pillow librosa # Para vision e áudio
pip install peft qlora # Para fine-tuning eficiente
```

**Tempo estimado:**
- 1-2h por módulo (leitura + código)
- Curso completo: 40-60h spread ao longo de 2 meses
- Fine-tuning de um modelo: 30min em Colab T4 (pequeno dataset)

**Custo:**
- Colab: grátis (35h GPU/mês)
- HuggingFace Hub storage: grátis até 50GB
- HF Spaces (deploy): grátis com compute grant ~USD 16/mês
- **Total: USD 0-20/mês se usar Colab, USD 0 se não fizer deploy**

## Armadilhas e limitações

**1. Colab memory timeout**
- Colab desconecta após 30min inatividade ou 12h conexão contínua
- **Solução**: Salvar checkpoints em Google Drive a cada 100 steps
```python
trainer = Trainer(
    ...,
    save_strategy="steps",
    save_steps=100,
    output_dir="/content/drive/MyDrive/checkpoints",  # Persistent
)
```

**2. Datasets grandes excedem Colab storage**
- ImageNet full (~150GB) impossível; limite Colab é ~50GB workspace
- **Solução**: Usar data sharding ou sample dataset
```python
dataset = load_dataset("imagenet-1k", split="train[:5%]")  # Pega 5%
```

**3. Fine-tuning full é lento para modelos 7B+**
- 7B model em 24GB RAM: ~5-10 epochs levam horas
- **Solução**: Usar LoRA (Low-Rank Adaptation) — reduz parâmetros treináveis em 100x
```python
from peft import LoraConfig, get_peft_model

lora_config = LoraConfig(
    r=8,
    lora_alpha=16,
    target_modules=["q_proj", "v_proj"],
    lora_dropout=0.05,
    bias="none"
)

model = get_peft_model(model, lora_config)
```

**4. Modelos multimodais (LLaVA, Gemini-like) exigem GPUs melhores**
- Vision + Language em T4 é muito lento (~1 token/seg)
- **Alternativa**: Usar apenas vision components ou inferência em CPU (viável)

**5. Qualidade de fine-tuning depende muito de dataset**
- Dataset ruim → modelo overfits ou aprende padrões spurios
- **Validação**: Sempre reservar 10-20% para validation set, monitorar divergence

**6. Autenticação HuggingFace Hub**
- Precisas de token para modelos gated (Llama-2, etc)
- **Setup**: `huggingface-cli login` ou passar `token="hf_..."` no código

**7. Incompatibilidade entre versões**
- `transformers==4.40.0` pode quebrar código escrito em `4.30.0`
- **Boas práticas**: Pinnar versões em `requirements.txt`, usar virtual env

## Conexões

[[construcao-de-llm-do-zero|Construindo LLM do zero — deep dive em pré-training]]
[[fine-tuning-de-llms-sem-codigo|Fine-tuning sem código — UI simplificada HF]]
[[democratizacao-de-modelos-de-ia|Rodando modelos 70B em consumer GPU]]
[[embeddings-multimodais-em-espaco-vetorial-unificado|Embeddings cross-modal]]
[[deepagent-gerar-app-funcional-90-segundos|Gerar apps com LLM agent]]

## Histórico

- 2026-04-11: Nota completamente reescrita com pesquisa, exemplos código full, armadilhas detalhadas
- 2026-04-02: Nota original criada
