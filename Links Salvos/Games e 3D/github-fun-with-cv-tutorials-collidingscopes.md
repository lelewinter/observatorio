---
date: 2025-09-15
tags: [github, computer-vision, tutorials, mediapipe, opencv, hand-tracking, three-js]
source: https://github.com/collidingScopes/fun-with-cv-tutorials
tipo: aplicacao
---

# 40+ tutoriais hand tracking, gesture, e 3D vision completos com demos

## O que é
Repositório educacional com 40+ projetos executáveis de computer vision: hand tracking, face detection, object tracking, síntese 3D, interações por gesto. Todos com live demos, código comentado, assets e configurações prontas. Stack: MediaPipe + OpenCV + Three.js rodando em browser.

## Como implementar

**Setup inicial:**

```bash
git clone https://github.com/collidingScopes/fun-with-cv-tutorials
cd fun-with-cv-tutorials

# Instalar dependências globais
npm install

# Navegar para um tutorial específico
cd hand-tracking-101
npm install
npm start
```

**Padrão arquitetônico comum (hand tracking base):**

```javascript
// Estrutura padrão usada em todos os tutoriais
import * as tf from "@tensorflow/tfjs";
import * as handpose from "@tensorflow-models/handpose";
import * as THREE from "three";

class HandTrackingProject {
  constructor() {
    this.model = null;
    this.renderer = null;
    this.scene = new THREE.Scene();
    this.handMeshes = [];
  }

  async init() {
    // Carregar modelo de hand pose
    this.model = await handpose.load();

    // Setup Three.js renderer
    this.renderer = new THREE.WebGLRenderer({ antialias: true });
    this.renderer.setSize(window.innerWidth, window.innerHeight);
    document.body.appendChild(this.renderer.domElement);

    // Câmera e iluminação
    const camera = new THREE.PerspectiveCamera(
      75,
      window.innerWidth / window.innerHeight,
      0.1,
      1000
    );
    camera.position.z = 5;

    const light = new THREE.DirectionalLight(0xffffff, 1);
    this.scene.add(light);

    this.camera = camera;
  }

  async detectAndRender() {
    const video = document.querySelector("video");
    const predictions = await this.model.estimateHands(video);

    // Limpar meshes antigos
    this.handMeshes.forEach(mesh => this.scene.remove(mesh));
    this.handMeshes = [];

    // Renderizar novas mãos
    predictions.forEach((hand, idx) => {
      const mesh = this.createHandMesh(hand.landmarks);
      this.scene.add(mesh);
      this.handMeshes.push(mesh);
    });

    this.renderer.render(this.scene, this.camera);
    requestAnimationFrame(() => this.detectAndRender());
  }

  createHandMesh(landmarks) {
    // landmarks = array 21x3 (x, y, z)
    const geometry = new THREE.BufferGeometry();
    const positions = new Float32Array(landmarks.flat());
    geometry.setAttribute("position", new THREE.BufferAttribute(positions, 3));

    // Conectar pontos em skeleton
    const indices = [
      0, 1, 1, 2, 2, 3, 3, 4, // polegar
      0, 5, 5, 6, 6, 7, 7, 8, // indicador
      0, 9, 9, 10, 10, 11, 11, 12, // meio
      0, 13, 13, 14, 14, 15, 15, 16, // anel
      0, 17, 17, 18, 18, 19, 19, 20 // mínimo
    ];
    geometry.setIndex(indices);

    const material = new THREE.LineBasicMaterial({ color: 0x00ff00 });
    return new THREE.LineSegments(geometry, material);
  }
}

// Iniciar
const project = new HandTrackingProject();
await project.init();
await project.detectAndRender();
```

**Piano Game (interactive gesture example):**

```javascript
class PianoGame {
  constructor() {
    this.audioContext = new (window.AudioContext || window.webkitAudioContext)();
    this.notes = [
      { name: "C4", freq: 262, hand: "left", xRange: [0.1, 0.3] },
      { name: "D4", freq: 294, hand: "left", xRange: [0.3, 0.5] },
      { name: "E4", freq: 330, hand: "left", xRange: [0.5, 0.7] },
      { name: "F4", freq: 349, hand: "right", xRange: [0.3, 0.5] },
      { name: "G4", freq: 392, hand: "right", xRange: [0.5, 0.7] }
    ];
    this.activeNotes = new Set();
  }

  async play() {
    const video = document.querySelector("video");
    const model = await handpose.load();

    const render = async () => {
      const predictions = await model.estimateHands(video);

      predictions.forEach(hand => {
        const indexTip = hand.landmarks[8]; // índice
        const x = indexTip[0] / video.width;

        // Detectar que nota é tocada
        this.notes.forEach(note => {
          const inRange = x >= note.xRange[0] && x <= note.xRange[1];
          const isHand = note.hand === (hand.handedness === "Right" ? "right" : "left");

          if (inRange && isHand && !this.activeNotes.has(note.name)) {
            this.playTone(note.freq);
            this.activeNotes.add(note.name);
          }
        });
      });

      requestAnimationFrame(render);
    };

    render();
  }

  playTone(freq) {
    const osc = this.audioContext.createOscillator();
    const gain = this.audioContext.createGain();

    osc.frequency.value = freq;
    osc.type = "sine";

    osc.connect(gain);
    gain.connect(this.audioContext.destination);

    gain.gain.setValueAtTime(0.3, this.audioContext.currentTime);
    gain.gain.exponentialRampToValueAtTime(
      0.01,
      this.audioContext.currentTime + 0.5
    );

    osc.start(this.audioContext.currentTime);
    osc.stop(this.audioContext.currentTime + 0.5);
  }
}

const piano = new PianoGame();
await piano.play();
```

**Guitar Hero detection (pose classification):**

```javascript
class GuitarHeroDetector {
  // Mapeamento de posições de dedos → acordes
  chordPatterns = {
    "G": { 2: true, 3: true, 4: false }, // 2º e 3º trastes
    "D": { 1: true, 2: true, 3: true },  // 1º, 2º, 3º trastes
    "A": { 0: true, 1: true, 2: true },  // Aberto
    "Em": { 0: true, 2: true }            // Aberto
  };

  detectChord(landmarks) {
    // landmarks[8] = índice, landmarks[12] = meio, etc
    // Calcular em que "traste" cada dedo está

    const fingerPositions = {
      1: this.getFingerFret(landmarks[5], landmarks[6]), // indicador
      2: this.getFingerFret(landmarks[9], landmarks[10]), // meio
      3: this.getFingerFret(landmarks[13], landmarks[14]), // anel
      4: this.getFingerFret(landmarks[17], landmarks[18]) // mínimo
    };

    // Comparar com padrões conhecidos
    for (const [chord, pattern] of Object.entries(this.chordPatterns)) {
      if (this.matchesPattern(fingerPositions, pattern)) {
        return chord;
      }
    }
    return null;
  }

  getFingerFret(base, tip) {
    // Y distance = distância vertical = indicador de traste
    const distance = Math.abs(tip[1] - base[1]);
    if (distance < 30) return 0; // Aberto
    if (distance < 60) return 1; // 1º traste
    if (distance < 90) return 2; // 2º traste
    return 3; // 3º+ traste
  }

  matchesPattern(positions, pattern) {
    return Object.entries(pattern).every(([finger, active]) => {
      return active ? positions[finger] > 0 : positions[finger] === 0;
    });
  }
}
```

**3D Graph visualization (com força-grafo):**

```javascript
import { ForceGraph3D } from "3d-force-graph";

async function create3DGraph() {
  // Dados do grafo
  const data = {
    nodes: [
      { id: "A", color: 0xff0000 },
      { id: "B", color: 0x00ff00 },
      { id: "C", color: 0x0000ff },
      { id: "D", color: 0xffff00 }
    ],
    links: [
      { source: "A", target: "B" },
      { source: "B", target: "C" },
      { source: "C", target: "D" },
      { source: "D", target: "A" }
    ]
  };

  const gData = ForceGraph3D()
    (document.getElementById("3d-graph"))
    .graphData(data)
    .nodeColor(node => node.color)
    .nodeLabel(node => node.id)
    .linkColor(() => 0xcccccc)
    .d3Force("charge").strength(-300)
    .d3Force("link").distance(150);

  // Hand interaction: arrastar nós com gesto
  const model = await handpose.load();
  const video = document.querySelector("video");

  setInterval(async () => {
    const predictions = await model.estimateHands(video);
    if (predictions.length > 0) {
      const hand = predictions[0];
      const thumbTip = hand.landmarks[4];
      // Mapear thumb position → graph camera control
      // ...
    }
  }, 50);
}
```

## Stack e requisitos

**Stack técnico:**
- **Frontend**: JavaScript ES6+, Three.js, Canvas API
- **Vision**: MediaPipe (ou TensorFlow.js hand-pose), OpenCV.js
- **Audio**: Web Audio API
- **3D**: Three.js, 3d-force-graph (alguns projetos)
- **Build**: Webpack (alguns), Parcel (outros)

**Browser:**
- Chrome/Edge 80+
- Firefox 75+
- Safari 14+
- Webcam: qualquer USB camera (ou integrada)

**Performance:**
- Hand tracking: 30-60 FPS em desktop GPU
- 3D rendering: 60 FPS em GPU moderna
- Mobile: 15-30 FPS (dependente do modelo telefone)

**Custos:**
- 100% gratuito (open-source MIT)
- Sem APIs pagas necessárias
- Roda offline (após download inicial)

## Armadilhas e limitações

**Configuração:**
- Alguns tutoriais usam TensorFlow.js (pesado ~50MB), outros MediaPipe (leve ~7MB)
- Path de imports varia por projeto (some usam relative paths)
- Node.js 14+ necessário para builds
- Alguns demos usam hardware-specific shaders (GLSL)

**Funcionalidade:**
- Hand tracking funciona melhor com 1-2 mãos em lighting bom
- Object detection (blob tracking) falha em ambientes caóticos
- 3D rendering limita-se a ~10K vertices antes de stutter
- Audio lags em mobile (latência >100ms)

**Quando usar repositório:**
- **Bom para**: aprender arquitetura, copiar padrões, prototipar rápido
- **Não é para**: produção (código sample, não robustez), performance crítica (use Micro-Handpose), aplicações comerciais complexas

**Manutenção:**
- Projeto ativo com 11 contribuidores, último update recente
- Alguns links de live demos podem estar quebrados
- Dependências podem desatualizar (Three.js, TensorFlow versões)

## Conexões
- [[MediaPipe Face Recognition Local Edge]]
- [[Micro-Handpose WebGPU Hand Tracking Browser]]
- [[tony-stark-jarvis-visualizacao-3d-mediapipe]]
- [[geracao-3d-com-ia-no-browser]]

## Histórico
- 2025-09-15: Nota original criada (zettelkasten)
- 2026-04-02: Reescrita como guia de implementação prática
