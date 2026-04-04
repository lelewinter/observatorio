---
tags: [web-3d, ia-agentes, omma, spline, webgl, interactivo-design, vibe-coding]
source: https://x.com/Aurelien_Gz/status/2036568382380585310?s=20
date: 2026-04-02
tipo: aplicacao
---

# Gerar Sites 3D Interativos com Agentes de IA

## O que é
Agentes IA (tipo Omma) geram websites 3D completos em linguagem natural: "landing page com produto rotacionável em fundo de galaxia". Output: código Three.js/Spline, pronto para deploy.

## Como implementar
**Fluxo com Omma.build**:

1. **Criar projeto**:
```
// Interface web, no browser
Omma Dashboard → Create New → "3D Web Experience"
```

2. **Descrever em chat**:
```
Prompt:
"Create a landing page for a AI music production tool.
Include:
- Hero section with 3D vinyl record spinning
- Product features listed as interactive cards that reveal on scroll
- Pricing table with 3D price tags
- Call-to-action button that lights up on hover
- Dark theme with neon accents (purple + cyan)
- Mobile responsive"
```

3. **Agente processa e gera**:
   - Lê prompt
   - Decompõe em componentes (hero, cards, pricing, button)
   - Gera 3D modelos via texto-to-3D
   - Posiciona em layout
   - Escreve interações (scroll triggers, hover effects)
   - Otimiza para mobile/desktop

4. **Resultado**:
```html
<!-- Omma output (Spline-compatible) -->
<!DOCTYPE html>
<html>
<head>
    <script src="https://cdn.spline.design/spline.js"></script>
</head>
<body>
    <canvas id="canvas3d"></canvas>

    <script>
    const spline = new Spline.Application('canvas3d', {
        scene: 'generated-scene-uuid',
        // Interações JS auto-geradas
        interactions: [
            {
                trigger: 'scroll',
                target: 'cards-container',
                animation: 'reveal-fade-in',
                duration: 800
            },
            {
                trigger: 'hover',
                target: 'cta-button',
                animation: 'glow-pulse',
                duration: 300
            }
        ]
    });
    </script>
</body>
</html>
```

**Fluxo manual com Three.js (mais controle)**:

```javascript
// Se quiser customizar além do Omma output
import * as THREE from 'three';

const scene = new THREE.Scene();
const camera = new THREE.PerspectiveCamera(75, window.innerWidth/window.innerHeight, 0.1, 1000);
const renderer = new THREE.WebGLRenderer({ antialias: true, alpha: true });

// Hero: vinyl record 3D
const vinylGroup = new THREE.Group();
const vinylGeometry = new THREE.CylinderGeometry(2, 2, 0.05, 64);
const vinylMaterial = new THREE.MeshStandardMaterial({
    color: 0x000000,
    roughness: 0.2,
    metalness: 0.8
});
const vinyl = new THREE.Mesh(vinylGeometry, vinylMaterial);
vinylGroup.add(vinyl);

// Animation loop
function animate() {
    requestAnimationFrame(animate);
    vinyl.rotation.z += 0.002; // Spin
    renderer.render(scene, camera);
}

animate();

// Scroll trigger
window.addEventListener('scroll', () => {
    const scrollPercent = window.scrollY / (document.body.scrollHeight - window.innerHeight);
    camera.position.z = 5 + scrollPercent * 2; // Zoom effect on scroll
});

// Hover glow effect on button
document.getElementById('cta-button').addEventListener('mouseenter', () => {
    // Dispatch custom event para Spline atualizar material brilho
    scene.getObjectByName('button-mesh').material.emissiveIntensity = 1;
});
```

**Performance optimization**:
```javascript
// Omma gera, mas você pode otimizar
// 1. LOD (Level of Detail)
const lod = new THREE.LOD();
lod.addLevel(highPoly, 0);      // < 10m
lod.addLevel(mediumPoly, 20);   // 10-20m
lod.addLevel(lowPoly, 50);      // > 20m
scene.add(lod);

// 2. Lazy load models off-screen
const intersectionObserver = new IntersectionObserver((entries) => {
    entries.forEach(entry => {
        if (entry.isIntersecting) {
            loadModel(entry.target);
            intersectionObserver.unobserve(entry.target);
        }
    });
});

document.querySelectorAll('.3d-section').forEach(el => {
    intersectionObserver.observe(el);
});
```

## Stack e requisitos
- **Plataforma**: Omma.build (recommended), ou DIY com Three.js + custom agent wrapper
- **Output engine**: Spline (underlying) ou Three.js code
- **Browser support**: Chrome 90+, Firefox 88+, Safari 14+ (WebGL 2)
- **Input**: prompt English/PT-BR (25-250 palavras)
- **Tempo geração**: 2-10 min (primeiro draft)
- **Iterações**: 3-5 prompts típicos pra ficar bom
- **Deploy**: vercel.com (Next.js), netlify.com (static), ou custom server
- **Custo Omma**: free tier (limited) ou $99+/mês (pro)
- **Custo infra**: $0-50/mês (Vercel) ou hospedagem própria

## Armadilhas e limitações
- **Prompt é fiddly**: "make it cool" gera resultado genérico. Ser específico (cores RGB, dimensões, comportamentos exatos)
- **Performance quebra em complexity**: > 100 3D objects + interactions = 10-20 FPS em mobile
- **Sem full 3D asset control**: agente gera aproximações. If quer precisão (pixel-perfect SVG overlay), manual editing é necessário
- **Acessibilidade negligenciada**: geração automática raramente inclui alt text, ARIA labels. Adicionar manually após
- **SEO prejudicado**: sites 3D pesados carregam lentamente (score Lighthouse = D/F). Lazy loading + code splitting crucial
- **UX pode confundir**: usuários esperam websites normais. 3D imersivo pode ser barreira (especialmente em mobile)
- **Responsividade limitada**: Spline responsive é melhor que Three.js bruto, mas ainda requer tweaks manuais
- **Custódia de dados**: Omma armazena seu projeto, não é open source (vendor lock-in)
- **Debugging difícil**: erro em interação JavaScript gerado é opaco (sem source map legível)

## Conexões
- [[three-js-para-desenvolvimento-de-jogos]]
- [[webgl-performance-optimization]]
- [[ia-agentes-especializados]]
- [[vibe-coding-interface-generation]]

## Histórico
- 2026-04-02: Nota criada
- 2026-04-02: Reescrita com implementação prática + otimizações