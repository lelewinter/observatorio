---
tags: [llm, treinamento, deep-learning, sebastian-raschka, mestrado, hands-on, transformers, pytorch]
source: https://www.linkedin.com/feed/update/urn:li:activity:7324180712985624578/ | https://www.manning.com/books/build-a-large-language-model-from-scratch | https://github.com/rasbt/LLMs-from-scratch
date: 2026-03-28
tipo: aplicacao
autor: "Victor Hugo Germano"
---

# Build LLM from Scratch: Projeto Mestrado com Sebastian Raschka (2026)

## O que é

"Build a Large Language Model (From Scratch)" é um livro prático publicado pela Manning em 2024 que estrutura a implementação de um LLM funcional semelhante ao GPT-2 em um projeto de 2-3 semanas. O diferencial é que o autor, Sebastian Raschka (Staff Research Engineer na Lightning AI), decompõe a construção em camadas incrementais — começando com tokenização e embeddings, progredindo para arquitetura transformer completa, até fine-tuning e instruction-following. Não usa bibliotecas pré-prontas de LLM; você escreve PyTorch puro, validando cada componente.

A obra é complementada pela série visual "Essence of Linear Algebra" e "Neural Networks" do 3Blue1Brown, que fornece intuição geométrica dos cálculos envolvidos. Essa combinação — código + visualização — torna compreensão profunda acessível a qualquer desenvolvedor com Python intermediário.

## Por que importa agora

Em 2026, o custo de acesso a LLMs via API continua crescente (tokens, contexto expandido, modelos mais pesados). Compreender LLMs "de dentro" permite três coisas práticas:

1. **Fine-tuning inteligente**: Você não justa cega modelos via prompt engineering; entende quais camadas congelam, qual learning rate funciona, por que batch size importa.
2. **Deploy local viável**: Modelos pequenos (100M-1B parâmetros) rodando local em GPU pessoal ou em VPS barato (~3 EUR/mês Oracle free tier) substituem custos recorrentes de API.
3. **Debugging de comportamento**: Quando um modelo produz output estranho, você consegue navegar até a camada que causou (atenção, embedding, normalization) em vez de lidar como "black box".

Leticia estuda à noite e fins de semana; este projeto encaixa numa sessão de 2 semanas, 1-2h/dia, com validação hands-on a cada etapa.

## Como implementar

### Pré-requisitos

- Python 3.9+
- Álgebra linear básica (multiplicação de matrizes, produto escalar, operações vetoriais)
- Conceitos de redes neurais (forward pass, gradientes, backprop em nível conceitual)
- Google Colab ou GPU local (recomendado, mas CPU funciona)

### Fluxo recomendado (14 dias)

**Dias 1-2: Tokenização & Embeddings**

```python
# Tokenização básica (BPE - Byte Pair Encoding)
import re
from collections import defaultdict

class SimpleTokenizer:
    def __init__(self, vocab_size=256):
        self.vocab = {i: bytes([i]) for i in range(256)}
        self.merges = {}
        
    def get_stats(self, ids):
        counts = defaultdict(int)
        for pair in zip(ids, ids[1:]):
            counts[pair] += 1
        return counts
    
    def merge(self, ids, pair, idx):
        newids = []
        i = 0
        while i < len(ids):
            if i < len(ids) - 1 and (ids[i], ids[i+1]) == pair:
                newids.append(idx)
                i += 2
            else:
                newids.append(ids[i])
                i += 1
        return newids
    
    def train(self, text, num_merges):
        ids = list(text.encode('utf-8'))
        for i in range(num_merges):
            stats = self.get_stats(ids)
            pair = max(stats, key=stats.get)
            idx = 256 + i
            ids = self.merge(ids, pair, idx)
            self.merges[pair] = idx

# Embedding: mapeamento token → vetor denso
import torch
import torch.nn as nn

embedding = nn.Embedding(num_embeddings=50257, embedding_dim=768)
token_id = torch.tensor([2])
embedded = embedding(token_id)  # shape: (1, 768)
```

**Dias 3-5: Arquitetura Transformer (Self-Attention)**

```python
class MultiHeadAttention(nn.Module):
    def __init__(self, d_model, num_heads):
        super().__init__()
        self.d_model = d_model
        self.num_heads = num_heads
        self.d_k = d_model // num_heads
        
        self.W_q = nn.Linear(d_model, d_model)
        self.W_k = nn.Linear(d_model, d_model)
        self.W_v = nn.Linear(d_model, d_model)
        self.W_o = nn.Linear(d_model, d_model)
    
    def forward(self, x, mask=None):
        batch_size = x.shape[0]
        
        # Linear transformations
        Q = self.W_q(x)  # (batch, seq_len, d_model)
        K = self.W_k(x)
        V = self.W_v(x)
        
        # Reshape para múltiplos heads
        Q = Q.view(batch_size, -1, self.num_heads, self.d_k).transpose(1, 2)
        K = K.view(batch_size, -1, self.num_heads, self.d_k).transpose(1, 2)
        V = V.view(batch_size, -1, self.num_heads, self.d_k).transpose(1, 2)
        
        # Scaled dot-product attention
        scores = torch.matmul(Q, K.transpose(-2, -1)) / torch.sqrt(torch.tensor(self.d_k))
        if mask is not None:
            scores = scores.masked_fill(mask == 0, float('-inf'))
        
        attention_weights = torch.softmax(scores, dim=-1)
        output = torch.matmul(attention_weights, V)
        
        # Concatenate heads
        output = output.transpose(1, 2).contiguous()
        output = output.view(batch_size, -1, self.d_model)
        return self.W_o(output)

# Transformer Block completo
class TransformerBlock(nn.Module):
    def __init__(self, d_model, num_heads, d_ff):
        super().__init__()
        self.attention = MultiHeadAttention(d_model, num_heads)
        self.feed_forward = nn.Sequential(
            nn.Linear(d_model, d_ff),
            nn.ReLU(),
            nn.Linear(d_ff, d_model)
        )
        self.norm1 = nn.LayerNorm(d_model)
        self.norm2 = nn.LayerNorm(d_model)
    
    def forward(self, x, mask=None):
        # Residual + attention
        attn_out = self.attention(x, mask)
        x = self.norm1(x + attn_out)
        
        # Residual + feed-forward
        ff_out = self.feed_forward(x)
        x = self.norm2(x + ff_out)
        return x
```

**Dias 6-10: Treinamento End-to-End**

```python
class GPT2Mini(nn.Module):
    def __init__(self, vocab_size=50257, d_model=768, num_heads=12, num_layers=12, d_ff=3072, max_seq_len=1024):
        super().__init__()
        self.embedding = nn.Embedding(vocab_size, d_model)
        self.positional_encoding = nn.Embedding(max_seq_len, d_model)
        
        self.transformer_blocks = nn.ModuleList([
            TransformerBlock(d_model, num_heads, d_ff) 
            for _ in range(num_layers)
        ])
        
        self.ln_final = nn.LayerNorm(d_model)
        self.lm_head = nn.Linear(d_model, vocab_size)
    
    def forward(self, input_ids, attention_mask=None):
        seq_len = input_ids.shape[1]
        
        # Embeddings + positional encoding
        x = self.embedding(input_ids)
        pos_ids = torch.arange(seq_len, device=input_ids.device).unsqueeze(0)
        x = x + self.positional_encoding(pos_ids)
        
        # Passar por transformer blocks
        for block in self.transformer_blocks:
            x = block(x, attention_mask)
        
        # Output layer
        x = self.ln_final(x)
        logits = self.lm_head(x)
        return logits

# Treinamento
model = GPT2Mini()
optimizer = torch.optim.AdamW(model.parameters(), lr=5e-5)
criterion = nn.CrossEntropyLoss()

for epoch in range(3):
    for batch in dataloader:
        input_ids = batch['input_ids']
        targets = batch['input_ids'].clone()
        
        logits = model(input_ids)
        loss = criterion(logits.view(-1, 50257), targets.view(-1))
        
        optimizer.zero_grad()
        loss.backward()
        torch.nn.utils.clip_grad_norm_(model.parameters(), 1.0)
        optimizer.step()
        
        print(f"Loss: {loss.item():.4f}")
```

**Dias 11-14: Fine-tuning & Inference**

Para fine-tuning em domínio específico (ex: textos médicos, código), o livro cobre:

1. **LoRA (Low-Rank Adaptation)**: Treinar apenas 0.1% dos parâmetros via matrizes de baixo rank, reduzindo VRAM de 8GB para ~2GB.
2. **Instruction-following**: Format dados como `<|user|> pergunta <|assistant|> resposta`, validando que o modelo apre captura intent.
3. **Evaluation**: Métricas (perplexidade, BLEU) + validação manual em holdout set.

```python
# LoRA injection (simplificado)
class LoRALinear(nn.Module):
    def __init__(self, linear_layer, r=8):
        super().__init__()
        self.linear = linear_layer
        self.r = r
        
        # Congelar pesos originais
        self.linear.weight.requires_grad = False
        
        # Matrizes de baixo rank
        self.lora_a = nn.Linear(linear_layer.in_features, r)
        self.lora_b = nn.Linear(r, linear_layer.out_features)
    
    def forward(self, x):
        return self.linear(x) + self.lora_b(self.lora_a(x))

# Aplicar LoRA ao modelo
for name, module in model.named_modules():
    if isinstance(module, nn.Linear) and 'attention' in name:
        # Substituir por LoRA
        setattr(model, name.split('.')[-1], LoRALinear(module, r=8))
```

### Recursos principais

- **Repositório oficial**: https://github.com/rasbt/LLMs-from-scratch
  - Código completo capítulo a capítulo
  - Datasets (Shakespeare, Wikipedia snippets)
  - Jupyter notebooks com visualizações

- **Google Colab T4 GPU**: Executa treinamento de 40MB Shakespeare em ~1h, acesso gratuito.
- **Documentação PyTorch**: Referência de nn.Module, autograd, distributed training.

## Stack e requisitos

### Hardware

- **Mínimo CPU**: Funciona, mas ~20x mais lento que GPU. Viável apenas para entender conceitos com datasets minúsculos (<1M tokens).
- **GPU recomendada**: NVIDIA T4 (Colab gratuito, 15h/dia) ou RTX 3060 local (~30min para treinar 40MB em Shakespeare).
- **VRAM**: 4-6GB para modelo 12-layer 768-dim (padrão do livro); 8GB+ para Large.

### Software

```bash
pip install torch torchvision torchaudio  # PyTorch 2.0+
pip install numpy scipy scikit-learn      # Utilitários
pip install jupyter matplotlib seaborn    # Visualização
pip install transformers datasets         # HuggingFace (opcional, para comparar)
pip install tensorboard                   # Monitorar treinamento
pip install wandb                         # Tracking (opcional)
```

### Dados

- **Shakespeare** (~1.1MB, 400k tokens): Treinar LLM para gerar prosa estilo Shakespeare.
- **TinyStories** (2GB): Dataset mais realista, histórias infantis com boa generalização.
- **OpenWebText** (~40GB): Escala realista; exige mais poder computacional.

## Armadilhas e limitações

### Técnicas

1. **Não pule capítulos**: Cada etapa constrói sobre a anterior. Se pular tokenização, não vai entender por que embeddings importam.

2. **Learning rate muito alto**: GPT-2 treina em ~1e-4 a 5e-5. Começar em 1e-3 causa divergência (loss → NaN). Use warmup: `lr = min(step / warmup_steps, 1.0) * max_lr`.

3. **Overfitting em datasets pequenos**: Shakespeare tem ~40MB (~400k tokens). Após ~10 épocas, training loss cai mas validation loss sobe. Normal; use early stopping em validation.

4. **Batch size vs memória**: Aumentar batch de 32 para 64 reduz noise no gradient mas duplica VRAM. Em Colab T4 com 15GB, máximo é ~64 com seq_len=1024.

5. **Atenção é O(n²) em memória**: seq_len=1024 gera attention maps de 1024×1024 por head. Com 12 heads, isso é ~96MB só para attention. Flash Attention reduz em 2-4x.

### Práticas

6. **Checkpointing**: Colab desconecta a cada 12h. Salve checkpoints a cada epoch para Google Drive:
```python
torch.save({
    'epoch': epoch,
    'model_state': model.state_dict(),
    'optimizer_state': optimizer.state_dict(),
    'loss': loss
}, f'/content/drive/MyDrive/checkpoint_epoch_{epoch}.pt')
```

7. **Validação isolada**: Use holdout set (10-20% dos dados), nunca treinar nele. Perplexidade em validation > training é esperado.

8. **Não compare com GPT-4**: Seu modelo treinado em 40MB é ~infinitamente menor que GPT-4 (1.7T tokens). Expectativa realista: gera prosa coerente por 1-2 sentenças, não papers.

### Conceituais

9. **"Entender profundamente" leva reler**: Primeira passada é scanning para familiaridade. Reler capítulos 1-2 após terminar capítulo 6-7 torna coisas claras que pareciam mágicas antes.

10. **Temperature em geração**: Temperatura=0 (argmax) gera texto determinístico mas repetitivo. Temperatura=0.7-1.0 amostrado gera variabilidade. Não é "melhor ou pior", é trade-off criatividade vs coherência.

## Conexões

- [[embeddings-multimodais-em-espaco-vetorial-unificado|Embeddings em espaço vetorial unificado]] — por que ativar embeddings é primeiro passo
- [[fine-tuning-de-llms-sem-codigo|Fine-tuning prático de LLMs]] — adaptação rápida após compreensão de base
- [[attention-is-all-you-need|Transformer: Attention Is All You Need]] — paper original, leitura após implementar
- [[aprendizado-acelerado-com-ia|Aprendizado acelerado com IA]] — usar o próprio LLM para debugar entendimento

## Histórico

- 2026-03-28: Referência original (Victor Hugo Germano)
- 2026-04-02: Reescrita pelo pipeline
- 2026-04-11: Expansão profunda com code examples, stack detalhado, armadilhas técnicas
