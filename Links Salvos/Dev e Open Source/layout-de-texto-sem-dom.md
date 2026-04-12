---
tags: [frontend, texto, performance, dom, canvas, layout, javascript, measurement]
date: 2026-04-02
tipo: aplicacao
---

# Calcular Layout de Texto em JavaScript Puro (Canvas)

## O que é

**Calcular altura, largura e quebras de linha de texto sem DOM reflow.**

Em vez de colocar texto no DOM, let browser render, medir, e deletar, você usa **Canvas API** para calcular **instantaneamente** — em microsegundos — exatamente como o texto vai se quebrar em um container, seu tamanho, espaçamento de linha, sem tocar no rendering engine.

Problema que resolve:
- **Sem DOM**: Você precisa saber o layout de texto antes de renderizar (ex: centering, truncate, wrap)
- **DOM approach** (errado): Coloca texto, mede, ajusta, remeasure — múltiplos reflows (lento, 100+ms)
- **Canvas approach** (certo): Calcula tudo em memória (instantâneo, 0-1ms)

Diferença prática: medir 100 textos leva ~100ms (DOM) vs ~1ms (Canvas).

## Por que importa

### Cenários comuns

1. **Text truncation em lista**: Você tem 1000 items em tabela, cada um com descrição. Antes de renderizar, precisa saber: "esse texto fica em 1 linha ou 2?" Se 2, ajusta altura do row. **Sem Canvas**: measureTerm iterativamente até achar ponto de truncate (3-5 reflows por item). **Com Canvas**: cálculo instantâneo.

2. **Virtual scrolling**: Renderiza apenas items visíveis. Precisa saber altura de cada item **antes** de renderizar. Canvas resolve sem layout trashing.

3. **Layout dinâmico em canvas/WebGL**: Game, diagrama interativo. Precisa saber bounding box de texto. DOM não existe lá.

4. **Editor de texto**: Você está escrevendo — cada caractere tipado precisa recalcular quebras de linha. Se usar DOM a cada keystroke, travará. Canvas recalcula em 0ms.

5. **Tipografia responsiva**: Texto que ajusta tamanho baseado em container width. Canvas pode fazer binary search para "qual font-size fica em 1 linha?" sem reflow.

## Como funciona / Como implementar

### Core: Canvas.measureText()

```javascript
const canvas = document.createElement('canvas');
const ctx = canvas.getContext('2d');
ctx.font = '14px Arial';

const metrics = ctx.measureText('Olá mundo');
console.log(metrics.width);  // ~60px
```

**Returned TextMetrics object:**
```javascript
{
  width: 60.5,
  actualBoundingBoxLeft: 0,
  actualBoundingBoxRight: 60.5,
  actualBoundingBoxAscent: 11,  // altura acima baseline
  actualBoundingBoxDescent: 3,  // altura abaixo baseline
  emHeightAscent: 11,
  emHeightDescent: 3,
  fontBoundingBoxAscent: 11,
  fontBoundingBoxDescent: 3
}
```

**Height real = actualBoundingBoxAscent + actualBoundingBoxDescent = 14px**

### Problema real: calcular quebras de linha

```javascript
/**
 * Calcula onde texto quebra em múltiplas linhas
 * Retorna: array de strings (linhas) + bounding boxes
 */
function wrapText(text, font, maxWidth) {
  const canvas = document.createElement('canvas');
  const ctx = canvas.getContext('2d');
  ctx.font = font;
  
  const lines = [];
  let currentLine = '';
  
  // Split por espaço e quebra de linha
  const words = text.split(/\s+/);
  
  for (const word of words) {
    const testLine = currentLine ? currentLine + ' ' + word : word;
    const metrics = ctx.measureText(testLine);
    
    if (metrics.width > maxWidth && currentLine) {
      // Essa linha ficou muito grande, quebra
      lines.push(currentLine);
      currentLine = word;
    } else {
      currentLine = testLine;
    }
  }
  
  // Última linha
  if (currentLine) lines.push(currentLine);
  
  return lines;
}

// Uso:
const text = 'A raposa marrom salta por cima do cachorro preguiçoso';
const lines = wrapText(text, '16px Arial', 200);
console.log(lines);
// Output: ['A raposa marrom', 'salta por cima do', 'cachorro preguiçoso']
```

### Caso avançado: calcular altura final com line-height

```javascript
function calculateTextBox(text, font, maxWidth, lineHeight = 1.5) {
  const canvas = document.createElement('canvas');
  const ctx = canvas.getContext('2d');
  ctx.font = font;
  
  // Pega altura de 1 linha
  const metrics = ctx.measureText('Hg'); // Caracteres com ascent/descent
  const singleLineHeight = metrics.actualBoundingBoxAscent + 
                          metrics.actualBoundingBoxDescent;
  
  // Calcula quebras
  const lines = wrapText(text, font, maxWidth);
  
  // Total
  const totalWidth = Math.max(...lines.map(l => ctx.measureText(l).width));
  const totalHeight = singleLineHeight * lines.length * lineHeight;
  
  return {
    width: totalWidth,
    height: totalHeight,
    lines: lines,
    lineCount: lines.length,
    lineHeight: singleLineHeight
  };
}

// Uso:
const box = calculateTextBox(
  'Sua descrição aqui que pode ter várias linhas',
  '14px -apple-system, BlinkMacSystemFont, "Segoe UI"',
  300,
  1.6
);
console.log(`${box.width}x${box.height}px, ${box.lineCount} linhas`);
// Output: 299x67.2px, 3 linhas
```

### Otimização: cache de canvas context

```javascript
// Criar apenas 1 canvas, reusar
const canvasCache = (() => {
  const canvas = document.createElement('canvas');
  return canvas.getContext('2d');
})();

// Usar em múltiplas medições (300x mais rápido que criar canvas novo)
function measureFast(text, font) {
  canvasCache.font = font;
  return canvasCache.measureText(text).width;
}

// Benchmark:
// Sem cache: medir 1000 textos = 50-100ms
// Com cache: medir 1000 textos = 0-2ms
```

### Caso: Virtual scroller com Canvas measurements

```javascript
class VirtualTextList {
  constructor(items, containerHeight, font = '14px sans-serif') {
    this.items = items;
    this.containerHeight = containerHeight;
    this.font = font;
    this.cachedHeights = new Map();
    this.ctx = document.createElement('canvas').getContext('2d');
    this.ctx.font = font;
  }

  getItemHeight(item) {
    if (this.cachedHeights.has(item)) {
      return this.cachedHeights.get(item);
    }

    // Primeira vez: calcula altura
    const metrics = this.ctx.measureText('Hg');
    const lineHeight = metrics.actualBoundingBoxAscent + 
                       metrics.actualBoundingBoxDescent;
    
    // Assume max-width = 300px
    const lines = this.wrapText(item, 300).length;
    const height = lines * lineHeight + 16; // + padding

    this.cachedHeights.set(item, height);
    return height;
  }

  wrapText(text, maxWidth) {
    const lines = [];
    let currentLine = '';
    
    for (const word of text.split(/\s+/)) {
      const test = currentLine ? currentLine + ' ' + word : word;
      if (this.ctx.measureText(test).width > maxWidth && currentLine) {
        lines.push(currentLine);
        currentLine = word;
      } else {
        currentLine = test;
      }
    }
    if (currentLine) lines.push(currentLine);
    return lines;
  }

  getVisibleRange() {
    // Calcula quais items são visíveis baseado em altura acumulada
    let offset = 0;
    const visibleStart = null;
    const visibleEnd = null;

    for (let i = 0; i < this.items.length; i++) {
      const h = this.getItemHeight(this.items[i]);
      if (offset < this.containerHeight + this.containerHeight) {
        if (visibleStart === null) visibleStart = i;
        visibleEnd = i;
      }
      offset += h;
      if (offset > this.containerHeight * 2) break;
    }

    return { visibleStart, visibleEnd };
  }
}

// Uso: renderizar apenas items visíveis, sem medir DOM
const scroller = new VirtualTextList(bigList, 800);
const { visibleStart, visibleEnd } = scroller.getVisibleRange();
// Renderizar items[visibleStart:visibleEnd] instantaneamente
```

## Stack técnico

- **API**: Canvas 2D Context (suportado em 100% dos browsers)
- **Performance**: 0-1ms por medição (vs 10-100ms com DOM)
- **Dependências**: Zero (Canvas é built-in)
- **Limitações técnicas**:
  - Não suporta CSS (gradients, shadows, etc) — apenas font, color
  - Não mede exatamente como renderização do DOM (pequeno erro em edge cases)
  - Precisa rodar em thread principal (não Web Worker, Canvas 2D não é threadable)

## Código prático: Snippet pronto

```javascript
// tiny-text-measure.js — copie e use
const TextMeasure = (() => {
  const ctx = document.createElement('canvas').getContext('2d');

  return {
    setFont(font) {
      ctx.font = font;
    },

    width(text) {
      return ctx.measureText(text).width;
    },

    height(font = ctx.font) {
      const m = ctx.measureText('Hg');
      return m.actualBoundingBoxAscent + m.actualBoundingBoxDescent;
    },

    wrapLines(text, maxWidth) {
      const lines = [];
      let line = '';
      for (const word of text.split(/\s+/)) {
        const test = line ? line + ' ' + word : word;
        if (ctx.measureText(test).width > maxWidth && line) {
          lines.push(line);
          line = word;
        } else {
          line = test;
        }
      }
      if (line) lines.push(line);
      return lines;
    },

    box(text, maxWidth, font) {
      ctx.font = font;
      const lines = this.wrapLines(text, maxWidth);
      const h = this.height(font);
      return {
        width: Math.max(...lines.map(l => this.width(l))),
        height: h * lines.length,
        lines
      };
    }
  };
})();

// Uso:
TextMeasure.setFont('14px Arial');
console.log(TextMeasure.width('Olá'));  // ~30
console.log(TextMeasure.height());      // ~16
const b = TextMeasure.box('Sua descrição', 200, '14px Arial');
console.log(b.height); // altura real se quebrar em 200px
```

## Armadilhas e limitações

### 1. **Canvas.measureText não mede exatamente como DOM**

Problema: Você mede com Canvas, layout fica diferente no browser.
Causa: Font rasterização, kerning, hinting diferem entre Canvas e CSS rendering.

Exemplo:
```javascript
const w1 = ctx.measureText('ff').width;  // Canvas: 15px
// Mas no DOM com mesmo font, "ff" pode ser 14.5px (ligadura "ffi")
```

Mitigação:
- **Testes visuais** — medir no Canvas, depois renderizar e verificar
- **Aceitar ~2% de erro** — geralmente aceitável para layouts
- **Usar font-family específica** — evita inconsistências entre sistemas

### 2. **CJK (Chinês, Japonês, Coreano) e RTL (árabe, hebraico) quebram**

Problema: `wrapText` simples divide por espaço, mas CJK não tem espaços (日本語は), RTL é right-to-left.

Exemplo:
```
Input: "これはテストです" (não há espaços)
wrapText output: ["これはテストです"] (não quebra)
```

Mitigação:
- **Detectar language** (heurística ou charset)
- **Para CJK**: dividir por caractere, não por palavra
- **Para RTL**: usar algoritmo de bidi (Unicode Bidirectional Algorithm)
- **Na prática**: use bibliotecas como [breakword](https://github.com/neetjn/breakword) ou [tweakpane-essentials](https://github.com/cocopon/tweakpane)

### 3. **Performance cai com textos muito longos**

Problema: `wrapText` com 10000 palavras é O(n*m) (n=palavras, m=medições).

Mitigação:
- **Cache resultados** — se mesmo texto+font+width, reusar splits
- **Binary search para truncate** — em vez de testar cada caractere, binary search ("onde corto?")
- **Web Worker** — calcular em thread separada

### 4. **Não funciona com Web Fonts que ainda estão carregando**

Problema:
```javascript
// HTML: <link href="https://fonts.googleapis.com/css?family=Roboto">
ctx.font = '14px Roboto';
const w = ctx.measureText('teste').width;  // Usa fallback, não Roboto!
// Depois de 500ms, Roboto carrega, mas w ainda é errado
```

Mitigação:
```javascript
// Espere fontes carregarem
document.fonts.ready.then(() => {
  // Agora meça
  const w = ctx.measureText('teste').width;
});
```

### 5. **Canvas 2D não é threaded (Web Workers)**

Problema: Se você tenta passar Canvas para Web Worker, falha.

Mitigação:
- **Criar canvas novo em Worker**: JavaScript puro, não DOM
- **Ou**: Fazer medições em thread principal, cache agressivo
- **Em React/Vue**: usar useMemo para cache

## Conexões

[[performance-web-frontend|Otimização Frontend — evitar reflow é uma das técnicas principais]]
[[virtual-scrolling|Virtual Scrolling — depende de measurements sem DOM]]
[[tipografia-web|Tipografia Web — entender font metrics para layout preciso]]
[[canvas-api|Canvas 2D Context — referência técnica completa]]
[[web-performance-metrics|Core Web Vitals — layout shift causado por remeasurement]]

## Histórico

- 2026-04-02: Nota criada (version basic)
- 2026-04-11: Expandida com exemplos práticos, casos de uso reais, armadilhas técnicas, code snippets
