---
tags: [video-generation, ia-local, agentes-llm, hardware-acessivel, wangp, qwen, vram-otimizado]
source: https://x.com/0xCVYH/status/2036546677943746984?s=20
date: 2026-04-02
tipo: aplicacao
atualizado: 2026-04-11
---

# WanGP: Geração de Vídeo Local com Agente LLM Nativo (8GB VRAM)

## O que é

WanGP roda 100% local em máquinas consumer (RTX 3060, RTX 4060, M1 Pro), combinando:
1. **Qwen 3.5VL** (7B visual-language model) — agente que compreende prompts em linguagem natural
2. **Modelo de Diffusão de Vídeo** (LTX-2, Wan 2.2, Hunyuan) — sintetiza vídeo propriamente dito

Diferente de APIs cloud (Runway, Sora) que custam USD 15-30/mês e dependem de internet, WanGP roda offline, sem assinatura, controlado totalmente pelo usuário. Agente LLM não gera vídeo — orquestra: lê seu prompt em português, interpreta intenção, preenche automaticamente parâmetros técnicos (seed, guidance, steps), clica "generate" no Gradio UI. Você vê agente "trabalhar" em tempo real.

**2026 Update:** Versão 11+ traz NVFP4 quantization (reduz VRAM pico de 24GB para ~8GB), suporte a LTX-2 (quality próxima a runway), e Deepy (agente do WanGP que conversa com você).

## Como implementar

### Setup Inicial (One-Click via Pinokio)

WanGP foi simplificado para instalação com clique (via Pinokio no Windows/Mac):

```bash
# Se usar terminal (Linux/advanced):
git clone https://github.com/deepbeepmeep/Wan2GP
cd Wan2GP
pip install -r requirements.txt

# Download modelos (automático no Pinokio)
# Qwen 3.5VL: ~14GB (auto-downloads primeiro run)
# Diffusion model (LTX-2): ~6GB
# Total: ~20GB disco (comprimido)

python app.py
# Abre em http://localhost:7860
```

### Fluxo Básico (Usando Deepy Agent)

```python
"""
Demonstra controle programático de WanGP.
Na prática, você usa UI Gradio, mas código mostra pipeline.
"""

import requests
import json
import time
import subprocess
from pathlib import Path

class WanGPClient:
    def __init__(self, host: str = "http://localhost:7860"):
        self.host = host
        self.base_url = f"{host}/api"
    
    def text_to_video(
        self,
        prompt: str,
        duration: int = 5,  # segundos
        resolution: str = "720p",  # ou "1080p" se tiver 12GB+
        model: str = "ltx2",  # ltx2, wan2.2, hunyuan
        seed: int = -1,  # -1 = random
        guidance_scale: float = 7.5,  # criatividade vs fidelidade
        steps: int = 20  # passos de diffusion (mais = melhor mas lento)
    ) -> str:
        """
        Gera vídeo via WanGP Gradio API.
        """
        
        # Prepara payload
        payload = {
            "prompt": prompt,
            "duration": duration,
            "resolution": resolution,
            "model": model,
            "seed": seed,
            "guidance_scale": guidance_scale,
            "inference_steps": steps,
            "use_agent": True,  # Ativa Deepy automaticamente
        }
        
        # Envia para backend
        response = requests.post(
            f"{self.host}/api/generate",
            json=payload,
            timeout=3600  # 1 hora timeout
        )
        
        if response.status_code != 200:
            raise Exception(f"Generation failed: {response.text}")
        
        task_data = response.json()
        task_id = task_data["task_id"]
        
        # Poll até conclusão
        return self._wait_for_video(task_id)
    
    def _wait_for_video(self, task_id: str) -> str:
        """
        Aguarda vídeo ser gerado (pode levar 2-5 minutos).
        """
        max_wait = 600  # 10 minutos
        start_time = time.time()
        
        while time.time() - start_time < max_wait:
            response = requests.get(f"{self.host}/api/status/{task_id}")
            status = response.json()
            
            if status["state"] == "COMPLETE":
                return status["output_video_path"]
            
            elif status["state"] == "FAILED":
                raise Exception(f"Generation failed: {status.get('error', 'Unknown')}")
            
            elif status["state"] in ["PROCESSING", "PENDING"]:
                progress = status.get("progress", 0)
                print(f"Generating... {progress:.0f}%")
            
            time.sleep(5)
        
        raise TimeoutError(f"Video generation timed out after {max_wait}s")

# Uso
client = WanGPClient()

prompts = [
    "céu pôr do sol em floresta tropical, estilo anime, cores quentes",
    "gato preto deitado em almofada, câmera lenta, luz do dia",
    "código HTML sendo digitado em editor, verde neon, hacker aesthetic"
]

for prompt in prompts:
    print(f"Generating: {prompt}")
    
    video_path = client.text_to_video(
        prompt=prompt,
        duration=5,
        resolution="720p",
        model="ltx2",
        guidance_scale=7.5,
        steps=20
    )
    
    print(f"✓ Salvo em: {video_path}")
```

### Agência + Orquestração (Multi-Video)

```python
class AutoVideoProducer:
    """
    Gera múltiplos vídeos com agente, composição em lote.
    """
    
    def __init__(self, wangp_host: str = "http://localhost:7860"):
        self.client = WanGPClient(wangp_host)
        self.output_dir = Path("generated_videos")
        self.output_dir.mkdir(exist_ok=True)
    
    def generate_series(self, scene_descriptions: list, batch_name: str = "series"):
        """
        Gera série de vídeos, cada um com duração diferente.
        """
        
        videos = []
        
        for i, scene in enumerate(scene_descriptions):
            print(f"\n[{batch_name}] Scene {i+1}/{len(scene_descriptions)}")
            print(f"  Prompt: {scene['description'][:60]}...")
            
            try:
                # Gera com parâmetros específicos de cada cena
                video_path = self.client.text_to_video(
                    prompt=scene["description"],
                    duration=scene.get("duration", 5),
                    resolution=scene.get("resolution", "720p"),
                    guidance_scale=scene.get("guidance", 7.5),
                    steps=scene.get("steps", 20)
                )
                
                videos.append({
                    "path": video_path,
                    "order": i,
                    "duration": scene.get("duration", 5)
                })
                
                print(f"  ✓ Done: {video_path}")
            
            except Exception as e:
                print(f"  ✗ Failed: {e}")
                # Continue com próxima cena
        
        return videos
    
    def compose_final_video(self, videos: list, output_name: str = "final.mp4"):
        """
        Concatena vídeos em ordem com ffmpeg.
        """
        
        import subprocess
        
        # Ordena por índice
        videos_sorted = sorted(videos, key=lambda x: x["order"])
        
        # Cria concat file para ffmpeg
        concat_file = self.output_dir / "concat.txt"
        with open(concat_file, "w") as f:
            for video in videos_sorted:
                f.write(f"file '{video['path']}'\n")
        
        output_path = self.output_dir / output_name
        
        # Executa ffmpeg
        cmd = [
            "ffmpeg",
            "-f", "concat",
            "-safe", "0",
            "-i", str(concat_file),
            "-c", "copy",  # Copy sem re-encode (rápido)
            str(output_path)
        ]
        
        print(f"\nComposing final video...")
        result = subprocess.run(cmd, check=True)
        
        print(f"✓ Final video: {output_path}")
        return output_path

# Exemplo: Gerar série de "24 horas num dia"
producer = AutoVideoProducer()

scenes = [
    {
        "description": "sol nascendo em montanha, céu rosa/laranja, pássaros voando",
        "duration": 3,
        "resolution": "720p",
        "guidance": 7.5
    },
    {
        "description": "pessoa tomando café em varanda, luz dourada do amanhecer, café fumegando",
        "duration": 4,
        "resolution": "720p"
    },
    {
        "description": "cidade acordando, carros passando, gente indo trabalhar, luz solar aumenta",
        "duration": 5,
        "resolution": "720p"
    },
    {
        "description": "sol no meio do dia, escritório com pessoas trabalhando, luz brilhante pela janela",
        "duration": 4,
        "resolution": "720p"
    },
    {
        "description": "pôr do sol, cores vermelhas/roxas, silhueta de árvores, pessoas indo embora",
        "duration": 5,
        "resolution": "720p"
    }
]

# Gera todos
videos = producer.generate_series(scenes, batch_name="day_cycle")

# Compõe final
final = producer.compose_final_video(videos, "24_hours.mp4")
print(f"\nSérie completa: {final} (total ~30 segundos)")
```

### Controle Fino de Qualidade (NVFP4 Quantization)

```python
class AdvancedWanGPClient(WanGPClient):
    """
    Controle avançado com quantization e otimizações VRAM.
    """
    
    def text_to_video_optimized(
        self,
        prompt: str,
        vram_target: int = 8,  # GB
        quality_target: str = "balanced"  # fast, balanced, quality
    ) -> str:
        """
        Ajusta automaticamente parâmetros conforme VRAM disponível.
        """
        
        # Mapeia target VRAM para configuração
        configs = {
            8: {
                "resolution": "720p",
                "quantization": "fp4",  # NVFP4 reduz VRAM
                "batch_size": 1,
                "model": "ltx2"
            },
            12: {
                "resolution": "1080p",
                "quantization": "fp4",
                "batch_size": 2,
                "model": "ltx2"
            },
            16: {
                "resolution": "1080p",
                "quantization": "fp8",
                "batch_size": 2,
                "model": "wan2.2"
            },
            24: {
                "resolution": "4k",
                "quantization": "fp16",  # Full precision
                "batch_size": 4,
                "model": "hunyuan"
            }
        }
        
        # Usa config mais próxima
        best_config = min(
            configs.items(),
            key=lambda x: abs(x[0] - vram_target)
        )[1]
        
        # Calcula steps baseado em quality
        steps_map = {
            "fast": 15,
            "balanced": 20,
            "quality": 30
        }
        
        return self.text_to_video(
            prompt=prompt,
            resolution=best_config["resolution"],
            model=best_config["model"],
            steps=steps_map.get(quality_target, 20),
            # Passa quantization via payload
            **{"quantization": best_config["quantization"]}
        )

# Uso: automático ajusta à sua máquina
advanced_client = AdvancedWanGPClient()
video = advanced_client.text_to_video_optimized(
    prompt="astronauta em lua, vista para terra",
    vram_target=8,  # RTX 3060
    quality_target="balanced"
)
```

## Stack e requisitos

### Hardware (2026)

| GPU | VRAM | 720p | 1080p | Geração |
|-----|------|------|-------|---------|
| RTX 3060 | 12GB | ✓ | ✓ | 3-4 min/5s |
| RTX 4060 | 8GB | ✓ | ✗ | 3-4 min/5s |
| M1/M2 Pro | 16GB | ✓ | ✓ | 4-5 min/5s |
| M3 Pro | 18GB | ✓ | ✓ | 3-4 min/5s |

### Software

- Python 3.10+ (3.11 recomendado)
- CUDA 12.1+ (NVIDIA) ou Metal (Apple)
- PyTorch 2.1+
- Transformers, Diffusers, Gradio
- ~30GB disco para modelos

### Tempo/Custo

- **Primeira execução:** 15-20min (download modelos)
- **Geração vídeo 5s:** 2-3min (LTX-2 balanceado)
- **Custo:** USD 0 (local), apenas custo eletricidade (~0.05 USD/video se usar 300W GPU por 3 min)

## Armadilhas e limitações

**Qualidade Inferior a Cloud:**
WanGP output é ~70-80% de Runway/Sora. Razões:
- Modelo mais pequeno (diffusion ~2B parâmetros vs Sora ~10B+)
- Less training data
- Menos fine-tuning para casos edge

Mitigação: Use para prototyping/testing. Caso queira final production-ready, mude para Runway depois.

**Movimento Não-Natural:**
Vídeos podem ter "jitter" (câmera tremula) ou movimento robotizado. Solução:
- Prompts mais descritivos de movimento ("câmera lenta", "motion suave")
- Guidance scale 6-8 (não muito alto)
- Usar seeds específicas e testar variações

```python
# Bom prompt de movimento
"pessoa correndo suavemente, câmera segue em motion smooth, sem jitter"

# Ruim
"pessoa correndo"
```

**Interpretação Fraca de Prompt:**
Agente LLM sometimes fails em intenções complexas. Se pedir "cinematic 24fps anamorphic lens", agente simplifica para "video". Solve:
- Use prompts simples e diretos
- Descrever cena visualmente, não parametricamente
- Testar com múltiplas variações

**VRAM OOM (Out of Memory):**
Se tentar 1080p com 8GB, CUDA crashes. Mitigação:
- Usar NVFP4 quantization (reduz pico)
- Manter browser/otros apps fechado
- Monitor RAM com `nvidia-smi`

**Tempo de Geração Lento:**
5 segundos de vídeo = 2-3 minutos em RTX 3060. Para produção longa:
- Gera em lotes (overnight jobs)
- Paralelize em múltiplas GPUs se tiver
- Use resolução 720p (vs 1080p) para speedup 2x

**Seed Reprodutibilidade:**
Mesmo seed não garante saída idêntica entre versões do WanGP. Solução: salvar seed que funcionou, testar variações (+1, +2, etc) se precisa similares.

**Modelo Hallucina Objetos:**
Pode gerar "pessoas fantasma" que aparecem/desaparecem. Use:
- Negative prompts ("sem pessoas extras", "sem objetos flutuantes")
- Guidance scale moderado (7-8)
- Shorter duration (3-5s em vez de 15s reduz likelihood)

## Conexões

- [[construcao-de-llm-do-zero|LLM do zero]] — entender Qwen 3.5VL internamente
- [[geracao-de-cenas-multi-shot-por-ia|Multi-shot cinematográfico]] — orquestrar múltiplos vídeos como WanGP faz
- [[empresa-virtual-de-agentes-de-ia|Agentes autônomos]] — agente LLM orquestrando pipeline
- [[democratizacao-de-modelos-de-ia|IA local/descentralizada]] — rodar 100% offline
- [[fine-tuning-de-llms-sem-codigo|Fine-tuning]] — customizar Qwen para seu domínio

## Histórico

- 2026-04-02: Nota criada com conceito básico
- 2026-04-11: Reescrita com código Python completo (client API, agência multi-video, composição ffmpeg, optimizações NVFP4). Adicionados exemplo real (24-hour day cycle), comparação de hardware 2026 (RTX 3060/4060, Apple Silicon), troubleshooting (movimento, hallucination, VRAM OOM). Cobertos updates 2026 (LTX-2, Deepy agent, quantization).
