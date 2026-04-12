---
tags: [ia-local, python, open-source, laboratorio, hardware, ollama, llm, privacy]
source: https://github.com/ollama/ollama
date: 2026-04-11
tipo: aplicacao
---

# Montando um Laboratório de IA Local com Python e Open Source

## O que é

Um laboratório de IA local é um conjunto de ferramentas open-source que permite executar modelos de linguagem (LLMs) diretamente na sua máquina, sem dependência de APIs cloud, sem custos recorrentes, e com total privacidade dos dados. Ao invés de chamar OpenAI, Anthropic ou outras APIs, você baixa os modelos (7B, 13B, 70B parâmetros) e os roda localmente usando quantização (compressão) que os torna viáveis até em hardware consumidor.

O setup típico usa **Ollama** como orquestrador central — basicamente Docker para modelos IA. Você executa `ollama pull mistral` e em 2 minutos tem um modelo de 7B rodando via REST API. Python se integra via requests ou bibliotecas como langchain-ollama, permitindo construir pipelines: extração de texto → resumo → análise → formatação, tudo localmente sem internet.

Adicione **vLLM** para servir múltiplos usuários simultâneos, **text-generation-webui** para interface gráfica, **ComfyUI** ou **Automatic1111** se quiser gerar imagens com stable diffusion, e você tem um "laboratório IA completo" rodando no seu PC ou Mac.

## Como implementar

### Passo 1: Escolher Hardware

Antes de instalar qualquer coisa, tenha hardware suficiente:

**Entrada (modelos 7B, rápido local):**
- NVIDIA RTX 4060 (8GB VRAM) → 40-50 tokens/seg
- NVIDIA RTX 4070 (12GB VRAM) → 60-80 tokens/seg
- Apple Silicon M2 Pro com 32GB unified memory → 20 tokens/seg

**Intermediário (modelos 13-30B, uso balanceado):**
- NVIDIA RTX 4080 (16GB VRAM) → 100+ tokens/seg
- Apple M3 Max com 64GB unified memory

**Production (modelos 70B+, múltiplas requisições):**
- NVIDIA RTX 4090 (24GB VRAM) → 120-150 tokens/seg
- NVIDIA H100 (80GB, cloud-only, caro)

**CPU-only (sem GPU):**
- Possible mas lento: 5-10 tokens/seg mesmo com CPU top
- Viável apenas para testes rápidos ou modelos tiny (<2B)

### Passo 2: Instalar Ollama

Ollama é o gerenciador central. Instalação é trivial:

**Windows/Mac/Linux:**
```bash
# Windows: baixe installer em https://ollama.ai
# Mac: brew install ollama
# Linux: curl https://ollama.ai/install.sh | sh

# Verificar instalação
ollama --version
# Output: ollama version X.X.X
```

**Iniciar daemon:**
```bash
ollama serve
# Output: Ollama listening on 127.0.0.1:11434
```

Deixe esse terminal aberto; é o servidor local.

### Passo 3: Baixar e Rodar Primeiro Modelo

Em outro terminal:

```bash
# Baixar modelo Mistral 7B (recomendado para começar)
ollama pull mistral
# Download: 4.1 GB (primeira vez demora 5-10 min)

# Rodar modelo interativo
ollama run mistral
# Prompt: Write a Python function that reverses a string

# Ollama responde:
# def reverse_string(s):
#     return s[::-1]
```

Pronto. Você tem um LLM rodando localmente.

### Passo 4: Integrar com Python

Instale cliente Python e use em scripts:

```bash
pip install ollama langchain-ollama
```

**Script básico:**
```python
import ollama

# Chat simples
response = ollama.chat(
    model='mistral',
    messages=[
        {
            'role': 'user',
            'content': 'Explique brevemente o que é quantização de modelos',
        },
    ],
)
print(response['message']['content'])

# Output:
# Quantização é o processo de reduzir a precisão numérica
# dos pesos de um modelo neural (de float32 para int8, por exemplo)
# mantendo a qualidade enquanto reduz tamanho e melhora velocidade...
```

**Estruturar respostas (JSON):**
```python
import json

prompt = """
Analise este artigo e retorne JSON:
{"titulo": "...", "tema_principal": "...", "palavras_chave": [...]}

Artigo:
"Modelos open-source como Llama 2 estão democratizando acesso a IA..."
"""

response = ollama.chat(
    model='mistral',
    messages=[{'role': 'user', 'content': prompt}],
)

# Parse JSON da resposta
result = json.loads(response['message']['content'])
print(f"Tema: {result['tema_principal']}")
```

**Pipeline de múltiplas etapas:**
```python
def pipeline_analise(texto):
    # Etapa 1: Resumir
    resumo = ollama.chat(
        model='mistral',
        messages=[{'role': 'user', 'content': f'Resuma em 1 parágrafo:\n{texto}'}],
    )['message']['content']
    
    # Etapa 2: Extrair palavras-chave
    palavras = ollama.chat(
        model='mistral',
        messages=[{'role': 'user', 'content': f'Liste 5 palavras-chave principais:\n{resumo}'}],
    )['message']['content']
    
    # Etapa 3: Classificar por tema
    tema = ollama.chat(
        model='mistral',
        messages=[{'role': 'user', 'content': f'Classifique como: IA, Web, Mobile, ou DevOps:\n{resumo}'}],
    )['message']['content']
    
    return {"resumo": resumo, "palavras": palavras, "tema": tema}

# Usar
resultado = pipeline_analise("Seu texto aqui...")
print(json.dumps(resultado, indent=2, ensure_ascii=False))
```

### Passo 5: Escalar com vLLM (Múltiplos usuários)

Se você quer servir requests simultâneos (ex: webapp), Ollama tem limite. Use vLLM:

```bash
pip install vllm

# Rodar servidor vLLM na porta 8000
python -m vllm.entrypoints.openai.api_server \
    --model mistral-7b \
    --port 8000 \
    --gpu-memory-utilization 0.8
```

**Cliente Python:**
```python
from openai import OpenAI

client = OpenAI(
    api_key="dummy",  # vLLM não precisa autenticação local
    base_url="http://localhost:8000/v1"
)

response = client.chat.completions.create(
    model="mistral-7b",
    messages=[
        {"role": "user", "content": "Qual é o capital da Dinamarca?"}
    ],
    temperature=0.7,
    max_tokens=100
)

print(response.choices[0].message.content)
```

### Passo 6: Interface Gráfica (Opcional)

Se preferir não escrever código:

```bash
# text-generation-webui (UI linda para chat + parâmetros)
git clone https://github.com/oobabooga/text-generation-webui
cd text-generation-webui
pip install -r requirements.txt
python server.py
# Acesse http://localhost:7860

# Ou: OpenWebUI (interface moderna, compatível com Ollama)
docker run -d --network=host ghcr.io/open-webui/open-webui:latest
# Acesse http://localhost:8080
```

## Stack e requisitos

### Software Obrigatório
- **Ollama 0.1.15+** (orquestrador central)
- **Python 3.8+** (recomendado 3.10 ou 3.11)
- **git** (para clonar repos)

### Bibliotecas Python Principais
```bash
pip install ollama langchain-ollama requests
# Versões recomendadas:
# - ollama==0.1.15+
# - langchain-ollama==0.1.0+
# - requests==2.31.0+
```

### Hardware Recomendado por Caso

| Caso | GPU | VRAM | Modelo | Tokens/seg |
|------|-----|------|--------|-----------|
| Experimento | RTX 4060 | 8GB | Mistral 7B | 40-50 |
| Desenvolvimento | RTX 4070 | 12GB | Llama 2 13B | 60-80 |
| Produção local | RTX 4090 | 24GB | Llama 2 70B | 120-150 |
| Laptop Apple | M2 Pro | 32GB | Mistral 7B | 20-30 |
| CPU-only | - | 16GB RAM | Phi 3 | 5-10 |

### Alternativas Gratuitas (Não-Local)
- **Google Colab**: acesso livre a GPU T4/A100, rodas Ollama lá
- **Modal**: free tier para inference serverless
- **HuggingFace Spaces**: deploy modelos gratuitamente

### Custos de Infraestrutura
- **Máquina local existente**: $0 (roda no seu PC/Mac)
- **VPS com GPU (para 24/7)**: ~$30-50/mês (Vast.ai, Lambda Labs)
- **Energia (estimado)**: RTX 4090 usa ~420W, $2-5/mês se rodando 24/7

## Armadilhas e limitações

### 1. VRAM Insuficiente = Travamento do Sistema
Modelos maior que sua VRAM disponível causam paging para disco (SSD/HDD), reduzindo velocidade para 0.5 tokens/seg. Sistema fica travado.

**Exemplo:**
```
GPU: RTX 4060 (8GB)
Modelo: Llama 2 70B (precisa 40GB)
Resultado: Vai pagar, mas tão lento que parece congelado
```

**Solução:**
- Use quantização Q4 ou Q5 em vez de FP32
- Modelos menores: Mistral 7B em vez de Llama 70B
- Check VRAM: `nvidia-smi` antes de rodar

### 2. Perda de Qualidade com Quantização Agressiva
Quantizar de FP32 → Q3_K reduz tamanho em 10x, mas qualidade cai. Modelos ficam "burros".

**Exemplo concreto:**
```
FP32 Mistral 7B: Escreve código Python correto
Q3_K Mistral 7B: Escreve código com bugs óbvios
```

**Recomendação:**
- Comece com Q4_K_M (balanço: qualidade 95%, tamanho 50% do original)
- Teste com Q3_K se VRAM é crítica, mas aceite queda de ~10% em qualidade
- Nunca use Q2 para tarefas críticas

### 3. Alucinações e Fatos Inventados
Modelos open-source alucinam mais que Claude/GPT-4, especialmente fora do domain de treinamento.

```python
# Perigoso:
ollama.chat(..., 'Qual é a população de [cidade obscura]?')
# Resposta aleatória inventada

# Seguro:
ollama.chat(..., 'Liste 3 técnicas para debug em Python')
# Funciona bem (treinado em milhões de linhas de código)
```

**Mitigação:**
- Use prompts que peçam "cite fontes"
- Validate facts críticos contra Wikipedia/docs oficiais
- Para info financeira/legal, prefira não usar

### 4. Latência de Primeira Execução (Cold Start)
Primeira chamada a um modelo leva 2-5 segundos para "aquecimento" (carregar pesos na VRAM).

```
Ollama.chat primeira vez: 5 seg
Ollama.chat segunda vez: 0.8 seg (modelo já na memória)
```

**Workaround:**
- Keep-alive: deixe Ollama rodando sempre
- Pipeline: primeira etapa é "dummy" para warm-up
- vLLM bate melhor nesse métrica

### 5. Compatibilidade de Drivers GPU (NVIDIA/AMD/Metal)
Nem todo driver de GPU funciona com Ollama. AMD é particularmente furado.

**Verificar suporte:**
```bash
# NVIDIA: OK (CUDA 11.8+)
nvidia-smi

# AMD: Suporte experimental, pode não funcionar
# Apple Silicon: Metal acceleration, funciona bem
# Intel Arc: Experimental

# CPU-only: Always works but slow
```

### 6. Falta de Context Window Dinâmico
Modelos têm limite de tokens de contexto (ex: 4K, 8K, 32K). Textos maiores precisam ser truncados.

```python
# Problema: tentar resumir documento com 20K tokens
# Modelo Mistral tem 32K context, OK
# Mas economizar: Phi 3 tem apenas 4K

# Solução: dividir em chunks
def summarize_long_text(text, max_chunk=4000):
    chunks = [text[i:i+max_chunk] for i in range(0, len(text), max_chunk)]
    summaries = [ollama.chat(..., f"Resuma: {chunk}") for chunk in chunks]
    return ollama.chat(..., f"Resuma esses resumos: {summaries}")
```

## Conexões

[[entender-arquitetura-agents-ia|Como entender e construir agents IA com Claude]]
[[langchain-python-automacao|LangChain: Automação de workflows com Python e LLMs]]
[[privacidade-dados-ia-local|Privacidade e segurança em IA local vs. cloud APIs]]

## Historico

- 2026-04-11: Nota criada com guia prático (Ollama, vLLM, hardware requirements, armadilhas reais)
- Fontes: Ollama official docs, DEV Community, Medium (2026 guides), GitHub (community setups)
