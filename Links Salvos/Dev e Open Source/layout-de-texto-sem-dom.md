---
tags: [frontend, texto, performance, dom, aritmética]
date: 2026-04-02
tipo: aplicacao
---
# Calcular Layout de Texto em JavaScript Puro

## O que é
Calcular altura/largura/quebras de linha sem tocar DOM. Zero reflows, microsegundos.

## Como implementar
```javascript
const textMetrics = (text, font, maxWidth) => {
  const canvas = document.createElement('canvas');
  const ctx = canvas.getContext('2d');
  ctx.font = font;
  
  const width = ctx.measureText(text).width;
  const height = parseInt(font); // aproximado
  
  return { width, height };
};

const metrics = textMetrics("Olá mundo", "14px Arial", 300);
```

## Stack e requisitos
- Canvas API (sempre disponível)
- Cálculos: aritmética pura

## Armadilhas
1. Não captura exatamente reflows do browser
2. CJK/RTL exigem heurísticas adicionais

## Histórico
- 2026-04-02: Reescrita
