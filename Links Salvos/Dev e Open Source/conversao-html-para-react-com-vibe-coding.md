---
tags: [react, frontend, conversao, html, vibe-coding, ia]
source: https://x.com/MengTo/status/2039288643811242350?s=20
date: 2026-04-02
tipo: aplicacao
---

# Converter HTML para React com Vibe Coding (Gerado por IA)

## O que é

Ferramenta gerada via "vibe coding" (usando Claude/GPT) que converte templates HTML estáticos em React completos, preservando design, integrando assets (Unicorn Studio) e gerando componentes editáveis.

## Como implementar

**Manual: HTML → React (com Claude)**

```bash
# 1. Copiar HTML
# 2. Passar para Claude com prompt:
# "Converter este HTML para React component,
# manter estilos CSS inline, exportar como .jsx"
```

**Exemplo:**
```html
<!-- Input HTML -->
<div class="card">
  <h2>Título</h2>
  <p>Descrição</p>
  <button onclick="handleClick()">Ação</button>
</div>
```

```jsx
// Output React
export default function Card() {
  const [clicked, setClicked] = useState(false);

  return (
    <div className="card">
      <h2>Título</h2>
      <p>Descrição</p>
      <button onClick={() => setClicked(!clicked)}>Ação</button>
    </div>
  );
}
```

**Com assets (Unicorn Studio):**
```jsx
import { UnicornStudio } from '@unicornstudio/react';

export default function AnimatedCard() {
  return (
    <div>
      <UnicornStudio src="animation.json" />
      <h2>Título Animado</h2>
    </div>
  );
}
```

**Full pipeline com Vite:**
```bash
npm create vite@latest my-app -- --template react
cd my-app
npm install @unicornstudio/react

# Converter múltiplos templates
# for file in templates/*.html; do
#   claude-convert-html-to-react "$file"
# done
```

## Stack e requisitos

- **React**: 18+
- **Vite**: para dev rápido
- **Unicorn Studio**: para animações
- **Tailwind/CSS-in-JS**: estilos
- **Claude API**: para automação (opcional)

## Armadilhas

1. **Estado complexo**: Claude pode não capturar lógica complexa. Validar.
2. **Assets**: Paths de imagens podem quebrar. Normalizar.
3. **Performance**: HTML grande pode degradar. Chunking necessário.

## Conexões

- [[design-generativo-por-ia]] - Design inteiro com IA
- [[spec-driven-ai-coding]] - Geração de código com IA

## Histórico

- 2026-04-02: Nota original
- 2026-04-02: Reescrita com implementação
