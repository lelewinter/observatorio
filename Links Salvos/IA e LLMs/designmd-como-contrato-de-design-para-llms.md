---
tags: [design-systems, llm, code-generation, ui, prompt-engineering, css]
source: https://x.com/GithubProjects/status/2039274093657325783?s=20
date: 2026-04-02
tipo: aplicacao
---

# DESIGN.md: Contrato Explícito de Sistema de Design para Agentes de Código

## O que é

DESIGN.md é um arquivo Markdown simples na raiz do projeto que funciona como **contrato de design** entre humanos e agentes de IA (Claude, Cursor, Copilot). Documenta em linguagem natural todo o design system: paleta de cores, tipografia, spacing, componentes, estado de UI, tom de voz e princípios de acessibilidade. Diferente de Figma exports ou JSON configs, é um documento legível por LLMs que elimina alucinações visuais e inconsistências de design em código gerado.

O conceito emergiu em 2025 como resposta prática ao problema: agentes de código precisam entender seu design system em contexto. DESIGN.md soluciona isso com zero overhead — apenas Markdown puro que você já versiona no Git.

## Por que importa

Quando você pede para uma IA gerar UI sem DESIGN.md, ela inventa:
- Cores aleatórias que não combinam com sua brand
- Tamanhos de fonte inconsistentes
- Spacing que desrespeita sua escala
- Componentes duplicados com variações ligeiramente diferentes

Com DESIGN.md no contexto, o agente tem referência imediata e gera código **on-brand** na primeira tentativa. Isso economiza ciclos de refinamento e reduz o que chamo de "débito de contexto de IA" — a divergência entre intenção visual e código gerado.

Para equipes, DESIGN.md também funciona como **documentação viva**: mudanças no design system ficam registradas, e qualquer novo agente que trabalhe com o projeto tem acesso imediato aos padrões.

## Como funciona / Como implementar

### Estrutura típica de DESIGN.md

```markdown
# Design System

## 1. Color Palette

### Semantic Colors
- **Primary**: #007AFF (azul, ações principais)
- **Secondary**: #5856D6 (destaque secundário)
- **Success**: #34C759 (estados positivos)
- **Warning**: #FF9500 (alertas não-críticos)
- **Danger**: #FF3B30 (erros, ações destrutivas)
- **Neutral-50**: #F9FAFB (backgrounds claros)
- **Neutral-900**: #111827 (texto principal)

Dark Mode: inverter contraste, manter relações semânticas.

## 2. Typography

- **Font Family**: "Inter", sans-serif (default), "Menlo", monospace (código)
- **Sizes**: 
  - H1: 32px, weight 700, line-height 1.2
  - H2: 24px, weight 600, line-height 1.3
  - Body: 16px, weight 400, line-height 1.5
  - Small: 12px, weight 400, line-height 1.4
  - Code: 13px, weight 500, monospace

## 3. Spacing Scale

Escala em múltiplos de 4px: 4, 8, 12, 16, 24, 32, 48, 64px

- Padding interno de botões: 8px horizontal, 12px vertical
- Margin entre elementos: 16px ou 24px
- Gap em grids: 16px

## 4. Components

### Button (Primary)
- Background: #007AFF
- Text: white, 14px, semibold
- Padding: 12px 16px
- Border Radius: 6px
- States:
  - Hover: bg = #0051D5 (darkened)
  - Disabled: opacity 0.5, cursor not-allowed
  - Active: box-shadow: inset 0 1px 3px rgba(0,0,0,0.2)

### Input
- Border: 1px solid #D1D5DB
- Padding: 8px 12px
- Border Radius: 4px
- Focus: border #007AFF, box-shadow: 0 0 0 3px rgba(0,122,255,0.1)
- Placeholder: #9CA3AF

## 5. Tone & Voice

- **Tone**: Profissional mas amigável
- **Quando ser imperativo**: Instruções de ação ("Clique aqui", "Confirmar")
- **Quando ser educado**: Confirmações, avisos ("Por favor, confirme sua senha")
- **Evitar**: Gírias, múltiplos exclamadores, tom condescendente

## 6. Princípios de Design

- **Acessibilidade**: Ratio de contraste mínimo 4.5:1 para texto
- **Mobile-first**: Layouts responsive começando em 320px
- **Dark Mode**: Suportado, inverte paleta mantendo semântica
- **Performance**: Preferir CSS puro a imagens quando possível
```

### Processo de integração

1. **Criar DESIGN.md** na raiz do projeto (2-5KB ideal)
2. **Fazer upload** ao iniciar sessão com agente de código (Claude, Cursor)
3. **Mencionar no prompt**: "Use o arquivo DESIGN.md fornecido como referência para UI"
4. **Code review**: Comparar componentes gerados contra especificação
5. **Manter atualizado**: Toda mudança no design system → atualizar DESIGN.md no mesmo commit

### Exemplo prático: gerar botão com DESIGN.md

**Sem DESIGN.md:**
```
User: Gera um botão de confirmação
```
→ IA gera botão com cores aleatórias, padding arbitrário, sem suporte a dark mode.

**Com DESIGN.md:**
```
User: Gera um botão de confirmação (use DESIGN.md)
```
→ IA gera:
```jsx
export const ConfirmButton = ({ onClick, disabled }) => (
  <button
    onClick={onClick}
    disabled={disabled}
    style={{
      background: disabled ? 'rgba(0, 122, 255, 0.5)' : '#007AFF',
      color: 'white',
      padding: '12px 16px',
      borderRadius: '6px',
      border: 'none',
      fontSize: '14px',
      fontWeight: 600,
      cursor: disabled ? 'not-allowed' : 'pointer',
      transition: 'background 0.2s',
    }}
    onMouseEnter={(e) => !disabled && (e.target.style.background = '#0051D5')}
    onMouseLeave={(e) => !disabled && (e.target.style.background = '#007AFF')}
  >
    Confirmar
  </button>
);
```

Direto, sem ciclos de refinamento.

## Stack técnico

- **Formato**: Markdown puro (`.md`)
- **Versionamento**: Git (parte do repositório)
- **Entrega ao LLM**: 
  - Upload via Claude/Cursor/Copilot
  - Incluir no prompt via prompt engineering
  - Armazenar em contexto de sessão
- **Validação**: Code review visual + testes de screenshot (para garantir aderência)
- **Integração contínua**: (opcional) Scripts que comparam CSS gerado contra especificação

**Ferramentas relacionadas:**
- [awesome-design-md](https://github.com/VoltAgent/awesome-design-md) — coleção de exemplos de DESIGN.md
- Storybook MCP — integra design systems a LLMs via Model Context Protocol
- Story UI — prototipagem integrada com design systems

## Código prático

### Template mínimo para copiar

```markdown
# Design System [Seu Projeto]

## Colors
- Primary: #007AFF
- Success: #34C759
- Danger: #FF3B30
- Neutral: #6B7280

## Typography
- Base: 16px, Inter, line-height 1.5
- Heading: 24px, weight 600
- Code: 12px, monospace

## Spacing
Grid: 4px. Usar multíplos: 4, 8, 12, 16, 24, 32px

## Components
- Button: 12px vertical, 16px horizontal padding, 6px border-radius
- Input: 8px vertical, 12px horizontal padding, 1px border
- Card: 16px padding, 8px border-radius

## Acessibilidade
- Contraste mínimo: 4.5:1
- Suporte a teclado: tab-order lógica
- Alt text obrigatório em imagens
```

### Script para validar conformidade (Node.js)

```javascript
// validate-design.js
const fs = require('fs');
const path = require('path');

function extractColors(designMd) {
  const colorRegex = /(?:Primary|Secondary|Success|Danger|Neutral):\s*(#[0-9A-F]{6})/gi;
  return [...designMd.matchAll(colorRegex)].map(m => m[1]);
}

function validateCSSAgainstDesign(cssPath, designPath) {
  const designMd = fs.readFileSync(designPath, 'utf8');
  const css = fs.readFileSync(cssPath, 'utf8');
  
  const designColors = extractColors(designMd);
  const orphanedColors = [];
  
  // Verifica se cores de DESIGN.md estão sendo usadas no CSS
  designColors.forEach(color => {
    if (!css.includes(color)) {
      orphanedColors.push(color);
    }
  });
  
  if (orphanedColors.length > 0) {
    console.warn(`⚠️ Cores definidas mas não usadas: ${orphanedColors.join(', ')}`);
  } else {
    console.log('✅ Todas as cores são utilizadas');
  }
}

validateCSSAgainstDesign('./style.css', './DESIGN.md');
```

## Armadilhas e limitações

### 1. **DESIGN.md desatualizado cria "débito de contexto"**

Problema: Design system evolui (você muda primary color de #007AFF para #2563EB), mas DESIGN.md não é atualizado. Agentes continuam gerando UI com cor antiga.

Mitigação:
- **Code review obrigatório** de componentes gerados
- **Teste visual** antes de merge (screenshot comparison)
- **Integração contínua** que valida conformidade
- **Versionar DESIGN.md** no mesmo commit que mudanças de design

### 2. **Especificidade insuficiente não agrega valor**

Arquivo muito genérico ("use cores bonitas", "fonts legíveis") não orienta LLM. Agente continua inventando.

Exemplo ruim:
```
## Colors
Use tons que combinem.

## Typography
Fontes legíveis.
```

Exemplo bom:
```
## Colors
Primary: #007AFF (azul Apple-style)
Success: #34C759 (verde confirmação)
Contrast ratio mínimo: 4.5:1

## Typography
Base: 16px Inter, line-height 1.5
Headings: 600 weight, não use bold em parágrafos
```

Mitigação: **Ser específico**. Hex codes, pixel values, nome de fontes, ratios exatos.

### 3. **DESIGN.md não substitui Figma para componentes complexos**

DESIGN.md é ótimo para:
- Paleta de cores
- Escala tipográfica
- Spacing rules
- Princípios

DESIGN.md é fraco para:
- Layout de cards complexos (use screenshots de referência)
- Animações (descrever em pseudocódigo)
- Ícones (link para iconset, não descrever pixel-por-pixel)

Mitigação: **Híbrido**. DESIGN.md + links para Figma/componentes reference.

### 4. **Mudanças frequentes requerem manutenção disciplinada**

Se você atualiza design system todo mês mas só mexe em DESIGN.md a cada trimestre, o arquivo fica obsoleto rapidamente.

Mitigação:
- Incluir atualização de DESIGN.md na **definition of done** de design changes
- Usar **git hooks** (pre-commit) para avisar se alterou CSS mas não DESIGN.md
- Revisar DESIGN.md **quinzenalmente** com time de design

### 5. **Agentes podem ainda alucivar com componentes bespoke**

DESIGN.md define o sistema, mas agente pode inventar componentes que não existem ("um card com 3 abas e um gráfico dentro"). 

Mitigação:
- **Listar explicitamente** componentes disponíveis em DESIGN.md
- **Dizer o que NÃO fazer** ("não criar botões com gradientes", "evitar efeitos de sombra além de...")
- Usar **prompts negativos**: "Ignore cores não listadas em DESIGN.md"

## Conexões

[[estrutura-claude-md-menos-200-linhas|Documentação concisa — DESIGN.md é uma extensão de conventions como README.md]]
[[falhas-criticas-em-apps-vibe-coded|Qualidade em vibe coding — evita o "é bonito?" com spec clara]]
[[geracao-automatizada-de-prompts|Prompts estruturados — DESIGN.md é um exemplo de context estruturado]]
[[prompt-engineering-efetivo|Prompt Engineering — técnicas para usar DESIGN.md no contexto]]
[[resumo-com-estrutura-markdown|Estrutura Markdown — formato ideal para LLMs]]

## Histórico

- 2026-04-02: Nota criada
- 2026-04-11: Expandida com exemplos, scripts, armadilhas técnicas e conexões
