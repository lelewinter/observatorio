---
tags: []
source: https://x.com/tom_doerr/status/2039400710962356575?s=20
date: 2026-04-02
---
# 3D Gaussian Splatting

## Resumo
3D Gaussian Splatting é uma técnica de representação e renderização de cenas 3D que utiliza gaussianas volumétricas como primitivas, permitindo reconstrução e síntese de imagens em tempo real a partir de fotos. OpenSplat é uma implementação open source dessa técnica em C++.

## Explicação
3D Gaussian Splatting (3DGS) é uma abordagem de representação de cenas 3D que substitui métodos volumétricos tradicionais (como NeRF, baseado em redes neurais densas) por um conjunto de gaussianas 3D posicionadas no espaço. Cada gaussiana possui atributos como posição, covariância (forma e orientação), opacidade e cor (representada via harmônicos esféricos para capturar efeitos de iluminação dependentes do ponto de vista). O processo de renderização consiste em "splatar" essas gaussianas na imagem 2D, acumulando contribuições de forma diferenciável.

O pipeline típico parte de uma nuvem de pontos esparsa gerada por Structure-from-Motion (SfM) a partir de imagens 2D, e otimiza iterativamente os parâmetros das gaussianas por gradiente descendente para minimizar o erro de reconstrução fotométrico. O resultado é uma representação compacta e eficiente que permite renderização em tempo real (dezenas a centenas de FPS), o que representa uma vantagem significativa sobre NeRFs tradicionais.

O projeto **OpenSplat** (github.com/pierotofy/OpenSplat) é uma implementação open source em C++ que torna a técnica acessível para uso local, sem dependência de infraestruturas proprietárias. Implementações em C++ tendem a oferecer melhor desempenho e portabilidade em relação a implementações puramente em Python/PyTorch, facilitando integração em pipelines de produção, aplicações embarcadas ou ferramentas de visualização 3D independentes.

A relevância prática do 3DGS se estende a reconstrução de cenas para realidade aumentada/virtual, digitalização de patrimônio cultural, geração de conteúdo 3D a partir de vídeos e simulações para robótica e veículos autônomos.

## Exemplos
1. **Digitalização de ambientes**: fotografar um ambiente com um smartphone e reconstruir uma cena 3D navegável em tempo real usando OpenSplat localmente.
2. **Realidade aumentada**: usar a representação gaussiana como base para inserir objetos virtuais em cenas reais com oclusão e iluminação corretas.
3. **Geração de datasets sintéticos**: renderizar novas vistas de uma cena reconstruída para aumentar datasets de treinamento de modelos de visão computacional.

## Relacionado
*(Nenhuma nota existente no vault para conectar no momento.)*

## Perguntas de Revisão
1. Qual é a diferença fundamental entre 3D Gaussian Splatting e NeRF em termos de representação da cena e velocidade de renderização?
2. Por que usar harmônicos esféricos nos atributos de cor de cada gaussiana, e que fenômeno físico isso modela?

## Histórico de Atualizações
- 2026-04-02: Nota criada a partir de Telegram