---
date: 2026-03-28
tags: [claude-code, dicas, configuração, debug]
source: https://x.com/Butanium_/status/2037575095569269201
autor: "@Butanium_"
tipo: aplicacao
---

# Ativar Resumo de Pensamentos Oculto em Claude Code

## O que é

Claude Code v2.1.69+ desativa silenciosamente visualização de resumos de pensamento (thinking summaries) no painel. Configuração `showThinkingSummaries` no settings.json restaura visibilidade do raciocínio interno.

## Como implementar

**1. Localizar arquivo settings.json**

Caminho Windows:
```
C:\Users\[seu_usuario]\AppData\Roaming\Claude\settings.json
```

Se não existir, crie-o.

**2. Editar arquivo**

Adicione ou modifique:
```json
{
  "showThinkingSummaries": true
}
```

Se o arquivo já contém outras configurações, insira apenas o campo `showThinkingSummaries`.

**3. Reiniciar Claude Code**

Feche completamente Claude Code. Reabra. Resumos aparecem no painel de debug imediatamente.

**4. Verificar status**

- Painel de debug (geralmente direita/lateral): "Thinking" resumido em texto
- Útil para entender decisões do modelo em tempo real
- Ajuda a refinar prompts com base no que Claude "pensou"

## Stack e requisitos

- Claude Code v2.1.69+
- Editor de texto qualquer (Notepad, VS Code, etc.)
- Acesso à pasta AppData\Roaming
- Sem dependências externas

## Armadilhas e limitações

- **Arquivo oculto**: AppData é pasta oculta no Windows. Ativar visualização em Propriedades > Exibir
- **Sincronização**: Se usa múltiplas máquinas, configure cada uma separadamente
- **Mudança silenciosa**: Anthropic não documentou desativação, descoberta pela comunidade
- **Resumos nem sempre claros**: Às vezes resumo é vago ou técnico demais
- **Performance**: Abas com muitas sessões podem ter resume delay

## Conexões

[[Claude Code - Melhores Práticas]]
[[Claude Code Subconscious Letta Memory Layer]]
[[configuracao-de-contexto-para-llms]]

## Histórico

- 2026-03-28: Nota criada
- 2026-04-02: Reescrita como guia de implementação
