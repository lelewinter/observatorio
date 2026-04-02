---
tags: [3d, web, scroll-animation, landing-page, ai-prompt, frontend]
source: https://x.com/viktoroddy/status/2037839395638899136?s=20
date: 2026-04-02
---
# Landing Page 3D Scroll-Based

## Resumo
Uma landing page scroll-based 3D é uma interface web onde elementos tridimensionais se animam e transformam em resposta ao scroll do usuário, criando experiências imersivas. Com prompts de IA, qualquer pessoa pode gerar esse tipo de experiência sem expertise técnica avançada.

## Explicação
Landing pages scroll-based 3D combinam duas técnicas: **scroll-driven animations** (onde o progresso da página controla o estado de animações) e **renderização 3D no browser** (via WebGL, Three.js ou CSS 3D transforms). O resultado é uma narrativa visual progressiva — o usuário "navega" por um espaço tridimensional simplesmente rolando a página.

O ponto central do post é a **democratização via prompts de IA**: ferramentas como Claude, GPT-4 ou Cursor permitem que desenvolvedores sem experiência em Three.js ou GSAP gerem código funcional para essas interfaces através de prompts descritivos. Isso reduz a barreira técnica de semanas de desenvolvimento para horas.

Do ponto de vista técnico, a implementação típica envolve: uma biblioteca 3D (Three.js, Spline, ou R3F — React Three Fiber), um controlador de scroll (ScrollTrigger do GSAP ou a nativa Scroll-Driven Animations API do CSS), e lógica de interpolação que mapeia `scrollY` para propriedades de câmera, rotação e posição de objetos na cena.

A relevância prática é alta em contextos de produto e marketing: páginas com scroll 3D aumentam tempo de engajamento e percepção de sofisticação da marca. Com IA gerando o boilerplate, o custo de produção dessas experiências caiu drasticamente.

## Exemplos
1. **Apresentação de produto**: Um smartphone que gira 360° enquanto o usuário rola, revelando features em cada ângulo — gerado via prompt descrevendo câmera orbital + hotspots de texto.
2. **Portfólio interativo**: Cena 3D de um escritório onde objetos "aparecem" em profundidade conforme o scroll avança, criado com Spline + ScrollTrigger via código gerado por IA.
3. **Hero section imersiva**: Partículas ou terreno 3D que se deformam em resposta ao scroll, implementado com Three.js + shader GLSL gerado por prompt no Cursor/Copilot.

## Relacionado
*(Nenhuma nota existente no vault para conectar no momento.)*

## Perguntas de Revisão
1. Quais são as principais bibliotecas para implementar scroll-driven animations com 3D no browser, e quais são os trade-offs entre elas?
2. Como a geração de código via prompts de IA muda o fluxo de trabalho de um desenvolvedor frontend ao construir experiências 3D complexas?

## Histórico de Atualizações
- 2026-04-02: Nota criada a partir de Telegram