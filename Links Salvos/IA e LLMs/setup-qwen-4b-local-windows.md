---
tags: [setup, qwen, local-llm, windows, tutorial, hands-on]
date: 2026-03-29
source: session-leticia-winter
tipo: aplicacao
---

# Setup Qwen 2.5-4B Local no Windows com Ollama em 30 Minutos

## Resumo

Instruções passo-a-passo para rodar Qwen 2.5-4B (4B parâmetros destilado de Claude Opus) completamente local no Windows com Ollama. Após 30 minutos, você terá um modelo local respondendo prompts sem enviar nada para cloud.

## Pré-requisitos

- Windows 10/11
- ~3GB de espaço em disco
- Conexão internet para download do modelo
- RAM: 6GB mínimo (8GB recomendado)
- GPU NVIDIA (opcional, vai rodar em CPU mesmo)

## Instruções Passo-a-Passo

### Fase 1: Instalar Ollama (5 minutos)

1. **Download:**
   - Vai para: https://ollama.ai/download/windows
   - Clica em "Download for Windows"
   - Abre o instalador `.exe`

2. **Instalação:**
   - Segue defaults
   - Espera completar
   - Vai ver Ollama na taskbar (ícone roxo)

3. **Verificação:**
   - Abre PowerShell ou CMD
   - Roda: `ollama --version`
   - Deve aparecer a versão

### Fase 2: Baixar Qwen 2.5-4B (15-20 minutos)

1. **PowerShell/CMD (deixa aberta)**
   ```powershell
   ollama pull qwen2.5-4b
   ```

2. **O que vai ver:**
   - `pulling manifest...`
   - `pulling abc123... X%` (vai de 0 a 100%)
   - `verifying sha256 digest...`
   - `writing manifest...` ← PRONTO quando aparecer

3. **Tempo:**
   - ~2.4GB no total
   - Velocidade depende internet (meu teste: 3min a 100Mbps)

### Fase 3: Primeira Prompt (2 minutos)

Mesma janela PowerShell:

```powershell
ollama run qwen2.5-4b "Você é um assistente local. Explique em uma frase o que significa quantização de modelos de IA."
```

**Esperado:**
- Cursor piscando por 3-5 segundos (processando)
- Resposta em português, coerente

Exemplo de saída:
```
Quantização reduz o tamanho de um modelo de IA comprimindo os números
que representam os pesos da rede neural, mantendo qualidade similar
enquanto usa menos memória e roda mais rápido.
```

### Fase 4: Teste com Multimodal (opcional, 5min)

Ou experimente com mais contexto:

```powershell
ollama run qwen2.5-4b @"
Você é especialista em modelos de IA. Responda:
1. O que é Qwen 2.5-4B?
2. Por que roda localmente?
3. Qual é o maior benefício?
"@
```

## Troubleshooting

| Problema | Solução |
|----------|---------|
| "ollama command not found" | Ollama não está no PATH. Reinicia computador ou abre terminal novo. |
| Modelo demora muito | Dependência de internet lenta. Deixa rodando. |
| "CUDA not found" | Normal se não tiver GPU NVIDIA. Vai rodar em CPU (mais lento mas funciona). |
| GPU NVIDIA não é usada | Roda: `ollama pull qwen2.5-4b-q4_0` para versão otimizada. |

## Próximas Fases

Depois que confirmar funcionando:

**Fase 2 (próximo): Otimização**
- Testar diferentes quantizações (Q3, Q4, Q5, Q8)
- Medir latência vs tamanho
- Escolher sweet spot para seu hardware

**Fase 3: Integração**
- Conectar com MCP servers
- Adicionar browser, terminal, RAG local
- Build seu próprio assistente

**Fase 4: Especialização**
- Fine-tune com seus próprios dados
- Criar "personas" para tarefas específicas

## Métricas Esperadas

Após setup completo, esperado:

| Métrica | Esperado |
|---------|----------|
| Tamanho no disco | ~2.4GB (Q4_K_M) |
| Tempo 1ª resposta | 2-5 segundos (CPU), <1s (GPU) |
| Latência por token | 50-150ms (CPU), 5-20ms (GPU) |
| Qualidade | ~95% comparado a Claude Opus |
| Custo | $0 (local) |
| Privacidade | 100% (nada sai da máquina) |

## Evidência de Sucesso

Você saberá que funcionou quando:

✅ Modelo responde em português com coerência
✅ Respostas aparecem sem chamadas de API
✅ Pode fazer prompts sequenciais sem delay
✅ Notebook não esquenta demais (normal <80°C)

## Relacionado

- [[Qwen 3.5 4B Destilado Claude Opus Local]]
- [[6-melhores-mcp-servers-assistente-ia-local]]
- [[local_llm_reddit_discussao]]

## Perguntas de Revisão

1. Por que Ollama é preferível a instalar llama.cpp manualmente?
2. Como você mede se quantização Q4 vs Q5 vale a troca de velocidade?
3. Qual é o próximo passo após validar que o modelo funciona?

