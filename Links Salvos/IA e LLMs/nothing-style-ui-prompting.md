---
tags: [ui-design, prompting, style-transfer, brand-reference, design-system]
source: https://x.com/ErickSky/status/2039419449573539983?s=20
date: 2026-04-02
tipo: aplicacao
---

# Gerar UI Premium com Prompting: "Nothing Style" e Brand Anchors

## O que e

Invocar marca específica em prompt Claude gera UI com identidade coesa (cores, tipografia, espaçamento, modo dark/light). "Nothing style" exemplifica: monospace, monocromático, espaçamento generoso, elementos dot-matrix. Uma palavra ancoreia todo sistema visual.

## Como implementar

**Técnica de brand anchoring**:
```
@claude "Generate a landing page in 'nothing style'.

Requirements:
- Single CTA button
- Hero section with minimal copy
- Feature list
- Footer with links

Use Nothing's visual identity: monospace typography,
black/white/grey palette, generous spacing,
industrial/minimal aesthetic."
```

Claude entende contexto treinado sobre marca e gera:
- Fontes: monospace (Courier, JetBrains Mono)
- Paleta: #000000, #FFFFFF, #888888, #CCCCCC
- Spacing: 24px, 48px, 64px (generoso)
- Componentes: bordas finas, tipografia grande, espaço branco

**Output esperado** (HTML + Tailwind):
```html
<div class="min-h-screen bg-black text-white font-mono">
  <div class="container mx-auto px-8 py-24">
    <h1 class="text-6xl font-light tracking-wider mb-8">
      Premium Design System
    </h1>
    <p class="text-xl text-gray-400 max-w-lg mb-12">
      Industrial. Minimal. Functional.
    </p>
    <button class="border border-white px-8 py-4 hover:bg-white hover:text-black transition">
      Get Started
    </button>
  </div>
</div>
```

**Outras âncoras de marca funcionais**:

1. **Apple style** (minimalista, espaço branco, rounded):
```
@claude "Design in Apple style: generous whitespace,
sans-serif (SF Pro Display), rounded corners (8-12px),
light grays, single accent color (blue typically)."
```

2. **Dark/tech** (neon, glassmorphism, cyber):
```
@claude "Design in cyberpunk tech style: dark navy background,
neon accent colors (cyan, magenta), sans-serif bold,
glassmorphism cards, animated elements."
```

3. **Playful/startup** (colorful, rounded, friendly):
```
@claude "Design in modern startup style: gradient backgrounds,
rounded everything (20px+), bold sans-serif (Poppins),
colorful palette (5-6 vibrant colors), playful icons."
```

**Design system bootstrapping** (agente gera tudo):
```
@claude "Create a complete design system in 'nothing style':
1. Color palette (with hex codes and CSS variables)
2. Typography scale (8 sizes with line-height)
3. Spacing scale (8 values)
4. Component library:
   - Button (primary, secondary, ghost variants)
   - Card
   - Input field
   - Modal
   - Navigation

Provide:
- HTML/CSS components
- Dark mode support
- Accessible (WCAG AA)
- Responsive
- Ready-to-use Tailwind config"
```

**Aplicação prática: MVP landing**:
```
@claude "I'm launching a developer tool. Generate landing page in:
- Nothing style (core aesthetic)
- Features section (5 key features)
- Pricing table
- CTA sections
- Footer
- Dark mode built-in

I want to look premium without hiring designer."
```

Result: Polished landing page em ~5 minutos, pode validar produto antes de investment.

## Stack e requisitos

- **Claude**: Qualquer modelo (3.5 Sonnet+ recomendado para consistência)
- **CSS framework**: Tailwind, Bootstrap, ou vanilla CSS
- **Dark mode**: CSS variables ou Tailwind dark mode
- **Responsive**: Mobile-first media queries
- **Acessibilidade**: ARIA labels, semantic HTML
- **Output**: HTML, JSX, Vue, Svelte (depende de contexto)

## Armadilhas e limitacoes

- **Brand knowledge variável**: Claude pode ter representação imperfeita de marca (ex: Nothing é mais recente, pode ter menos dados). Testar e refinar.
- **Inconsistência iterativa**: Se pedir múltiplas telas, estilo pode divergir levemente; adicionar design system file como contexto para manter coerência.
- **Accessibilidade**: Auto-generated pode miss acessibilidade; sempre revisar contrast ratios, ARIA labels, keyboard navigation.
- **Responsividade**: LLM às vezes gera quebras de layout ruins em mobile; testar em múltiplas resoluções.
- **Originalidade**: UI fica previsível (clones visuais de marcas conhecidas); usar como prototype, refinar design manual depois.

## Conexoes

[[Motion Graphics Gerados por IA com Design System]] [[Modelos de Codificacao Multimodal]] [[Claude Code Melhores Praticas]]

## Historico

- 2026-04-02: Nota criada
- 2026-04-02: Reescrita para template aplicacao