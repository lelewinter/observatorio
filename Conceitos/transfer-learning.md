---
tags: [conceito, machine-learning, deep-learning, reutilizacao]
date: 2026-04-02
tipo: conceito
aliases: [Transfer Learning, Fine-tuning]
---

# Transfer Learning: Reutilizar Modelos Treinados

## O que é

Transfer learning é usar um modelo pré-treinado em tarefa A como ponto de partida para tarefa B, requer muito menos dados e computação do que treinar do zero.

Estratégias:
- **Feature extraction**: Congelar pesos, treinar apenas últimas camadas
- **Fine-tuning**: Descongelar últimas camadas, ajustar pesos com learning rate baixo
- **Domain adaptation**: Adaptar modelo de domínio similar

## Como funciona

```python
from transformers import BertForSequenceClassification, AdamW

# Modelo pré-treinado (já aprendeu linguagem)
model = BertForSequenceClassification.from_pretrained('bert-base-uncased',
                                                      num_labels=2)

# Seu dataset (classificação de sentimento)
# ~500 exemplos (vs 1 milhão sem transfer learning)
train_loader = get_dataloader("sentiment_data.csv")

# Fine-tune: learning rate baixo para não destruir pesos aprendidos
optimizer = AdamW(model.parameters(), lr=2e-5)

for epoch in range(3):  # Apenas 3 épocas necessárias
    for batch in train_loader:
        outputs = model(**batch)
        loss = outputs.loss
        loss.backward()
        optimizer.step()
        optimizer.zero_grad()
```

## Para que serve

- **Dados limitados**: Seu dataset é pequeno (< 10k exemplos). Sem transfer learning, overfitting é garantido.
- **Computação limitada**: Treinar BERT do zero = 72 TPUs por 4 dias. Fine-tune = 1 GPU por 2 horas.
- **Padrões universais**: Detecção de bordas, features semânticas são reutilizáveis entre domínios.

Exemplo prático:
- Treinar detector de objetos em ImageNet (1M imagens) → usar para detectar defeitos em manufatura (500 imagens)
- Treinar LLM em internet inteira → fine-tune para seu domínio específico

## Exemplo prático

**Vision:**
```python
from torchvision import models

# ResNet50 pré-treinado em ImageNet
model = models.resnet50(pretrained=True)

# Congelar todos os pesos
for param in model.parameters():
    param.requires_grad = False

# Descongelar apenas última camada
model.fc.requires_grad = True

# Treinar apenas fc (fully connected) no seu dataset
optimizer = torch.optim.Adam(model.fc.parameters(), lr=0.001)
```

**NLP:**
```python
# GPT-2 pré-treinado
model = GPT2LMHeadModel.from_pretrained('gpt2')

# Fine-tune em seu corpus (ex: posts técnicos)
# Apenas 3 épocas em dados seu próprio
```

## Aparece em

- [[16_github_repos_melhor_curso_ml]] - Técnica fundamental em ML
- [[leitor-de-ebooks-com-busca-semantica]] - Embeddings pré-treinados
- [[spec-driven-ai-coding]] - LLMs usam transfer learning

---
*Conceito extraído em 2026-04-02*
