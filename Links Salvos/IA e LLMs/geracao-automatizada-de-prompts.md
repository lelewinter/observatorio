---
tags: [prompting, dspy, optimization, llms, automation]
source: https://x.com/hasantoxr/status/2037512068015026197?s=20
date: 2026-04-02
tipo: aplicacao
---
# Geração Automatizada de Prompts: IA Otimiza Prompts para Diferentes Sistemas

## O que é

Ao invés de você iterar manualmente um prompt 20 vezes ("mais detalhado", "menos fluff", "use estrutura de 3 partes"), uma ferramenta de otimização de prompts **gera automaticamente o prompt ideal** para um modelo-alvo específico. A entrada é: intenção em linguagem natural ("quero gerar imagem de cidade futurista com neon"). A saída é: prompt otimizado e pronto para copiar-colar ou executar via API, calibrado para idiossincrasias daquele modelo.

Esse campo evoluiu em 2026:
- **DSPy** (Stanford) inverte o paradigma de "prompting" para "programação" de LLMs — você define tarefas em alto nível (classifier, Q&A, summarization) e o framework otimiza prompts + weights automaticamente
- **MIPROv2** (multi-step prompt optimization) coleta exemplos de input/output, propõe melhorias de instrução, e testa em lote contra exemplos para encontrar prompt ideal
- **Meta-prompting** instrui o modelo a criticar e refinar suas próprias instruções, criando loops de feedback automatizados

## Como Implementar

### Abordagem Manual: DSPy Framework

DSPy substitui a ideia de "escrever prompts" por "compilar programas LLM". Você define um módulo de tarefa, fornece exemplos de entrada/saída esperada, e o framework otimiza o prompt automaticamente.

```python
# Antes (manual prompting)
prompt = """
Classifique a sentença abaixo como positiva ou negativa.
Sentença: {sentence}
Resposta (apenas "positivo" ou "negativo"):
"""
response = openai.ChatCompletion.create(
  model="gpt-4",
  messages=[{"role": "user", "content": prompt.format(sentence=text)}]
)

# Depois (DSPy)
import dspy

class Sentiment(dspy.Signature):
    """Classify text sentiment."""
    sentence = dspy.InputField(desc="Sentence to classify")
    label = dspy.OutputField(desc="'positive' or 'negative'")

class SentimentClassifier(dspy.ChainOfThought):
    def forward(self, sentence):
        return dspy.ChainOfThought(Sentiment)(sentence=sentence)

# Compile with examples (automatic prompt optimization)
dspy.settings.configure(lm=dspy.OpenAI(model="gpt-4"))

classifier = SentimentClassifier()
optimizer = dspy.MIPROv2(
    metric=accuracy,  # How to measure quality
    num_examples=5    # Use 5 examples to optimize
)
optimized = optimizer.compile(classifier, trainset=examples)

# Result: DSPy has auto-generated optimal prompt + few-shot examples
result = optimized(sentence="This product is amazing!")
```

**O que acontece internamente**:
1. DSPy toma a `Signature` (definição de tarefa)
2. Coleta outputs para exemplos em `trainset`
3. Gera 5-10 variações de prompt (diferentes wordings, estruturas)
4. Testa cada variação contra os 5 exemplos, calcula score
5. Mantém a variação com melhor score
6. Resultado: prompt otimizado + few-shot examples = ~25-40% improvement vs manual

### Meta-Prompting: Loop de Autocrítica

O modelo critica sua própria instrução e itera.

```python
import anthropic

def meta_prompt_optimization(initial_prompt: str, task: str, examples: list) -> str:
    """
    Use Claude to refine its own prompt via meta-prompting.
    """
    client = anthropic.Anthropic()
    
    # Step 1: Test initial prompt
    def evaluate_prompt(prompt: str) -> float:
        scores = []
        for example in examples:
            response = client.messages.create(
                model="claude-opus-4",
                max_tokens=100,
                messages=[{
                    "role": "user",
                    "content": f"{prompt}\n\nInput: {example['input']}"
                }]
            )
            # Compare output to expected
            expected = example['output']
            actual = response.content[0].text
            score = 1.0 if actual.strip() == expected.strip() else 0.0
            scores.append(score)
        return sum(scores) / len(scores)
    
    initial_score = evaluate_prompt(initial_prompt)
    print(f"Initial score: {initial_score:.2%}")
    
    # Step 2: Ask Claude to critique and improve its own prompt
    critique_request = f"""
    I want to optimize a prompt for the following task:
    {task}
    
    Current prompt:
    {initial_prompt}
    
    Current performance: {initial_score:.0%} accuracy on examples.
    
    What parts of this prompt could be clearer or more effective?
    Suggest a specific improved version that:
    - Removes ambiguous language
    - Adds concrete examples or formats
    - Clarifies expectations
    - Reduces wordiness
    
    Return ONLY the improved prompt, no explanation.
    """
    
    improved = client.messages.create(
        model="claude-opus-4",
        max_tokens=500,
        messages=[{"role": "user", "content": critique_request}]
    )
    improved_prompt = improved.content[0].text.strip()
    improved_score = evaluate_prompt(improved_prompt)
    print(f"Improved score: {improved_score:.2%}")
    
    # Keep iterating if improvement detected
    if improved_score > initial_score:
        return meta_prompt_optimization(improved_prompt, task, examples)
    return improved_prompt

# Usage
examples = [
    {"input": "London is the capital of England", "output": "true"},
    {"input": "Paris is in Germany", "output": "false"},
    {"input": "Tokyo is the biggest city in Japan", "output": "true"},
]

optimized = meta_prompt_optimization(
    initial_prompt="Determine if statement is true or false.",
    task="Fact verification",
    examples=examples
)
print("Optimized prompt:")
print(optimized)
```

### Abordagem Prática: Multi-Model Prompt Templates

Diferentes modelos têm idiossincrasias. Midjourney ama "cinematic quality, 8k, trending on artstation". Claude adora "step-by-step reasoning". GPT-4 Vision quer descrições detalhadas em ordem visual (topo→baixo, esquerda→direita).

```python
PROMPT_TEMPLATES = {
    "midjourney": {
        "prefix": "Create a professional image:",
        "suffix": ", cinematic quality, 8k, volumetric lighting, trending on artstation --ar 16:9 --quality 2",
        "forbidden": ["text", "writing", "words"],  # MJ não renderiza texto bem
    },
    "dall-e-3": {
        "prefix": "Generate:",
        "suffix": "",
        "forbidden": [],
    },
    "claude-vision": {
        "prefix": "Analyze this image. Structure: 1) Subject, 2) Composition, 3) Colors, 4) Details",
        "suffix": "Be precise and concise.",
        "forbidden": ["I cannot"],  # Avoid disclaimers
    },
    "gpt-4-vision": {
        "prefix": "Describe the image in detail from top to bottom, left to right:",
        "suffix": "Focus on spatial relationships and composition.",
        "forbidden": [],
    }
}

def optimize_for_model(description: str, target_model: str) -> str:
    """Generate model-specific prompt."""
    template = PROMPT_TEMPLATES.get(target_model, PROMPT_TEMPLATES["claude-vision"])
    
    # Remove forbidden words
    optimized = description
    for forbidden in template.get("forbidden", []):
        optimized = optimized.replace(forbidden, "")
    
    return f"{template['prefix']} {optimized} {template['suffix']}"

# Usage
user_intent = "A woman coding at night, surrounded by holographic code"

print("For Midjourney:")
print(optimize_for_model(user_intent, "midjourney"))

print("\nFor DALL-E 3:")
print(optimize_for_model(user_intent, "dall-e-3"))

print("\nFor Claude Vision:")
print(optimize_for_model(user_intent, "claude-vision"))
```

Output esperado:
```
For Midjourney:
Create a professional image: A woman coding at night, surrounded by holographic code, cinematic quality, 8k, volumetric lighting, trending on artstation --ar 16:9 --quality 2

For DALL-E 3:
Generate: A woman coding at night, surrounded by holographic code

For Claude Vision:
Analyze this image. Structure: 1) Subject, 2) Composition, 3) Colors, 4) Details A woman coding at night, surrounded by holographic code Be precise and concise.
```

### Integration com Obsidian Pipeline

Se você já usa o pipeline `second-brain-pipeline`, pode estender para auto-otimizar prompts:

```python
# extensions/prompt-optimizer.py
import os
import json
import dspy
from pathlib import Path

def optimize_link_prompt_on_save(vault_path: str, note_name: str):
    """
    When a new link note is created, optimize the extraction prompt.
    Called as post-save hook in pipeline.
    """
    note_path = Path(vault_path) / "Links Salvos" / note_name
    content = note_path.read_text()
    
    # Extract source URL from frontmatter
    import re
    match = re.search(r'source: (https?://\S+)', content)
    if not match:
        return
    
    source_url = match.group(1)
    
    # Auto-optimize extraction prompt for this URL's domain
    domain = source_url.split('/')[2]
    optimized_prompt = optimize_extraction_for_domain(domain)
    
    # Log optimization (for debugging)
    optim_log = vault_path / "optim-log.json"
    log_data = json.loads(optim_log.read_text()) if optim_log.exists() else {}
    log_data[note_name] = {
        "domain": domain,
        "optimized_prompt": optimized_prompt,
        "timestamp": str(datetime.now())
    }
    optim_log.write_text(json.dumps(log_data, indent=2))

def optimize_extraction_for_domain(domain: str) -> str:
    """Generate best extraction prompt for this domain."""
    templates = {
        "twitter.com": "Extract: author, timestamp, retweets, quote. Focus on technical insight.",
        "reddit.com": "Extract: subreddit, upvotes, comments, poster. Identify if question or discussion.",
        "github.com": "Extract: repo name, stars, description, language. Flag if code or documentation.",
        "medium.com": "Extract: author, reading time, claps, topic. Identify if tutorial or opinion.",
        "default": "Extract: title, author, date, main points. Summarize in 3 bullets."
    }
    return templates.get(domain, templates["default"])
```

## Stack e Requisitos

### Mínimo Viável
- Python 3.10+
- Acesso a Claude API ou OpenAI API (USD 0.05-0.20 por otimização de prompt)
- DSPy: `pip install dspy-ai`
- Exemplos de input/output (3-5 no mínimo)

### Avançado
- Ray (distribuído): otimizar múltiplos prompts em paralelo
- Weights & Biases: rastrear scores de prompts ao longo do tempo
- GitHub Actions: CI/CD que testa novos prompts contra baseline

### Custo
- **DSPy local**: Zero (roda offline com modelos locais)
- **DSPy com Claude**: USD 0.10-0.50 por otimização (5-10 variações testadas)
- **Produção**: Cache de prompts otimizados em Redis = economiza 80% de reprocessamento

## Armadilhas e Limitações

### 1. Gerador Não Captura Contexto Muito Específico

**Problema**: Template genérico não entende nuances do seu brand ("meu estilo é steampunk dos anos 1890").

**Solução**: Fornecer exemplos de referência visual + descritores específicos:
```
❌ "Uma casa bonita"
✅ "Casa vitoriana, telhado de ardósia, janelas com vidro emplomado, porão de pedra, neveiro do moor ao fundo, estilo Wuthering Heights"
```

### 2. Knowledge Base Desatualiza

Quando DALL-E 4 é lançado, prompts otimizados para DALL-E 3 perdem efetividade.

**Mitigação**: Versionamento de templates, atualizar a cada release significante de modelo.

### 3. Risco de "Prompt Abstraction Atrofia"

Se você **sempre** usa gerador de prompts, nunca aprende **por quê** um prompt é melhor que outro. Você se torna dependente da ferramenta.

**Mitigação**: Estudar 1-2 prompts otimizados por semana para entender padrão. Revisar prompt log trimestralmente.

### 4. Contradições Entre Modelos

Um prompt excelente para Midjourney pode ser terrível para DALL-E (diferentes syntaxes, capabilities).

**Mitigação**: Manter templates separados por modelo, testar antes de produção.

### 5. Overfitting em Exemplos

Se treinar otimizador com 5 exemplos muito similares, prompt fica ótimo para esses 5, péssimo em novos casos.

**Mitigação**: 15-20 exemplos com variação ampla; cross-validation (treinar em 12, testar em 3).

## Conexões

- [[contexto-persistente-em-llms|Contexto estruturado que alimenta otimizador]]
- [[estrutura-claude-md-menos-200-linhas|Instruções compactas como baseline para otimização]]
- [[framework-winston-para-apresentacoes|Comunicação estruturada (output template)]]
- [[second-brain-pipeline-telegram-obsidian|Pipeline que auto-otimiza prompts de extração]]

## Histórico

- 2026-04-02: Nota criada
- 2026-04-11: Reescrita com DSPy + MIPROv2, meta-prompting código funcional, multi-model templates, Obsidian integration, 5 armadilhas detalhadas
