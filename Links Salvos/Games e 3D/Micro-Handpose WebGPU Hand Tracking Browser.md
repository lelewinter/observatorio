---
date: 2026-03-24
tags: [computer-vision, webgpu, hand-tracking, browser, performance, lightweight]
source: https://x.com/nsthorat/status/2036287147179651477?s=20
tipo: aplicacao
---

# Hand tracking 21 keypoints em browser com latência <3ms

## O que é
Implementação extremamente otimizada de detecção de mão rodando 100% em GPU via WebGPU shaders. 15 shaders WGSL paralelizados: palm detection → landmark inference. 74KB JS + 7.7MB modelo. 2.2ms latência em desktop (454 FPS), 72ms em mobile (13.9 FPS). 4x menor e 2x mais rápido que MediaPipe.

## Como implementar

**Setup básico:**

```bash
npm install @svenflow/micro-handpose
```

**JavaScript - Detecção em tempo real:**

```javascript
import { createHandpose } from "@svenflow/micro-handpose";

let handpose;

async function init() {
  // Carregar modelo (7.7MB, ~2s)
  handpose = await createHandpose();
}

async function detectHands(videoElement) {
  // Detecta 1-2 mãos por frame
  const predictions = await handpose.estimateHands(videoElement, false);

  predictions.forEach((hand, handIdx) => {
    const { keypoints, bbox, confidence } = hand;

    console.log(`Hand ${handIdx}: confidence=${confidence.toFixed(2)}`);

    // 21 keypoints nomeados
    const keyPointNames = [
      "wrist", "thumb_cmc", "thumb_mcp", "thumb_ip", "thumb_tip",
      "index_mcp", "index_pip", "index_dip", "index_tip",
      "middle_mcp", "middle_pip", "middle_dip", "middle_tip",
      "ring_mcp", "ring_pip", "ring_dip", "ring_tip",
      "pinky_mcp", "pinky_pip", "pinky_dip", "pinky_tip"
    ];

    keypoints.forEach((kp, idx) => {
      console.log(`${keyPointNames[idx]}: (${kp[0]}, ${kp[1]})`);
    });
  });

  return predictions;
}

// Loop principal
const video = document.querySelector("video");
const canvas = document.querySelector("canvas");
const ctx = canvas.getContext("2d");

async function render() {
  ctx.drawImage(video, 0, 0, canvas.width, canvas.height);

  const hands = await detectHands(video);

  // Desenhar skeleton
  hands.forEach(hand => {
    drawHandSkeleton(ctx, hand.keypoints);
  });

  requestAnimationFrame(render);
}

video.addEventListener("loadedmetadata", async () => {
  await init();
  render();
});
```

**Desenhar hand skeleton com lógica de conexão:**

```javascript
function drawHandSkeleton(ctx, keypoints) {
  // Conexões entre dedos (21 keypoints)
  const connections = [
    // Dedos
    [0, 1], [1, 2], [2, 3], [3, 4],        // Polegar
    [0, 5], [5, 6], [6, 7], [7, 8],        // Indicador
    [0, 9], [9, 10], [10, 11], [11, 12],   // Meio
    [0, 13], [13, 14], [14, 15], [15, 16], // Anel
    [0, 17], [17, 18], [18, 19], [19, 20]  // Mínimo
  ];

  // Desenhar conexões (linhas)
  ctx.strokeStyle = "rgba(0, 255, 0, 0.8)";
  ctx.lineWidth = 2;
  connections.forEach(([start, end]) => {
    ctx.beginPath();
    ctx.moveTo(keypoints[start][0], keypoints[start][1]);
    ctx.lineTo(keypoints[end][0], keypoints[end][1]);
    ctx.stroke();
  });

  // Desenhar keypoints (círculos)
  ctx.fillStyle = "rgba(255, 0, 0, 0.9)";
  keypoints.forEach(kp => {
    ctx.beginPath();
    ctx.arc(kp[0], kp[1], 5, 0, 2 * Math.PI);
    ctx.fill();
  });
}
```

**Gesture recognition avançada:**

```javascript
function detectGesture(hand) {
  const { keypoints, handedness } = hand;

  // Extrair coordenadas normalizadas
  const wrist = keypoints[0];
  const thumbTip = keypoints[4];
  const indexTip = keypoints[8];
  const middleTip = keypoints[12];
  const ringTip = keypoints[16];
  const pinkyTip = keypoints[20];

  const indexBase = keypoints[5];
  const middleBase = keypoints[9];

  // Thumbs up: polegar acima de todos, outros dedos fechados
  const thumbsUp = (
    thumbTip[1] < indexTip[1] &&
    thumbTip[1] < middleTip[1] &&
    distance(indexTip, indexBase) < 30 &&
    distance(pinkyTip, keypoints[17]) < 30
  );

  // Peace sign: índice e meio abertos, outros fechados
  const peaceSign = (
    distance(indexTip, middleTip) > 50 &&
    distance(ringTip, keypoints[13]) < 30 &&
    distance(pinkyTip, keypoints[17]) < 30
  );

  // Pinça: polegar e índice próximos
  const pinch = distance(thumbTip, indexTip) < 20;

  // OK sinal: polegar e índice fechados, outros abertos
  const okSign = (
    distance(thumbTip, indexTip) < 25 &&
    distance(middleTip, middleBase) > 40
  );

  return { thumbsUp, peaceSign, pinch, okSign };
}

function distance(p1, p2) {
  return Math.sqrt((p1[0] - p2[0]) ** 2 + (p1[1] - p2[1]) ** 2);
}
```

**Aplicação: Game controls via hand:**

```javascript
const gameControls = {
  moveLeft: () => console.log("Mover esquerda"),
  moveRight: () => console.log("Mover direita"),
  jump: () => console.log("Pular"),
  attack: () => console.log("Atacar")
};

async function handleGameInput() {
  const hands = await detectHands(video);

  if (hands.length === 0) return;

  const hand = hands[0];
  const gesture = detectGesture(hand);
  const indexTip = hand.keypoints[8];
  const wrist = hand.keypoints[0];

  // Movimento horizontal via posição de índice
  if (indexTip[0] < wrist[0] - 50) {
    gameControls.moveLeft();
  } else if (indexTip[0] > wrist[0] + 50) {
    gameControls.moveRight();
  }

  // Saltar via gesture
  if (gesture.peaceSign) {
    gameControls.jump();
  }

  // Atacar via pinça
  if (gesture.pinch) {
    gameControls.attack();
  }
}
```

## Stack e requisitos

**Browser Support:**
- Chrome 113+ (WebGPU stable)
- Edge 113+ (Chromium base)
- Safari 18+ (WebGPU beta)
- **Firefox**: suporte parcial (WebGPU ainda experimental)

**Performance:**
- Desktop (M4 Pro Chrome): 2.2ms latência, 454 FPS
- Desktop (RTX 3080): <1ms latência, >1000 FPS
- Mobile (iPhone 14 Safari): 72ms latência, 13.9 FPS
- Bandwidth: 7.7MB initial + ~100KB/min metadata

**Hardware:**
- GPU obrigatória (WebGPU compute shaders)
- VRAM: ~100MB durante execução
- CPU: minimal (tudo offloaded pra GPU)
- Webcam: qualquer resolução (640x480 minimum recomendado)

**Dependências:**
- 0 dependências externas (puro WebGPU)
- File size: 74KB JS (17KB gzip) + 7.7MB modelo

## Armadilhas e limitações

**Limitações de detecção:**
- Funciona melhor com palma visível (não detecta mão completamente fechada)
- Lighting ruim degrada accuracy (mãos muito escuras)
- Óclusão parcial: dedos ocultos reduzem confiança
- Requer distância 0.3-2m de câmera (muito perto/longe falha)
- Não detecta ambas mãos se muito próximas (overlap de bounding boxes)

**Performance pitfalls:**
- WebGPU ainda em evolução: Chrome updates podem quebrar (mas raro)
- Safari iOS: 35% mais lento que desktop Chrome mesmo modelo
- Shaders compilados por browser: cold start ~200ms primeira execução
- Gesture detection caseiro é brittle: pequenas variações causam false positives

**Quando não usar Micro-Handpose:**
- Aplicações que precisam de 60+ FPS em mobile (fica <30 FPS)
- Ambientes muito dinâmicos/caóticos (múltiplas mãos ocluídas)
- Sign language recognition profissional (não validado, use MediaPipe Holistic)
- Análise forense (modelo não auditable, weights binários)

**Trade-offs vs MediaPipe:**
- Micro-Handpose: 4x menor, 2x mais rápido, 0 dependências
- MediaPipe: mais stável, > documentação, suporte multi-task (face+pose+hands)
- Escolha Micro-Handpose se **só precisa hands + performance crítica**
- Escolha MediaPipe se **precisa stabilidade + múltiplas tasks**

## Conexões
- [[MediaPipe Face Recognition Local Edge]]
- [[github-fun-with-cv-tutorials-collidingscopes]]
- [[tony-stark-jarvis-visualizacao-3d-mediapipe]]

## Histórico
- 2026-03-24: Nota original criada
- 2026-04-02: Reescrita como guia de implementação prática
