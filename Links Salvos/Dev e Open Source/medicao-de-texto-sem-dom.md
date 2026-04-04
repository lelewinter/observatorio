---
tags: [frontend, texto, bbox, metricas, rendering]
date: 2026-04-02
tipo: aplicacao
---
# Medir Posição de Caracteres sem Acessar DOM

## O que é
Calcular bbox (bounding box) de cada caractere de forma que não cause reflows.

## Como implementar
```javascript
const charBounds = (text, font, x=0, y=0) => {
  const canvas = document.createElement('canvas');
  const ctx = canvas.getContext('2d');
  ctx.font = font;
  
  let currentX = x;
  const bounds = [];
  
  for (let char of text) {
    const metrics = ctx.measureText(char);
    bounds.push({
      char, 
      x: currentX, 
      width: metrics.width,
      y, 
      height: parseInt(font)
    });
    currentX += metrics.width;
  }
  
  return bounds;
};
```

## Histórico
- 2026-04-02: Reescrita
