---
tags: [scroll-animation, 3d-web, threejs, gsap, landing-page, ai-code-generation]
source: https://x.com/viktoroddy/status/2037839395638899136?s=20
date: 2026-04-02
tipo: aplicacao
---

# Construir Landing Page 3D com Scroll-Driven Animation

## O que é
Página web onde scroll do usuário controla animações 3D: câmera orbita, objetos giram, partículas deformam. Gerado por prompt IA (Claude, GPT-4, Cursor).

## Como implementar
**Stack base** (Three.js + GSAP ScrollTrigger):

```javascript
import * as THREE from 'three';
import gsap from 'gsap';
import { ScrollTrigger } from 'gsap/ScrollTrigger';

gsap.registerPlugin(ScrollTrigger);

// Setup cena
const scene = new THREE.Scene();
const camera = new THREE.PerspectiveCamera(75, window.innerWidth/window.innerHeight, 0.1, 1000);
const renderer = new THREE.WebGLRenderer({ antialias: true, alpha: true });
renderer.setSize(window.innerWidth, window.innerHeight);
document.body.appendChild(renderer.domElement);

// Objeto 3D (ex: smartphone)
const phoneGeometry = new THREE.BoxGeometry(1, 2, 0.1);
const phoneMaterial = new THREE.MeshStandardMaterial({ color: 0x000000 });
const phone = new THREE.Mesh(phoneGeometry, phoneMaterial);
scene.add(phone);

// Lighting
const light = new THREE.DirectionalLight(0xffffff, 1);
light.position.set(5, 5, 5);
scene.add(light);

// Scroll-driven animation
gsap.to(phone.rotation, {
  y: Math.PI * 2,  // 360° rotation
  duration: 1,
  scrollTrigger: {
    trigger: '#section-phone',
    start: 'top center',
    end: 'bottom center',
    scrub: 1,  // "scrub" = bind animation ao scroll
    markers: true  // debug visual
  }
});

// Camera zoom on scroll
gsap.to(camera.position, {
  z: 2,
  duration: 1,
  scrollTrigger: {
    trigger: '#section-hero',
    start: 'top top',
    end: 'bottom top',
    scrub: 1
  }
});

// Animation loop
function animate() {
  requestAnimationFrame(animate);
  renderer.render(scene, camera);
}
animate();

// Handle window resize
window.addEventListener('resize', () => {
  camera.aspect = window.innerWidth / window.innerHeight;
  camera.updateProjectionMatrix();
  renderer.setSize(window.innerWidth, window.innerHeight);
});
```

**Prompt IA para gerar (via Cursor/Claude)**:

```
Create a landing page for a luxury watch brand using Three.js and GSAP.

Requirements:
- Hero section with 3D rotating watch (use BoxGeometry as placeholder)
- Scroll down: watch zooms and rotates 360°
- Second section: watch explodes into parts (position offset), reveals features
- Third section: 3D particles fly around watch in swirl pattern
- Final CTA button at bottom

Styling: dark background (black), gold accents (#DAA520), sans-serif font
Performance: optimize for 60fps, use LOD or visibility culling

Include responsive design for mobile (reduce particle count, simplify geometry).
```

**Resultado gerado** (exemplo saída Claude):
- HTML boilerplate + Three.js setup
- GSAP ScrollTrigger configurations
- Responsive canvas resize logic
- Mobile performance fallbacks

## Stack e requisitos
- **Frontend libs**: Three.js (175 KB), GSAP (45 KB), R3F optional (React)
- **API generation**: Claude 3.5, GPT-4, Cursor (integrated IDE)
- **Browser support**: Chrome 90+, Firefox 88+, Safari 14+ (WebGL 2)
- **Performance targets**: 60 FPS desktop, 30+ FPS mobile
- **Entrada**: descrição textual (200-500 palavras)
- **Output**: vanilla JS (ou React/Next.js flavor)
- **Deploy**: Vercel, Netlify, ou servidor customizado
- **Tempo desenvolvimento**: 2-4 horas (prompt writing + iteration) vs 40-80 horas manual
- **Custo infra**: $0-20/mês (Vercel free tier até 100GB bandwidth)

## Armadilhas e limitações
- **Performance quebra em mobile**: > 50k vertices + particulas = 10-15 FPS. Usar vertex culling ou switch para 2D fallback
- **Scroll binding é frame-locked**: qualquer frame drop = animação "salta". Use GSAP `scrub: true` vs `scrub: 1` para smoothing
- **Shader compilation stutter**: primeira vez que shader roda = 100-500ms lag. Pre-compile ou usar simpler materials
- **GPU memory leak**: não cleanup objects em scroll heavy pages. Sempre `.dispose()` geometries/textures
- **SEO prejudicado**: canvas não é indexável. Colocar fallback `<img>` + "noscript" para bots
- **Touch events finicky**: scroll em tablet é diferente de mouse wheel. Testar extensivamente em múltiplos devices
- **Code generation é 70-80% pronto**: 20-30% de tweaks manuais (cor errada, tamanho fora) sempre necessário
- **Vendor lock-in**: código gerado por Cursor = acoplado ao IDE (hard copypaste sem setup)
- **Accessibility negligenciada**: canvas é cego para screen readers. Adicionar ARIA labels manualmente

## Conexões
- [[three-js-para-desenvolvimento-de-jogos]]
- [[scroll-driven-animation-gsap]]
- [[webgl-performance-mobile]]
- [[ia-code-generation-web]]

## Histórico
- 2026-04-02: Nota criada
- 2026-04-02: Reescrita com exemplo código + prompt IA
