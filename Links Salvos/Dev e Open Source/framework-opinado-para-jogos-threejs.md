---
tags: [threejs, gamedev, framework, javascript, 3d, open-source]
source: https://x.com/
date: 2026-04-02
tipo: aplicacao
---

# Framework Three.js Opinado para Desenvolvimento de Jogos 3D

## O que é

Framework gerado via vibe coding que abstrai Three.js com opinões sobre arquitetura (ECS, física, animações). Reduz boilerplate e acelera prototipagem de jogos 3D.

## Como implementar

**Setup:**
```bash
npm create vite my-game -- --template vanilla
npm install three @your-framework/game
```

**Estrutura básica:**
```javascript
import { Game, Entity, Transform, Renderer } from '@framework/game';

const game = new Game({
  renderer: 'three',
  physics: 'cannon-es6',
  canvas: document.getElementById('app')
});

// Criar entidade
const cube = new Entity('cube', {
  components: [
    new Transform({ pos: [0, 0, 0] }),
    new Mesh({ geometry: 'BoxGeometry', material: 'MeshPhong' }),
    new Rigidbody({ mass: 1, shape: 'box' })
  ]
});

game.add(cube);
game.start();
```

**Sistema de componentes:**
```javascript
class RotateSystem extends System {
  execute(entities, deltaTime) {
    entities.forEach(e => {
      const transform = e.get(Transform);
      transform.rotation.y += deltaTime;
    });
  }
}

game.registerSystem(RotateSystem);
```

**Cena com iluminação:**
```javascript
game.scene.background = new THREE.Color(0x1a1a2e);

const light = new THREE.DirectionalLight(0xffffff, 1);
light.position.set(5, 10, 5);
game.scene.add(light);

const ambient = new THREE.AmbientLight(0xffffff, 0.5);
game.scene.add(ambient);
```

**Input simplificado:**
```javascript
game.input.on('keydown', 'w', () => {
  player.getComponent(Transform).pos.z -= 0.1;
});

game.input.on('click', (event) => {
  console.log('Clicou em:', event);
});
```

## Stack e requisitos

- **Three.js**: 3D rendering
- **Cannon-es6**: Física 2D/3D
- **Vite**: Dev server rápido
- **TypeScript** (opcionalmente): type safety

## Armadilhas

1. **Performance**: 3D browser é limitado. Otimizar geometria/texturas.
2. **Compatibilidade**: WebGL tem suporte variável entre browsers.
3. **Mobile**: Reduce quality para mobile. Use LOD (Level of Detail).

## Conexões

- [[geracao-3d-em-tempo-real-por-imagem]] - Gerar assets 3D
- [[world-model-interativo-em-tempo-real]] - Ambientes procedurais

## Histórico

- 2026-04-02: Reescrita com implementação
