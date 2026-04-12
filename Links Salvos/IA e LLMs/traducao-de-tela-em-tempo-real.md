---
tags: []
source: https://x.com/sharbel/status/2039299741826142377?s=20
date: 2026-04-02
tipo: aplicacao
---

# Implementar OCR Local + Tradução em Tempo Real para Qualquer Interface

## Resumo
Tradução de tela em tempo real via OCR local é um pipeline que combina reconhecimento óptico de caracteres + modelos de tradução compactos rodando 100% offline. Permite ler e traduzir qualquer texto visível — jogos, apps, vídeos — sem APIs externas, latência aceitável (<100ms por frame) e zero custos por requisição.

## O que é

Tradução de tela em tempo real é um sistema de visão computacional que:
1. Captura frames da tela continuamente (30+ FPS)
2. Detecta regiões com texto usando redes neurais de detecção (YOLO, CRAFT, etc.)
3. Processa OCR local em cada região (Tesseract, EasyOCR, PaddleOCR, RapidOCR, OneOCR)
4. Traduz o texto reconhecido usando modelos de tradução compactos (marian, flores-101 ou LLMs quantizados)
5. Renderiza a tradução sobreposta no frame original

A diferença crítica da abordagem clássica é que tudo roda **em máquina local**, sem dependência de Internet. Isso elimina latência de rede, custos por API e risco de exposição de dados sensíveis (documentos corporativos, propriedade intelectual em pitch decks).

## Por que importa

**1. Acesso imediato a conteúdo em idioma estrangeiro** — jogos sem patch de tradução, streams ao vivo, documentos técnicos corporativos e interfaces de software passam a ser acessíveis sem espera ou custo.

**2. Privacidade e segurança** — dados visuais nunca saem da máquina local. Crítico para contextos de compliance (documentos confidenciais) ou uso corporativo.

**3. Custo zero** — sem cobranças por requisição de API (Google Translate, DeepL) que escalavam com volume de uso.

**4. Zero latência de rede** — a captura e processamento acontecem no mesmo ciclo de renderização, mantendo a fluidez da experiência do usuário (gameplay, visualização de vídeo, navegação em documentos).

**5. Customização de domínio** — é possível treinar ou fine-tunar modelos de OCR e tradução para domínios específicos (terminologia médica, jurídica, nomes de marcas em linguagem de games).

## Como funciona / Como implementar

### Arquitetura mínima

```
[Screen Capture] → [Text Detection (YOLO/CRAFT)] → [OCR (EasyOCR)] → [Translation Model] → [Text Rendering] → [Output Display]
```

### Pipeline em Python + OpenCV

```python
import cv2
import easyocr
from transformers import pipeline
import numpy as np
import time

class ScreenTranslator:
    def __init__(self, source_lang='ja', target_lang='pt'):
        # Inicializa OCR reader
        self.reader = easyocr.Reader([source_lang], gpu=True)
        
        # Inicializa modelo de tradução compacto
        self.translator = pipeline(
            'translation_ja_to_pt',
            model='Helsinki-NLP/opus-mt-ja-pt',
            device=0
        )
        self.source_lang = source_lang
        self.target_lang = target_lang
        
    def capture_screen(self):
        """Captura tela usando mss para performance."""
        import mss
        with mss.mss() as sct:
            monitor = sct.monitors[1]  # Monitor principal
            screenshot = sct.grab(monitor)
            frame = cv2.cvtColor(np.array(screenshot), cv2.COLOR_RGBA2BGR)
        return frame
    
    def process_frame(self, frame):
        """Processa OCR + tradução em um frame."""
        results = self.reader.readtext(frame)
        translated_frame = frame.copy()
        
        for (bbox, text, confidence) in results:
            if confidence < 0.3:  # Filtro de confiança
                continue
            
            # Traduz o texto
            translated_text = self.translator(text)[0]['translation_text']
            
            # Renderiza bounding box e texto traduzido
            bbox = np.array(bbox, dtype=int)
            top_left = tuple(bbox[0])
            bottom_right = tuple(bbox[2])
            
            # Fundo semi-transparente para legibilidade
            overlay = translated_frame.copy()
            cv2.rectangle(overlay, top_left, bottom_right, (255, 255, 255), -1)
            cv2.addWeighted(overlay, 0.3, translated_frame, 0.7, 0, translated_frame)
            
            # Escreve texto traduzido
            cv2.putText(
                translated_frame,
                translated_text,
                (top_left[0] + 5, top_left[1] + 20),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.6,
                (0, 0, 0),
                2
            )
        
        return translated_frame
    
    def run(self):
        """Loop principal de captura e tradução."""
        while True:
            start_time = time.time()
            
            frame = self.capture_screen()
            output_frame = self.process_frame(frame)
            
            # Exibe FPS
            elapsed = time.time() - start_time
            fps = 1 / elapsed if elapsed > 0 else 0
            cv2.putText(
                output_frame,
                f'FPS: {fps:.1f}',
                (10, 30),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.8,
                (0, 255, 0),
                2
            )
            
            # Exibe em janela ou buffer
            cv2.imshow('Screen Translator', cv2.resize(output_frame, (1280, 720)))
            
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break
        
        cv2.destroyAllWindows()

# Uso
translator = ScreenTranslator(source_lang='ja', target_lang='pt')
translator.run()
```

### Alternativas open-source prontas

**RSTGameTranslation** — suporta EasyOCR, RapidOCR, PaddleOCR, OneOCR, com interface gráfica e presets para idiomas.

```bash
git clone https://github.com/thanhkeke97/RSTGameTranslation.git
cd RSTGameTranslation
pip install -r requirements.txt
python main.py
```

**OCR-Translator (GitHub)** — especializado em tradução de games com suporte a 20+ idiomas, modelos offline.

**Realtime Screen OCR Translator** (Steam) — aplicação compilada pronta para uso, sem linha de comando, integrada ao Windows.

## Stack técnico

**OCR (Detecção + Reconhecimento de Caracteres):**
- **EasyOCR** — usar se quiser Python puro, boa suporte multilíngue
- **PaddleOCR** — mais rápido, menos memória, suporte a idiomas asiáticos melhor
- **RapidOCR** — ultra-otimizado, viável em dispositivos edge
- **Tesseract** — legacy, ainda útil para idiomas específicos

**Detecção de Texto (Bounding Boxes):**
- **CRAFT** — detecta texto em qualquer ângulo (importante para HUDs de games)
- **YOLO-v8** (com fine-tuning) — real-time, mas requer treinamento próprio

**Modelos de Tradução:**
- **Helsinki-NLP/opus-mt-\*-\*** — modelos compactos (100-300M params), via HuggingFace
- **Whisper + Small LLM** — para contexto maior, mas latência ~500ms
- **LLMs quantizados (Ollama)** — se quiser tradução com mais contexto (setup mais complexo)

**Renderização / Overlay:**
- **OpenCV** — nativo em Python, com suporte a transformações de imagem
- **PyQt6 / Tkinter** — se quiser GUI customizada
- **Pygame** — para casos que precisam de alta performance gráfica

**Captura de Tela:**
- **mss** — muito mais rápido que PIL.ImageGrab em loops contínuos
- **PIL.ImageGrab** — simples, mas mais lento (~30ms por frame)

## Código prático

### Setup mínimo com EasyOCR + Ollama (tradução local)

```bash
# Instalar dependências
pip install easyocr opencv-python mss ollama

# Baixar modelo de tradução em Ollama (rodar localmente)
ollama pull translate  # Modelo especializado em tradução
```

```python
import easyocr
import cv2
import mss
import requests
import json

reader = easyocr.Reader(['ja'], gpu=True)

def translate_with_ollama(text):
    """Usa Ollama para tradução (roda local, requer ollama serve)."""
    response = requests.post(
        'http://localhost:11434/api/generate',
        json={
            'model': 'translate',  # ou outro modelo disponível
            'prompt': f'Traduza para português: {text}',
            'stream': False
        }
    )
    return response.json()['response'].strip()

with mss.mss() as sct:
    monitor = sct.monitors[1]
    screenshot = sct.grab(monitor)
    frame = cv2.cvtColor(np.array(screenshot), cv2.COLOR_RGBA2BGR)

results = reader.readtext(frame)
for bbox, text, conf in results:
    if conf > 0.4:
        translated = translate_with_ollama(text)
        print(f"{text} → {translated}")
```

### Otimização para FPS alto (crítico em games)

```python
import threading
from queue import Queue

class AsyncScreenTranslator:
    def __init__(self):
        self.ocr_queue = Queue(maxsize=2)
        self.translation_queue = Queue(maxsize=2)
        
    def ocr_worker(self):
        """Thread dedicada a OCR."""
        while True:
            frame = self.ocr_queue.get()
            results = self.reader.readtext(frame)
            self.translation_queue.put(results)
    
    def run_async(self):
        """Roda OCR e rendering em threads separadas."""
        ocr_thread = threading.Thread(target=self.ocr_worker, daemon=True)
        ocr_thread.start()
        
        while True:
            frame = self.capture_screen()
            self.ocr_queue.put_nowait(frame)  # Non-blocking
            
            try:
                results = self.translation_queue.get_nowait()
                frame = self.render_results(frame, results)
            except:
                pass  # Não tem resultado pronto ainda
            
            cv2.imshow('Async Translator', frame)
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break
```

## Armadilhas e Limitações

**1. Fontes estilizadas e HUDs de games**
- OCR falha em fonts renderizadas diretamente em shaders (UI de games modernos), antialiasing agressivo, e text com efeitos (shadow, glow).
- Solução: usar CRAFT ou treinar detector custom em imagens de games. Alternativa: integrar com API de OCR de device (Windows.Media.Ocr) que tem drivers otimizados.

**2. Latência de OCR + Tradução**
- EasyOCR + modelo de tradução podem levar 50-200ms dependendo do volume de texto na tela. Em games a 60 FPS, isso significa um lag visível entre frame capturado e tradução renderizada.
- Solução: implementar threads assíncronas (OCR em thread 1, tradução em thread 2, rendering em thread principal). Usar modelos menores (RapidOCR, modelos INT8 quantizados).

**3. Custo de memória**
- EasyOCR + modelo de tradução carregam 500MB-2GB de memória (GPU VRAM). Em máquinas com <8GB VRAM, isso comprime availability para outros apps.
- Solução: usar PaddleOCR (mais leve), quantizar modelos de tradução, ou optar por APIs lightweight como TrOCR com fine-tuning.

**4. Reconhecimento de idioma misto**
- Um frame pode ter texto em múltiplos idiomas (eng + jp em mesmo game). EasyOCR suporta multi-language, mas a detecção de qual idioma usar é heurística e falha frequentemente.
- Solução: manter um estado de idioma detectado por região, ou treinar modelo custom que rotula idiomas por bounding box.

**5. Contexto de tradução perdido**
- Modelos de tradução simples não têm contexto de UI/game para traduzir termos de forma consistente (um NPC pode ter nome diferente em botão de diálogo vs texto de fala).
- Solução: manter dicionário local de termos (ex: "Boss" → "Chefe"), ou usar LLM com prompt que inclui contexto anterior de tradução (mais latência, menos viável em real-time).

## Conexões

- [[Modelos de Tradução Multilíngue]] — arquitetura de OPUS-MT e Helsinki-NLP
- [[OCR Local e Tesseract]] — técnicas de reconhecimento óptico de caracteres
- [[PaddleOCR para Idiomas Asiáticos]] — OCR especializado
- [[Anotações Visuais Como Input para IA]] — input visual para agentes
- [[Pipelines Multimodais de IA Permitem Produção Automatizada de Vídeo a Custo Marginal Próximo de Zero|Pipelines Multimodais de IA]] — visão + linguagem
- [[Quantizacao-de-llms|Quantização de LLMs]] — para models de tradução compactos

## Histórico de Atualizações
- 2026-04-11: Expandida com arquitetura, código prático, stack técnico, armadilhas e otimizações para real-time
- 2026-04-02: Nota criada a partir de Telegram