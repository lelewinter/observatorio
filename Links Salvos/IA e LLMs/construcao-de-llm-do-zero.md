---
tags: [llm, transformers, pytorch, fine-tuning, deep-learning, educacao]
source: https://x.com/Sumanth_077/status/2039332313910383043?s=20
date: 2026-04-02
tipo: aplicacao
atualizado: 2026-04-11
---

# Construir LLM do Zero: Transformers até Fine-Tuning em 7 Etapas

## O que é

Pipeline estruturado que leva você de conceitos teóricos de redes neurais até um modelo funcionalmente pré-treinado e fine-tuned. Diferente de usar HuggingFace como caixa preta, você implementa cada componente (embeddings, atenção, feedforward) em PyTorch puro, compreendendo isoladamente antes da integração. O projeto segue o livro "Build a Large Language Model (From Scratch)" de Sebastian Raschka, que implementa um ChatGPT-like em menos de 300 linhas de Python com arquitetura decimal e treinável em GPU consumer.

A jornada começa no "absolute zero" — você escreve tokenizadores, matrizes de embedding, mecanismo de atenção scaled dot-product, e blocos transformer decoder-only. Cada etapa é debugável, visualizável, e transferível para modelos maiores. Isso contrasta com copiar código de tutorials: você entende *por que* gradient descent funciona em redes profundas, *por que* layer normalization previne divergência, *como* fine-tuning reutiliza conhecimento pré-treinado.

## Como implementar

### Etapas 1-2: Fundamentos (Tokenização + Embeddings)
Comece tokenizando texto. Em vez de usar bibliotecas prontas, implemente um tokenizador BPE (Byte-Pair Encoding) simples:

```python
import re
from collections import Counter

def tokenize_bpe(text, vocab_size=256):
    """Tokenização BPE minimalista."""
    # Começa com caracteres individuais
    tokens = list(text.encode('utf-8'))
    
    # Itera vocab_size vezes, merging pares mais frequentes
    for _ in range(vocab_size - 256):
        pairs = Counter(zip(tokens[:-1], tokens[1:]))
        if not pairs:
            break
        most_common = pairs.most_common(1)[0][0]
        tokens = merge_pair(tokens, most_common)
    
    return tokens

def merge_pair(tokens, pair):
    """Merge um par de tokens."""
    new_token = max(tokens) + 1
    new_tokens = []
    i = 0
    while i < len(tokens) - 1:
        if (tokens[i], tokens[i+1]) == pair:
            new_tokens.append(new_token)
            i += 2
        else:
            new_tokens.append(tokens[i])
            i += 1
    return new_tokens
```

Depois, crie embeddings learnable. Em PyTorch:

```python
import torch
import torch.nn as nn

class TokenEmbedding(nn.Module):
    def __init__(self, vocab_size, embedding_dim):
        super().__init__()
        self.embeddings = nn.Embedding(vocab_size, embedding_dim)
    
    def forward(self, token_ids):
        return self.embeddings(token_ids)  # [seq_len, embed_dim]

# Positional embeddings (crucial para capturar ordem)
class PositionalEmbedding(nn.Module):
    def __init__(self, max_seq_len, embedding_dim):
        super().__init__()
        self.pos_embeddings = nn.Embedding(max_seq_len, embedding_dim)
    
    def forward(self, seq_len):
        positions = torch.arange(seq_len)
        return self.pos_embeddings(positions)

# Combinar
embeddings = TokenEmbedding(vocab_size=1024, embedding_dim=128)
pos_embeddings = PositionalEmbedding(max_seq_len=512, embedding_dim=128)
token_ids = torch.tensor([10, 25, 100])
x = embeddings(token_ids) + pos_embeddings(len(token_ids))  # [3, 128]
```

### Etapa 3: Mecanismo de Atenção (Scaled Dot-Product)
Aqui está o coração. Atenção computa relações entre tokens:

```python
import torch.nn.functional as F

class ScaledDotProductAttention(nn.Module):
    def __init__(self, embed_dim, num_heads=4):
        super().__init__()
        self.embed_dim = embed_dim
        self.num_heads = num_heads
        self.head_dim = embed_dim // num_heads
        
        assert embed_dim % num_heads == 0, "embed_dim must be divisible by num_heads"
        
        self.W_q = nn.Linear(embed_dim, embed_dim)
        self.W_k = nn.Linear(embed_dim, embed_dim)
        self.W_v = nn.Linear(embed_dim, embed_dim)
        self.W_o = nn.Linear(embed_dim, embed_dim)
    
    def forward(self, query, key, value, mask=None):
        batch_size = query.shape[0]
        
        # Linear projections
        Q = self.W_q(query)  # [batch, seq_len, embed_dim]
        K = self.W_k(key)
        V = self.W_v(value)
        
        # Reshape para multi-head
        Q = Q.view(batch_size, -1, self.num_heads, self.head_dim).transpose(1, 2)
        K = K.view(batch_size, -1, self.num_heads, self.head_dim).transpose(1, 2)
        V = V.view(batch_size, -1, self.num_heads, self.head_dim).transpose(1, 2)
        
        # Scaled dot-product attention
        scores = torch.matmul(Q, K.transpose(-2, -1)) / (self.head_dim ** 0.5)
        if mask is not None:
            scores = scores.masked_fill(mask == 0, -1e9)
        attention_weights = F.softmax(scores, dim=-1)
        
        # Apply attention to values
        context = torch.matmul(attention_weights, V)  # [batch, num_heads, seq_len, head_dim]
        context = context.transpose(1, 2).contiguous().view(batch_size, -1, self.embed_dim)
        
        output = self.W_o(context)
        return output, attention_weights
```

### Etapa 4: Bloco Transformer Completo
Integra atenção + feedforward + normalização:

```python
class TransformerBlock(nn.Module):
    def __init__(self, embed_dim, num_heads, ff_dim, dropout=0.1):
        super().__init__()
        self.attention = ScaledDotProductAttention(embed_dim, num_heads)
        
        # Feedforward network
        self.ff = nn.Sequential(
            nn.Linear(embed_dim, ff_dim),
            nn.ReLU(),
            nn.Linear(ff_dim, embed_dim)
        )
        
        # Layer normalization
        self.norm1 = nn.LayerNorm(embed_dim)
        self.norm2 = nn.LayerNorm(embed_dim)
        self.dropout = nn.Dropout(dropout)
    
    def forward(self, x, mask=None):
        # Self-attention com residual connection
        attn_out, _ = self.attention(x, x, x, mask)
        x = self.norm1(x + self.dropout(attn_out))
        
        # Feedforward com residual
        ff_out = self.ff(x)
        x = self.norm2(x + self.dropout(ff_out))
        
        return x

class TransformerDecoder(nn.Module):
    def __init__(self, vocab_size, embed_dim, num_layers, num_heads, ff_dim):
        super().__init__()
        self.token_embedding = TokenEmbedding(vocab_size, embed_dim)
        self.pos_embedding = PositionalEmbedding(512, embed_dim)
        
        self.blocks = nn.ModuleList([
            TransformerBlock(embed_dim, num_heads, ff_dim) 
            for _ in range(num_layers)
        ])
        
        self.output_layer = nn.Linear(embed_dim, vocab_size)
    
    def forward(self, token_ids):
        seq_len = token_ids.shape[-1]
        x = self.token_embedding(token_ids) + self.pos_embedding(seq_len)
        
        for block in self.blocks:
            x = block(x)
        
        logits = self.output_layer(x)  # [batch, seq_len, vocab_size]
        return logits
```

### Etapa 5: Pré-Treinamento (Language Modeling)
Treina o modelo a prever o próximo token:

```python
class LanguageModelTrainer:
    def __init__(self, model, learning_rate=1e-3, device='cuda'):
        self.model = model.to(device)
        self.optimizer = torch.optim.Adam(model.parameters(), lr=learning_rate)
        self.loss_fn = nn.CrossEntropyLoss()
        self.device = device
    
    def train_step(self, input_ids, target_ids):
        self.model.train()
        self.optimizer.zero_grad()
        
        logits = self.model(input_ids.to(self.device))
        loss = self.loss_fn(
            logits.view(-1, logits.size(-1)),
            target_ids.view(-1).to(self.device)
        )
        
        loss.backward()
        torch.nn.utils.clip_grad_norm_(self.model.parameters(), max_norm=1.0)
        self.optimizer.step()
        
        return loss.item()
    
    def train_epoch(self, dataloader, num_epochs=3):
        for epoch in range(num_epochs):
            total_loss = 0
            for batch_idx, (input_ids, target_ids) in enumerate(dataloader):
                loss = self.train_step(input_ids, target_ids)
                total_loss += loss
                
                if batch_idx % 10 == 0:
                    print(f"Epoch {epoch}, Batch {batch_idx}, Loss: {loss:.4f}")
            
            avg_loss = total_loss / len(dataloader)
            print(f"Epoch {epoch} completed. Avg Loss: {avg_loss:.4f}")

# Uso
model = TransformerDecoder(vocab_size=1024, embed_dim=128, num_layers=4, num_heads=4, ff_dim=512)
trainer = LanguageModelTrainer(model)

# Supondo que você tem um DataLoader
# trainer.train_epoch(train_dataloader, num_epochs=3)
```

### Etapa 6-7: Fine-Tuning (Instruction Following)
Adapta modelo pré-treinado para seguir instruções:

```python
class InstructionFineTuner:
    def __init__(self, pretrained_model, learning_rate=1e-4):
        self.model = pretrained_model  # Reutiliza pré-treino
        # Congela camadas early layers (reutiliza features)
        for param in list(self.model.parameters())[:-2]:
            param.requires_grad = False
        
        self.optimizer = torch.optim.Adam(
            filter(lambda p: p.requires_grad, self.model.parameters()),
            lr=learning_rate  # Learning rate 5-10x menor
        )
        self.loss_fn = nn.CrossEntropyLoss()
    
    def finetune_step(self, instruction_tokens, response_tokens):
        self.model.train()
        self.optimizer.zero_grad()
        
        # Input: instrução + prompt do modelo
        # Target: resposta desejada
        combined_ids = torch.cat([instruction_tokens, response_tokens], dim=1)
        
        logits = self.model(combined_ids)
        
        # Aplica loss apenas na parte de resposta (label smoothing ajuda)
        loss = self.loss_fn(logits[:, -len(response_tokens):].reshape(-1, logits.size(-1)),
                           response_tokens.reshape(-1))
        
        loss.backward()
        self.optimizer.step()
        
        return loss.item()

# Demonstração de economia de dados: 
# Pré-treino: ~1M tokens para treino
# Fine-tuning: ~10k tokens suficientes para transferência efetiva
```

## Stack e requisitos

**Mínimo viável:**
- Python 3.10+
- PyTorch 2.1+ (`pip install torch torchvision`)
- GPU com 4GB+ VRAM (RTX 3050, RTX 4050, M1 Pro/Max)
- Jupyter/VSCode para iteração

**Produção (opcional):**
- Wandb para logging (`pip install wandb`)
- Einops para operações de tensor (`pip install einops`)
- Flash Attention para speedup (`pip install flash-attn`)
- Transformers HuggingFace para comparação (`pip install transformers`)

**Datasets recomendados:**
- TinyStories (200MB, perfeito para começar)
- Wikipedia dump (primeiros 100M tokens)
- OpenWebText (1.2TB, mais realista)
- ORCA (SFT dataset, bom para instruction following)

**Tempo de execução:**
- Pré-treino (6 camadas, 128 hidden, 4 heads, 100k tokens): ~30min em RTX 3060
- Fine-tuning (5k instruction pairs): ~5-10min
- Inferência (geração de 100 tokens): <1s

## Armadilhas e limitações

**Gradient Explosion/Vanishing:**
Redes profundas sofrem com gradientes instáveis. Use sempre:
- Layer normalization antes de cada bloco
- Gradient clipping (`torch.nn.utils.clip_grad_norm_(model.parameters(), 1.0)`)
- Learning rate warmup (cresce de 0 até target em primeiros 10% do treino)

```python
# Warmup scheduler
def get_warmup_schedule(optimizer, warmup_steps, total_steps):
    def lr_lambda(step):
        if step < warmup_steps:
            return step / warmup_steps
        return max(0, (total_steps - step) / (total_steps - warmup_steps))
    return torch.optim.lr_scheduler.LambdaLR(optimizer, lr_lambda)
```

**Overfitting em pré-treino pequeno:**
Com datasets <1M tokens, loss de validação cresce enquanto training loss cai. Mitigação:
- Use early stopping (parar quando val loss plateua por 3 epochs)
- Dropout 0.1-0.2 em feedforward layers
- Não deixe modelo treinar indefinidamente

**Dimensionalidade em Multi-Head Attention:**
Comum: 768 hidden dims com 12 heads = 64 dims por head. Se não divida evenly, código quebra. Sempre use:
```python
assert embed_dim % num_heads == 0
head_dim = embed_dim // num_heads
```

**Fine-tuning apaga conhecimento:**
Learning rate muito alta (~1e-3) faz modelo "esquecer" tudo que aprendeu. Use:
- Learning rate 1e-4 ou 5e-5 para fine-tuning
- Freeze early layers (manter features pré-treinadas)
- LoRA (Low-Rank Adaptation) para máxima eficiência: treina só matrizes (d x r) em vez de toda camada

**Escala não é trivial:**
Aumentar modelo de 6 para 12 camadas multiplica memória e tempo. Planeje:
- 6 camadas, 128 hidden: ~2GB VRAM
- 12 camadas, 256 hidden: ~8GB VRAM
- 24 camadas, 768 hidden: ~40GB VRAM (precisa A100)

## Conexões

- [[fine-tuning-de-llms-sem-codigo|Fine-tuning sem código]] — quando não quer codificar do zero
- [[construir-llm-do-zero-projeto-mestrado-sebastian-raschka|Livro Sebastian Raschka LLM]] — referência principal
- [[geracao-automatizada-de-prompts|Prompts estruturados]] — como usar modelo após treino
- [[mecanismo-de-atencao-multi-cabeca|Attention is All You Need]] — paper teórico
- [[democratizacao-de-modelos-de-ia|IA local e descentralizada]] — rodar modelo em casa

## Histórico

- 2026-04-02: Nota criada com estrutura básica
- 2026-04-11: Reescrita com código PyTorch completo, exemplos de tokenização, embeddings, atenção multi-head, blocos transformer, loops de treino e fine-tuning. Adicionadas armadilhas práticas (gradient clipping, layer norm, warmup, learning rate schedule).
