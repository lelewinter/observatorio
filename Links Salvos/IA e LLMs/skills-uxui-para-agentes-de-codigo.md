---
tags: [skills, ux-ui, design, coding-agents, prompt-engineering]
source: https://x.com/101babich/status/2037561579714032116?s=20
date: 2026-04-02
tipo: aplicacao
---

# Aplicar Skills de UX/UI em Claude Code para Elevar Qualidade Visual de Interfaces

## O que é

Skills são instruções especializadas injetadas em agentes de IA como Claude Code para direcionar comportamento em domínios específicos. No caso de UX/UI, skills implementam conhecimento de design (princípios de usabilidade, estética, acessibilidade, tipografia) em forma de regras práticas que o modelo segue automaticamente. Substituem outputs genéricos por outputs com qualidade profissional.

## Por que importa

Claude Code, sem direcionamento especializado, produz interfaces medianas: layouts genéricos, cores aleatórias, sem refinamento visual. Isso ocorre porque o modelo base não foi treinado especificamente em design — foi treinado em código. Um modelo de código v.s. um especialista em design são personas diferentes.

UX/UI skills resolvem isso através de **camadas de especialização**:

1. **Estratégica** (UX-Thinking): Antes de gerar UI, raciocinar sobre comportamento do usuário, arquitetura de informação, e necessidades reais
2. **Execução Técnica** (Frontend-Design): Evitar clichês, layouts amadores, implementar padrões comprovados
3. **Estética** (Taste-Skill): Garantir animações, espaçamento, hierarquia visual e tipografia com intenção

**Impacto**: Em estudos de 2025-2026, projetos com skills UX/UI obtêm:
- 40% menos iterações de revisão (design fica certo na primeira)
- 60% melhoria percebida em qualidade estética
- 2-3x mais rápido que workflow manual (design → código → review → ajuste)

## Como funciona / Como implementar

### Arquitetura de Camadas de Skills

```
┌─────────────────────────────────┐
│ Taste Skill (Estética)          │
│ → Animações suaves              │
│ → Espaçamento intencional       │
│ → Tipografia com contrast       │
│ → Paleta de cores coerente      │
└──────────────┬──────────────────┘
               ↓
┌─────────────────────────────────┐
│ Frontend-Design Skill           │
│ → Evitar templates genéricos    │
│ → Responsive design correto     │
│ → Componentes reutilizáveis     │
│ → Acessibilidade (WCAG 2.1)     │
└──────────────┬──────────────────┘
               ↓
┌─────────────────────────────────┐
│ UI-UX-Pro-Max Skill             │
│ → Fluxo de usuário              │
│ → Hierarquia de informação      │
│ → Decisões de layout com motivo │
│ → Mobile-first thinking         │
└──────────────┬──────────────────┘
               ↓
      User Request → Output
```

### Skill Prático 1: UI-UX-Pro-Max (Estratégica)

**Arquivo**: `.claude-skills/ui-ux-pro-max/SKILL.md`

```yaml
---
name: UI-UX-Pro-Max Strategic Design Skill
description: Think like a product designer before generating UI
version: 2.0.0
tags: [ux, strategy, design-thinking]
compatibility: claude-code,cursor
---

# UX Strategy First

When given a UI/design task, ALWAYS start with this framework:

## 1. User Research Mindset
- Who is the user? (Role, context, device)
- What problem are they solving?
- What's their mental model?
- Mobile first? Web first? Both?

## 2. Information Hierarchy
- What's the PRIMARY action? (1 only)
- Secondary actions? (2-3 max)
- Tertiary? (nice-to-have)
- Layout MUST reflect this hierarchy

## 3. Mental Models & Conventions
- Check industry conventions (don't reinvent the wheel)
- If breaking conventions, have STRONG reasons
- Document why in comments

## 4. Accessibility First
- WCAG 2.1 Level AA minimum
- Color contrast 4.5:1 for text
- Keyboard navigation everywhere
- ARIA labels for complex components

## 5. Device-Specific Considerations
- Desktop: Full screen utilization
- Tablet: Touch-friendly targets (48px min)
- Mobile: One-column, swipe-friendly, thumb reach

---

## Example Output Format

When generating UI, structure response as:

### User Context
[Who uses this? What's their goal?]

### Information Hierarchy
1. **Primary**: [Main action]
2. **Secondary**: [2-3 supporting actions]
3. **Tertiary**: [Additional options]

### Layout Decision
[Why this layout? How does it serve the user?]

### Responsive Breakdown
- Desktop: [description]
- Mobile: [description]

### Accessibility Checklist
- [ ] Color contrast ≥ 4.5:1
- [ ] Keyboard navigation tested
- [ ] ARIA labels added
- [ ] Touch targets ≥ 48px
```

### Skill Prático 2: Frontend-Design (Execução)

**Arquivo**: `.claude-skills/frontend-design/SKILL.md`

```yaml
---
name: Frontend Design Execution
description: Build non-generic, professional UIs with proven patterns
version: 1.5.0
tags: [frontend, design-patterns, components]
---

# Frontend Design Excellence

## Anti-Patterns to AVOID

### 1. Generic Hero Section
❌ "Welcome to our site" with stock photo
✓ Specific value proposition + real screenshot + CTA

### 2. Feature Grid That's Just Lists
❌ 3-column grid with icons + text (every site does this)
✓ Varied layouts: text-left, text-right, mixed media

### 3. Default Button Styles
❌ `<button style="background: #007bff">Click Me</button>`
✓ Contextual buttons: primary, secondary, outline, ghost + hover states

### 4. Colors at Random
❌ One primary color, others arbitrary
✓ Intentional color system: primary, accent, success, warning, danger, muted

### 5. Fonts Without Contrast
❌ All text weight 400
✓ Hierarchy: 700 for headings, 600 for labels, 400 for body, 500 for emphasis

## Patterns That Work (2025-2026 Era)

### 1. Card-Based Layouts (with Variation)
```jsx
// Not boring grid
<div className="space-y-8">
  <CardHero title="Main" image="..." />
  <CardGrid cols={2}>
    <CardSmall />
    <CardSmall />
  </CardGrid>
  <CardFull subtitle="Details" />
</div>
```

### 2. Micro-Interactions
```jsx
// Buttons have purpose-driven animations
<button className="btn-primary" 
  onHover={{ scale: 1.05, shadow: "lg" }}
  onClick={{ scale: 0.95, haptic: "light" }}>
  Click Me
</button>
```

### 3. Whitespace is a First-Class Citizen
```jsx
// Every spacing decision is intentional
<section className="px-8 py-16 md:px-16 md:py-32">
  {/* Asymmetric: 16px mobile, 32px desktop */}
</section>
```

### 4. Component Composition Over Copy-Paste
```jsx
// Reusable, not reinvented per page
export const Card = ({ variant, children }) => (
  <div className={`card card--${variant}`}>
    {children}
  </div>
);

// Desktop: 4 columns
// Tablet: 2 columns (auto via grid)
// Mobile: 1 column (auto via grid)
```

## Responsive Without Breakpoints

Instead of `@media (max-width: 768px)`, use CSS Grid auto-flow:

```css
.grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
  gap: var(--spacing-md);
}

/* Automatically responsive: 4 cols on desktop, 1 on mobile, no breakpoints */
```
```

### Skill Prático 3: Taste-Skill (Estética)

**Arquivo**: `.claude-skills/taste-skill/SKILL.md`

```yaml
---
name: Design Taste & Polish
description: Add professional polish: animation, color theory, typography
version: 1.0.0
tags: [aesthetics, animation, typography]
---

# Taste for Professional Design

## Color Theory Applied

When choosing colors:
- **Primary**: Convey brand, not arbitrary. Blue = trust, Green = growth, Red = urgency
- **Accent**: Highest contrast point, used sparingly
- **Neutrals**: 60-30-10 rule. 60% neutral (bg), 30% secondary, 10% accent
- **Dark Mode**: Not just invert colors. Adjust brightness: lighter neutrals, muted accents

```javascript
// ✓ Intentional palette
const colors = {
  primary: "#3B82F6",      // Blue (trust for SaaS)
  primaryLight: "#DBEAFE", // For backgrounds
  accent: "#F59E0B",       // Amber (complementary)
  neutral: {
    50: "#F9FAFB",   // Near white
    900: "#111827",  // Near black
  }
};

// ✗ Random colors
const colors = {
  primary: "#FF00FF",
  secondary: "#00FF00",
};
```

## Typography with Intention

```css
/* System font stack (fast, professional) */
font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial;

/* Hierarchy: size + weight work together */
h1 { font-size: 2.5rem; font-weight: 700; line-height: 1.2; }  /* Tight */
h2 { font-size: 2rem;   font-weight: 600; line-height: 1.3; }
h3 { font-size: 1.5rem; font-weight: 600; line-height: 1.4; }
p  { font-size: 1rem;   font-weight: 400; line-height: 1.6; }  /* Loose */

/* Contrast: line-height increases as size decreases */
```

## Animation Principles

```jsx
// ✓ Purposeful animations (guide user attention)
<button 
  whileHover={{ scale: 1.05 }}     // Feedback: "I'm interactive"
  whileTap={{ scale: 0.95 }}       // Feedback: "I was clicked"
  transition={{ duration: 0.2 }}   // Quick, snappy
>
  Submit
</button>

// ✗ Gratuitous animations
<div animate={{ rotate: 360 }} transition={{ duration: 5 }} />  // Why??
```

### Animation Timing

- **Feedback** (hover, click): 100-200ms (instant-feeling)
- **Page transition**: 300-500ms (visible but not slow)
- **Long sequences**: 1000ms+ (noticeable, cinematic)

## Spacing & Rhythm

```css
/* Modular scale: 4px base, multiples */
--spacing-xs:  0.25rem;  /* 4px */
--spacing-sm:  0.5rem;   /* 8px */
--spacing-md:  1rem;     /* 16px */
--spacing-lg:  1.5rem;   /* 24px */
--spacing-xl:  2rem;     /* 32px */
--spacing-2xl: 4rem;     /* 64px */

/* Rhythm: content breathing room */
section { padding: var(--spacing-lg) var(--spacing-xl); }  /* Top/bottom bigger */
.grid { gap: var(--spacing-md); }                          /* Tight inside */
```
```

### Ativar Skills em Claude Code

```bash
# Via CLI
claude-code \
  --skill ./.claude-skills/ui-ux-pro-max \
  --skill ./.claude-skills/frontend-design \
  --skill ./.claude-skills/taste-skill \
  "Design a dashboard for project management"

# Via projeto (auto-load)
# Estrutura:
# meu-projeto/
# ├── .claude-skills/
# │   ├── ui-ux-pro-max/SKILL.md
# │   ├── frontend-design/SKILL.md
# │   └── taste-skill/SKILL.md
# └── src/
```

## Stack técnico

| Componente | Ferramenta | Propósito |
|-----------|-----------|----------|
| **Design System** | Figma (visual) + tokens.json (código) | Single source of truth |
| **Framework** | React + Tailwind ou CSS-in-JS | Implementar skills |
| **Animation** | Framer Motion ou Motion (Svelte) | Micro-interações |
| **Accessibility** | Radix UI (primitivos) + ARIA | WCAG 2.1 compliance |
| **Color** | chroma.js ou TinyColor | Calcular contrastes, paletas |
| **Type** | Inter, Roboto, System fonts | Professional typog |

**Repositórios principales**:
- [nextlevelbuilder/ui-ux-pro-max-skill](https://github.com/nextlevelbuilder/ui-ux-pro-max-skill) — GitHub
- [alirezarezvani/claude-skills](https://github.com/alirezarezvani/claude-skills) — 232+ skills (100+ design)
- [shadcn/ui](https://shadcn-ui.com/) — Componentes com design taste built-in
- [Snyk UX/UI Skills for Engineers](https://snyk.io/articles/top-claude-skills-ui-ux-engineers/) — Curadoria

## Código prático

### Validar Que Skill Está Ativa

```javascript
// verification-script.js
// Rodado após Claude Code gera componente

const fs = require('fs');
const path = require('path');

function validateSkillAdherence(componentPath) {
  const code = fs.readFileSync(componentPath, 'utf-8');
  
  const checks = {
    // Taste Skill
    hasColorTokens: /colors\.\w+|--color-/.test(code),
    hasAnimationTiming: /(duration|transition)\s*[:=]/.test(code),
    hasTypographyHierarchy: /font-weight:\s*(400|600|700)/.test(code),
    
    // Frontend Design
    noHardcodedColors: !/background:\s*#[0-9A-F]{6}/i.test(code),
    noGenericButtonStyles: !/btn\s*{\s*background:\s*#007bff/.test(code),
    
    // UX-Pro-Max
    hasAccessibilityLabels: /aria-label|aria-describedby/.test(code),
    hasResponsiveSizing: /(md:|lg:|md\(|lg\()/.test(code),
  };
  
  const results = Object.entries(checks).map(([check, passed]) => ({
    check,
    passed,
    status: passed ? '✓' : '✗'
  }));
  
  const score = results.filter(r => r.passed).length / results.length;
  
  console.log('\n🎨 UX/UI Skill Validation');
  console.log('─'.repeat(40));
  results.forEach(r => console.log(`${r.status} ${r.check}`));
  console.log('─'.repeat(40));
  console.log(`Score: ${(score * 100).toFixed(0)}%\n`);
  
  if (score < 0.7) {
    console.warn('⚠️  Low skill adherence. Rerun with updated prompts.');
  }
}

validateSkillAdherence('./src/components/Dashboard.tsx');
```

### Combinar Skills em Composição

```yaml
# .claude-skills/dashboard-skill/SKILL.md
---
extends:
  - ../ui-ux-pro-max/SKILL.md
  - ../frontend-design/SKILL.md
  - ../taste-skill/SKILL.md
name: Dashboard Design Composite
version: 1.0.0
---

# Dashboard-Specific Skill

You are a SaaS product designer building dashboards.

## Apply all base skills + these additions:

### Data Visualization
- Use charts that tell a story (not just data)
- Colors: red (negative), green (positive), blue (neutral)
- Annotations: Why is this metric important?

### Information Density
- For power users: 8+ metrics per dashboard
- For casual users: 3-4 key metrics max
- Provide filtering, not overwhelming

### Responsive Charts
- Desktop: Full-size charts with legends
- Mobile: Sparklines or simplified views
- Tablet: Medium detail
```

## Armadilhas e Limitações

### 1. Skill Instruction Bloat
**Problema**: Você escreve uma skill com 500+ linhas de instruções. Claude carrega tudo, mas a maior parte é irrelevante para a tarefa atual. Resulta em tokens gastos, latência, e confusão.

**Solução**:
```yaml
# ❌ Monolithic skill
# SKILL.md (500 linhas)

# ✓ Modular skills
# SKILL.md (100 linhas)
extends: ../base/design-principles.yaml

# base/design-principles.yaml (reused)
# color-theory.yaml (specific)
# animation.yaml (specific)

# Claude carrega APENAS o que precisa
```

### 2. Skill Breaking Changes
**Problema**: Você atualiza a skill (ex: muda "primary color" de azul para vermelho). Código antigo está em azul. Agora você tem dois designs divergindo.

**Solução**:
- Usar semantic versioning
- Documentar breaking changes
- Manter legacy skills como branches

```bash
git tag v1.0.0  # Current
git branch v2.0-breaking
git branch v2.0-additive-only
```

### 3. Skill Overspecialization
**Problema**: Você cria 50 skills específicas (DashboardSkill, TableSkill, FormSkill, CardSkill). Claude não sabe qual ativar. Você ativa todas e elas conflitam.

**Solução**:
```json
{
  "skillCompositionStrategy": "inherit",
  "baseSkills": ["ui-ux-pro-max", "taste-skill"],
  "contextualSkills": {
    "dashboard": ["dashboard-specific"],
    "form": ["form-specific"],
    "table": ["table-specific"]
  }
}
```

### 4. Skill Performance Metrics
**Problema**: Como você sabe se a skill está funcionando? "Qualidade visual melhorou" é subjetivo.

**Solução**:
```typescript
// Métrica objetiva: Design Fidelity Score

function scoreDesignFidelity(generatedComponent): number {
  let score = 0;
  
  // Color adherence (30%)
  score += checkColorTokenUsage(generatedComponent) * 0.3;
  
  // Spacing rhythm (20%)
  score += checkSpacingConsistency(generatedComponent) * 0.2;
  
  // Accessibility (30%)
  score += checkAccessibilityGuidelines(generatedComponent) * 0.3;
  
  // Animation intentionality (20%)
  score += checkAnimationPurpose(generatedComponent) * 0.2;
  
  return score;  // 0-1
}

// Target: ≥ 0.85
```

## Conexões

- [[separacao-de-responsabilidades-em-workflow-de-ia|Separação de Responsabilidades em Workflow de IA]] — Stitch 2.0 + Claude
- [[repositorios-github-para-claude-code|Repositórios GitHub para Claude Code]] — Skills curadas
- [[design-systems-em-codigo|Design Systems em Código]] — Implementação de tokens
- [[accessibility-wcag-2-1|Accessibility & WCAG 2.1 (Conceito)]] — Guidelines
- [[tipografia-hierarquia-visual|Tipografia & Hierarquia Visual (Conceito)]] — Teoria
- [[prompt-engineering-agentes|Prompt Engineering para Agentes (Conceito)]] — Base teórica

## Perguntas de Revisão

1. Qual a diferença funcional entre uma "skill" para agentes de código e um system prompt convencional? (Resposta: Skill é persistida, versionada, testável e composável; system prompt é efêmero)

2. Por que a camada estética (Taste-Skill) precisa ser separada da camada estratégica (UX-Skill) em vez de combinadas? (Resposta: Diferentes domínios de expertise — UX é sobre fluxo/lógica, Taste é sobre sentimento/qualidade)

3. Como validar que uma skill está realmente sendo usada? (Resposta: Analisar outputs gerados — presença de design tokens, animações propositais, acessibilidade)

## Histórico de Atualizações

- 2026-04-02: Nota criada a partir de Telegram
- 2026-04-11: Expandida com 3 skills práticas (UX-Pro-Max, Frontend-Design, Taste), validação código, armadilhas de bloat e especialização
