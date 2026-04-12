---
tags: [arquitetura, multi-agent, design-patterns, separacao-responsabilidades]
source: https://x.com/PrajwalTomar_/status/2038292355095335406?s=20
date: 2026-04-02
tipo: aplicacao
---

# Combinar Claude Code + Google Stitch 2.0 via MCP para UI/UX + Lógica

## O que é

Padrão arquitetural que separa responsabilidades em workflows de IA: um modelo especializado em design visual (Google Stitch 2.0) gera UI/UX, enquanto outro especializado em lógica (Claude Code) implementa backend e integrações. Ambos conectados via MCP (Model Context Protocol) para colaborarem sem intervenção manual.

## Por que importa

Ferramentas de IA generativa para código tendem a produzir interfaces funcionais mas visualmente pobres — "AI slop". Claude Code excele em raciocínio lógico e estrutura de código, mas não foi otimizado para decisões estéticas. Stitch 2.0 foi treinado especificamente em design systems, tipografia, animações e consistência visual.

O padrão de **separação de responsabilidades** é princípio fundamental de engenharia de software: não exija que um componente seja excelente em tudo. Aplicado a workflows de IA, significa orquestrar modelos especializados em vez de exigir que um LLM genérico execute todas as tarefas com qualidade uniforme.

**Resultado prático**: Protótipos visuais fidedignos em 48h (antes: 2 semanas de back-and-forth design ↔ dev).

## Como funciona / Como implementar

### Entender o Problema: "AI Slop" em Interfaces

Quando você pede apenas a Claude Code:
```
"Build a landing page for a SaaS product"
```

Você típicamente obtém:
- Layout genérico (hero + features + CTA — padrão de template)
- Cores defaults ou aleatórias
- Espaçamento uniforme, sem hierarquia
- Sem animações ou efeitos
- Tipografia sem intenção (padrão serif/sans serif)

**Por quê?** Claude Code prioriza funcionalidade e corretude sobre estética. Não há "estética correta" — há preferências, tendências, e contexto cultural que o modelo base não conhece bem.

### Arquitetura: Stitch 2.0 → MCP → Claude Code

```
┌────────────────────────────────────────────────────────────┐
│ Step 1: Design Generation (Google Stitch 2.0)             │
├────────────────────────────────────────────────────────────┤
│                                                            │
│ Input: "SaaS landing page for developer tools"           │
│                ↓                                           │
│ Stitch 2.0 gera:                                         │
│  • design.md (design system, colors, spacing)            │
│  • UI components em Figma-compatible format              │
│  • design-tokens.json (tipografia, paleta, etc)          │
│  • screenshots dos estados (normal, hover, active)       │
│                ↓                                           │
│ Output: design_artifact.json                             │
└────────────────────────────────────────────────────────────┘
                      ↓
             [MCP Bridge Handler]
                      ↓
┌────────────────────────────────────────────────────────────┐
│ Step 2: Logic Implementation (Claude Code)                │
├────────────────────────────────────────────────────────────┤
│                                                            │
│ Input: design_artifact.json + "Implement authentication" │
│                ↓                                           │
│ Claude Code (com Stitch MCP):                            │
│  • Lê design system                                       │
│  • Implementa componentes em React/Vue respeitando design │
│  • Conecta lógica de backend                             │
│  • Mantém consistência visual via design.md              │
│                ↓                                           │
│ Output: production-ready app (React + API + CSS)         │
└────────────────────────────────────────────────────────────┘
```

### Setup: Google Stitch MCP + Claude Code

**1. Instalar Stitch MCP**

```bash
# Clonar ou instalar via npm
git clone https://github.com/davideast/stitch-mcp
cd stitch-mcp
npm install
npm run build

# Ou via npm global
npm install -g stitch-mcp
stitch-mcp --init
```

**2. Configurar MCP no seu projeto Claude Code**

Arquivo: `.claude/mcp.json`
```json
{
  "mcpServers": {
    "stitch": {
      "command": "stitch-mcp",
      "args": ["--workspace", "./stitch-designs"],
      "env": {
        "STITCH_API_KEY": "${STITCH_API_KEY}",
        "STITCH_WORKSPACE_ID": "your-workspace-id"
      }
    }
  }
}
```

**3. Workflow no Claude Code**

```
@stitch-mcp Generate a landing page design for TechStartup
- Hero section with product demo video
- Feature cards with icons
- Pricing table
- CTA buttons (Sign Up, Try Free)

Claude Code recebe via MCP:
- design_artifact.json com design tokens
- component_specs.md com dimensões, cores, fonts
- asset_urls.json com ícones/imagens
```

### Exemplo Prático: SaaS Dashboard

**Fase 1: Stitch 2.0 Design**

```prompt
Generate a professional SaaS dashboard design:
- Header with logo, nav, user menu
- Sidebar with collapsible sections
- Main area with 4 cards: Revenue, Users, Churn, NPS
- Cards should have sparklines showing trends
- Dark theme with accent color #6366F1 (Indigo)
- Responsive: mobile sidebar collapses
- Include hover states and loading states
```

Stitch gera: `dashboard.design.json`
```json
{
  "design_system": {
    "colors": {
      "primary": "#6366F1",
      "background": "#0F172A",
      "surface": "#1E293B",
      "text": "#F1F5F9"
    },
    "typography": {
      "heading": "Inter, 600, 24px, line-height: 1.3",
      "body": "Inter, 400, 14px, line-height: 1.5"
    },
    "spacing": {
      "xs": "4px",
      "sm": "8px",
      "md": "16px",
      "lg": "32px"
    }
  },
  "components": [
    {
      "name": "DashboardCard",
      "states": ["default", "hover", "loading"],
      "props": ["title", "value", "trend", "trendPercentage"]
    }
  ],
  "screens": {
    "desktop": {...},
    "mobile": {...}
  }
}
```

**Fase 2: Claude Code com Stitch MCP**

```prompt
@stitch-mcp Use the dashboard design to implement:

1. React component structure (App, Sidebar, Header, CardGrid)
2. Fetch mock data from /api/metrics
3. Animate sparklines with Framer Motion (respect design tokens)
4. Implement responsive sidebar toggle
5. Add accessibility: ARIA labels, keyboard nav

Constraint: All colors/spacing/fonts MUST come from design.md
```

Claude gera: `src/components/Dashboard.tsx`
```typescript
// Claude carrega design tokens via MCP
import { designTokens } from '@stitch-mcp/design';

const DashboardCard = ({ title, value, trend }: Props) => (
  <div
    style={{
      backgroundColor: designTokens.colors.surface,
      padding: designTokens.spacing.md,
      borderRadius: designTokens.spacing.sm,
    }}
  >
    <h3 style={{ 
      fontFamily: designTokens.typography.heading.family,
      fontSize: designTokens.typography.heading.size,
    }}>
      {title}
    </h3>
    <p style={{ color: designTokens.colors.text }}>
      {value}
    </p>
    <Sparkline data={trend} />
  </div>
);

// Claude garante: nenhuma cor hardcoded, tudo vem do design
```

## Stack técnico

| Layer | Tool | Propósito |
|-------|------|----------|
| **Design** | Google Stitch 2.0 | UI/UX generation, design system |
| **Design Format** | design.md + design-tokens.json | Intermediate representation |
| **MCP Protocol** | stitch-mcp (CLI server) | Claude ↔ Stitch communication |
| **Code Generation** | Claude Code (com Stitch skill) | React/Vue/Svelte implementation |
| **CSS Management** | Tailwind (via design tokens) ou CSS-in-JS | Garantir fidelidade ao design |
| **Component Library** | shadcn/ui (built-in design support) ou Radix | Componentes acessíveis pré-estilizados |

**Links principais**:
- [davideast/stitch-mcp](https://github.com/davideast/stitch-mcp) — MCP bridge
- [google-labs-code/stitch-skills](https://github.com/google-labs-code/stitch-skills) — Skills para Claude
- [Google Stitch codelab](https://codelabs.developers.google.com/design-to-code-with-antigravity-stitch) — Tutorial oficial

## Código prático

### Implementar Design Tokens Bridge

```typescript
// stitch-bridge.ts - Sincronizar design tokens automaticamente

import { readFileSync, writeFileSync } from 'fs';
import { designTokensFromStitch } from '@stitch-mcp/api';

export async function syncDesignTokens() {
  // 1. Puxar design tokens do Stitch
  const tokens = await designTokensFromStitch('dashboard-design');
  
  // 2. Gerar CSS variables
  const cssVars = Object.entries(tokens.colors)
    .map(([key, value]) => `--color-${key}: ${value};`)
    .join('\n');
  
  // 3. Salvar como CSS
  writeFileSync('src/tokens.css', `:root { ${cssVars} }`);
  
  // 4. Ou gerar TypeScript para type-safety
  const tsTokens = `
export const designTokens = {
  colors: ${JSON.stringify(tokens.colors)},
  spacing: ${JSON.stringify(tokens.spacing)},
} as const;
`;
  writeFileSync('src/tokens.ts', tsTokens);
  
  console.log('✓ Design tokens synced');
}

// Rodar ao iniciar dev server
syncDesignTokens();
```

### Validar Fidelidade ao Design

```typescript
// validate-design-fidelity.ts - Garantir que código respeita design

import { designTokens } from './tokens';
import { parse } from 'css-in-js-parser';

export function validateComponentFidelity(component: React.FC) {
  const rendered = renderToString(<component />);
  const styles = extractComputedStyles(rendered);
  
  // Whitelist: cores, spacing, fonts SÓ do designTokens
  const allowedColors = Object.values(designTokens.colors);
  const allowedSpacing = Object.values(designTokens.spacing);
  
  styles.forEach(style => {
    if (style.color && !allowedColors.includes(style.color)) {
      throw new Error(
        `Color ${style.color} not in design tokens. Use: ${allowedColors.join(', ')}`
      );
    }
    if (style.padding && !allowedSpacing.includes(style.padding)) {
      throw new Error(
        `Spacing ${style.padding} not in design tokens`
      );
    }
  });
  
  console.log('✓ Component fidelity validated');
}
```

### Workflow Automático: Design → Code

```bash
#!/bin/bash
# design-to-code.sh

echo "1. Gerar design no Stitch 2.0..."
stitch-mcp generate --prompt "$1" --output ./stitch-designs/latest.json

echo "2. Sync design tokens..."
npx ts-node stitch-bridge.ts

echo "3. Chamar Claude Code com contexto..."
claude-code \
  --skill ./skills/stitch-mcp-skill \
  --context ./stitch-designs/latest.json \
  "Implement this design in React, respecting all design tokens"

echo "4. Validar fidelidade..."
npm run validate:design-fidelity

echo "✓ Design → Code complete!"
```

## Armadilhas e Limitações

### 1. Design Tokens Versionamento Desync
**Problema**: Stitch atualiza design tokens (ex: muda cor primária de #6366F1 para #8B5CF6). Seu código React ainda está usando a cor antiga hardcoded ou em cache. Você tem dois "designs" divergindo.

**Solução**:
```typescript
// NUNCA fazer:
const card = styled.div`
  background: #6366F1;  // ❌ Hardcoded, desync com Stitch
`;

// SEMPRE fazer:
const card = styled.div`
  background: var(--color-primary);  // ✓ Dinâmico
`;

// Com versionamento
// stitch-config.json
{
  "design_token_version": "1.2.0",
  "auto_update_on_stitch_change": true,
  "notify_on_breaking_changes": true
}
```

### 2. MCP Bridge Latência
**Problema**: Toda chamada do Claude a Stitch via MCP tem latência de rede (~500ms-2s). Se seu workflow invoca MCP 20+ vezes, você está adicionando minutos.

**Solução**:
```typescript
// Batch requests
const batchRequest = {
  operations: [
    { op: "get_colors", params: {} },
    { op: "get_spacing", params: {} },
    { op: "get_typography", params: {} },
  ]
};

// Uma chamada MCP, múltiplas operações
const results = await mcp.batch(batchRequest);
```

### 3. Responsive Design Mismatch
**Problema**: Stitch gera design para desktop (1920px). Claude implementa com media queries `max-width: 768px` para mobile. Mas o design original não tinha spec mobile — Claude está inventando.

**Solução**:
```prompt
@stitch-mcp Ensure design includes mobile specs
- Desktop: 1920px
- Tablet: 768px
- Mobile: 375px

Generate layout, spacing, and typography for ALL breakpoints
before handing to Claude Code.
```

### 4. Estilo vs. Componentes Confusion
**Problema**: Stitch gera "componentes" (Button, Card, Modal), mas Claude Code implementa como "styled divs". Quando você reutiliza o Card em 10 páginas, mudanças não propagam — cada instância é sua própria cópia.

**Solução**:
```typescript
// Usar component-level abstraction, não just styles
// design-components/Card.tsx
import { designTokens } from '@stitch-mcp/design';

export const Card = ({ children, variant = 'default' }: Props) => (
  <div style={designTokens.components.card[variant]}>
    {children}
  </div>
);

// Reutilizar em toda parte
import { Card } from '@design-components/Card';

// Se Stitch muda Card, toda aplicação atualiza
```

## Conexões

- [[skills-uxui-para-agentes-de-codigo|Skills UX/UI para Agentes de Código]] — Especialização de design
- [[repositorios-github-para-claude-code|Repositórios GitHub para Claude Code]] — Stitch MCP como skill
- [[mcp-tool-composition|MCP Tool Composition (Conceito)]] — Como MCP conecta ferramentas
- [[multi-agent-decomposition|Multi-Agent Decomposition (Conceito)]] — Teoria por trás da separação
- [[design-systems-em-codigo|Design Systems em Código]] — Implementação de design tokens
- [[prompt-engineering-agentes|Prompt Engineering para Agentes (Conceito)]] — Briefs para Claude

## Perguntas de Revisão

1. Por que delegar design visual a um LLM de código como Claude tende a produzir resultados de baixa qualidade estética? (Resposta: Claude foi treinado em código e documentação, não em design history, tendências e princípios estéticos — não tem "gosto")

2. Qual é o papel do MCP nesse workflow e por que ele é necessário para conectar Stitch 2.0 ao Claude Code? (Resposta: MCP padroniza chamadas de função entre sistemas — Claude chama "stitch.get_design_tokens()" e Stitch responde com JSON estruturado, sem copy-paste manual)

3. O que acontece se o Claude implementa componentes que não existem no design Stitch? (Resposta: Você tem dois sistemas de verdade — design drift. Solução: validação automática no CI)

## Histórico de Atualizações

- 2026-04-02: Nota criada a partir de Telegram
- 2026-04-11: Expandida com arquitetura detalhada, setup MCP, armadilhas de sync e component abstraction
