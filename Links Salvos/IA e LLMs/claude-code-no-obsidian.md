---
tags: [obsidian, claude-code, plugin, pkm, ai-research]
source: https://x.com/thisguyknowsai/status/2038890248772763842?s=20
date: 2026-04-02
tipo: aplicacao
---

# Integrar KatmerCode (Claude Code) em Obsidian

## O que é

Plugin KatmerCode open-source embarca Claude Code em sidebar Obsidian. Inclui: 7 skills pesquisa acadêmica, diff inline, suporte MCP. Transforma vault em ambiente intelectual aumentado por IA.

## Como implementar

**1. Instalar KatmerCode**

```bash
# Opção A: Marketplace Obsidian
Obsidian → Settings → Community Plugins → Search "KatmerCode" → Install

# Opção B: Manual (desenvolvimento)
git clone https://github.com/katmercode/katmercode.git
cd katmercode
npm install && npm run dev
# Copy manualmente para .obsidian/plugins/
```

**2. Configurar API Anthropic**

Settings → KatmerCode → Cole API key

```json
{
  "apiKey": "[your-anthropic-key]",
  "model": "claude-opus-4-1",
  "autoSync": true,
  "mcpEnabled": true
}
```

**3. Abrir painel Claude**

- Sidebar esquerda: icone "KatmerCode"
- Ou: Ctrl+Shift+P → "KatmerCode: Open Panel"
- Chat interface aparece na sidebar

**4. Usar 7 skills de pesquisa acadêmica**

```
// 1. Síntese: resumir conjunto de notas
"Sintetize notas em [[MOC - Agentes Autonomos/]]
Identifique tema central, conceitos-chave, lacunas"

// 2. Extração de argumentos
"Leia [[paper-xyz.md]]. Extraia: tese principal,
3 argumentos principais, contraargumentos, conclusão"

// 3. Análise de fontes
"Revise [[Referencias/]]. Para cada entrada:
Tipo (livro/artigo/blog), autor, relevância,
como cita este projeto"

// 4. Mapping conceitual
"Crie mapa conceitual: [[conceito-A.md]] → [[conceito-B.md]]
Mostre relações, diretas vs. indiretas"

// 5. Crítica e validação
"Critique argumento em [[nota.md]]:
Assumções, evidência, gaps lógicos"

// 6. Expansão/aprofundamento
"Expanda [[intro-note.md]]. Adicione:
História, aplicações práticas, casos de estudo"

// 7. Síntese cruzada
"Compare 3 notas sobre tema X. Consenso? Divergências?
Integre em nova nota [[síntese-tema-X.md]]"
```

**5. Edição com diff inline**

```
Selecione trecho no vault.
KatmerCode → "Refine selected text"
Aprove/rejeite cada linha de mudança
Aceitar ou descartar mudanças atomicamente
```

**6. Integração MCP (Model Context Protocol)**

Conectar ferramentas externas:

```json
{
  "mcpServers": [
    {
      "type": "web_search",
      "enabled": true
    },
    {
      "type": "arxiv",
      "enabled": true
    },
    {
      "type": "github_search",
      "enabled": false
    }
  ]
}
```

Agora agente pode:
- Pesquisar web durante análise
- Buscar papers acadêmicos
- Enriquecer notas com referências

**7. Workflow prático PKM+IA**

```
1. Ler/salvar novo artigo em [[Lidos/]]
2. Abrir KatmerCode → "Extract from current file"
3. Aprova extração automática: tese, args, referências
4. Pergunta: "Onde esta nota se conecta em meu vault?"
5. Agente sugere [[wikilinks]] (aprova manualmente)
6. "Sintetize com notas relacionadas"
7. Novo arquivo de síntese gerado
```

## Stack e requisitos

- Obsidian v1.5+
- Node.js 16+ (desenvolvimento)
- Anthropic API key
- Opcional: MCP servers (web, arxiv, etc)
- ~100MB RAM para sidebar panel

## Armadilhas e limitações

- **Open source ≠ privado**: Código é aberto, mas dados ainda vão a Anthropic API
- **Diff inline impreciso**: Às vezes marca mudanças que não são relevantes
- **MCP ainda emergente**: Nem todos os integrations testadas. Pode quebrar
- **Performance**: Vaults >50k notas lentificam searches de contexto
- **Conflitos git**: Se vault tem git, edits simultâneos plugin+manual = merge conflicts
- **Context janela**: Claude tem limite. Vault gigante não cabe em um prompt

## Conexões

[[claude-code-embarcado-em-editor-de-notas]]
[[CLAUDE-md-template-plan-mode-self-improvement]]
[[contexto-persistente-em-llms]]
[[consolidacao-de-memoria-em-agentes]]

## Histórico

- 2026-04-02: Nota criada
- 2026-04-02: Reescrita como guia de implementação
