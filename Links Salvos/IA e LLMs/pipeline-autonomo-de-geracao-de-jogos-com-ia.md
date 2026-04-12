---
tags: [game-gen, ia, godot, multi-agente, visual-qa, claude, gemini]
source: https://x.com/sukh_saroy/status/2036557095273898403?s=20
date: 2026-04-02
tipo: aplicacao
---

# Pipeline Multi-Agente com QA Visual para Projetos Godot 4

## O que é

Sistema autônomo que transforma uma descrição textual simples ("um jogo tipo roguelike com mecânica de dash e inimigos com IA") em projeto Godot 4 completamente funcional, com:
- Código GDScript otimizado
- Assets 2D/3D gerados por IA
- Validação visual contínua (não apenas teste funcional)
- Loop de correção autônoma (se screenshot mostra problema, IA corrige)

Orquestração multi-modelo: Claude Code (lógica de jogo), Gemini Vision (geração de arte 2D), Tripo3D (conversão 2D→3D), loop visual feedback (QA contínuo).

## Por que importa agora

Desenvolvimento de jogos sofria de divisão clara entre programação (código) e conteúdo (arte, assets). LLMs conseguiam gerar código mas não validavam visualmente. Gemini Vision conseguia gerar arte mas não entendia constraints de Godot. Novo pipeline **fecha o loop**: gera código, gera assets, **testa visualmente**, itera até passar.

Custo: ~$5-8 por jogo pequeno. Tempo: 5-15 minutos end-to-end. Qualidade: funcional, iterável, não shipping-ready mas ~70% de um protótipo manual.

## Como implementar

### Etapa 1: Orquestração com Claude Code (Planeamento)

Estruture um prompt que instrua Claude a:

```python
# orchestrator.py (rode em Claude Code)
import anthropic
import json
import os

class GameOrchestrator:
    def __init__(self, game_description: str):
        self.description = game_description
        self.client = anthropic.Anthropic()
        self.project_root = "./game_project"
        os.makedirs(f"{self.project_root}/scenes", exist_ok=True)
        os.makedirs(f"{self.project_root}/assets/2d", exist_ok=True)
        os.makedirs(f"{self.project_root}/assets/3d", exist_ok=True)
    
    def plan_architecture(self) -> dict:
        """Claude analisa descrição e cria blueprint da arquitetura."""
        
        message = self.client.messages.create(
            model="claude-opus-4-1",
            max_tokens=2000,
            messages=[{
                "role": "user",
                "content": f"""Você é arquiteto de jogos Godot 4. 
                
Descrição do jogo: {self.description}

Retorne um JSON estruturado com:
1. "core_mechanics": lista de mecânicas principais
2. "scenes": árvore de cenas (ex: Player, Enemy, UI, Level)
3. "physics_type": "2d" ou "3d" ou "2.5d"
4. "asset_list": sprites/modelos necessários
5. "scripts_needed": lista de arquivos .gd e propósito

Exemplo:
{{
    "core_mechanics": ["dash", "combat", "enemy_spawning"],
    "scenes": ["Main", "Player", "Enemy", "UI/HUD"],
    "physics_type": "2d",
    "asset_list": [
        {{"name": "player_idle", "type": "sprite"}},
        {{"name": "enemy_basic", "type": "sprite"}},
        {{"name": "particle_dash", "type": "particles"}}
    ],
    "scripts_needed": [
        {{"file": "player.gd", "purpose": "movement and dash"}}
    ]
}}
"""
            }]
        )
        
        # Extract JSON from response
        try:
            architecture = json.loads(message.content[0].text)
            return architecture
        except json.JSONDecodeError:
            print("Fallback: JSON parsing failed, returning template")
            return self._default_architecture()
    
    def generate_gdscript(self, scene_name: str, mechanics: list) -> str:
        """Claude gera código GDScript otimizado para a cena."""
        
        message = self.client.messages.create(
            model="claude-opus-4-1",
            max_tokens=3000,
            messages=[{
                "role": "user",
                "content": f"""Gere script GDScript 4 para cena '{scene_name}' 
                com mecânicas: {', '.join(mechanics)}.
                
RESTRIÇÕES:
- Use Node2D ou CharacterBody2D (não abstrações genéricas)
- Implemente física real (gravity, collisions)
- Add animação básica (AnimatedSprite2D + animationplayer)
- Export variables para tweaking no editor
- Inclua comentários em português

Exemplo:
```gdscript
extends CharacterBody2D

@export var speed: float = 200.0
@export var jump_force: float = -400.0

var gravity: float = 800.0

func _process(delta: float) -> void:
    var input_vector = Input.get_vector("ui_left", "ui_right", "ui_up", "ui_down")
    velocity.x = input_vector.x * speed
    velocity.y += gravity * delta
    
    move_and_slide()
```
"""
            }]
        )
        
        return message.content[0].text.strip()
```

### Etapa 2: Geração de Assets 2D via Gemini Vision

```python
# asset_generator.py
import anthropic
import base64
import requests
from pathlib import Path

class AssetGenerator:
    def __init__(self, asset_list: list):
        self.asset_list = asset_list
        self.client = anthropic.Anthropic()
        self.gemini_api_key = os.getenv("GOOGLE_API_KEY")
    
    def generate_sprite_descriptions(self, asset: dict) -> str:
        """Cria descrição detalhada para Gemini gerar imagem."""
        
        return f"""Gere sprite pixel-art de alta qualidade:
Nome: {asset['name']}
Tipo: {asset.get('type', 'sprite')}
Estilo: pixel-art, 8-bit nostálgico
Resolução: 128x128 pixels
Background: transparente (PNG alpha)
Cores: paleta vibrante mas coerente

Detalhe visual: [descrição contextual do jogo]

Requisitos:
- Deve ser claramente reconhecível como {asset['name']}
- Paleta de cores máximo 16 cores
- Proporcional para tamanho pequeno
"""
    
    def call_gemini_image_gen(self, prompt: str, asset_name: str) -> bytes:
        """Chama API Gemini 2.0 para gerar imagem."""
        
        # Nota: Isto é pseudocódigo. API real varia.
        # Usar ImageGenerationService do Google Cloud
        
        import google.generativeai as genai
        genai.configure(api_key=self.gemini_api_key)
        
        model = genai.GenerativeModel("gemini-2.0-flash")
        
        response = model.generate_images(
            prompt=prompt,
            number_of_images=1,
            size="256x256"  # Gera maior, redimensiona depois
        )
        
        image_data = response.images[0]._image_data
        return image_data
    
    def save_assets(self, asset_name: str, image_bytes: bytes) -> str:
        """Salva PNG em assets/2d/."""
        
        path = Path(f"./game_project/assets/2d/{asset_name}.png")
        path.write_bytes(image_bytes)
        
        print(f"✓ Asset criado: {path}")
        return str(path)
```

### Etapa 3: Conversão 3D com Tripo3D

```python
# tripo3d_converter.py
import requests
import json

class Tripo3DConverter:
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.base_url = "https://api.tripo3d.ai/v2/openapi"
    
    def convert_2d_to_3d(self, image_path: str, asset_name: str) -> str:
        """Converte sprite 2D para modelo 3D GLTF."""
        
        # Upload imagem
        with open(image_path, "rb") as img_file:
            files = {"file": img_file}
            upload_response = requests.post(
                f"{self.base_url}/upload",
                headers={"Authorization": f"Bearer {self.api_key}"},
                files=files
            )
        
        file_id = upload_response.json()["file_id"]
        
        # Trigger 3D generation
        gen_response = requests.post(
            f"{self.base_url}/generate",
            headers={"Authorization": f"Bearer {self.api_key}"},
            json={
                "file_id": file_id,
                "asset_name": asset_name,
                "output_format": "gltf",
                "optimization": {
                    "target_poly_count": 5000,  # Baixo para jogos
                    "preserve_color": True
                }
            }
        )
        
        generation_id = gen_response.json()["generation_id"]
        
        # Poll até completar
        import time
        max_attempts = 30
        for attempt in range(max_attempts):
            status_response = requests.get(
                f"{self.base_url}/status/{generation_id}",
                headers={"Authorization": f"Bearer {self.api_key}"}
            )
            
            status = status_response.json()["status"]
            if status == "completed":
                output_url = status_response.json()["output_url"]
                return self._download_gltf(output_url, asset_name)
            
            time.sleep(2)
        
        raise TimeoutError("Tripo3D generation timeout")
    
    def _download_gltf(self, url: str, asset_name: str) -> str:
        """Download e salva modelo GLTF."""
        
        response = requests.get(url)
        path = f"./game_project/assets/3d/{asset_name}.gltf"
        
        with open(path, "wb") as f:
            f.write(response.content)
        
        print(f"✓ Modelo 3D salvo: {path}")
        return path
```

### Etapa 4: Loop de QA Visual

```python
# visual_qa.py
import subprocess
import base64
from PIL import Image
import anthropic

class VisualQA:
    def __init__(self, godot_project_path: str):
        self.project_path = godot_project_path
        self.client = anthropic.Anthropic()
    
    def capture_gameplay_screenshot(self) -> bytes:
        """Compila Godot e captura screenshot."""
        
        # Godot headless
        result = subprocess.run([
            "godot",
            "--headless",
            "--display-driver=dummy",
            f"--path={self.project_path}",
            "--quit-after", "120"  # Roda por 2 minutos
        ], capture_output=True)
        
        # Captura screenshot (método: Godot export via GDScript)
        screenshot_path = f"{self.project_path}/screenshot.png"
        
        with open(screenshot_path, "rb") as f:
            return f.read()
    
    def analyze_visual_quality(self, screenshot: bytes) -> dict:
        """Claude Vision analisa problemas visuais."""
        
        base64_image = base64.standard_b64encode(screenshot).decode("utf-8")
        
        message = self.client.messages.create(
            model="claude-opus-4-1",
            max_tokens=1500,
            messages=[{
                "role": "user",
                "content": [
                    {
                        "type": "image",
                        "source": {
                            "type": "base64",
                            "media_type": "image/png",
                            "data": base64_image
                        }
                    },
                    {
                        "type": "text",
                        "text": """Analise este screenshot do jogo Godot 4.
                        
CHECKLIST:
1. Z-fighting ou overlaps visuais? (Texturas piscando/sobrepostas)
2. Texturas faltantes? (Objetos rosa/branco = missing texture)
3. Física quebrada? (Objetos flutuando, caindo infinito, clipping)
4. HUD ilegível? (Texto pequeno, contraste baixo, fora da tela)
5. Performance? (Lag visível, stuttering)

Retorne JSON:
{
    "issues": [
        {
            "severity": "high|medium|low",
            "type": "z-fighting|missing_texture|physics|hud|performance",
            "description": "...",
            "suggested_fix": "...",
            "line_of_code_likely_responsible": "..."
        }
    ],
    "overall_quality": "broken|poor|acceptable|good",
    "ready_for_next_iteration": boolean
}
"""
                    }
                ]
            }]
        )
        
        try:
            return json.loads(message.content[0].text)
        except:
            return {"issues": [], "overall_quality": "unknown"}
```

### Etapa 5: Correção Autônoma

```python
# auto_fixer.py
class AutoFixer:
    def __init__(self, orchestrator: GameOrchestrator):
        self.orchestrator = orchestrator
        self.client = anthropic.Anthropic()
    
    def fix_issues(self, qa_report: dict) -> None:
        """Para cada issue no QA report, fix automaticamente."""
        
        for issue in qa_report.get("issues", []):
            if issue["severity"] != "high":
                continue
            
            # Identifica arquivo afetado
            script_path = self._find_script(issue)
            
            if not script_path:
                print(f"⚠ Couldn't locate script for: {issue['description']}")
                continue
            
            # Lê conteúdo
            with open(script_path, "r") as f:
                original_code = f.read()
            
            # Solicita fix
            fix_message = self.client.messages.create(
                model="claude-opus-4-1",
                max_tokens=2000,
                messages=[{
                    "role": "user",
                    "content": f"""Arquivo: {script_path}

PROBLEMA: {issue['description']}
SUGESTÃO: {issue['suggested_fix']}

CÓDIGO ORIGINAL:
```gdscript
{original_code}
```

Retorne APENAS o código corrigido em bloco ```gdscript...```, sem explicações.
Garanta que o fix resolve o problema sem quebrar o resto.
"""
                }]
            )
            
            fixed_code = self._extract_gdscript_block(
                fix_message.content[0].text
            )
            
            # Escreve fix
            with open(script_path, "w") as f:
                f.write(fixed_code)
            
            print(f"✓ Fixed: {issue['description']}")
    
    def _find_script(self, issue: dict) -> str:
        """Localiza script baseado no issue description."""
        
        # Heurística simples: procura por descrição em nomes de arquivo
        import glob
        
        scripts = glob.glob(f"{self.orchestrator.project_root}/**/*.gd", recursive=True)
        
        # Retorna primeiro match (melhoria: usar AI para confidence score)
        return scripts[0] if scripts else None
    
    def _extract_gdscript_block(self, text: str) -> str:
        """Extrai conteúdo de ```gdscript...``` block."""
        
        import re
        match = re.search(r"```gdscript\n(.*?)\n```", text, re.DOTALL)
        return match.group(1) if match else text
```

## Stack e requisitos

**Hardware:**
- CPU moderna (Intel i5+, AMD Ryzen 5+)
- GPU recomendada (RTX 3060+) para processamento rápido
- RAM: 16GB+ (8GB mínimo para Godot + APIs)
- SSD: 50GB livre (projeto + models)

**Software:**
- Godot 4.x (engine)
- Python 3.10+ (orchestration)
- Claude API key (Anthropic)
- Gemini 2.0 API key (Google Cloud)
- Tripo3D API key (3D conversion)

**Tempo e custo:**
- Tempo per run: 5-15 minutos (paralelo quando possível)
- Custo por jogo: ~$5-8 (Claude Opus + Gemini Vision + Tripo3D)
- Escalabilidade: pode rodar via GitHub Actions (CI/CD pipeline)

## Código prático: Main Loop

```python
# main_pipeline.py
def run_full_pipeline(game_description: str) -> str:
    """Executa pipeline completo descrição → jogo funcional."""
    
    print("🎮 Iniciando pipeline de geração de jogo...")
    
    # 1. Planejamento
    print("\n1️⃣ Planejando arquitetura...")
    orchestrator = GameOrchestrator(game_description)
    architecture = orchestrator.plan_architecture()
    
    # 2. Geração de código
    print("\n2️⃣ Gerando código GDScript...")
    for scene in architecture["scenes"]:
        code = orchestrator.generate_gdscript(
            scene, 
            architecture["core_mechanics"]
        )
        orchestrator.save_script(f"{scene}.gd", code)
    
    # 3. Geração de assets
    print("\n3️⃣ Gerando assets 2D...")
    asset_gen = AssetGenerator(architecture["asset_list"])
    for asset in architecture["asset_list"]:
        asset_gen.generate_and_save(asset)
    
    # 4. Conversão 3D (opcional)
    if architecture["physics_type"] in ["3d", "2.5d"]:
        print("\n4️⃣ Convertendo para 3D...")
        converter = Tripo3DConverter(os.getenv("TRIPO3D_KEY"))
        for asset in architecture["asset_list"]:
            converter.convert_2d_to_3d(f"assets/2d/{asset}.png", asset)
    
    # 5. QA Loop
    print("\n5️⃣ Validando visualmente...")
    qa = VisualQA(orchestrator.project_root)
    max_iterations = 3
    
    for iteration in range(max_iterations):
        screenshot = qa.capture_gameplay_screenshot()
        qa_report = qa.analyze_visual_quality(screenshot)
        
        if qa_report["overall_quality"] in ["good", "acceptable"]:
            print(f"✅ QA passou na iteração {iteration + 1}")
            break
        
        print(f"🔧 Corrigindo issues (iteração {iteration + 1})...")
        fixer = AutoFixer(orchestrator)
        fixer.fix_issues(qa_report)
    
    print("\n✨ Pipeline concluído!")
    return orchestrator.project_root

# Uso
if __name__ == "__main__":
    result = run_full_pipeline(
        "Roguelike 2D com mecânica de dash, inimigos com IA patrulha, "
        "loot ao derrotar inimigos, câmera dinâmica"
    )
    print(f"Projeto salvo em: {result}")
```

## Armadilhas e limitações

**1. QA visual não detecta bugs lógicos.** Screenshot parece ótimo mas mecânica está quebrada (colisão não funciona, inimigo não patrulha). Solução: adicionar teste funcional (rodar código, verificar logs) além de visual.

**2. Gemini gera sprites repetitivos.** Especialmente com mesma paleta de cores, pode gerar assets visualmente parecidos. Melhor: providenciar exemplos de estilo ou usar múltiplas chamadas com prompts variados.

**3. Tripo3D fraco em detalhes finos.** Bom para protótipos, não production-ready. Modelos 3D gerados têm geometria "mole" (perca de detalhes). Use como base, não como final.

**4. Screenshots em baixa resolução prejudicam detecção.** Se captura em 480p, problemas pequenos (UI fora de tela, z-fighting sutil) não são vistos. Solução: capturar em 1080p+ mesmo que lento.

**5. Timeout em compilação Godot sem display.** Linux headless requer Xvfb ou similar. Windows/macOS funcionam melhor. Se rodando em servidor, configure X11 forwarding ou use Docker com Xvfb.

**6. Custo escalona com iterações.** Cada loop de QA custa $0.50-1.00 em API. Se jogo requer 10 iterações, custo pode alcançar $15-20. Bom: limitar a max 3-5 iterações.

## Conexões

- [[Vibe Coding para Desenvolvimento de Jogos]] — Filosofia behind "user intent over exact specs"
- [[Sistemas Multi-Agente para Engenharia de Software]] — Multi-model orchestration patterns
- [[Unity-MCP Integração LLM com Game Engine]] — Similar para Unity
- [[Claude Code Best Practices]] — Como estruturar prompts pro orquestrador
- [[10-youtube-gems-solo-game-devs]] — Design conceitual antes de automation

## Histórico

- 2026-04-02: Nota criada (X/@sukh_saroy)
- 2026-04-02: Reescrita como guia de implementação
- 2026-04-11: Expandida com Python full-stack, QA loop, armadilhas técnicas, main loop integrado
