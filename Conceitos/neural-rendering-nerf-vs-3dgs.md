---
tags: [conceito, neural-rendering, 3d, graphics]
date: 2026-04-02
tipo: conceito
aliases: [NeRF, Gaussian Splatting, 3D Rendering]
---

# Neural Rendering: NeRF vs 3D Gaussian Splatting

## O que é
Comparação entre duas técnicas modernas de renderização 3D: NeRF (Neural Radiance Fields) usa redes neurais densas para representar cenas; 3D Gaussian Splatting usa primitivas gaussianas discretas. Ambos permitem reconstrução de cenas reais a partir de imagens 2D.

## Como funciona
**NeRF (2020)**:
- Entrada: múltiplas vistas fotográficas de uma cena
- Representação: MLP (multi-layer perceptron) que mapeia coordenadas 3D (x, y, z) + ângulo de visualização (θ, φ) → cor RGB + densidade
- Query: para renderizar um pixel, lance raio desde câmera, amostre pontos no raio, query MLP para densidade/cor, integre via volume rendering
- Velocidade: 10-50ms por frame (muito lento para real-time)
- Vantagem: representação compacta (MLP ~5MB), smooth/detalhado, generaliza bem
- Desvantagem: renderização é custosa, difícil de editar ou animar

**3D Gaussian Splatting (2023)**:
- Entrada: mesma coisa, múltiplas vistas 2D
- Representação: nuvem de gaussianas 3D (posição, covariância, opacidade, cor via harmônicos esféricos)
- Renderização: "splat" (projetar) cada gaussiana na tela 2D, acumule contribuições por alpha-blending
- Velocidade: 60-120 FPS em GPU moderna (real-time)
- Vantagem: rápido, renderização é standard rasterization, fácil de integrar em engines
- Desvantagem: muitas gaussianas (100k-1M), arquivo maior (~20-50MB)

## Pra que serve
- **NeRF**: quando você precisa renderização de altíssima qualidade e velocidade não importa (offline rendering, cinematics, visualização científica)
- **3D Gaussian Splatting**: quando você quer tempo real — games, AR, aplicações web, visualização interativa
- [[Reconstruir Cenas 3D em Tempo Real com Gaussian Splatting]] — aplicação prática de 3DGS

## Exemplo prático
Comparação lado-a-lado em pseudocódigo:

**NeRF Query** (lento, computacionalmente caro):
```python
def nerf_render_pixel(ray_origin, ray_direction, model):
    # Amostre 64 pontos ao longo do raio
    points = [ray_origin + t * ray_direction for t in linspace(0, far_plane, 64)]

    colors = []
    densities = []

    for point in points:
        color, density = model.forward(point, ray_direction)  # MLP query
        colors.append(color)
        densities.append(density)

    # Volume rendering integral
    final_color = integrate(colors, densities)
    return final_color
    # ~10ms por pixel em GPU
```

**3D Gaussian Splatting** (rápido, paralelizável):
```python
def splat_render(gaussians, camera):
    # Projetar cada gaussiana na tela
    image = zeros((height, width, 3))

    for gaussian in gaussians:
        # Gaussiana 3D → covariância 2D via projeção
        projected_cov_2d = project_covariance(gaussian.cov_3d, camera)

        # Renderizar splat (disso gaussiano 2D)
        for pixel in affected_pixels(gaussian.pos_2d, projected_cov_2d):
            alpha = gaussian.opacity * gaussian.color_importance[pixel]
            image[pixel] += alpha * gaussian.color

    return image
    # ~16ms para 1M gaussianas em GPU (5-8 FPS)
```

## Aparece em
- [[Reconstruir Cenas 3D em Tempo Real com Gaussian Splatting]] - implementação 3DGS prática
- [[captura-3d-estrutura-movimento]] - pipeline compartilhado para ambos

---
*Conceito extraído em 2026-04-02*
