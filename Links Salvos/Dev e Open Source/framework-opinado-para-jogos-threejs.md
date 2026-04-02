---
tags: [threejs, gamedev, framework, ferramentas, vibe-coding, open-source]
source: https://x.com/alightinastorm/status/2038393642130272762?s=20
date: 2026-04-02
---
# Framework Opinado para Jogos ThreeJS

## Resumo
GGEZ é um framework open source que adiciona camadas de abstração sobre ThreeJS — editor de mundo, estúdio de animação e CLI — para facilitar o desenvolvimento de jogos 3D no browser com integração nativa a agentes de IA (Codex).

## Explicação
O GGEZ posiciona-se como o equivalente do Next.js para ThreeJS: assim como Next.js não substitui React mas adiciona convenções, roteamento e ferramentas de produção, o GGEZ não substitui ThreeJS mas empacota o que está faltando para construir jogos funcionais. O runtime oferece uma camada de abstração sobre bibliotecas de física, character controllers e carregamento automático de cenas e animações — mas sem magia: tudo ainda é ThreeJS por baixo.

O componente mais diferenciado é o Trident, um editor visual de mundo que exporta arquivos JSON e assets GLB, permitindo que designers e desenvolvedores posicionem objetos, esculpam terreno e configurem física sem depender exclusivamente de código. Isso resolve um problema clássico de desenvolvimento 3D no browser: a dificuldade de posicionar objetos no espaço 3D iterando apenas via código e prompts. O Animation Studio complementa isso com suporte a state machines, blend trees multidimensionais, edição de keyframes e — notavelmente — root motion, feature raramente disponível em ferramentas web.

A integração com Codex (via ChatGPT) é tratada como cidadã de primeira classe: cada módulo principal (World Editor, Animation Studio) possui um agente dedicado. Isso enquadra o GGEZ explicitamente no paradigma de "vibe coding" — desenvolvimento orientado a intenção e linguagem natural, onde o desenvolvedor descreve o que quer e o agente gera ou ajusta o resultado. A escolha de Bun como runtime e o CLI `bunx create-ggez` reforçam o foco em experiência de desenvolvedor moderna e setup zero.

Por ser assumidamente experimental e em desenvolvimento ativo, o GGEZ é uma aposta de produtividade para prototipagem rápida de jogos, não uma solução de produção estável. O trade-off é explícito: velocidade de iteração em troca de estabilidade garantida.

## Exemplos
1. **Prototipagem de jogo 3D assistida por IA**: usar o agente Codex do Trident para descrever em linguagem natural uma cena ("floresta com colinas e um castelo ao fundo") e gerar automaticamente o JSON de cena e assets GLB correspondentes.
2. **Animação de personagem com root motion**: configurar no Animation Studio um blend tree para transição entre idle/walk/run com root motion, eliminando o deslizamento de personagem comum em implementações manuais no ThreeJS.
3. **Setup instantâneo via CLI**: rodar `bunx create-ggez meu-jogo` para ter um ambiente de desenvolvimento completo com physics, editor e animation studio integrados sem configuração manual.

## Relacionado
*(Nenhuma nota existente no vault para conectar no momento.)*

## Perguntas de Revisão
1. Qual é a diferença arquitetural entre usar GGEZ e usar ThreeJS puro com Rapier/Cannon para física — e quando cada abordagem é mais adequada?
2. O paradigma de "vibe coding" aplicado a game dev (posicionamento via linguagem natural) resolve o problema de iteração 3D ou apenas transfere a imprecisão do código para o prompt?

## Histórico de Atualizações
- 2026-04-02: Nota criada a partir de Telegram