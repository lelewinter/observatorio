---
tags: [ia, coding, specification, claude, development]
date: 2026-04-02
tipo: aplicacao
---
# Implementar Código Driven por Specs com Claude/GPT

## O que é
Escrever especificação em linguagem natural e LLM gera código testado e funcional.

## Como implementar
**Spec:**
```
Criar função que:
1. Recebe array de números
2. Retorna média, mediana, desvio padrão
3. Handle array vazio (return null)
4. Testes: [1,2,3] → {mean: 2, median: 2, std: 0.816}
```

**Claude gera:**
```python
def stats(arr):
    if not arr: return None
    mean = sum(arr) / len(arr)
    sorted_arr = sorted(arr)
    n = len(sorted_arr)
    median = (sorted_arr[n//2] + sorted_arr[(n-1)//2]) / 2
    std = (sum((x-mean)**2 for x in arr) / len(arr)) ** 0.5
    return {'mean': mean, 'median': median, 'std': std}
```

## Stack e requisitos
- Claude API ou ChatGPT API
- Prompt template bem estruturado
- Teste gerado automaticamente

## Histórico
- 2026-04-02: Reescrita
