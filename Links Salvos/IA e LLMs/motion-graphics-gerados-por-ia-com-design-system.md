---
tags: [motion-graphics, ia, design-system, remotion, video-generation]
source: https://x.com/jasondoesstuff/status/2039444150743867561?s=20
date: 2026-04-02
tipo: aplicacao
---

# Gerar Motion Graphics com Agente IA: Extrair Design System e Animar com Remotion

## O que e

Agente Claude Code extrai design system de projeto existente em markdown. Usa como contexto para gerar animações de app interactions com Remotion (React video library). Resultado: b-roll 16:9 com tokens visuais consistentes, sem motion designer.

## Como implementar

**Etapa 1: Extrair design system** (agente lê projeto):
```bash
# Instruir Claude Code a fazer isso:
@claude "Analyze my project and extract:
- All color tokens (variables, hex values)
- Typography (fonts, sizes, line heights, weights)
- Spacing scale (padding, margin standard values)
- Component library (buttons, cards, inputs)
- Animation easing curves and durations
Output as design-system.md"
```

Claude produz (exemplo):
```markdown
# Design System

## Colors
- primary: #0066CC
- success: #22C55E
- error: #EF4444
- bg-light: #F9FAFB
- text-dark: #111827

## Typography
- font-family: Inter, sans-serif
- h1: 32px, 700, line-height 1.2
- body: 16px, 400, line-height 1.5

## Spacing
- xs: 4px
- sm: 8px
- md: 16px
- lg: 24px
- xl: 32px

## Animations
- standard-curve: cubic-bezier(0.4, 0, 0.2, 1)
- duration-short: 150ms
- duration-default: 300ms
```

**Etapa 2: Instalar Remotion**:
```bash
npm install remotion
npm install @remotion/cli
```

**Etapa 3: Criar animações** (agente gera código Remotion):
```javascript
// user-onboarding-animation.tsx
import React from 'react';
import {
  AbsoluteComposition,
  Sequence,
  spring,
  interpolate,
  Easing,
} from 'remotion';

// Importar design system
import { designSystem } from './design-system';

export const UserOnboardingAnimation = () => {
  const { duration, fps } = {
    duration: 10,
    fps: 30,
  };

  return (
    <AbsoluteComposition
      width={1920}
      height={1080}
      durationInFrames={duration * fps}
      fps={fps}
      style={{ backgroundColor: designSystem.colors['bg-light'] }}
    >
      {/* Sequence 1: Logo animado aparecendo */}
      <Sequence from={0} durationInFrames={60}>
        <AnimatedLogo
          color={designSystem.colors.primary}
          easing={designSystem.animations['standard-curve']}
        />
      </Sequence>

      {/* Sequence 2: Botão com ripple */}
      <Sequence from={120} durationInFrames={90}>
        <AnimatedButton
          text="Get Started"
          color={designSystem.colors.primary}
          spacing={designSystem.spacing.md}
        />
      </Sequence>

      {/* Sequence 3: Transição para dashboard */}
      <Sequence from={210} durationInFrames={120}>
        <DashboardTransition
          colors={designSystem.colors}
          easing={designSystem.animations['standard-curve']}
        />
      </Sequence>
    </AbsoluteComposition>
  );
};
```

**Etapa 4: Render video**:
```bash
npx remotion render user-onboarding-animation.tsx output.mp4
# Gera vídeo 1920x1080 16:9, pronto para YouTube
```

**Fluxo automático** (agente faz tudo):
```bash
@claude "Generate a 16:9 video animation showing:
1. App loading with spinner
2. Authentication flow (login form)
3. Dashboard appearing
4. Key features highlighted

Use design-system.md for all visual tokens.
Output: Remotion TypeScript file ready to render."
```

Claude gera arquivo completo, você apenas:
```bash
npx remotion render generated-animation.tsx output.mp4
```

**Mockups de referência** (recreate existing UIs):
```javascript
// Recreate Slack sidebar as animation
export const SlackAnimationDemo = () => {
  return (
    <AbsoluteComposition ...>
      <SlackSidebar
        channels={['general', 'random', 'design']}
        activeChannel="general"
        animate={true}
        colors={designSystem.colors}
      />
      <SlackChat
        messages={[...]}
        animate={true}
      />
    </AbsoluteComposition>
  );
};
```

## Stack e requisitos

- **Node.js**: 16+
- **Remotion**: 4.0+
- **FFmpeg**: 4.4+ (para rendering)
- **React**: 18.0+
- **Rendering time**: ~2 minutos por 10s video (depende da complexidade)
- **Disk space**: 100-500MB por vídeo renderizado
- **Design system**: arquivo Markdown ou JSON

## Armadilhas e limitacoes

- **Extração incompleta**: Agente pode miss tokens CSS obscuros ou comportamentos dinâmicos (hover, focus states).
- **Interatividade**: Remotion é para video output; não é app interativa. Para demos interativas, usar Framer Motion ou Three.js.
- **Performance rendering**: Videos complexos (muitas animações, 4K) levam tempo; use preview mode (`--prores=h265`) para otimizar.
- **Sincronização áudio**: Remotion suporta áudio, mas sincronizar com narração requer timings precisos.
- **Animação natural**: LLM às vezes gera animações mecanicamente perfeitas mas não naturais; humano precisa revisar easing curves.

## Conexoes

[[Nothing Style UI Prompting]] [[Claude Code Melhores Praticas]] [[Modelos de Codificacao Multimodal]]

## Historico

- 2026-04-02: Nota criada
- 2026-04-02: Reescrita para template aplicacao