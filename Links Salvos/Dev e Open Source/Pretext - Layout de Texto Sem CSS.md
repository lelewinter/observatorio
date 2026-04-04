---
date: 2026-03-28
tags: [frontend, css, typescript, ia, desenvolvimento, open-source, performance]
source: https://x.com/namcios/status/2037956753812328761
tipo: aplicacao
---

# Calcular Layout de Texto Sem Reflows — Aritmética em Vez de CSS

## O que é

Pretext é uma biblioteca TypeScript que calcula dimensões e posições de texto através de aritmética pura (sem tocar DOM ou CSS do browser). Retorna altura, largura, quebras de linha e posição de caracteres em ~microsegundos, 500x mais rápido que methods tradicionais baseados em reflow.

## Como implementar

**Setup básico:**
```bash
npm install pretext-engine
```

**Caso de uso 1: Chat com layout fluido**
```typescript
import { TextMeasurer } from 'pretext-engine';

const measurer = new TextMeasurer({
  font: 'system-ui',
  fontSize: 14,
  lineHeight: 1.5,
  maxWidth: 300,
  textAlign: 'left'
});

// Renderizar bolha de chat sem tocar DOM
const message = "Olá! Como você está hoje?";
const measured = measurer.measure(message);

console.log({
  width: measured.width,        // 180px
  height: measured.height,      // 28px
  lines: measured.lines,        // 1 linha
  lineBreaks: measured.breaks   // []
});

// Usar em React/Vue sem cause reflow
const ChatBubble = ({ text }) => (
  <div style={{
    width: measurer.measure(text).width,
    height: measurer.measure(text).height,
  }}>
    {text}
  </div>
);
```

**Caso de uso 2: Dashboard responsivo**
```typescript
// Sem Pretext: browser recalcula layout 60x/s
// Com Pretext: cálculo sincronamente no JS
const resizeObserver = new ResizeObserver((entries) => {
  entries.forEach((entry) => {
    const containerWidth = entry.contentRect.width;

    // Calcular quantas colunas cabem
    const columnWidth = measurer.measure("X").width * 20; // 20 chars
    const columns = Math.floor(containerWidth / columnWidth);

    // Layout update sem tocar DOM
    updateLayoutState({ columns });
  });
});

resizeObserver.observe(container);
```

**Caso de uso 3: Suporte a CJK e RTL**
```typescript
const measurer_ja = new TextMeasurer({
  font: 'Noto Sans JP',
  fontSize: 16,
  language: 'ja' // Habilita clustering de grafemas CJK
});

const textJP = "こんにちは世界"; // "Olá Mundo"
const measured_jp = measurer_ja.measure(textJP);
// Corretamente conta: 7 caracteres (não 14 bytes UTF-16)

const measurer_ar = new TextMeasurer({
  direction: 'rtl', // Árabe/Hebraico
  font: 'Arial'
});

const textAR = "مرحبا بالعالم";
const measured_ar = measurer_ar.measure(textAR);
// Posições renderizadas da direita para esquerda
```

**Integração com rendering engine:**
```typescript
// Framework agnóstico
const calculateTextLayout = (
  text: string,
  constraints: { maxWidth: number; lineHeight: number }
) => {
  return measurer.measure(text);
};

// Usar em Canvas/WebGL para máxima performance
const canvas = document.querySelector('canvas');
const ctx = canvas.getContext('2d');

const layout = measurer.measure("Renderizar no Canvas");

ctx.font = '14px system-ui';
ctx.fillText(layout.text, 0, layout.height);
```

## Stack e requisitos

- **Pretext**: versão latest
- **Node.js**: 14+
- **TypeScript**: 4.5+ (opcional, suporta JS vanilla também)
- **Suporte de fontes**: Metricas pré-calculadas para fonts do sistema (Arial, system-ui, Helvetica, Segoe UI). Para fonts customizadas, forneça métricas manualmente.

Requisitos de hardware: **nenhum**. Roda em CPU qualquer; zero GPU needed.

Tamanho do bundle: ~50KB (gzipped ~15KB).

## Armadilhas e limitações

1. **Armadilha: confundir cálculo com renderização**: Pretext calcula *dimensões*, não renderiza pixels. Você ainda precisa renderizar com DOM/Canvas/WebGL. Não use como substituto a renderer.

2. **Limitação: fontes dinâmicas**: Se o usuário instalar fonte customizada no OS, métricas não serão precisas. Pretext usa métricas do sistema — para fontes web loader (Google Fonts), força carregamento com `@font-face` antes.

3. **Armadilha: esquecer bounding boxes**: Alguns caracteres (like "j", "g") têm descenders. `height` retorna altura do linha, não altura visual. Use `getBounds()` para bounding box preciso.

4. **Limitação: ligaduras (ligatures)**: Sequências como "fi" em fontes tipográficas colapsam para único glyph. Pretext não suporta ligaduras automaticamente — você precisa passar `{ligatures: false}` ou usar fonte sans-serif.

5. **Armadilha: cache agressivo**: Pretext cacheia resultados. Se mudar estilo (font-weight, font-size), nova instancia é necessária:
   ```typescript
   // Certo
   const measurer_bold = new TextMeasurer({ fontSize: 14, fontWeight: 'bold' });

   // Errado — reusa cache
   measurer.fontSize = 16;
   ```

## Conexões

- [[layout-de-texto-sem-dom]] - Extensão: como medir sem tocar DOM
- [[medicao-de-texto-sem-dom]] - Técnicas de bbox e posição de caracteres
- [[renderizacao-virtualizada-de-terminal]] - Padrão: virtualizar renderização
- [[conversao-html-para-react-com-vibe-coding]] - Converter layouts manuais para componentes

## Histórico

- 2026-03-28: Nota original
- 2026-04-02: Reescrita com exemplos de implementação
