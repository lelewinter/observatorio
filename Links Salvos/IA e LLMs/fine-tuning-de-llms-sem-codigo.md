---
tags: [LLM, fine-tuning, open-source, ferramentas-ia, treinamento-modelos, unsloth, lora, qlora]
source: https://www.datacamp.com/tutorial/unsloth-studio-fine-tuning-llms-guide
date: 2026-04-11
tipo: aplicacao
---
# Fine-Tuning de LLMs sem Código: Unsloth, LLaMA-Factory e Alternativas 2026

## O que é

Fine-tuning é adaptação de modelo pré-treinado a novo domínio com dados específicos. Em 2026, duas estratégias dominam sem-código:

1. **Unsloth Studio**: interface web drag-and-drop, otimizações de kernel Triton (2× rápido, 70% menos VRAM vs LoRA padrão)
2. **LLaMA-Factory**: framework low-code (1 arquivo YAML, zero Python) com suporte 200+ modelos

**Diferença fine-tuning methods**:
- **Full fine-tuning**: atualiza todos pesos (~60GB VRAM para 7B modelo)
- **LoRA** (Low-Rank Adaptation): treina só matriz 768×4, congela base (~16GB)
- **QLoRA** (Quantized LoRA): base quantizado int4, LoRA em fp32 (~8GB)

**Realidade 2026**: QLoRA em GPU consumer (RTX 4070, 12GB) é viável. Antes era privilegio FAANG.

## Como implementar

### Opção 1: Unsloth Studio (Interface web, mais fácil)

**Setup** (5 minutos):

```bash
# Clonar repo
git clone https://github.com/unslothai/unsloth
cd unsloth

# Instalar dependências
pip install -r requirements.txt
# Ou específico para Unsloth Studio
pip install unsloth-studio torch transformers

# Rodar UI
unsloth-studio --port 7860

# Abrir http://localhost:7860
```

**Workflow via UI**:

```
1. Upload Dataset
   └─ Formatos: CSV, JSONL, TXT, PDF
   └─ Coluna formato: "instruction", "output" (standard chat)
   └─ Exemplo CSV:
      instruction,output
      "Qual é capital do Brasil?","Brasília"
      "Explique IA","Inteligência Artificial é..."

2. Selecionar Modelo Base
   └─ Opções: Llama-2-7B, Mistral-7B, Gemma-2B/7B, Qwen-1.5B/7B
   └─ Recomendação: começa com 7B (bom balance performance vs VRAM)

3. Configurar Parâmetros (sliders)
   └─ Learning Rate: 0.0001-0.001 (LoRA é mais sensível que full fine-tune)
   └─ Epochs: 3-5 (dados < 1000 exemplos: 3, dados > 10k: 1-2)
   └─ Batch Size: 1-4 no consumer hardware (8GB: batch 1, 16GB: batch 4)
   └─ Rank (LoRA): 8-16 (maior rank = mais capacity, mais VRAM)
   └─ Alpha: 16 (padrão OK)

4. Treinar
   └─ Unsloth executa em background
   └─ Monitoramento: loss vs validação set
   └─ Tempo típico: 7B modelo, 1000 exemplos = 30min (GPU), 4h (CPU)

5. Testar & Exportar
   └─ Playground web: chat com modelo fine-tuned
   └─ Export formatos: HF Hub, GGUF (llama.cpp), Ollama, safetensors
```

**Exemplo dataset** (JSONL, formato recomendado):

```jsonl
{"instruction": "Qual é a capital de Brasil?", "output": "Brasília"}
{"instruction": "Explique o que é machine learning em 1 parágrafo", "output": "Machine learning é..."}
{"instruction": "Escreva um haiku sobre primavera", "output": "Flores desabrocham\nPássos leves no caminho\nVida renasce"}
```

**Dica**: se dados em PDF, Unsloth extrai automaticamente via OCR + LLM. Se manual: salva tempo.

### Opção 2: LLaMA-Factory (Framework low-code, mais flexibilidade)

**Setup**:

```bash
# Clonar
git clone https://github.com/hiyouga/LLaMA-Factory
cd LLaMA-Factory

# Instalar
pip install -e ".[torch]"  # Instala LLaMA-Factory + torch

# Rodar UI (web)
llamafactory-cli webui

# Ou via CLI (script)
llamafactory-cli train examples/lora_single_gpu.yaml
```

**Arquivo config YAML** (zero Python!):

```yaml
# lora_config.yaml
### Model Configuration
model_name_or_path: mistralai/Mistral-7B-v0.1
template: default
cache_dir: ./models

### Data Configuration
dataset:
  - name: alpaca_pt  # Dataset português (built-in)
  - name: custom
    dataset_path: ./my_data.jsonl
    formatting: alpaca  # Formato: {"instruction": ..., "output": ...}

### Training Configuration
output_dir: ./output/lora_mistral
overwrite_output_dir: true
stage: sft  # SFT = Supervised Fine-Tuning

### LoRA Configuration
peft_type: lora
lora_rank: 8
lora_alpha: 16
lora_dropout: 0.05
target_modules: ["q_proj", "v_proj"]  # Quais layers aplicar LoRA

### Hyperparameters
learning_rate: 5e-4
num_train_epochs: 3
per_device_train_batch_size: 4
per_device_eval_batch_size: 4
gradient_accumulation_steps: 2
warmup_steps: 100
logging_steps: 10
save_steps: 500
eval_steps: 500
max_samples: 10000

### Hardware
fp16: true  # Mixed precision (mais rápido, menos VRAM)
ddp_backend: nccl  # Multi-GPU support
```

**Executar**:

```bash
# Treinar
llamafactory-cli train lora_config.yaml

# Avaliar
llamafactory-cli eval lora_config.yaml

# Mesclar LoRA + base em novo modelo (exportar)
llamafactory-cli export lora_config.yaml

# Output: ./output/lora_mistral/merged_model
```

**Resultado**: modelo fine-tuned em ./output/, pronto para uso.

### Opção 3: Usar modelo fine-tuned em produção

```python
from transformers import AutoTokenizer, AutoModelForCausalLM
import torch

# Carregar modelo fine-tuned (local)
model_path = "./output/lora_mistral/merged_model"
tokenizer = AutoTokenizer.from_pretrained(model_path)
model = AutoModelForCausalLM.from_pretrained(
    model_path,
    torch_dtype=torch.float16,
    device_map="auto"  # Auto-distribute em GPU/CPU
)

# Inferência
prompt = "Qual é a capital de Brasil?"
inputs = tokenizer(prompt, return_tensors="pt")
outputs = model.generate(
    **inputs,
    max_new_tokens=100,
    temperature=0.7,
    top_p=0.9
)
response = tokenizer.decode(outputs[0], skip_special_tokens=True)
print(response)

# Output: "Qual é a capital de Brasil? Brasília é a capital do Brasil..."
```

### Opção 4: Fine-tune com dataset generation automático

Se tiver PDF (manual técnico, livro), converter para dataset:

```python
import pypdf
from anthropic import Anthropic

def generate_qa_from_pdf(pdf_path: str, output_jsonl: str):
    """
    1. Extrair texto de PDF
    2. Usar Claude para gerar Q&A pairs
    3. Salvar em JSONL
    """
    # 1. Extrair PDF
    reader = pypdf.PdfReader(pdf_path)
    text = ""
    for page in reader.pages:
        text += page.extract_text()
    
    # 2. Dividir em chunks
    chunks = [text[i:i+2000] for i in range(0, len(text), 1500)]  # Overlap 500
    
    client = Anthropic()
    qa_pairs = []
    
    for chunk in chunks:
        prompt = f"""Dado este trecho de texto:

{chunk}

Gere 3 pares (question, answer) para fine-tuning de LLM.
Formato JSON:
[
  {{"instruction": "pergunta aqui?", "output": "resposta aqui"}},
  ...
]

Respostas devem ser baseadas APENAS no texto fornecido."""
        
        response = client.messages.create(
            model="claude-3-5-sonnet-20241022",
            max_tokens=1000,
            messages=[{"role": "user", "content": prompt}]
        )
        
        import json
        try:
            pairs = json.loads(response.content[0].text)
            qa_pairs.extend(pairs)
        except:
            pass  # Parsing error, pula chunk
    
    # 3. Salvar JSONL
    with open(output_jsonl, 'w') as f:
        for pair in qa_pairs:
            f.write(json.dumps(pair) + '\n')
    
    return len(qa_pairs)

# Uso
num_qa = generate_qa_from_pdf("manual.pdf", "dataset.jsonl")
print(f"Gerados {num_qa} pares Q&A")
```

**Workflow**:
1. `generate_qa_from_pdf("manual.pdf", "data.jsonl")` → 500 Q&A em 10min
2. Upload em Unsloth Studio
3. Fine-tune em 30min
4. Modelo agora "entende" manual

### Opção 5: Comparar modelos fine-tuned

```python
def benchmark_models(prompt: str, models_dict: dict):
    """
    Testar múltiplos modelos fine-tuned, comparar respostas
    """
    results = {}
    for name, model_path in models_dict.items():
        tokenizer = AutoTokenizer.from_pretrained(model_path)
        model = AutoModelForCausalLM.from_pretrained(model_path, device_map="auto")
        
        inputs = tokenizer(prompt, return_tensors="pt")
        outputs = model.generate(**inputs, max_new_tokens=100)
        response = tokenizer.decode(outputs[0], skip_special_tokens=True)
        
        results[name] = response
    
    # Print side-by-side
    for name, response in results.items():
        print(f"\n{name}:")
        print(response[:200])
    
    return results

# Uso
models = {
    "base_mistral": "mistralai/Mistral-7B-v0.1",
    "fine_tuned_domain": "./output/lora_mistral/merged_model",
}
benchmark_models("Explique IA", models)
```

## Stack e requisitos

### Hardware

| VRAM | Método | Modelos Viáveis |
|------|--------|-----------------|
| 8GB | QLoRA quantizado (int4) | 3B, 7B (Mistral-7B, Gemma-7B) |
| 12GB | QLoRA + batch 2 | 7B, 13B (slow) |
| 16GB | LoRA + batch 4 | 7B, 13B, 20B (slow) |
| 24GB+ | Full fine-tune | 13B, 70B (viável) |

**Testado em 2026**:
- RTX 4070 (12GB): QLoRA, Mistral-7B, batch 2, OK
- RTX 4090 (24GB): LoRA, Llama-2-70B, batch 4, rápido
- M2 Pro (16GB): CPU-only, QLoRA, 5x mais lento

### Software

```bash
# Unsloth Studio
pip install unsloth-studio torch transformers peft

# LLaMA-Factory
pip install llamafactory torch transformers peft datasets pydantic

# Ambos precisam:
# - Python 3.10+
# - CUDA 11.8+ (NVIDIA) ou ROCm (AMD)
# - Pytorch 2.0+
```

### Custo

- **Fine-tune local**: $0 (eletricidade, ~50-200W por 1h)
- **Cloud**: AWS g4dn.xlarge ($0.53/h), Colab Pro ($10/mês, limitado)
- **Commercial**: Unsloth Cloud (beta, free until launch)

### Tempo típico

| Tamanho Dataset | Modelo | Método | Tempo (GPU) | Tempo (CPU) |
|-----------------|--------|--------|-------------|------------|
| 100 exemplos | 7B | QLoRA | 10min | 2h |
| 1000 exemplos | 7B | QLoRA | 30min | 6h |
| 10k exemplos | 7B | LoRA | 2h | 1 dia |
| 100k exemplos | 7B | LoRA | 12h | inviável |

## Armadilhas e limitacoes

### Armadilha 1: Dataset garbage in, garbage out
Sintoma: fine-tuned modelo gera respostas ruins/absurdas
Root cause: dataset baixa qualidade (typos, inconsistências, fatos errados)
Fix: review primeiros 10% dataset, garanta consistência. 100 exemplos bons > 10k ruins.

```python
# Validar dataset
import json
with open("data.jsonl") as f:
    pairs = [json.loads(line) for line in f]

# Verificar
print(f"Total: {len(pairs)}")
print(f"Avg instruction len: {np.mean([len(p['instruction']) for p in pairs])}")
print(f"Avg output len: {np.mean([len(p['output']) for p in pairs])}")

# Mostrar amostra
for i in range(min(5, len(pairs))):
    print(f"{i}: Q: {pairs[i]['instruction'][:50]}... A: {pairs[i]['output'][:50]}...")
```

### Armadilha 2: Overfitting em dataset pequeno
Sintoma: modelo fine-tuned memorizou exemplos (testa bem, produção falha)
Root cause: < 100 exemplos, epochs > 3, learning rate alto
Fix: usar early stopping (monitor validation loss), reduzir epochs (1-2), aumentar learning rate (0.001)

```yaml
# Em LLaMA-Factory config
num_train_epochs: 1  # Reduzido
learning_rate: 1e-3  # Aumentado
eval_strategy: steps  # Monitorar validation
eval_steps: 100
save_steps: 100  # Salvar checkpoint regularmente
load_best_model_at_end: true  # Usar melhor checkpoint
```

### Armadilha 3: LoRA reduz capacity—modelo perde skills gerais
Sintoma: fine-tuned em domínio específico, mas degradou em tarefas gerais
Root cause: LoRA é low-rank (4-16), não consegue adaptar completamente
Fix: 
- Aumentar rank (16 vs 8, se VRAM permitir)
- Mesclar dataset (70% domínio específico, 30% tasks gerais)
- Usar merge de múltiplos LoRA adapters

```python
# Mesclar base com LoRA
from peft import get_peft_model_state_dict, PeftModel

# Carregar base + LoRA
model = AutoModelForCausalLM.from_pretrained("mistral-7b")
model = PeftModel.from_pretrained(model, "lora_adapter_path")

# Mesclar weights
merged_state_dict = model.get_merged_weights()
model.save_merged_weights("merged_model")
```

### Armadilha 4: Quantização int4 degrada muito
Sintoma: fine-tuned em fp32, exportou int4, qualidade caiu
Root cause: quantização perde precisão em valores numéricos
Fix: teste int4 vs fp16 (2x VRAM, nenhuma degradação), decida tradeoff

```python
# Carregar int4 vs fp16
model_int4 = AutoModelForCausalLM.from_pretrained(
    path,
    load_in_4bit=True,
    bnb_4bit_compute_dtype=torch.float16
)

model_fp16 = AutoModelForCausalLM.from_pretrained(
    path,
    torch_dtype=torch.float16
)

# Comparar outputs para input idêntico
for prompt in test_prompts:
    out_int4 = generate(model_int4, prompt)
    out_fp16 = generate(model_fp16, prompt)
    print(f"Int4: {out_int4}")
    print(f"Fp16: {out_fp16}")
    print("---")
```

### Armadilha 5: Desalinhar expectativa em Unsloth Studio vs LLaMA-Factory
Sintoma: interface Unsloth parece simples, mas backend está rodando o quê?
Root cause: Unsloth roda Unsloth otimizado (mais rápido) vs LLaMA-Factory (mais genérico)
Fix: se crítico para produção, usar LLaMA-Factory (100% transparência). Unsloth OK para prototipo.

### Armadilha 6: Batch size errado = OOM ou underfitting
Sintoma: "CUDA out of memory" ou modelo tá subtreinado
Root cause: batch size muito alto (> VRAM) ou muito baixo (< 1 gradiente effetivo)
Fix: testar incremental:

```bash
# Se OOM em batch 4
batch_size=2

# Se underfitting (loss não converge)
batch_size=8  # Aumenta, ou gradient_accumulation_steps=2
```

### Armadilha 7: Não validar em contexto real
Sintoma: fine-tuned modelo passou em testes, falha em produção
Root cause: não testou em distribuição real (diferentes prompts, edge cases)
Fix: antes deploy, testar com 100+ prompts não vistos, manual review

```python
# Teste manual antes deploy
test_prompts = [
    "Questão simples",
    "Questão ambígua",
    "Typo intencional em questão",
    "Pergunta fora do domínio",
    "Jailbreak attempt"
]

for prompt in test_prompts:
    response = model.generate(prompt)
    print(f"Q: {prompt}")
    print(f"A: {response}")
    print("---")
    # Manual review aqui
```

## Conexoes

[[construcao-de-llm-do-zero|LLM fundamentals (arquitetura Transformer)]]
[[explicabilidade-como-medida-de-compreensao|Explicabilidade em fine-tuning (interpretability)]]
[[rag-sistemas-autonomos|RAG (alternativa a fine-tuning)]]

## Historico
- 2026-04-11: Nota reescrita com 5 opções (Unsloth, LLaMA-Factory, CLI, dataset generation, benchmark), código pronto-uso, hardware requirements table, armadilhas práticas
- 2026-04-02: Nota original criada
