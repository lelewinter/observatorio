---
tags: []
source: https://x.com/i/status/2039749628737019925
date: 2026-04-03
tipo: aplicacao
---
# Inspecionar e Intervir em Representacoes Emocionais Internas do Claude via Steering

## O que e

A Anthropic publicou pesquisa identificando que modelos como o Claude possuem representacoes internas de conceitos emocionais — estruturas vetoriais no espaço de ativacoes que funcionam como análogos computacionais de estados afetivos (valência positiva/negativa, excitação, etc.) e que influenciam comportamento de forma mensurável. Isso importa na prática porque abre caminho para **interpretabilidade mecanística aplicada**: em vez de tratar o modelo como caixa preta, você pode mapear, medir e até modificar esses estados internos usando técnicas de activation steering e probing. Para quem constrói sistemas com LLMs em producao, isso significa novas ferramentas para diagnosticar comportamentos inesperados, ajustar tom de resposta sem fine-tuning, e compreender quando o modelo está operando em regimes afetivos que degradam a qualidade da saída.

## Como implementar

**1. Entenda a arquitetura do problema antes de codar**

O ponto de partida é a hipótese de que estados emocionais no modelo existem como direções no espaço residual de ativacoes — vetores que, quando ativados com alta magnitude, correlacionam com comportamentos associados a emoções específicas. A pesquisa da Anthropic usa análise de componentes principais (PCA), probes lineares e causal interventions para demonstrar isso. Na prática, você vai precisar de acesso às ativacoes intermediárias do modelo, o que restringe o trabalho a modelos open-source (GPT-style com pesos acessíveis) ou às APIs com endpoints experimentais de ativacão que algumas organizacoes estão comecarando a expor.

**2. Setup do ambiente com TransformerLens ou nnsight**

Para modelos open-source (Llama 3, Mistral, Gemma), a biblioteca mais consolidada para este tipo de trabalho é o **TransformerLens** (desenvolvido pela Neel Nanda / EleutherAI). Instale via:

```bash
pip install transformer_lens
pip install nnsight  # alternativa mais flexivel para modelos HuggingFace
```

Com TransformerLens, carregue um modelo e capture o stream residual:

```python
import transformer_lens
model = transformer_lens.HookedTransformer.from_pretrained("mistral-7b")

# Captura ativacoes da camada 16 (residual stream pos-MLP)
logits, cache = model.run_with_cache(prompt_tokens)
residual_stream = cache["resid_post", 16]  # shape: [batch, seq, d_model]
```

Escolha camadas intermediárias (entre 40-70% da profundidade total do modelo) — a pesquisa de interpretabilidade consistentemente mostra que representacoes semânticas de alto nível emergem nessa faixa.

**3. Construir um dataset de contraste para isolar o conceito emocional**

Para extrair a "direção de valência positiva", por exemplo, você precisa de pares contrastivos: prompts que induzem o modelo a estados positivos vs. negativos, capturando as ativacoes de ambos. Construa um dataset mínimo de ~200-500 pares:

```python
positive_prompts = [
    "Acabei de conseguir meu emprego dos sonhos!",
    "Meu filho deu os primeiros passos hoje.",
    # ...
]
negative_prompts = [
    "Acabei de perder meu emprego inesperadamente.",
    "Recebi um diagnóstico preocupante hoje.",
    # ...
]
```

Capture ativacoes para cada conjunto, calcule a diferenca de média entre os dois grupos no espaço residual, e normalize — isso gera o **vetor de direção** do conceito emocional. Tecnicamente:

```python
import torch
import numpy as np

pos_acts = torch.stack([get_residual(p, layer=16) for p in positive_prompts])
neg_acts = torch.stack([get_residual(p, layer=16) for p in negative_prompts])

direction = (pos_acts.mean(0) - neg_acts.mean(0))
direction = direction / direction.norm()  # normaliza para unit vector
```

**4. Treinar um probe linear para validar a representacao**

Antes de fazer qualquer intervencao, valide que a direcao capturada é de fato preditiva do comportamento. Treine um classificador linear (logistic regression) sobre as ativacoes para prever a classe emocional:

```python
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import cross_val_score

X = np.vstack([pos_acts.numpy(), neg_acts.numpy()])
y = np.array([1]*len(positive_prompts) + [0]*len(negative_prompts))

probe = LogisticRegression()
scores = cross_val_score(probe, X, y, cv=5)
print(f"Probe accuracy: {scores.mean():.3f}")  # >0.85 e um bom sinal
```

Accuracy acima de 80-85% com probe linear sugere que a representacao é genuinamente linear e localmente separável — condição necessária para que steering funcione de forma previsível.

**5. Activation Steering: intervir causalmente no estado emocional**

Com a direcao validada, você pode **injetar** ou **suprimir** o conceito durante a forward pass. No TransformerLens isso é feito via hooks:

```python
def steering_hook(value, hook, direction, alpha=15.0):
    # Adiciona alpha * direction ao residual stream em cada posicao
    value[:, :, :] += alpha * direction.to(value.device)
    return value

# Rodando o modelo com steering ativo
with model.hooks(fwd_hooks=[
    (f"blocks.16.hook_resid_post",
     lambda v, h: steering_hook(v, h, direction, alpha=20.0))
]):
    steered_output = model.generate(prompt_tokens, max_new_tokens=100)
```

Varie o valor de `alpha` sistematicamente: valores pequenos (5-10) produzem mudancas sutis de tom; valores grandes (30+) frequentemente causam incoerência ou saídas degeneradas. Documente a curva de comportamento vs. alpha — ela raramente é linear.

**6. Medir efeito comportamental de forma quantitativa**

Nao confie apenas na leitura qualitativa das saídas. Use métricas automáticas:
- **Sentiment scoring** das saídas com um modelo externo (ex: `cardiffnlp/twitter-roberta-base-sentiment`)
- **Embedding similarity** entre saídas steered e exemplos de referência do estado alvo
- **Fluência e perplexidade** para detectar degradacao da coerência

Isso permite construir uma curva de Pareto: quanto de mudanca afetiva você consegue sem custo de qualidade.

**7. Aplicar o framework em pipeline de producao (uso prático real)**

Em sistemas de producao onde você nao tem acesso à forward pass (usando APIs como Claude ou GPT-4), a abordagem muda: você opera no nível de **prompt engineering baseado em conhecimento mecanístico**. Saber que o modelo possui representacoes emocionais internas informa que:
- Descrever o contexto emocional do usuário no system prompt ativa essas representacoes e modifica o comportamento de forma mais robusta que instruções imperativas ("seja empático")
- Usar exemplos contrastivos no few-shot (ex: mostrar resposta inadequada seguida de resposta com tom correto) aciona mecanismos de comparacao que usam essas direcoes internamente
- Monitorar tokens de alta surpresa (perplexidade local elevada) nas saídas pode servir como proxy para detectar quando o modelo entrou em regime emocional atípico

## Stack e requisitos

- **Linguagem**: Python 3.10+
- **Bibliotecas principais**:
  - `transformer_lens >= 1.19.0` (interpretabilidade, hooking)
  - `nnsight >= 0.3` (alternativa para modelos HuggingFace nativos)
  - `torch >= 2.1` com CUDA 12.x
  - `scikit-learn >= 1.3` (probes lineares)
  - `numpy`, `pandas`, `matplotlib` (análise e visualizacao)
  - `transformers >= 4.40` (carregar modelos)
- **Modelos recomendados para início**:
  - Gemma-2-2B (menor, roda em 8GB VRAM) — bom para prototipagem rápida
  - Mistral-7B-Instruct (16GB VRAM) — melhor balanco para pesquisa
  - Llama-3-8B (16GB VRAM) — representacoes mais estáveis e pesquisadas
- **Hardware mínimo**: GPU com 8GB VRAM para modelos 2-3B; 16-24GB para 7-8B
- **Hardware recomendado**: RTX 3090/4090 (24GB) ou A100 40GB para experimentacao sem restricao de batch
- **Custo de API (se usando Claude como referência)**: experimentos de steering nao são possíveis via API Claude atual — você replica o *framework conceitual* em modelos open-source e transfere insights para prompt design no Claude
- **Tempo estimado de setup**: 2-4 horas para ambiente funcional com primeiro