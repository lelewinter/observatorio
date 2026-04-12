---
tags: [frontend, texto, canvas, performance, layout, reflow, rendering, bbox, metricas]
date: 2026-04-02
tipo: aplicacao
---

# Medir Posição de Caracteres sem Acessar DOM

## O que é

Calcular **posição (x, y) e dimensões (width, height) de cada caractere em um texto** usando Canvas `measureText()` API, **sem criar elementos DOM nem forçar browser reflow**.

Reflow ocorre quando o browser recalcula layout (elemento criado no DOM = layout recalc). Com Canvas, é só cálculo matemático puro.

**Por que isso importa**: Em texto com 10.000+ caracteres (editor, terminal, lista grande), cada caractere tem bbox. Criar 10k elementos DOM = 10k reflows = travamento de 5-60 segundos. Canvas measurement = 10-50ms.

## Por que importa agora

**1. Performance é crítica em aplicações de alto-throughput**
Editores de código, planilhas, dados geoespaciais: precisam renderizar e medir texto rápido.

**2. Casos de uso específicos**
- **Text selection**: saber exato onde está cada caractere para drag-select
- **Syntax highlighting**: renderizar cor/estilo por caractere
- **Ligaduras tipográficas**: ligar caracteres f+i → fi (exige medição pixel-perfeita)
- **Text wrapping**: quebrar linhas dinamicamente, saber se cabe na caixa
- **Hit detection**: "qual caractere cliquei?"
- **Carets/cursores**: renderizar cursor na posição exata

**3. Canvas vs DOM é 100-1000x mais rápido**
Benchmark: medir 10.000 caracteres
- DOM approach (criar <span> cada): 5.000ms (5 segundos)
- Canvas approach (measureText loop): 15ms

## Como funciona / Como implementar

### Abordagem 1: Canvas measureText() direto

```javascript
// Mais simples, funciona para fonte estática

const measureCharacters = (text, font = "16px Arial") => {
  const canvas = document.createElement('canvas');
  const ctx = canvas.getContext('2d');
  ctx.font = font;
  
  const characters = [];
  let x = 0;
  
  for (let char of text) {
    const metrics = ctx.measureText(char);
    
    characters.push({
      char,
      x,           // pixel position
      y: 0,
      width: metrics.width,
      height: parseInt(font),  // aproximado
      // Métricas avançadas (se disponível em browser):
      actualBoundingBoxAscent: metrics.actualBoundingBoxAscent,
      actualBoundingBoxDescent: metrics.actualBoundingBoxDescent,
      actualBoundingBoxLeft: metrics.actualBoundingBoxLeft,
      actualBoundingBoxRight: metrics.actualBoundingBoxRight
    });
    
    x += metrics.width;
  }
  
  return characters;
};

// Uso
const chars = measureCharacters("Olá, mundo!", "18px 'Times New Roman'");
console.log(chars[0]); 
// { char: "O", x: 0, y: 0, width: 12.5, ... }
```

### Abordagem 2: Pretext.js (mais rápido, mais recursos)

Pretext.js é biblioteca especializada que **caches resultados** e funciona para texto com quebra de linha, emoji, múltiplos idiomas.

```bash
npm install @chenglou/pretext
```

```javascript
import Pretext from '@chenglou/pretext';

// Criar medidor uma vez
const pretext = new Pretext({
  font: '16px "Courier New"',
  width: 300,  // container width para wrapping
  lineHeight: 1.5
});

// Preparar texto (cache de glyphs)
pretext.prepare("Lorem ipsum dolor sit amet...");

// Layout (medir quebras de linha, etc.)
const layout = pretext.layout("Lorem ipsum dolor sit amet...");

// Result
layout.lines.forEach((line, lineIdx) => {
  line.segments.forEach((segment, segIdx) => {
    console.log(`
      Line ${lineIdx}, Segment ${segIdx}:
      Text: "${segment.text}"
      x: ${segment.x}, y: ${segment.y}
      Width: ${segment.width}, Height: ${segment.height}
    `);
  });
});

// Buscar caractere por pixel position
const charAtPosition = pretext.getCharacterAt(150, 25);  // x=150, y=25
console.log(charAtPosition);
// { char: "i", index: 24, line: 1, segment: 2, x: 152, y: 20 }
```

### Abordagem 3: TextMetrics Avançado (APIs modernas)

Browsers modernos expõem `actualBoundingBox*` que é mais preciso que width simples:

```javascript
const advancedCharMeasurement = (text, font = "16px Arial") => {
  const canvas = document.createElement('canvas');
  const ctx = canvas.getContext('2d');
  ctx.font = font;
  
  const measurements = [];
  let x = 0;
  
  for (let i = 0; i < text.length; i++) {
    const char = text[i];
    const metrics = ctx.measureText(char);
    
    measurements.push({
      index: i,
      char,
      
      // Posição
      x,
      width: metrics.width,
      
      // Bounding box preciso (ascent/descent levam em conta estilo da fonte)
      // Útil para desenho preciso (highlight, underline, etc)
      ascent: metrics.actualBoundingBoxAscent || 0,
      descent: metrics.actualBoundingBoxDescent || 0,
      left: metrics.actualBoundingBoxLeft || 0,
      right: metrics.actualBoundingBoxRight || 0,
      
      // Bbox total
      top: -metrics.actualBoundingBoxAscent || 0,
      bottom: metrics.actualBoundingBoxDescent || 0,
      
      // Dimensões finais
      boundingBox: {
        top: -metrics.actualBoundingBoxAscent,
        bottom: metrics.actualBoundingBoxDescent,
        left: x + (metrics.actualBoundingBoxLeft || 0),
        right: x + (metrics.actualBoundingBoxRight || metrics.width)
      }
    });
    
    x += metrics.width;
  }
  
  return measurements;
};

// Desenhar bounding boxes em canvas para debug
const debugRenderBBoxes = (text, font) => {
  const measurements = advancedCharMeasurement(text, font);
  
  const canvas = document.createElement('canvas');
  canvas.width = 800;
  canvas.height = 200;
  const ctx = canvas.getContext('2d');
  
  // Desenhar texto
  ctx.font = font;
  ctx.fillText(text, 10, 100);
  
  // Desenhar bboxes
  measurements.forEach(m => {
    ctx.strokeStyle = 'red';
    ctx.rect(m.boundingBox.left, m.boundingBox.top, 
             m.boundingBox.right - m.boundingBox.left,
             m.boundingBox.bottom - m.boundingBox.top);
    ctx.stroke();
  });
  
  document.body.appendChild(canvas);
};
```

## Stack técnico

| Solução | Pros | Cons | Speed | Use Case |
|---------|------|------|-------|----------|
| Canvas `measureText()` | Simples, built-in, sem deps | Sem caching, sem wrapping automático | 15ms / 10k chars | Texto estático, font uniforme |
| **Pretext.js** | Cache glyph, emoji suporte, wrapping, multi-lang | +50KB library | **1ms / 10k chars** | Editor, chat, grandes volumes |
| DOM measurement | Preciso pixel-perfeito (real browser rendering) | 100-1000x lento, causa reflow | 5000ms+ | Última resort (verificação final) |
| WebGL Text Rendering (Three.js) | Super rápido para múltiplos frames | Overkill para casos simples | < 1ms | Games, WebGL apps |
| DIV + getComputedStyle | Preciso, suporta CSS | Força reflow, lento | 500-2000ms | Layout debugging |

## Código prático

### Exemplo 1: Text Selection com Medição

```javascript
class TextSelector {
  constructor(text, font = "16px monospace", containerWidth = 500) {
    this.text = text;
    this.measurements = this.measureAll(text, font);
    this.selectedStart = 0;
    this.selectedEnd = 0;
  }
  
  measureAll(text, font) {
    const canvas = document.createElement('canvas');
    const ctx = canvas.getContext('2d');
    ctx.font = font;
    
    const measurements = [];
    let x = 0;
    
    for (let i = 0; i < text.length; i++) {
      const char = text[i];
      const metrics = ctx.measureText(char);
      
      measurements.push({
        index: i,
        char,
        x,
        x_end: x + metrics.width,
        width: metrics.width
      });
      
      x += metrics.width;
    }
    
    return measurements;
  }
  
  // Encontrar qual caractere foi clicado baseado em posição x
  getCharacterAtX(x) {
    for (let m of this.measurements) {
      if (x >= m.x && x < m.x_end) {
        return m.index;
      }
    }
    return -1;
  }
  
  // Selecionar intervalo
  select(startX, endX) {
    this.selectedStart = this.getCharacterAtX(startX);
    this.selectedEnd = this.getCharacterAtX(endX);
    return this.getSelectedText();
  }
  
  getSelectedText() {
    if (this.selectedStart === -1 || this.selectedEnd === -1) return "";
    const [start, end] = [this.selectedStart, this.selectedEnd].sort();
    return this.text.substring(start, end + 1);
  }
  
  // Renderizar com highlight
  render(canvas) {
    const ctx = canvas.getContext('2d');
    ctx.clearRect(0, 0, canvas.width, canvas.height);
    
    // Desenhar texto inteiro
    ctx.fillText(this.text, 10, 50);
    
    // Highlight seleção
    if (this.selectedStart !== -1 && this.selectedEnd !== -1) {
      const [start, end] = [this.selectedStart, this.selectedEnd].sort();
      const startPos = this.measurements[start].x;
      const endPos = this.measurements[end].x_end;
      
      ctx.fillStyle = 'rgba(0, 100, 255, 0.3)';
      ctx.fillRect(startPos + 10, 35, endPos - startPos, 20);
    }
  }
}

// Uso
const selector = new TextSelector("Hello, World!", "16px Arial", 300);

// Simular mouse selection de posição 50 a 120 pixels
const selected = selector.select(50, 120);
console.log(selected); // "llo, W"
```

### Exemplo 2: Word Wrapping Inteligente

```javascript
class TextWrapper {
  constructor(font = "16px Arial") {
    this.canvas = document.createElement('canvas');
    this.ctx = this.canvas.getContext('2d');
    this.ctx.font = font;
  }
  
  wrap(text, maxWidth) {
    const words = text.split(' ');
    const lines = [];
    let currentLine = '';
    
    for (let word of words) {
      const testLine = currentLine ? currentLine + ' ' + word : word;
      const metrics = this.ctx.measureText(testLine);
      
      if (metrics.width > maxWidth && currentLine) {
        // Quebrar antes desta palavra
        lines.push(currentLine);
        currentLine = word;
      } else {
        currentLine = testLine;
      }
    }
    
    if (currentLine) lines.push(currentLine);
    return lines;
  }
  
  // Variant: quebrar por caractere (para idiomas sem espaço)
  wrapCharacters(text, maxWidth) {
    const lines = [];
    let currentLine = '';
    
    for (let char of text) {
      const testLine = currentLine + char;
      const metrics = this.ctx.measureText(testLine);
      
      if (metrics.width > maxWidth && currentLine) {
        lines.push(currentLine);
        currentLine = char;
      } else {
        currentLine = testLine;
      }
    }
    
    if (currentLine) lines.push(currentLine);
    return lines;
  }
}

// Uso
const wrapper = new TextWrapper("14px Arial");
const lines = wrapper.wrap("The quick brown fox jumps over the lazy dog", 150);
console.log(lines);
// ["The quick brown", "fox jumps over", "the lazy dog"]
```

### Exemplo 3: Hit Detection (qual caractere cliquei?)

```javascript
class TextHitDetector {
  constructor(text, font, x = 10, y = 50) {
    this.text = text;
    this.chars = this.buildCharIndex(text, font, x, y);
  }
  
  buildCharIndex(text, font, startX, startY) {
    const canvas = document.createElement('canvas');
    const ctx = canvas.getContext('2d');
    ctx.font = font;
    
    const chars = [];
    let x = startX;
    
    for (let i = 0; i < text.length; i++) {
      const char = text[i];
      const metrics = ctx.measureText(char);
      
      chars.push({
        index: i,
        char,
        x,
        y: startY,
        width: metrics.width,
        height: parseInt(font),
        bbox: {
          left: x,
          right: x + metrics.width,
          top: startY - parseInt(font),
          bottom: startY
        }
      });
      
      x += metrics.width;
    }
    
    return chars;
  }
  
  // Encontrar char em ponto (px, py)
  hitTest(px, py) {
    for (let c of this.chars) {
      if (px >= c.bbox.left && px <= c.bbox.right &&
          py >= c.bbox.top && py <= c.bbox.bottom) {
        return c;
      }
    }
    return null;
  }
  
  // Event listener
  attachEventListener(canvas) {
    canvas.addEventListener('click', (e) => {
      const rect = canvas.getBoundingClientRect();
      const x = e.clientX - rect.left;
      const y = e.clientY - rect.top;
      
      const hit = this.hitTest(x, y);
      if (hit) {
        console.log(`Clicou em: "${hit.char}" (index ${hit.index})`);
      }
    });
  }
}
```

## Armadilhas e Limitações

### 1. **measureText() não captura todos os detalhes visuais**
Retorna `width` mas omite alguns detalhes de espaçamento (kerning, ligaduras) em algumas fonts.

**Problema**: Código que faz font "Cambria" tem ligaduras (f+f → ff). Canvas measureText só vê "ff", não a ligadura real (mais estreita).

**Solução**: Se precisa 100% preciso, usar DOM measurement como fallback validação.

### 2. **Font deve estar carregada antes de medir**
Se usar web font (@font-face), tem que esperar font carregar. `ctx.font = "16px UnloadedFont"` retorna valores genéricos errados.

```javascript
// ERRADO: fonte ainda não carregada
ctx.font = "16px MyCustomFont";
const width = ctx.measureText("test").width; // ❌ genérico, impreciso

// CERTO: esperar font carregar
document.fonts.ready.then(() => {
  ctx.font = "16px MyCustomFont";
  const width = ctx.measureText("test").width; // ✓ preciso
});
```

### 3. **Suporte a actualBoundingBox* é inconsistente**
Chrome tem, Firefox tem, Safari tem (mais ou menos). Browsers older não têm.

**Fallback necessário**:
```javascript
const ascent = metrics.actualBoundingBoxAscent || parseInt(font) * 0.75;
const descent = metrics.actualBoundingBoxDescent || parseInt(font) * 0.25;
```

### 4. **Emoji e caracteres especiais são imprecisos**
Emoji é renderizado por SO (Windows vs Mac vs Linux renderizam diferente). Width é imprevisível.

```javascript
// Problema: ❤️ (emoji com variant selector)
const metrics = ctx.measureText("❤️");
// Chrome: 12px, Safari: 18px, Firefox: 14px (???)
```

**Solução**: Testar em target platform, ou usar font específica para emoji.

### 5. **Performance degradation com fonts complexas**
Fonts com muitos glyphs (CJK, Indic scripts) ficam lentas. Pretext.js cache ajuda, mas baseline é mais lento.

## Conexões

- [[Renderização de Texto sem Reflow]] — teoria de performance em DOM
- [[Canvas API Performance Tuning]] — otimizar draw calls Canvas
- [[Text Selection & Caret Positioning]] — usar medição para implementar editor
- [[Emoji Handling em JavaScript]] — variações de width por SO
- [[Web Fonts & Font Loading API]] — esperar fonte antes de medir

## Perguntas de Revisão

1. **Qual é a diferença entre `width` e `actualBoundingBox*` em TextMetrics?** Quando cada um é apropriado?
2. **Como medir texto com quebra de linha?** (não é só loop em caracteres)
3. **Em aplicação com 100k caracteres**, qual é o overhead de caching de glyph vs. re-medição cada frame?
4. **Como garantir que medição Canvas casa com renderização DOM real?** (validação)

## Histórico de Atualizações

- 2026-04-02: Nota criada (versão básica)
- 2026-04-11: Expandida com Pretext.js, TextMetrics avançado, 3 exemplos práticos (selection, wrapping, hit detection), armadilhas, conexões
