---
tags: []
source: https://x.com/nsthorat/status/2036287147179651477?s=20
date: 2026-04-02
---
# Hand Tracking via WebGPU

## Resumo
Hand tracking no browser pode ser executado inteiramente via WebGPU compute shaders, eliminando dependências pesadas e superando soluções baseadas em WASM+WebGL como o MediaPipe em velocidade e tamanho de pacote.

## Explicação
`micro-handpose` é uma biblioteca de rastreamento de mãos para o browser que roda exclusivamente via WebGPU, utilizando 15 shaders WGSL para executar dois estágios de inferência: detecção de palma (palm detection) e estimativa de landmarks (keypoints como ponta do polegar, nós dos dedos, etc.). A abordagem difere fundamentalmente do MediaPipe, que depende de WASM para execução de CPU e WebGL para GPU, resultando em um pipeline mais pesado e mais lento.

A vantagem arquitetural central é o uso de **compute shaders** diretamente no pipeline de GPU, sem intermediários. WebGPU compute shaders permitem paralelismo massivo para operações matriciais de redes neurais, o que explica os ganhos de latência: 2.2ms no M4 Pro Chrome versus 4.0ms do MediaPipe GPU, e 72ms no Safari/iPhone versus 97ms. O pacote total é de 74KB de JS (17KB gzip) + 7.7MB de pesos, contra 34MB do MediaPipe — uma redução de mais de 4x no tamanho do bundle.

Do ponto de vista de engenharia de ML para web, isso representa uma tendência importante: modelos de inferência leve sendo reescritos do zero para tirar proveito do WebGPU, em vez de adaptar pipelines existentes via compilação WASM. Zero dependências externas reduz risco de supply chain e simplifica integração em projetos existentes via `npm install @svenflow/micro-handpose`.

A API é deliberadamente minimalista — `createHandpose()` retorna um objeto com método `detect(video)` que devolve keypoints nomeados semanticamente (ex: `hands[0].keypoints.thumb_tip`), tornando o consumo dos dados de pose imediato sem necessidade de mapeamento manual de índices, como é comum em bibliotecas mais antigas.

## Exemplos
1. **Interfaces gestuais sem hardware especializado**: controle de apresentações, jogos ou aplicações criativas usando apenas a câmera do navegador, com latência abaixo de 3ms em desktops modernos.
2. **Aplicações de realidade aumentada web**: sobreposição de objetos virtuais nas mãos em experiências AR no browser, beneficiando-se da baixa latência para manter coerência visual.
3. **Acessibilidade**: navegação por gestos para usuários com limitações motoras que impedem uso de mouse/teclado, rodando localmente sem envio de dados para servidores.

## Relacionado
*(Nenhuma nota existente no vault para conectar no momento.)*

## Perguntas de Revisão
1. Por que compute shaders WebGPU produzem menor latência do que a abordagem WASM+WebGL do MediaPipe para inferência de redes neurais?
2. Quais são os dois estágios do pipeline de detecção de mãos em `micro-handpose` e qual a função de cada um?

## Histórico de Atualizações
- 2026-04-02: Nota criada a partir de Telegram