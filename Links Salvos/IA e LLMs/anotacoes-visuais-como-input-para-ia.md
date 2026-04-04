---
tags: []
source: https://x.com/om_patel5/status/2036599662665249060?s=20
date: 2026-04-02
tipo: aplicacao
---
# Implementar Feedback Visual Direto para Agentes

## O que é
Ferramenta que permite desenhar anotações (círculos, setas, texto) diretamente sobre a tela, convertendo-as em input multimodal estruturado para agentes de IA. Reduz ciclos de feedback de 5-10 turnos para 1-2 ao eliminar ambiguidade de descrição textual.

## Como implementar
**1. Captura de tela anotada**:

```python
from PIL import Image, ImageDraw
from datetime import datetime

class ScreenAnnotator:
    def __init__(self):
        self.original_image = None
        self.drawing = None
        self.annotations = []

    def capture_screenshot(self):
        """Captura tela atual."""
        import pyautogui
        screenshot = pyautogui.screenshot()
        self.original_image = screenshot
        return screenshot

    def add_circle(self, x: int, y: int, radius: int, color: str = "red", width: int = 3):
        """Adiciona círculo anotado."""
        draw = ImageDraw.Draw(self.original_image)
        bbox = [x - radius, y - radius, x + radius, y + radius]
        draw.ellipse(bbox, outline=color, width=width)
        self.annotations.append({
            "type": "circle",
            "position": (x, y),
            "radius": radius,
            "color": color
        })

    def add_arrow(self, x1: int, y1: int, x2: int, y2: int, color: str = "blue", width: int = 3):
        """Adiciona seta anotada."""
        draw = ImageDraw.Draw(self.original_image)
        # Desenha linha
        draw.line([(x1, y1), (x2, y2)], fill=color, width=width)
        # Adiciona ponta de seta
        import math
        angle = math.atan2(y2 - y1, x2 - x1)
        arrow_size = 20
        x3 = x2 - arrow_size * math.cos(angle - math.pi / 6)
        y3 = y2 - arrow_size * math.sin(angle - math.pi / 6)
        x4 = x2 - arrow_size * math.cos(angle + math.pi / 6)
        y4 = y2 - arrow_size * math.sin(angle + math.pi / 6)
        draw.line([(x2, y2), (x3, y3)], fill=color, width=width)
        draw.line([(x2, y2), (x4, y4)], fill=color, width=width)

        self.annotations.append({
            "type": "arrow",
            "from": (x1, y1),
            "to": (x2, y2),
            "color": color
        })

    def add_text(self, x: int, y: int, text: str, color: str = "black", size: int = 20):
        """Adiciona texto anotado."""
        draw = ImageDraw.Draw(self.original_image)
        draw.text((x, y), text, fill=color)
        self.annotations.append({
            "type": "text",
            "position": (x, y),
            "content": text,
            "color": color
        })

    def save_annotated(self, path: str = None):
        """Salva imagem anotada."""
        if not path:
            path = f"annotated_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png"
        self.original_image.save(path)
        return path
```

**2. Parser de anotações para texto estruturado**:

```python
def generate_annotation_context(annotations: list, image_dimensions: tuple) -> str:
    """Converte anotações em descrição estruturada para o agente."""
    width, height = image_dimensions

    context = "Anotações do usuário na tela:\n\n"

    for i, annotation in enumerate(annotations, 1):
        if annotation["type"] == "circle":
            x, y = annotation["position"]
            r = annotation["radius"]
            # Converter para posição relativa (porcentagem)
            x_pct = (x / width) * 100
            y_pct = (y / height) * 100
            context += f"- Círculo {i}: posição ({x_pct:.1f}%, {y_pct:.1f}%), raio={r}px. Cor: {annotation['color']}.\n"

        elif annotation["type"] == "arrow":
            x1, y1 = annotation["from"]
            x2, y2 = annotation["to"]
            x1_pct, y1_pct = (x1 / width) * 100, (y1 / height) * 100
            x2_pct, y2_pct = (x2 / width) * 100, (y2 / height) * 100
            context += f"- Seta {i}: de ({x1_pct:.1f}%, {y1_pct:.1f}%) para ({x2_pct:.1f}%, {y2_pct:.1f}%). Cor: {annotation['color']}.\n"

        elif annotation["type"] == "text":
            x, y = annotation["position"]
            x_pct, y_pct = (x / width) * 100, (y / height) * 100
            context += f"- Texto {i}: '{annotation['content']}' em ({x_pct:.1f}%, {y_pct:.1f}%). Cor: {annotation['color']}.\n"

    return context
```

**3. Integração com Claude Code**:

```python
from anthropic import Anthropic
import base64

def send_annotated_screenshot_to_agent(annotated_image_path: str, user_feedback: str):
    """Envia screenshot anotado com feedback estruturado."""
    client = Anthropic()

    # Codificar imagem em base64
    with open(annotated_image_path, "rb") as f:
        image_base64 = base64.standard_b64encode(f.read()).decode("utf-8")

    # Enviar com contexto estruturado
    response = client.messages.create(
        model="claude-3-5-sonnet-20241022",
        max_tokens=2000,
        messages=[{
            "role": "user",
            "content": [
                {
                    "type": "image",
                    "source": {
                        "type": "base64",
                        "media_type": "image/png",
                        "data": image_base64
                    }
                },
                {
                    "type": "text",
                    "text": f"""Vejo as anotações do usuário na screenshot.

Feedback do usuário: {user_feedback}

As anotações visuais (círculos, setas, textos) indicam exatamente o que precisa ser corrigido.
Implemente as correções."""
                }
            ]
        }]
    )

    return response.content[0].text
```

**4. Script interativo com mouse listener**:

```python
from pynput import mouse
import threading

class InteractiveAnnotator:
    def __init__(self):
        self.annotator = ScreenAnnotator()
        self.drawing_mode = None
        self.start_pos = None
        self.listener = mouse.Listener(
            on_move=self.on_move,
            on_click=self.on_click,
            on_scroll=self.on_scroll
        )

    def on_click(self, x, y, button, pressed):
        if button == mouse.Button.left:
            if pressed:
                self.start_pos = (x, y)
                self.drawing_mode = "circle"  # ou "arrow" dependendo de tecla pressionada
            else:
                if self.drawing_mode == "circle":
                    radius = max(abs(x - self.start_pos[0]), abs(y - self.start_pos[1]))
                    self.annotator.add_circle(self.start_pos[0], self.start_pos[1], radius)

    def on_scroll(self, x, y, dx, dy):
        """Scroll para ajustar tamanho/raio."""
        pass

    def start_annotation(self):
        """Inicia modo de anotação."""
        print("Capturando tela...")
        self.annotator.capture_screenshot()
        print("Clique e arraste para anotar (ESC para terminar)")

        self.listener.start()
        # Aguardar ESC
        try:
            while True:
                time.sleep(0.1)
        except KeyboardInterrupt:
            self.listener.stop()
            path = self.annotator.save_annotated()
            print(f"Anotações salvas em {path}")
            return path
```

**5. CLI para fluxo completo**:

```bash
#!/usr/bin/env python3
import argparse

parser = argparse.ArgumentParser(description="Feedback visual para agentes de IA")
parser.add_argument("--capture", action="store_true", help="Capturar tela com anotações")
parser.add_argument("--feedback", type=str, help="Texto de feedback do usuário")
parser.add_argument("--image", type=str, help="Caminho da imagem anotada")

args = parser.parse_args()

if args.capture:
    annotator = InteractiveAnnotator()
    image_path = annotator.start_annotation()

if args.feedback and args.image:
    response = send_annotated_screenshot_to_agent(args.image, args.feedback)
    print("Resposta do agente:")
    print(response)
```

## Stack e requisitos
- **Captura**: `pyautogui`, `PIL` (Pillow)
- **Mouse control**: `pynput`
- **Modelo**: Claude 3.5 Sonnet (vision multimodal)
- **Armazenamento**: local ou S3 para imagens
- **Sistema operacional**: Windows, macOS, Linux (suporta todos via pyautogui)
- **Tempo de setup**: ~15 minutos

## Armadilhas e limitações
- **Ambiguidade de anotações**: múltiplos usuários podem interpretar mesma anotação diferentemente. Inclua context textual complementar.
- **Resolução de tela**: em resoluções muito altas, anotações podem perder precisão. Normalizar para percentuais de tela.
- **Performance de rendering**: desenhar muitas anotações ralenta captura. Limitar a ~20 anotações por screenshot.
- **Sensibilidade ao layout**: se UI mudar entre screenshots, anotações antigas deixam de ser relevantes. Sempre usar screenshot mais recente.

## Conexões
[[Claude Code]], [[Multimodal Input para Agentes]], [[Tool Use com Vision]], [[Interface Humano-Agente]]

## Histórico
- 2026-04-02: Nota criada
- 2026-04-02: Reescrita em padrão aplicação
