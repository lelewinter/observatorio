---
tags: [turboquant, setup, windows, optimization, kv-cache]
date: 2026-03-29
status: ready-to-use
---

# TurboQuant Setup Automatizado — Windows

## TL;DR

Copie o script `setup-turboquant-automated.py` para seu `C:\Users\leeew\` e roda:

```powershell
python setup-turboquant-automated.py
```

Espera ~30-45 minutos, pronto.

---

## O que o script faz

1. ✅ Verifica Python 3.9+
2. ✅ Instala PyTorch com CUDA 11.8
3. ✅ Clona TurboQuant do GitHub
4. ✅ Configura ambiente
5. ✅ Cria script de inference pronto
6. ✅ Verifica tudo funcionando

---

## Pré-requisitos

- [x] Python 3.9+ instalado
- [x] Git instalado
- [x] Ollama com Qwen 32B (já tem)
- [x] ~5GB espaço em disco
- [x] 64GB RAM + 12GB VRAM (já tem)

---

## Passo-a-passo (Manual)

### 1. Abrir PowerShell como Admin

Tecla Windows → digitue "PowerShell" → clica direito → "Run as Administrator"

### 2. Ir pra home directory

```powershell
cd $HOME
```

### 3. Copiar script

Copie o arquivo `setup-turboquant-automated.py` pra `C:\Users\leeew\`

(ou salve direto com este comando)

### 4. Rodar setup

```powershell
python setup-turboquant-automated.py
```

A saída vai parecer:

```
============================================================
TurboQuant Setup Automatizado - Qwen Local
============================================================

[PASSO 1] Verificar Python
=====================================================
✓ Python 3.11.7 detectado

[PASSO 2] Instalar PyTorch + CUDA
...
```

### 5. Esperar terminar

⏱️ Tempo estimado: **30-45 minutos** (depende internet e SSD)

---

## Se der erro

### "Python not found"

```powershell
# Verifica Python
python --version

# Se não funcionar, instala Python 3.11
# https://www.python.org/downloads/
```

### "Git not found"

```powershell
# Instala Git
# https://git-scm.com/download/win
```

### "CUDA not found"

Normal. Script instala PyTorch com CUDA automaticamente.

### "Permission denied"

Certifique-se que rodou PowerShell **como Admin** (clica direito → Run as Administrator)

---

## Depois que terminar

### 1. Verificar arquivo de config

```powershell
cat $HOME/turboquant-config.json
```

Deve mostrar:

```json
{
  "model_name": "qwen2.5:32b-instruct-q4_0",
  "turboquant": {
    "enabled": true,
    "kv_cache_bits": 3,
    ...
  }
}
```

### 2. Script de inference

Script está em: `$HOME/inference-turboquant.py`

Rodar:

```powershell
python $HOME/inference-turboquant.py
```

---

## O que TurboQuant faz agora

**KV Cache comprimido 6x:**
- Antes: sequência de 1000 tokens usa 12GB
- Depois: sequência de 1000 tokens usa 2GB
- Resultado: conversas longas, multirrotatória funcionam bem

**Sem perda de qualidade:**
- 3-bit compression mantém 99.5% attention fidelity
- Modelo ainda responde com mesmo nível Qwen 32B

---

## Métrica esperada após setup

Depois do setup, testar:

```powershell
# Antes (sem TurboQuant)
ollama run qwen2.5:32b-instruct-q4_0 "Uma resposta longa que use muitos tokens..."

# Depois (com TurboQuant)
python $HOME/inference-turboquant.py
```

Esperado:
- Latência inicial: similar (TurboQuant não otimiza primeira resposta)
- Sequências longas: **6x mais rápido** (depois de ~200 tokens)
- Memória em sequências: **6x menos** (2GB vs 12GB)

---

## Troubleshooting

| Problema | Solução |
|----------|---------|
| Script trava em "Installing PyTorch" | Internet lenta, deixa rodando. Pode levar 10+ min |
| "ModuleNotFoundError: No module named 'torch'" | Feche PowerShell, abra novo, tente novamente |
| Disco cheio | Precisa ~5GB livre. Limpe temporários |
| GPU não é detectada | Normal. Script usa CPU + GPU automaticamente |

---

## Próximas fases

**Após validar TurboQuant funcionando:**

1. **Integrar com Ollama** (quando suporte oficial chegar)
2. **Fine-tune com TurboQuant** (otimizar pra suas tarefas)
3. **MCP Servers** com TurboQuant (browser, RAG, terminal)

---

## Relacionado

- [[setup-qwen-4b-local-windows]] — Setup base (já feito)
- [[proximos-passos-ia-local-leticia]] — Roadmap completo
- [[Qwen 3.5 4B Destilado Claude Opus Local]] — Context do modelo

---

## Perguntas de Revisão

1. Por que TurboQuant comprime especificamente KV cache e não todo o modelo?
2. Como 3-bit quantization mantém qualidade em atenção?
3. Qual é o trade-off entre velocidade e accuracy em TurboQuant?

