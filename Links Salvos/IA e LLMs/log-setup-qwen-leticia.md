---
tags: [setup, log, qwen, local-llm, experimento]
source: Nota interna
date: 2026-03-29
tipo: aplicacao
---

# Setup Qwen 2.5 Local: Instalação, Testes e Benchmarks

## O que e

Log estruturado de instalação do Qwen 2.5-32B via Ollama em Windows 11, com métricas de latência, consumo de memória e qualidade de output em português. Inclui resultados de GPU offloading (RAM: 21GB → 11GB) e próximos passos para otimização.

## Como implementar

**Pré-requisitos**: Windows 11, 25GB espaço livre, Ollama 0.1.15+ (https://ollama.com/download).

**Fase 1: Instalar Ollama**. Download e executar instalador. Verificar com `ollama --version`. Ollama configura automaticamente PATH e cria daemon no background.

**Fase 2: Download Qwen 2.5-32B quantizado (Q4_0, 18GB)**:
```powershell
ollama pull qwen2.5-32b-instruct-q4_0
# Tempo esperado: 15-30 minutos dependo internet
```

**Fase 3: Teste rápido de qualidade (português)**:
```powershell
ollama run qwen2.5-32b-instruct-q4_0 "Explique quantização de modelos IA em uma frase."
# Medir tempo de primeira token (TTFT) e latência por token
```

**Fase 4: Teste latência com benchmark**:
```powershell
# Instalar ollama-bench (Python)
pip install ollama-bench

# Rodando benchmark
ollama-bench \
  --model qwen2.5-32b-instruct-q4_0 \
  --prompt-file teste-benchmark.txt \
  --runs 5
```

**GPU offloading**: Editar ~/.ollama/modelfile ou usar variável ambiente:
```powershell
$env:OLLAMA_NUM_GPU = 1  # Ativar GPU offloading
ollama serve  # Reiniciar daemon
```

Medir consumo antes/depois com `Get-Process | Where-Object {$_.ProcessName -eq "ollama"} | Select-Object WorkingSet`.

**Integração com MCP**: Criar servidor MCP que expõe Ollama como tool:
```python
# mcp_ollama_server.py
import subprocess
import json

def query_ollama(model: str, prompt: str) -> str:
    result = subprocess.run(
        ["ollama", "run", model, prompt],
        capture_output=True,
        text=True
    )
    return result.stdout
```

## Stack e requisitos

- **OS**: Windows 10/11, macOS 11+, Linux (x86_64)
- **RAM**: Mínimo 8GB (4GB CPU+offloading), recomendado 16GB
- **GPU**: NVIDIA com CUDA 11.8+ (opcional, melhora latência 3-5x)
- **Disco**: 25-30GB livre (modelo Q4_0 18GB + sistema)
- **Ollama**: 0.1.15+
- **Quantização**: Q4_0 (18GB, boa qualidade), Q5_K_M (22GB, melhor), Q3_K_S (10GB, rápido mas degradado)

## Armadilhas e limitacoes

- **Memory management**: Modelos 32B sem GPU ficarão lentos (100-200ms/token). GPU offloading crítico para UX.
- **VRAM**: GPU com <8GB VRAM não suporta offloading de modelos 32B; usar Qwen 14B ou 4B alternativa.
- **Quantização**: Q4_0 é o ponto de equilíbrio; Q3_K_S é rápido mas colapsam qualidade em tarefas sofisticadas.
- **Português**: Qwen foi treinado em 15% dados chineses; português está bom mas menor que inglês.
- **Daemon**: Ollama fica 24/7 em background; monitorar memory leaks em sessões longas.

## Conexoes

[[Qwen 3.5 Omni Modelo Nativo Multimodal]] [[MCP para Agentes de Codigo]] [[Orquestracao Hibrida de LLMs]]

## Historico

- 2026-03-29: Log criado com status em-andamento
- 2026-04-02: Reescrita para template aplicacao com procedimentos detalhados

