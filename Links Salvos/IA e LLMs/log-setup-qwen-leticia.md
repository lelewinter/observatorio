---
tags: [setup, log, qwen, local-llm, experimento]
date: 2026-03-29
status: em-andamento
---

# Log Setup Qwen 4B — Leticia Winter

## Status Atual

- [x] Ollama instalado
- [x] Qwen 2.5-32B baixado (18GB, Q4_0)
- [x] Primeira prompt testada (sucesso, português excelente)
- [x] Latência medida (lento, RAM-heavy)
- [x] GPU offloading tentado (melhorou RAM de 21GB → 11GB)
- [ ] Próximo passo: decidir entre Qwen 14B ou TurboQuant

## Hardware

**Sua máquina:**
- SO: Windows 11
- CPU: [preencher]
- RAM: [preencher]
- GPU: [preencher ou "nenhuma"]
- Espaço em disco disponível: [preencher]

## Fase 1: Instalação Ollama

**Data/Hora início:** [preencher]
**Data/Hora fim:** [preencher]

Problemas encontrados:
- [list aqui se houver]

Logs (copiar output do terminal):
```
[colar aqui]
```

## Fase 2: Download Qwen

**Data/Hora início:** [preencher]
**Data/Hora fim:** [preencher]
**Tempo total:** [preencher]
**Velocidade internet:** [preencher Mbps se souber]

Output do `ollama pull qwen2.5-4b`:
```
[colar aqui]
```

## Fase 3: Teste Primeira Prompt

**Comando rodado:**
```powershell
ollama run qwen2.5-4b "Você é um assistente local. Explique em uma frase o que significa quantização de modelos de IA."
```

**Tempo processamento:** [ms ou segundos]

**Resposta do modelo:**
```
[colar aqui]
```

**Qualidade (1-5):** ___

## Fase 4: Teste Multimodal

**Comando:**
```powershell
ollama run qwen2.5-4b @"
Você é especialista em modelos de IA. Responda:
1. O que é Qwen 2.5-4B?
2. Por que roda localmente?
3. Qual é o maior benefício?
"@
```

**Tempo:** [segundos]

**Resposta:**
```
[colar aqui]
```

## Métricas Coletadas

| Métrica | Seu valor | Esperado |
|---------|-----------|----------|
| Tamanho disco | ___ GB | ~2.4GB |
| Tempo 1ª token | ___ ms | 2-5s (CPU) |
| Latência/token | ___ ms | 50-150ms |
| Qualidade | ___/5 | 4-5 |

## Observações

[Escrever aqui suas impressões, o que funcionou bem, o que não funcionou]

## Próximos Passos

Após confirmar tudo funcionando:

1. Testar diferentes quantizações (Q3_K_S, Q5_K_M)
2. Conectar MCP servers
3. Fine-tune com dados próprios

## Referências

- [[setup-qwen-4b-local-windows]] — Guia original
- [[Qwen 3.5 4B Destilado Claude Opus Local]] — Context do modelo
- [[6-melhores-mcp-servers-assistente-ia-local]] — Próxima fase

