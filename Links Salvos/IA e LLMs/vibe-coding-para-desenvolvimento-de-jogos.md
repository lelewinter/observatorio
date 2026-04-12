---
tags: [ia, desenvolvimento-jogos, vibe-coding, threejs, llm, game-dev]
source: https://x.com/alightinastorm/status/2028246608811348355?s=20
date: 2026-04-02
tipo: aplicacao
---

# Aplicar Vibe Coding em Desenvolvimento AAA de Jogos com ThreeJS e LLMs

## O que é

Vibe Coding é um paradigma de desenvolvimento de software (cunhado por Andrej Karpathy em fevereiro de 2025) onde o programador descreve o projeto em linguagem natural e a IA gera código, assets, design de gameplay e narrativa. Aplicado a jogos, significa produzir jogos completos com mecânicas complexas, ambientes 3D, animações e audio — tudo via prompts iterativos, sem modelagem ou scripting manual.

## Por que importa agora

**Democratização do desenvolvimento AAA**: um desenvolvedor solo pode hoje produzir em semanas o que levaria meses com equipes tradicionais. Em 2025, 25% das startups do Y Combinator Winter batch tinham codebases 95% gerados por IA. Rosebud (plataforma de vibe coding para games) reporta 70.000 criadores fazendo isso, com 1 milhão+ de games criados.

**Velocidade exponencial**: AI game jams agora têm participantes gerando jogos completos (com arte, código, som) em **horas** ao invés de meses. Pieter Levels popularizou o conceito entregando produtos em fim-de-semana.

**Validação técnica**: ThreeJS + LLMs provaram-se viáveis em escala. Os modelos têm densidade altíssima de treinamento em ThreeJS (bem documentada, open source), resultando em código de qualidade consistente na primeira iteração.

## Como funciona / Como implementar

### Fluxo Iterativo Típico

```
1. Descrição de Visão (prompt inicial)
   "Quero um jogo de plataforma 3D onde o jogador pode voltar no tempo"

2. AI gera estrutura base (ThreeJS + Babylon.js setup)
   scene, camera, renderer, player controller

3. Iterações por camada:
   - Mecânicas do jogador (movimento, jump, colisão)
   - World building (geometrias, texturas, lighting)
   - Gameplay systems (pontos, vidas, checkpoints)
   - Narrativa (diálogos, cutscenes, progression)
   - Polish (animações, efeitos, audio)

4. Validação humana em cada etapa
   Testa, dá feedback, pede refinements
```

### Exemplo de Prompt Estruturado

```
Crie um jogo em ThreeJS com as seguintes especificações:

**Mecânicas:**
- Jogador controla um cubo que pode se mover em WASD
- Espaço para pular (physics-based, gravity 9.8)
- Click para disparar uma "bola reversora de tempo"
- Objetos atingidos congelam por 3 segundos

**Ambiente:**
- Plataformas flutuantes em um vazio azul
- 3 fases crescentes em dificuldade
- Inimigos (cubos vermelhos) que patrulham
- Objetivo é chegar ao cristal no final de cada fase

**Polimento:**
- Efeitos de partículas no salto
- Som de passos
- UI com contador de vidas (3 vidas total)
- Menu inicial e tela de game over

Exporte como arquivo HTML único com three.min.js inline.
```

### Stack Recomendado para Vibe Coding de Jogos

```javascript
// Setup mínimo para começar
const scene = new THREE.Scene();
const camera = new THREE.PerspectiveCamera(75, window.innerWidth / window.innerHeight, 0.1, 1000);
const renderer = new THREE.WebGLRenderer({ antialias: true });

// Physics engine (integra bem com prompts)
import * as CANNON from 'cannon-es';
const world = new CANNON.World();
world.gravity.set(0, -9.82, 0);

// Audio
const audioListener = new THREE.AudioListener();
camera.add(audioListener);
const sound = new THREE.Audio(audioListener);

// Input handling
const keys = {};
document.addEventListener('keydown', (e) => keys[e.key] = true);
document.addEventListener('keyup', (e) => keys[e.key] = false);
```

## Stack técnico

| Camada | Recomendado | Alternativa | Razão |
|--------|---|---|---|
| **3D Rendering** | Three.js | Babylon.js, PlayCanvas | ThreeJS: alta densidade em corpus de treinamento LLM |
| **Physics** | Cannon-ES | Jolt.js, Ammo.js | Cannon-ES: integração simples, bem documentado |
| **Audio** | Web Audio API + Three.Audio | Howler.js, Wad.js | Nativa no navegador, integra com Three.js |
| **Asset Loading** | GLTFLoader | FBXLoader, OBJLoader | GLTF é padrão moderno, melhor suporte LLM |
| **Animação** | Mixamo + Blender | Mixamo-only | Blend permite ajustes locais quando necessário |
| **Build/Deploy** | Vite + Vercel | Webpack + AWS | Vite: mais rápido, melhor DX |

## Código prático

### Exemplo 1: Mechânica de Reversão de Tempo

```javascript
class TimeReversal {
  constructor() {
    this.activeObjects = new Map();
    this.freezeDuration = 3; // segundos
    this.frozenColor = 0xff0000; // vermelho
  }

  freezeObject(obj) {
    if (this.activeObjects.has(obj)) return;
    
    const originalColor = obj.material.color.getHex();
    const startTime = Date.now();
    
    obj.material.color.setHex(this.frozenColor);
    obj.userData.frozen = true;
    
    // Armazenar estados da física
    if (obj.body) {
      obj.userData.originalVelocity = obj.body.velocity.clone();
      obj.userData.originalAngularVel = obj.body.angularVelocity.clone();
      obj.body.velocity.set(0, 0, 0);
      obj.body.angularVelocity.set(0, 0, 0);
    }
    
    this.activeObjects.set(obj, { startTime, originalColor });
  }

  update(deltaTime) {
    for (const [obj, data] of this.activeObjects) {
      const elapsed = (Date.now() - data.startTime) / 1000;
      
      if (elapsed >= this.freezeDuration) {
        // Descongelar
        obj.material.color.setHex(data.originalColor);
        obj.userData.frozen = false;
        
        if (obj.body && obj.userData.originalVelocity) {
          obj.body.velocity.copy(obj.userData.originalVelocity);
          obj.body.angularVelocity.copy(obj.userData.originalAngularVel);
        }
        
        this.activeObjects.delete(obj);
      }
    }
  }
}

// Uso
const timeReversal = new TimeReversal();
document.addEventListener('click', (e) => {
  const raycaster = new THREE.Raycaster();
  const mouse = new THREE.Vector2(
    (e.clientX / window.innerWidth) * 2 - 1,
    -(e.clientY / window.innerHeight) * 2 + 1
  );
  raycaster.setFromCamera(mouse, camera);
  const intersects = raycaster.intersectObjects(scene.children);
  if (intersects.length > 0) {
    timeReversal.freezeObject(intersects[0].object);
  }
});

// No loop de animação
function animate() {
  requestAnimationFrame(animate);
  timeReversal.update(deltaTime);
  renderer.render(scene, camera);
}
```

### Exemplo 2: Gerador de World Blockout via Prompt

```javascript
// Para pedir à IA:
/*
Crie uma função que gera um nível proceduralmente com:
- 5 plataformas flutuantes em grid (x, z)
- Altura varia de y: 0 a 20
- Distância entre plataformas: 5-10 unidades
- Cada plataforma: cube 2x1x2
- Material: MeshStandardMaterial com cor aleatória
- Physics body para cada uma
*/

function generateLevelBlockout(scene, world, numPlatforms = 5) {
  const platforms = [];
  const spacing = 8;
  
  for (let i = 0; i < numPlatforms; i++) {
    const x = (i % 3) * spacing;
    const z = Math.floor(i / 3) * spacing;
    const y = Math.random() * 20;
    
    // Visual
    const geometry = new THREE.BoxGeometry(2, 1, 2);
    const material = new THREE.MeshStandardMaterial({
      color: Math.random() * 0xffffff,
      metalness: 0.1,
      roughness: 0.8
    });
    const mesh = new THREE.Mesh(geometry, material);
    mesh.position.set(x, y, z);
    scene.add(mesh);
    
    // Physics
    const shape = new CANNON.Box(new CANNON.Vec3(1, 0.5, 1));
    const body = new CANNON.Body({ mass: 0 });
    body.addShape(shape);
    body.position.set(x, y, z);
    world.addBody(body);
    
    mesh.body = body;
    platforms.push(mesh);
  }
  
  return platforms;
}
```

## Armadilhas e Limitações

### 1. **Qualidade divergente em código complexo**
O que funciona bem em componentes isolados (um player controller, um inimigo) pode divergir quando 3+ sistemas interagem. LLMs geram código que "parece correto" mas tem lógica de estado inconsistente.

**Exemplo**: AI gera sistema de vidas, sistema de pontos e sistema de checkpoints independentemente. Quando jogador morre em checkpoint, pontos não resetam corretamente.

**Solução**: Sempre peça à IA para gerar um "state manager" centralizado que coordena sistemas, não abstrações isoladas.

### 2. **Reflow de assets durante iterações**
Cada mudança de mecânica pode exigir re-modelagem de assets 3D. Se você pede "adiciona inimigos que voam", mas o Level já foi todo desenhado em ground-level, haverá desajustes de proporção e espaço.

**Solução**: Fazer "placeholder pass" primeiro (tudo com cubos/esferas simples, sem texturas). Validar gameplay. Só depois pedir polimento visual.

### 3. **Overhead de validação humana é subestimado**
Vibe Coding promete "reduzir trabalho manual", mas na verdade desloca 50-70% do esforço para QA. Cada output de IA precisa ser testado:
- Bugs de lógica (estado inconsistente)
- Performance (cenas com 1000+ objetos ficam lentas)
- Compatibilidade (code que roda no Chrome pode quebrar no Firefox)

Developers solo gastam 4-6h testando, reproduzindo erros, e escrevendo prompts de correção para cada 2h de "desenvolvimento" via IA.

### 4. **Compilação de prompts é un-scalable**
Conforme o projeto cresce (100+ entities, 5+ sistemas), o prompt inicial vira incontrolável. A IA começa a "esquecer" restrições anteriores ou conflita requisitos novos com antigos.

**Solução**: Usar "prompt chaining" com markdown docs:
```
Documento ARCHITECTURE.md com diagrama de sistemas
Documento STYLE_GUIDE.md com padrões de código (naming, estrutura)
Documento COMPLETED_FEATURES.md listando o que já foi feito
Pedir sempre à IA: "Baseado em ARCHITECTURE.md, implemente X"
```

### 5. **Testes automatizados precisam de retrofit**
IA gera código sem testes. Descobrindo bugs late no projeto significa reescrever lógica de novo. Testes unitários para mecânicas são criticamente ignorados na maioria dos prompts vibe coding.

**Prática**: Pedir explicitamente: "Implemente X com testes Jest coverage 80%+"

## Conexões

- [[Claude Code]] — agente que executa vibe coding em escala produtiva
- [[Auto-Melhoria Persistente em Agentes de Código]] — loop iterativo inerente ao vibe coding
- [[Meshy MCP para Pipeline End-to-End de Geração 3D]] — automatizar assets 3D com rigging/animação
- [[Gerar Modelos 3D em Tempo Real a Partir de Imagens]] — alternativa procedural a modelagem manual
- [[LLM Game Jams e Product Shipping]] — contexto de adoção em mercado

## Perguntas de Revisão

1. **Por que ThreeJS é melhor que Unreal Engine para vibe coding?** Qual o trade-off entre rendimento (Unreal) vs. iteração rápida (Three)?
2. **Como estruturar um "prompt document" escalonável** para um jogo com 50+ horas de gameplay?
3. **Qual é o custo real de QA** em um projeto vibe-coded de média complexidade? Como prioriz o que testar?
4. **Quando parar de usar vibe coding** e começar a escrever código manualmente? (Qual é o ponto de inflexão em tamanho/complexidade?)

## Histórico de Atualizações
- 2026-04-02: Nota criada a partir de Telegram
- 2026-04-11: Expandida com exemplos de código, stack técnico, armadilhas e conexões