---
tags: [projeto, ia-local, ollama, gemma-4, open-webui, inferencia-local]
date: 2026-04-11
tipo: projeto
status: pendente
prioridade: alta
tempo-estimado: 2-3 horas
---
# Projeto 1: Lab de IA Local com Ollama + Gemma 4

## Objetivo

Montar ambiente de inferencia local completo que funcione como fallback quando creditos de API acabarem. Ao final, ter um chat local com modelo competitivo rodando na propria maquina, acessivel via interface web.

## Por que fazer isso agora

Gemma 4 foi lancado em 2 de abril com Apache 2.0. O modelo 31B esta no top 3 do LMSYS Arena, batendo modelos 20x maiores. Combinado com Ollama (52M downloads/mes em 2026), o custo de rodar IA local caiu pra basicamente zero. Voce ficou sem creditos da API Anthropic esta semana. Ter um lab local resolve isso.

## Pre-requisitos

- Windows 11 (ja tem)
- 16GB+ RAM (ideal 32GB)
- GPU NVIDIA com 8GB+ VRAM (RTX 3060 minimo, RTX 4060+ ideal)
- ~20GB de espaco em disco para modelos
- Docker Desktop instalado (para Open WebUI)

## Passo a Passo

### Etapa 1: Instalar Ollama (15 min)

```powershell
# Baixar e instalar Ollama para Windows
# https://ollama.com/download/windows
# Apos instalar, verificar:
ollama --version
```

Ollama roda como servico no Windows. Apos instalar, o endpoint fica em `http://localhost:11434`.

### Etapa 2: Baixar Gemma 4 (20-30 min dependendo da internet)

```powershell
# Modelo 31B Dense (melhor qualidade, precisa ~20GB VRAM para rodar sem quantizar)
ollama pull gemma4:31b

# Se sua GPU nao aguenta 31B, use o 26B MoE (mais leve, quase mesma qualidade)
ollama pull gemma4:26b

# Se GPU < 12GB VRAM, use o 4B (mais leve, bom pra tarefas simples)
ollama pull gemma4:4b

# Testar se funciona
ollama run gemma4:31b "Explique o que e RAG em 3 linhas"
```

Dica: rodar `nvidia-smi` antes para ver quanta VRAM voce tem disponivel.

### Etapa 3: Instalar Open WebUI (15 min)

```powershell
# Via Docker (mais simples)
docker run -d -p 3000:8080 --add-host=host.docker.internal:host-gateway -v open-webui:/app/backend/data --name open-webui --restart always ghcr.io/open-webui/open-webui:main

# Acessar em http://localhost:3000
# Criar conta local (primeiro usuario vira admin)
```

Open WebUI detecta Ollama automaticamente. Todos os modelos baixados aparecem no dropdown.

### Etapa 4: Teste Comparativo (30 min)

Rodar 3 tarefas identicas no Gemma 4 local e comparar mentalmente com Claude:

1. **Analise de nota**: copiar uma nota do vault e pedir para sumarizar + sugerir conexoes
2. **Geracao de codigo**: pedir um script Python que faz X (algo que voce precise)
3. **Pesquisa estruturada**: dar um topico e pedir resumo no formato das notas do vault

Anotar: qualidade, velocidade, onde falha vs Claude.

### Etapa 5: Configurar como Fallback no Pipeline (30 min)

```python
# Adicionar ao config.json do pipeline:
# "fallback_model": "gemma4:31b"
# "fallback_endpoint": "http://localhost:11434/v1"

# Teste rapido de integracao:
import requests

response = requests.post("http://localhost:11434/api/generate", json={
    "model": "gemma4:31b",
    "prompt": "Resuma este link em 3 bullet points: ...",
    "stream": False
})
print(response.json()["response"])
```

## Checklist de Conclusao

- [ ] Ollama instalado e rodando
- [ ] Gemma 4 baixado (pelo menos uma variante)
- [ ] Open WebUI acessivel em localhost:3000
- [ ] Teste comparativo feito (3 tarefas)
- [ ] Decisao: qual modelo usar como fallback
- [ ] (Opcional) Integrar endpoint no pipeline

## Notas Relacionadas

- [[rodar-gemma-4-localmente-para-reasoning-e-workflows-agentivos]]
- [[montar-laboratorio-ia-local-python-open-source]]
- [[stack-de-ia-local-self-hosted]]
- [[bitnet-cpp-llm-1-bit-100b-parametros-na-cpu]]
- [[qwen-3-6-plus-agente-multimodal-1m-contexto]]

## Criterios de Sucesso

Minimo: Ollama + Gemma 4 rodando, conseguir fazer perguntas via terminal.
Ideal: Open WebUI funcional, teste comparativo feito, decisao de qual modelo usar.
Bonus: endpoint integrado no pipeline como fallback automatico.

## Historico

- 2026-04-11: Projeto criado
