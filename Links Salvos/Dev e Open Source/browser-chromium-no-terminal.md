---
tags: [browser, terminal, rust, chromium, cli, webgpu, webgl, open-source, automation]
source: https://x.com/Star_Knight12/status/2039355225895760062?s=20
date: 2026-04-02
tipo: aplicacao
---

# Rodar Browser Chromium Completo no Terminal sem X11

## O que é

Carbonyl é um browser Chromium portado para funcionar em TTY (terminal), renderizando como ANSI/ASCII colorido. Suporta WebGL, WebGPU, áudio, vídeo a 60 FPS. Permite automação remota via SSH sem need for X11 forwarding ou VNC.

## Como implementar

**Install e uso básico:**
```bash
cargo install carbonyl
# ou build from source
git clone https://github.com/fathyb/carbonyl
cd carbonyl
./build.sh

# Executar
carbonyl https://example.com

# Via SSH (sem servidor X11)
ssh user@remote "carbonyl https://example.com"
```

**Caso de uso 1: Teste de interface em CI/CD**

```bash
#!/bin/bash
# test-ci.sh - Rodar testes de screenshot em servidor headless

# Antes: Puppeteer em Node (overhead)
# Agora: Carbonyl direto
carbonyl --screenshot=output.png --window-size=1920,1080 \
  https://staging.app.com

# Verificar visual
if [ -f output.png ]; then
  # Comparar com golden screenshot
  compare -metric AE golden.png output.png diff.png
fi
```

**Caso de uso 2: Scraping com renderização real**

```python
import subprocess
import time
import os

class TerminalBrowser:
    def __init__(self):
        self.proc = None

    def screenshot(self, url, output_file):
        """Capturar screenshot via Carbonyl"""
        cmd = [
            'carbonyl',
            f'--screenshot={output_file}',
            '--window-size=1920,1080',
            '--disable-gpu',  # CPU-only (mais compatível)
            url
        ]
        result = subprocess.run(cmd, capture_output=True, timeout=30)
        return result.returncode == 0

    def eval_js(self, url, javascript):
        """Executar JS no page (advanced)"""
        # Carbonyl suporta DevTools Protocol
        # Implementação seria via WebSocket remote
        pass

browser = TerminalBrowser()
browser.screenshot('https://example.com', 'output.png')
```

**Caso de uso 3: Automação remota via SSH**

```bash
# Local machine
ssh -X remote_server "DISPLAY=:0 carbonyl https://dashboard.company.com"

# Ou melhor: sem X11 overhead
ssh remote_server "carbonyl https://dashboard.company.com" > page.html

# Capturar output como imagem (requer imagemagick)
ssh remote_server "carbonyl --screenshot - https://site.com" | \
  convert - output.png
```

**Caso de uso 4: Teste de compatibilidade WebGL/WebGPU**

```html
<!-- test.html -->
<canvas id="canvas"></canvas>
<script>
const canvas = document.getElementById('canvas');
const gl = canvas.getContext('webgl');

if (gl) {
  console.log('WebGL suportado');
  gl.clearColor(0, 0, 1, 1);
  gl.clear(gl.COLOR_BUFFER_BIT);
} else {
  console.log('WebGL NÃO suportado');
}
</script>
```

```bash
carbonyl file:///test.html
# Se renderizar azul = WebGL funciona
```

**Caso de uso 5: Monitoramento contínuo de página**

```bash
#!/bin/bash
# monitor.sh - Capturar estado de página a cada minuto

while true; do
  timestamp=$(date +%s)
  carbonyl --screenshot="screenshots/$timestamp.png" \
    https://api-status.company.com

  if [ $? -ne 0 ]; then
    echo "[ERROR] Carbonyl falhou em $timestamp"
    # Enviar alerta
  fi

  sleep 60
done
```

## Stack e requisitos

- **Carbonyl**: build from source (Rust)
- **Rust**: 1.70+
- **Dependências**: libx11 (para input), libxcb (para X11)
- **Terminal**: suporte ANSI-256 colors (xterm, tmux, bash)
- **Alternativa sem GUI**: rodar em container Docker Alpine

```dockerfile
FROM rust:latest
RUN git clone https://github.com/fathyb/carbonyl.git /app
WORKDIR /app
RUN ./build.sh
ENTRYPOINT ["carbonyl"]
```

**Requisitos de hardware:**
- CPU: 2+ cores (rendering é CPU-intensive)
- RAM: 512MB mínimo; 2GB+ recomendado
- Disk: 50MB para binary

**Browser compatibilidade:**
- Suporta JS (V8 engine), WebGL, WebGPU, áudio, vídeo
- Não suporta: Flash (deprecado anyway), PPAPI plugins

## Armadilhas e limitações

1. **Limitação: fonte de caracteres**: Qualidade de renderização depende de fonte terminal. Use monospace (Courier, Menlo, DejaVu).

2. **Armadilha: cores limitadas**: 256 cores ANSI é limite. Imagens ficam pixeladas/low-quality. Para documentação, PDF é melhor.

3. **Limitação: input**: Sem mouse (TTY não suporta bem). Navegação via teclado (Tab, Enter).

4. **Armadilha: performance**: Renderizar 1920x1080 em ASCII é slow (~2-3 seg por frame). Para testes rápidos, reduzir resolução.

5. **Limitação: proprietary sites**: Sites com DRM (Netflix, Disney+) não funcionam (como esperado).

## Conexões

- [[web-scraping-sem-api-para-agentes-ia]] - Usar Carbonyl para scraping com JS
- [[spec-driven-ai-coding]] - Gerar testes com Carbonyl para validar código
- [[renderizacao-virtualizada-de-terminal]] - Técnicas de renderização terminal

## Histórico

- 2026-04-02: Nota original
- 2026-04-02: Reescrita com casos práticos
