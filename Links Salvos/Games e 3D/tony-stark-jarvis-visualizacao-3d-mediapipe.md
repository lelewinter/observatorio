---
date: 2025-07-21
tags: [3d-visualization, three-js, mediapipe, web-speech-api, hand-tracking, voice-commands]
source: https://x.com/measure_plan/status/1947353805391077482
tipo: aplicacao
---

# Interface Jarvis: Hand tracking + voz para exploração 3D de grafos

## O que é
UI imersiva multimodal para dados complexos: hand tracking (MediaPipe) controla câmera 3D em tempo real, Web Speech API reconhece comandos de voz, Three.js renderiza grafo interativo. Resultado: interface tipo Iron Man onde você manipula dados com gestos e voz.

## Como implementar

**Setup inicial:**

```bash
npm install three mediapipe-tasks web-speech-api
```

**Estrutura base - Hand tracking + 3D graph:**

```javascript
import * as THREE from "three";
import { HandLandmarker, FilesetResolver } from "@mediapipe/tasks-vision";
import { ForceGraph3D } from "3d-force-graph";

class JarvisInterface {
  constructor() {
    this.handLandmarker = null;
    this.scene = new THREE.Scene();
    this.renderer = new THREE.WebGLRenderer({ antialias: true, alpha: true });
    this.camera = new THREE.PerspectiveCamera(
      75,
      window.innerWidth / window.innerHeight,
      0.1,
      1000
    );
    this.cameraRotation = { x: 0, y: 0 };
    this.cameraZoom = 5;

    // Dados de exemplo (grafo)
    this.graphData = {
      nodes: [],
      links: []
    };

    this.initRenderer();
  }

  initRenderer() {
    this.renderer.setSize(window.innerWidth, window.innerHeight);
    this.renderer.setClearColor(0x000000);
    document.body.appendChild(this.renderer.domElement);

    this.camera.position.z = this.cameraZoom;

    // Iluminação
    const light = new THREE.DirectionalLight(0xffffff, 1);
    light.position.set(10, 10, 10);
    this.scene.add(light);

    const ambientLight = new THREE.AmbientLight(0x404040);
    this.scene.add(ambientLight);
  }

  async init() {
    // Carregar MediaPipe Hand Landmarker
    const filesetResolver = await FilesetResolver.forVisionTasks(
      "https://cdn.jsdelivr.net/npm/@mediapipe/tasks-vision/wasm"
    );

    this.handLandmarker = await HandLandmarker.createFromOptions(
      filesetResolver,
      {
        baseOptions: {
          modelAssetPath:
            "https://storage.googleapis.com/mediapipe-tasks/vision/hand_landmarker_lite.task",
          delegate: "GPU"
        },
        numHands: 2,
        runningMode: "VIDEO"
      }
    );

    // Iniciar loops
    this.startHandTracking();
    this.startVoiceRecognition();
    this.render();
  }

  startHandTracking() {
    const video = document.querySelector("video");
    const canvas = document.querySelector("canvas#debug");

    const track = async () => {
      if (!video.paused) {
        const results = await this.handLandmarker.detectForVideo(
          video,
          performance.now()
        );

        // Processar gestos
        results.landmarks.forEach((landmarks, handIdx) => {
          this.processHandGesture(landmarks, handIdx);
        });

        // Debug: desenhar landmarks
        if (canvas) {
          this.drawDebugOverlay(canvas, video, results);
        }
      }

      requestAnimationFrame(track);
    };

    track();
  }

  processHandGesture(landmarks, handIdx) {
    // landmarks[9] = posição base da mão (pulso)
    // landmarks[8] = dedo médio
    // landmarks[4] = polegar
    // landmarks[5] = base do índice

    const wrist = landmarks[9];
    const middleFinger = landmarks[12];
    const thumb = landmarks[4];
    const index = landmarks[8];

    // ROTAÇÃO: posição horizontal da mão → rotação Y
    const handX = wrist.x; // 0 a 1
    this.cameraRotation.y = (handX - 0.5) * Math.PI;

    // ZOOM: distância polegar-índice → zoom
    const pinchDistance = this.distance(thumb, index);
    this.cameraZoom = 3 + pinchDistance * 5; // 3 a 8

    // TILT: altura da mão → rotação X
    const handY = wrist.y; // 0 a 1
    this.cameraRotation.x = (0.5 - handY) * Math.PI * 0.5;

    // Atualizar câmera
    this.camera.position.x = Math.sin(this.cameraRotation.y) * this.cameraZoom;
    this.camera.position.z = Math.cos(this.cameraRotation.y) * this.cameraZoom;
    this.camera.position.y = Math.sin(this.cameraRotation.x) * this.cameraZoom;
    this.camera.lookAt(0, 0, 0);
  }

  distance(p1, p2) {
    return Math.sqrt((p1.x - p2.x) ** 2 + (p1.y - p2.y) ** 2);
  }

  drawDebugOverlay(canvas, video, results) {
    const ctx = canvas.getContext("2d");
    ctx.drawImage(video, 0, 0, canvas.width, canvas.height);

    results.landmarks.forEach(landmarks => {
      landmarks.forEach((landmark, idx) => {
        const x = landmark.x * canvas.width;
        const y = landmark.y * canvas.height;

        ctx.fillStyle = idx === 9 ? "red" : "green";
        ctx.beginPath();
        ctx.arc(x, y, 5, 0, 2 * Math.PI);
        ctx.fill();
      });
    });
  }

  startVoiceRecognition() {
    const SpeechRecognition =
      window.SpeechRecognition || window.webkitSpeechRecognition;
    const recognition = new SpeechRecognition();

    recognition.continuous = true;
    recognition.interimResults = false;
    recognition.lang = "pt-BR";

    recognition.onresult = event => {
      const transcript = event.results[event.results.length - 1][0].transcript
        .toLowerCase();

      console.log("Comando:", transcript);

      // Mapeamento de comandos
      if (transcript.includes("zoom")) {
        this.cameraZoom = 2;
      }
      if (transcript.includes("afastar")) {
        this.cameraZoom = 10;
      }
      if (transcript.includes("destacar influenciadores")) {
        this.highlightTopNodes();
      }
      if (transcript.includes("mostrar cluster")) {
        this.filterByCluster();
      }
      if (transcript.includes("resetar")) {
        this.resetView();
      }
    };

    recognition.start();
  }

  loadGraphData(nodes, links) {
    // Criar geometria de nós
    const geometry = new THREE.SphereGeometry(0.3, 32, 32);

    nodes.forEach((node, idx) => {
      const material = new THREE.MeshPhongMaterial({
        color: new THREE.Color().setHSL(Math.random(), 0.7, 0.6)
      });
      const mesh = new THREE.Mesh(geometry, material);

      // Posicionamento pseudo-aleatório (idealmente force-directed)
      mesh.position.set(
        (Math.random() - 0.5) * 10,
        (Math.random() - 0.5) * 10,
        (Math.random() - 0.5) * 10
      );

      mesh.userData = { nodeId: node.id, label: node.label };
      this.scene.add(mesh);
    });

    // Criar linhas de conexão
    const lineMaterial = new THREE.LineBasicMaterial({ color: 0x888888 });
    links.forEach(link => {
      // Buscar posições dos nós
      const source = this.scene.children.find(
        child => child.userData?.nodeId === link.source
      );
      const target = this.scene.children.find(
        child => child.userData?.nodeId === link.target
      );

      if (source && target) {
        const geometry = new THREE.BufferGeometry().setFromPoints([
          source.position,
          target.position
        ]);
        const line = new THREE.Line(geometry, lineMaterial);
        this.scene.add(line);
      }
    });

    this.graphData = { nodes, links };
  }

  highlightTopNodes() {
    // Ordenar nós por conectividade e destacar top 5
    const nodeDegree = {};

    this.graphData.links.forEach(link => {
      nodeDegree[link.source] = (nodeDegree[link.source] || 0) + 1;
      nodeDegree[link.target] = (nodeDegree[link.target] || 0) + 1;
    });

    const topNodes = Object.entries(nodeDegree)
      .sort((a, b) => b[1] - a[1])
      .slice(0, 5)
      .map(entry => entry[0]);

    // Alterar cor dos top nodes
    this.scene.children.forEach(child => {
      if (child.userData?.nodeId && topNodes.includes(child.userData.nodeId)) {
        child.material.color.set(0xffff00); // Amarelo
        child.scale.set(1.5, 1.5, 1.5);
      }
    });
  }

  filterByCluster() {
    // Exemplo: destacar nós com grau > 3
    this.scene.children.forEach(child => {
      if (child.userData?.nodeId) {
        const degree = this.graphData.links.filter(
          link =>
            link.source === child.userData.nodeId ||
            link.target === child.userData.nodeId
        ).length;

        child.visible = degree > 3;
      }
    });
  }

  resetView() {
    this.cameraZoom = 5;
    this.cameraRotation = { x: 0, y: 0 };
    this.scene.children.forEach(child => {
      if (child.material?.color) {
        child.material.color.set(0x4488ff);
      }
      child.visible = true;
      child.scale.set(1, 1, 1);
    });
  }

  render() {
    this.renderer.render(this.scene, this.camera);
    requestAnimationFrame(() => this.render());
  }
}

// Uso
const jarvis = new JarvisInterface();
await jarvis.init();

// Carregar dados de exemplo
jarvis.loadGraphData(
  [
    { id: "A", label: "Node A" },
    { id: "B", label: "Node B" },
    { id: "C", label: "Node C" },
    { id: "D", label: "Node D" }
  ],
  [
    { source: "A", target: "B" },
    { source: "B", target: "C" },
    { source: "C", target: "D" },
    { source: "D", target: "A" }
  ]
);
```

**HTML template:**

```html
<!DOCTYPE html>
<html>
<head>
  <style>
    body {
      margin: 0;
      overflow: hidden;
      background: black;
    }
    video {
      display: none;
    }
    canvas#debug {
      position: absolute;
      top: 0;
      left: 0;
      width: 320px;
      height: 240px;
      opacity: 0.5;
    }
  </style>
</head>
<body>
  <video autoplay playsinline width="640" height="480"></video>
  <canvas id="debug"></canvas>
  <script type="module" src="jarvis.js"></script>
</body>
</html>
```

**Setup de câmera (browser permissões):**

```javascript
async function setupCamera() {
  const video = document.querySelector("video");

  try {
    const stream = await navigator.mediaDevices.getUserMedia({
      video: {
        width: { ideal: 1280 },
        height: { ideal: 720 }
      },
      audio: true // Para Web Speech API
    });

    video.srcObject = stream;

    return new Promise(resolve => {
      video.onloadedmetadata = () => {
        video.play();
        resolve(video);
      };
    });
  } catch (error) {
    console.error("Erro ao acessar câmera:", error);
  }
}

await setupCamera();
```

## Stack e requisitos

**Browser:**
- Chrome 90+ (WebGL, MediaPipe, Web Speech)
- Firefox 88+ (suporte similar)
- Safari 15+ (suporte parcial, sem MediaPipe GPU)

**Dependências:**
- Three.js 140+
- MediaPipe Tasks Vision
- Web Speech API (nativo, sem npm)

**Hardware:**
- Webcam (qualquer USB ou integrada)
- Microfone (para voz)
- GPU desejável (Three.js + 10K+ nós precisa de VRAM)
- VRAM: ~500MB para grafo com 100K nós

**Performance:**
- Hand tracking: 30 FPS em desktop, 15-20 FPS mobile
- 3D rendering: 60 FPS com <10K nós, 30 FPS com 100K nós
- Latência gesto→câmera: 50-100ms

## Armadilhas e limitações

**Hand tracking:**
- Gestos caseiros são frágeis (pequenas variações causam erros)
- Precisa de mão bem visível (não funciona ocluída)
- Lighting ruim degrada detecção (mãos muito escuras)

**Voice recognition:**
- Web Speech API varia muito por browser/SO
- Não suporta bem português em alguns browsers
- Comandos curtos (< 5 palavras) funcionam melhor
- Latência: 500-1000ms entre fala e reconhecimento

**3D rendering:**
- Limite prático de ~100K nós antes de stutter
- Links (edges) não otimizados = O(n²) complexidade
- Câmera sem constraints: pode "virar" enquanto navega

**Quando não usar:**
- Dados estritamente tabulares (use DataTable normal)
- Grafos > 1M nós (usar WebGL direto, não Three.js)
- Aplicações que exigem precisão de cliques (hand tracking é aproximado)

**Manutenção:**
- MediaPipe Task Vision mudou API recentemente (v0.10+)
- Web Speech API não padronizado entre browsers
- Three.js major versions quebram backwards compatibility

## Conexões
- [[MediaPipe Face Recognition Local Edge]]
- [[Micro-Handpose WebGPU Hand Tracking Browser]]
- [[github-fun-with-cv-tutorials-collidingscopes]]

## Histórico
- 2025-07-21: Nota original criada (zettelkasten)
- 2026-04-02: Reescrita como guia de implementação prática
