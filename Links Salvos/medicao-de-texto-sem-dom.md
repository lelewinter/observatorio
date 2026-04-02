---
tags: []
source: https://x.com/_chenglou/status/2037713766205608234?s=20
date: 2026-04-02
---
# Medição de Texto Sem DOM

## Resumo
Algoritmo de medição tipográfica implementado em TypeScript puro que calcula dimensões de texto sem depender do DOM ou do CSS, eliminando reflow no browser.

## Explicação
Medir texto com precisão é um dos problemas mais antigos e custosos do desenvolvimento de interfaces. Historicamente, a única forma confiável de saber o tamanho real de um bloco de texto era inserir elementos no DOM e consultar propriedades como `getBoundingClientRect()` ou `offsetWidth`, operações que forçam o browser a executar reflow — um processo síncrono e potencialmente bloqueante que recalcula o layout inteiro da página. Isso cria um gargalo fundamental para qualquer sistema de layout dinâmico ou de alta performance.

A proposta descrita por Cheng Lou é um algoritmo de medição de texto implementado inteiramente em TypeScript userland — ou seja, sem chamar APIs do DOM, sem CSS e sem depender do motor de renderização do browser. O algoritmo é descrito como rápido, preciso e abrangente o suficiente para ser usado no layout de páginas inteiras. Isso implica que ele reimplementa, em software, a lógica de quebra de linha, espaçamento entre glifos (kerning/tracking), métricas de fonte e wrapping que normalmente residem no browser ou no sistema operacional.

Por que isso importa: desacoplar medição de texto do DOM abre caminho para renderização em ambientes não-browser (Node.js, workers, servidores), para sistemas de layout determinístico e reproduzível, e para engines de UI que operam fora do modelo tradicional de HTML/CSS. É uma peça fundacional para canvas renderers, PDF generators, editores de texto customizados e qualquer interface que precise de controle preciso sobre tipografia sem pagar o custo do pipeline de layout do browser.

A relevância conceitual é ainda maior que a implementacional: mesmo que a implementação específica seja substituída futuramente, o conceito de medir tipografia de forma independente do ambiente de renderização representa uma mudança de paradigma na engenharia de UI — aproximando o frontend de modelos usados em engines gráficas nativas (como Flutter, Skia ou engines de jogos) onde o layout é calculado de forma programática e determinística.

## Exemplos
1. **Server-side layout**: Calcular o layout de uma página inteira no servidor antes de enviá-la ao cliente, sem precisar de um browser headless (ex: Puppeteer), útil para geração de PDFs ou imagens de alta fidelidade.
2. **Canvas / WebGL UI**: Construir interfaces renderizadas em `<canvas>` ou WebGL onde não existe DOM, mas é necessário posicionar texto com precisão tipográfica real.
3. **Editores de texto customizados**: Implementar cursor positioning, seleção de texto e wrapping em editores ricos (como Notion, Linear) sem depender das medições inconsistentes entre browsers.

## Relacionado
*(Nenhuma nota existente no vault para conectar no momento.)*

## Perguntas de Revisão
1. Por que consultar o DOM para medir texto causa reflow, e quais são as consequências de performance disso em layouts dinâmicos?
2. Quais informações tipográficas (métricas de fonte, kerning, line-height) um algoritmo desse tipo precisa reimplementar para ser preciso sem depender do browser?

## Histórico de Atualizações
- 2026-04-02: Nota criada a partir de Telegram