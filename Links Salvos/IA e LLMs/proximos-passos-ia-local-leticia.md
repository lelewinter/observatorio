---
tags: [setup, roadmap, próximos-passos, ia-local, otimização]
date: 2026-03-29
status: ativo
---

# Próximos Passos — IA Local Leticia Winter

## Fase 1: COMPLETA ✅

**O que você já tem:**
- Ollama instalado e funcionando
- Qwen 2.5 32B Q4_0 (18GB) baixado
- Modelo testado com sucesso (português perfeito)
- GPU offloading ativo (RAM otimizada de 21GB → 11GB)

**Aprendizados:**
- Ollama tem limitações em GPU offloading
- Qwen 32B entra, mas aperta memória
- Modelo é de qualidade excelente (MMLU ~82)

---

## Fase 2: Otimização — ESCOLHA AGORA

Você precisa escolher um caminho:

### Opção A: Downgrade pra Qwen 14B (Recomendado)
```powershell
ollama pull qwen2.5:14b-instruct-q4_0
```

**Vantagens:**
- ✅ Roda smooth, sem problema
- ✅ Latência 3-4x melhor
- ✅ Usa 8GB VRAM confortavelmente
- ✅ Qualidade ainda excelente (MMLU 76)

**Desvantagens:**
- ❌ Menos capacidade que 32B

**Tempo:** 10 minutos download

---

### Opção B: TurboQuant + llama.cpp (Advanced)
```powershell
git clone https://github.com/tonbistudio/turboquant-pytorch
# Setup complexo em Python
```

**Vantagens:**
- ✅ Otimiza KV cache (6x menos memória em sequências longas)
- ✅ Mantém Qwen 32B
- ✅ Mais controle

**Desvantagens:**
- ❌ Setup complexo
- ❌ Nem tudo funciona perfeito ainda
- ❌ Não resolve latência inicial

**Tempo:** 1-2 horas setup

---

### Opção C: Continuar com Qwen 32B + Ollama (Current)
- Deixa como está
- Funciona, mas não é ideal

---

## Meu voto

**Fase 2a (Agora):** Testa **Qwen 14B**
- 10 minutos
- Validar que é smooth
- Documentar performance

**Fase 2b (Depois):** Se precisar mais poder, testa **TurboQuant**
- Quando sequências ficarem longas
- Quando quiser otimização extrema

---

## Fase 3: Extensão com MCP (Próximas semanas)

Depois que estabilizar em 14B ou 32B:

1. **Browser MCP** — scraping local
2. **Terminal MCP** — executar código
3. **RAG local** — buscar seus próprios documentos
4. **Memory graph** — persistência de conhecimento

Isso transforma seu modelo em assistente completo.

---

## Fase 4: Specialização (Mensal)

Baseado em seu caso de uso:
- Fine-tune com seus próprios dados
- Criar "personas" especializadas
- Integração com seu workflow

---

## Arquitetura Final (Visão)

```
Qwen 2.5-14B (otimizado)
        ↓
   [Ollama Runtime]
        ↓
   MCP Servers
   ├── Browser
   ├── Terminal
   ├── RAG
   └── Memory
        ↓
   [Seu Assistente Local 100% Privado]
```

---

## Decision Point AGORA

**Qual é seu próximo passo?**

A. Testar Qwen 14B (recomendado, rápido)
B. Ir direto pro TurboQuant (quer otimização extrema)
C. Continuar com 32B e lidar com latência

Qual escolhe?

---

## Recursos

- [[setup-qwen-4b-local-windows]] — Setup original
- [[Qwen 3.5 4B Destilado Claude Opus Local]] — Context do modelo
- [[6-melhores-mcp-servers-assistente-ia-local]] — Fase 3
- [[local_llm_reddit_discussao]] — Comunidade r/LocalLLM

