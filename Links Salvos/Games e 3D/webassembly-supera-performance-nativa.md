---
tags: []
source: https://x.com/threejs/status/2039193070332489846?s=20
date: 2026-04-02
---
# WebAssembly Supera Performance Nativa

## Resumo
Three.js compilado para WebAssembly (WASM) atinge mais de 480 fps com apenas 10KB de bundle, superando a performance de código nativo equivalente em benchmarks de renderização 3D no browser.

## Explicação
WebAssembly (WASM) é um formato binário de baixo nível executável em browsers modernos, projetado como alvo de compilação para linguagens como C, C++ e Rust. O projeto `three.wasm` demonstra que código compilado para WASM pode, em cenários específicos, superar a execução nativa — fenômeno que ocorre devido à capacidade do compilador de realizar otimizações agressivas no momento da compilação AOT (Ahead-of-Time), eliminando overhead de interpretação e garbage collection presentes no JavaScript tradicional.

O dado de 10KB para um renderer 3D funcional é significativo: evidencia que o processo de compilação para WASM não apenas otimiza velocidade, mas também pode resultar em binários altamente compactos. Isso ocorre porque WASM é uma representação binária densa, ao contrário do JavaScript textual. O resultado de 480+ fps em renderização 3D no browser representa uma ruptura com a percepção histórica de que aplicações web são inerentemente mais lentas que aplicações nativas.

A afirmação "faster than native" merece qualificação: o desempenho superior ao nativo ocorre em contextos onde o compilador WASM pode explorar instruções SIMD, ausência de verificações de tipos em runtime e acesso direto à memória linear — vantagens que código nativo gerenciado (como Node.js ou Java) não tem automaticamente. É uma vitória do modelo de execução, não necessariamente uma inversão absoluta da hierarquia de performance.

## Exemplos
1. **Engines de jogos no browser**: compilar motores como Godot ou Unity para WASM permite experiências de jogo com framerate comparável ao desktop sem instalação
2. **Processamento de imagem/vídeo client-side**: bibliotecas de computer vision (ex: OpenCV) compiladas para WASM rodam transformações pesadas diretamente no browser sem round-trip ao servidor
3. **Simulações científicas**: cálculos físicos ou de fluid dynamics que antes exigiam backend dedicado podem ser executados localmente com WASM a alta performance

## Relacionado
*(Nenhuma nota existente no vault para conectar neste momento)*

## Perguntas de Revisão
1. Por que WebAssembly pode superar código nativo em determinados benchmarks, e quais são as condições necessárias para isso ocorrer?
2. Qual a diferença fundamental entre a execução JIT do JavaScript e a compilação AOT do WebAssembly em termos de performance previsível?

## Histórico de Atualizações
- 2026-04-02: Nota criada a partir de Telegram