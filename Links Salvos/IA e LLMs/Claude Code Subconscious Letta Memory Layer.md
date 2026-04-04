---
date: 2026-03-23
tags: [ia, claude-code, memoria-ia, letta, open-source]
source: https://x.com/charliejhills/status/2035999601954865229?s=20
autor: "@charliejhills"
tipo: aplicacao
---

# Integrar Claude Subconscious para Memória Persistente entre Sessões

## O que é

Plugin Letta open-source que executa agente de background monitorando sessões Claude Code em tempo real. Injeta contexto automático derivado de padrões de trabalho anteriores, aprendizado de bug fixes, técnicas testadas. Transforma cada sessão de "amnésia" em "continuidade inteligente".

## Como implementar

**1. Instalação via marketplace**

```bash
/plugin marketplace add @thibetis-ai/claude-subconscious
/plugin install claude-subconscious
```

Ou via Claude Code UI: Marketplace → Search "claude-subconscious" → Install.

**2. Configuração inicial**

Arquivo config (auto-gerado):
```json
{
  "enableBackground": true,
  "memoryInjectPoint": "prePrompt",
  "syncInterval": 30000,
  "maxMemorySize": "10MB",
  "diffOnly": true
}
```

Ativa injeção de contexto antes de você digitar cada prompt. Sincroniza a cada 30s (ajustável).

**3. Fluxo de uso**

- Trabalha normalmente em Claude Code
- Subconscious monitora: arquivos abertos, bugs encontrados, soluções aplicadas, padrões de codificação
- Antes de novo prompt: agente injeta memória relevante (bugs similares resolvidos, técnicas aplicadas antes)
- Sem interferência manual — automático

**4. Otimização de tokens**

- Primeira injeção: bloco completo de memória
- Subsequent: apenas diffs (mudanças) → economia significativa
- Agente tem acesso a ferramentas para research em background
- Sincronização direta de contexto entre múltiplas sessões paralelas

**5. Casos de uso estruturados**

| Cenário | Benefício |
|---------|-----------|
| Múltiplos projetos | Contexto automático quando muda de projeto |
| Bugs recorrentes | Aviso "você já debugou isso em ProjectX" |
| Técnicas | Sugere padrão que funcionou antes |
| Sessões interrompidas | Retoma com memória do que foi feito |

## Stack e requisitos

- Claude Code (qualquer versão recente)
- Letta Framework (incluído no plugin)
- ~50-100MB disco (armazenamento de memória)
- Zero dependências externas (100% open source)

## Armadilhas e limitações

- **Privacidade local**: Memória armazenada localmente, não sincronizada (por design)
- **Overhead inicial**: Primeira sessão mais lenta (indexação de histórico)
- **Tamanho crescente**: Se não limpar histórico, memória cresce lentamente
- **Imprecisão**: Ocasionalmente injeta contexto levemente incorreto (rejeite manualmente)
- **Compatibilidade**: Requer versão Letta compatible, verifique release notes

## Conexões

[[Claude Code - Melhores Práticas]]
[[Claude Peers Multiplas Instancias Coordenadas]]
[[CLAUDE-md-template-plan-mode-self-improvement]]
[[consolidacao-de-memoria-em-agentes]]
[[contexto-persistente-em-llms]]

## Histórico

- 2026-03-23: Nota criada
- 2026-04-02: Reescrita como guia de integração
