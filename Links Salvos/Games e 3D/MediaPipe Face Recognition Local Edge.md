---
date: 2026-03-24
tags: [mediapipe, face-recognition, local-ai, edge-computing, computer-vision, google]
source: https://x.com/neural_avb/status/2036202822186967499?s=20
tipo: aplicacao
---

# Rodar face recognition local em web, mobile ou desktop

## O que é
Framework de computer vision do Google para executar detecção de rosto, hand tracking, pose estimation e tarefas similares **inteiramente no dispositivo** sem enviar dados para cloud. Face Recognition especificamente: 468 pontos de face mesh + 10 landmarks de íris = rastreamento facial completo em 3.7 MB.

## Como implementar

**Setup Web (JavaScript/TypeScript):**

```javascript
// NPM setup
npm install @mediapipe/tasks-vision

// Carregamento do modelo
import vision from "@mediapipe/tasks-vision";

const createFaceDetector = async () => {
  const vision = await FaceDetector.createFromOptions(
    await FilesetResolver.forVisionTasks(
      "https://cdn.jsdelivr.net/npm/@mediapipe/tasks-vision/wasm"
    ),
    { runningMode: "VIDEO", numFaces: 5 }
  );
  return vision;
};

// Detecção em tempo real
const faceDetector = await createFaceDetector();
const video = document.querySelector("video");

const detectFaces = async () => {
  const detections = await faceDetector.detectForVideo(video, performance.now());

  detections.detections.forEach(detection => {
    const { boundingBox, keypoints } = detection;
    console.log(`Rosto detectado: bbox=${boundingBox}`);
    keypoints.forEach(kp => {
      console.log(`${kp.name}: (${kp.x}, ${kp.y})`);
    });
  });
};

// Loop de renderização
const render = async () => {
  await detectFaces();
  requestAnimationFrame(render);
};

video.addEventListener("loadedmetadata", () => render());
```

**Integração com Canvas/WebGL para visualização:**

```javascript
// Desenhar face mesh
function drawFaceMesh(detection, canvas) {
  const ctx = canvas.getContext("2d");

  // Desenhar bounding box
  const bbox = detection.boundingBox;
  ctx.strokeStyle = "rgba(0, 255, 0, 0.8)";
  ctx.lineWidth = 2;
  ctx.strokeRect(bbox.originX, bbox.originY, bbox.width, bbox.height);

  // Desenhar keypoints
  detection.keypoints.forEach(kp => {
    ctx.fillStyle = "rgba(255, 0, 0, 0.8)";
    ctx.beginPath();
    ctx.arc(kp.x * canvas.width, kp.y * canvas.height, 4, 0, 2 * Math.PI);
    ctx.fill();
  });
}
```

**Setup Python local (desktop/server):**

```python
import mediapipe as mp
import cv2

# Inicializar modelo
mp_face_detection = mp.solutions.face_detection
face_detector = mp_face_detection.FaceDetection(
    model_selection=0,  # 0=short-range (< 2m), 1=full-range
    min_detection_confidence=0.5
)

# Processar vídeo
cap = cv2.VideoCapture(0)

while cap.isOpened():
    ret, frame = cap.read()
    if not ret:
        break

    results = face_detector.process(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB))

    if results.detections:
        for detection in results.detections:
            # Bounding box
            bbox = detection.location_data.relative_bounding_box
            h, w, c = frame.shape
            x = int(bbox.xmin * w)
            y = int(bbox.ymin * h)
            width = int(bbox.width * w)
            height = int(bbox.height * h)

            cv2.rectangle(frame, (x, y), (x + width, y + height), (0, 255, 0), 2)

            # Keypoints (olhos, nariz, boca)
            for keypoint in detection.location_data.relative_keypoints:
                kp_x = int(keypoint.x * w)
                kp_y = int(keypoint.y * h)
                cv2.circle(frame, (kp_x, kp_y), 5, (255, 0, 0), -1)

    cv2.imshow("Face Detection", frame)
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()
```

**Casos de uso avançados:**

```python
# Face liveness detection (detectar se é rosto real vs foto)
def liveness_check(detections, consecutive_frames=5):
    """
    Verificar movimento de rosto em N frames consecutivos
    Rosto estático por muito tempo = suspeito (foto/vídeo)
    """
    face_positions = []
    for detection in detections:
        bbox = detection.location_data.relative_bounding_box
        center = (bbox.xmin + bbox.width/2, bbox.ymin + bbox.height/2)
        face_positions.append(center)

    # Calcular variância de movimento
    if len(face_positions) >= consecutive_frames:
        variance = sum([
            abs(face_positions[i][0] - face_positions[i-1][0]) +
            abs(face_positions[i][1] - face_positions[i-1][1])
            for i in range(1, len(face_positions))
        ]) / (len(face_positions) - 1)

        return variance > 0.01  # Threshold de movimento

# Detecção de expresión (piscada, sorriso)
def detect_blink(keypoints_history):
    """
    Usar posição dos landmarks dos olhos para detectar piscadas
    Eye aspect ratio: distância vertical / distância horizontal
    """
    for kp in keypoints_history[-1]:
        if "eye" in kp.name:
            # Implementar EAR (Eye Aspect Ratio)
            pass
```

## Stack e requisitos

**Web/Browser:**
- Node.js 14+ (para build)
- Browser com suporte WebGL/WebAssembly (Chrome, Firefox, Safari 15+)
- Webcam ou arquivo de vídeo
- ~3.7 MB download (modelo comprimido)

**Desktop/Python:**
- Python 3.8+
- `pip install mediapipe opencv-python`
- GPU opcional (CUDA 11+ para aceleração, CPU viable)
- ~50-100 MB RAM durante execução

**Performance:**
- Latência: 50-100ms em CPU, 10-20ms em GPU
- Throughput: 1 minuto de vídeo processado em ~10 segundos (6x tempo real)
- Sem custos de API (roda localmente 100%)

## Armadilhas e limitações

**Limitações de detecção:**
- Não funciona bem com rosto de lado > 90 graus (precisa frontal)
- Distância mínima ~0.5m, máxima ~3-4m (depende resolução câmera)
- Óculos escuros, máscaras reduzem acurácia
- Requer boa iluminação (faces muito escuras falham)

**Performance:**
- Model selection 0 = rápido mas menos robusto (~30ms), model 1 = mais preciso (~80ms)
- Em mobile baixo fim, frame rate pode cair abaixo de 15 FPS
- WebAssembly em Safari é 2-3x mais lento que em Chrome

**Quando não usar MediaPipe:**
- Reconhecimento facial (comparar dois rostos) = não é designed para isso, usar [[Face Recognition API]] ou face_recognition library
- Múltiplos rostos muitíssimo próximos = bounding boxes se sobrepõem
- Análise forense/precisão judicial = modelos de face detection não são validados legalmente

**Dados e privacidade:**
- Garantia local é real (nenhum upload), mas ainda captura vídeo cru localmente
- Se armazenar frames em disco, aplicar criptografia
- GDPR/CCPA: documentar processamento local, ainda é "processamento de dados biométricos"

## Conexões
- [[Micro-Handpose WebGPU Hand Tracking Browser]]
- [[github-fun-with-cv-tutorials-collidingscopes]]
- [[tony-stark-jarvis-visualizacao-3d-mediapipe]]

## Histórico
- 2026-03-24: Nota original criada
- 2026-04-02: Reescrita como guia de implementação prática
