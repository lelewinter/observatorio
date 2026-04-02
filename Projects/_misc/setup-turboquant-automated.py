#!/usr/bin/env python3
"""
TurboQuant Setup Automatizado para Qwen Local
Instala e configura TurboQuant para otimização de KV cache
Leticia Winter - 2026-03-29
"""

import os
import sys
import subprocess
import json
from pathlib import Path

class TurboQuantSetup:
    def __init__(self):
        self.home = Path.home()
        self.ollama_dir = self.home / ".ollama" / "models" / "manifests"
        self.turboquant_dir = self.home / "turboquant-pytorch"
        self.config_file = self.home / "turboquant-config.json"

    def print_step(self, step_num, title):
        print(f"\n{'='*60}")
        print(f"[PASSO {step_num}] {title}")
        print(f"{'='*60}\n")

    def run_command(self, cmd, description=""):
        """Executa comando e mostra progresso"""
        print(f"→ {description}")
        try:
            result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
            if result.returncode == 0:
                print(f"  ✓ Sucesso")
                return True
            else:
                print(f"  ✗ Erro: {result.stderr}")
                return False
        except Exception as e:
            print(f"  ✗ Exceção: {e}")
            return False

    def check_python(self):
        """Verifica se Python 3.9+ tá instalado"""
        self.print_step(1, "Verificar Python")

        version = sys.version_info
        if version.major >= 3 and version.minor >= 9:
            print(f"✓ Python {version.major}.{version.minor}.{version.micro} detectado")
            return True
        else:
            print(f"✗ Python 3.9+ requerido. Você tem {version.major}.{version.minor}")
            return False

    def install_dependencies(self):
        """Instala PyTorch e dependências"""
        self.print_step(2, "Instalar PyTorch + CUDA")

        commands = [
            (
                "pip install --upgrade pip",
                "Atualizando pip"
            ),
            (
                "pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu118",
                "Instalando PyTorch com CUDA 11.8"
            ),
            (
                "pip install numpy scipy scikit-learn tqdm",
                "Instalando dependências base"
            ),
        ]

        success = True
        for cmd, desc in commands:
            if not self.run_command(cmd, desc):
                success = False

        return success

    def clone_turboquant(self):
        """Clona repositório TurboQuant"""
        self.print_step(3, "Clonar TurboQuant GitHub")

        if self.turboquant_dir.exists():
            print(f"✓ {self.turboquant_dir} já existe")
            return True

        cmd = f"git clone https://github.com/tonbistudio/turboquant-pytorch {self.turboquant_dir}"
        return self.run_command(cmd, "Clonando turboquant-pytorch")

    def install_turboquant(self):
        """Instala TurboQuant localmente"""
        self.print_step(4, "Instalar TurboQuant")

        os.chdir(self.turboquant_dir)
        commands = [
            (
                "pip install -e .",
                "Instalando TurboQuant em modo desenvolvimento"
            ),
        ]

        success = True
        for cmd, desc in commands:
            if not self.run_command(cmd, desc):
                success = False

        return success

    def create_config(self):
        """Cria arquivo de configuração"""
        self.print_step(5, "Criar Configuração")

        config = {
            "model_name": "qwen2.5:32b-instruct-q4_0",
            "turboquant": {
                "enabled": True,
                "compression_ratio": 6.0,
                "kv_cache_bits": 3,
                "method": "qjl"
            },
            "inference": {
                "max_tokens": 512,
                "temperature": 0.7,
                "top_p": 0.9,
                "gpu_layers": 50
            },
            "paths": {
                "ollama_dir": str(self.ollama_dir),
                "turboquant_dir": str(self.turboquant_dir),
                "models_dir": str(self.home / "turboquant_models")
            }
        }

        with open(self.config_file, 'w') as f:
            json.dump(config, f, indent=2)

        print(f"✓ Configuração salva em: {self.config_file}")
        return True

    def create_inference_script(self):
        """Cria script de inference com TurboQuant"""
        self.print_step(6, "Criar Script de Inference")

        script_path = self.home / "inference-turboquant.py"

        script_content = '''#!/usr/bin/env python3
"""
Inference com TurboQuant - Qwen Local
"""

import json
import sys
from pathlib import Path
from transformers import AutoTokenizer, AutoModelForCausalLM
import torch

class TurboQuantInference:
    def __init__(self, config_path):
        with open(config_path) as f:
            self.config = json.load(f)

        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        self.model = None
        self.tokenizer = None

    def load_model(self, model_name):
        """Carrega modelo com TurboQuant"""
        print(f"Carregando {model_name}...")

        try:
            from turboquant import TurboQuantQuantizer

            self.tokenizer = AutoTokenizer.from_pretrained(model_name)
            self.model = AutoModelForCausalLM.from_pretrained(
                model_name,
                torch_dtype=torch.float16,
                device_map="auto"
            )

            # Aplica TurboQuant
            quantizer = TurboQuantQuantizer(self.config["turboquant"])
            self.model = quantizer.quantize(self.model)

            print(f"✓ Modelo carregado em {self.device}")
            return True
        except Exception as e:
            print(f"✗ Erro carregando modelo: {e}")
            return False

    def generate(self, prompt, max_tokens=256):
        """Gera resposta com TurboQuant KV cache"""
        if not self.model:
            print("Modelo não carregado")
            return None

        inputs = self.tokenizer(prompt, return_tensors="pt").to(self.device)

        with torch.no_grad():
            outputs = self.model.generate(
                **inputs,
                max_new_tokens=max_tokens,
                temperature=self.config["inference"]["temperature"],
                top_p=self.config["inference"]["top_p"]
            )

        response = self.tokenizer.decode(outputs[0], skip_special_tokens=True)
        return response

if __name__ == "__main__":
    config_path = Path.home() / "turboquant-config.json"

    if not config_path.exists():
        print(f"Arquivo de config não encontrado: {config_path}")
        sys.exit(1)

    inference = TurboQuantInference(config_path)

    # Carrega modelo Qwen
    model_name = "Qwen/Qwen2.5-32B-Instruct"  # Ou seu modelo local
    if not inference.load_model(model_name):
        sys.exit(1)

    # Teste
    prompt = "Explique quantização de modelos de IA"
    print(f"\\nPrompt: {prompt}\\n")
    response = inference.generate(prompt)
    print(f"Resposta:\\n{response}")
'''

        with open(script_path, 'w') as f:
            f.write(script_content)

        print(f"✓ Script de inference criado: {script_path}")
        return True

    def verify_installation(self):
        """Verifica se tudo foi instalado"""
        self.print_step(7, "Verificar Instalação")

        checks = [
            ("PyTorch", lambda: __import__('torch')),
            ("TurboQuant", lambda: __import__('turboquant')),
            ("Transformers", lambda: __import__('transformers')),
            ("Config file", lambda: self.config_file.exists()),
        ]

        all_good = True
        for name, check in checks:
            try:
                check()
                print(f"✓ {name}")
            except:
                print(f"✗ {name}")
                all_good = False

        return all_good

    def run(self):
        """Executa setup completo"""
        print("\n" + "="*60)
        print("TurboQuant Setup Automatizado - Qwen Local")
        print("="*60)

        steps = [
            ("Python", self.check_python),
            ("Dependências", self.install_dependencies),
            ("TurboQuant Repo", self.clone_turboquant),
            ("TurboQuant Install", self.install_turboquant),
            ("Configuração", self.create_config),
            ("Script Inference", self.create_inference_script),
            ("Verificação", self.verify_installation),
        ]

        for step_name, step_func in steps:
            try:
                if not step_func():
                    print(f"\n✗ Falhou em: {step_name}")
                    return False
            except Exception as e:
                print(f"\n✗ Erro em {step_name}: {e}")
                return False

        self.print_step(99, "Setup Completo!")
        print(f"""
✓ TurboQuant está pronto!

Próximos passos:

1. Rodar inference:
   python {self.home}/inference-turboquant.py

2. Verificar config:
   cat {self.config_file}

3. Testar com seu modelo Qwen:
   ollama run qwen2.5:32b-instruct-q4_0

Documentação: {self.home}/turboquant-pytorch/README.md
""")
        return True

if __name__ == "__main__":
    setup = TurboQuantSetup()
    success = setup.run()
    sys.exit(0 if success else 1)
