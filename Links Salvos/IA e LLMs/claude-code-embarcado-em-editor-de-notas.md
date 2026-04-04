---
tags: [obsidian, claude, ai-coding, plugin, llm-tools]
source: https://x.com/tom_doerr/status/2036564539748049212?s=20
date: 2026-04-02
tipo: aplicacao
---

# Integrar Claude Code em Obsidian com Plugin Claudian

## O que é

Plugin Claudian expõe Claude Code dentro painel Obsidian. Agente lê/escreve notas do vault, acessa grafo de conhecimento como contexto implícito. Transforma PKM estático em ambiente onde IA atua sobre conhecimento armazenado.

## Como implementar

**1. Instalar plugin Claudian**

```bash
# Opção 1: Via plugin marketplace Obsidian
Obsidian → Settings → Community Plugins → Search "Claudian" → Install

# Opção 2: Manual
git clone https://github.com/YishenTu/claudian.git
cd claudian
npm install && npm run dev
# Copy `main.js` para `.obsidian/plugins/claudian/`
```

**2. Configurar API key**

Obsidian → Settings → "Claudian" → Cole Anthropic API key

```json
{
  "apiKey": "[sua-chave-anthropic]",
  "modelDefault": "claude-opus-4-1",
  "vaultPath": "[caminho vault]"
}
```

**3. Acessar painel Claude**

- Ctrl+Shift+P → "Claudian: Open Claude Panel"
- Ou: sidebar button
- Chat interface nativo no Obsidian

**4. Usar agente com contexto vault**

Prompt tipos:

```
// Gerar Zettelkasten a partir rascunho
"Leia o arquivo rascunho.md do meu vault.
Reescreva como nota Zettelkasten estruturada:
- O que é (2-3 frases)
- Por que importa
- Exemplos
- Conexões a outras notas [[wikilinks]]"

// Encontrar conexões
"Revise todas notas em [[MasterClaude/]]
Identifique conceitos similares
Sugira novos links [[wikilinks]] entre notas"

// Processar em batch
"Para cada arquivo em Projects/*/config.json
Extrait 'version' e 'lastUpdate'
Gere summary.md com table
Salve em Projects/MANIFEST.md"
```

**5. Controles de agência**

Configurar limites de segurança:

```json
{
  "allowFileWrites": true,
  "allowFileDeletes": false,
  "fileWritePath": ["Links Salvos/", "Projects/"],
  "allowShellCommit": false,
  "allowVaultNavigation": true,
  "sendFullVaultContext": false
}
```

**6. Workflow prático**

```
1. Paste raw text/link em vault
2. Abra Claudian panel
3. "Process this note: [file path]"
4. Revise sugestões antes de confirmar writes
5. Plugin atualiza notas, mantém histórico
```

## Stack e requisitos

- Obsidian v1.4+
- Claudian plugin (github.com/YishenTu/claudian)
- Anthropic API key (Claude 3.5 Sonnet+)
- Node.js 14+ (se instalar manualmente)
- ~50MB RAM para painel integrado

## Armadilhas e limitações

- **Privacidade**: Conteúdo vault enviado a servidores Anthropic. Não usar com dados sensíveis
- **Limites agência**: Segurança tight. Agente não pode deletar, só write. Configure explicitamente
- **Latência**: Cada request é HTTP. Lento em vaults grandes (>10k notas)
- **Context limit**: Se vault > 100k tokens, agente não vê contexto completo. Use prefixo path
- **Sync conflicts**: Se Obsidian Sync ativo, edits simultâneos do plugin + manual = conflitos
- **Rate limits**: Anthropic throttles. Usar cache/batch para operações em lote

## Conexões

[[CLAUDE-md-template-plan-mode-self-improvement]]
[[Claude Code - Melhores Práticas]]
[[claude-code-no-obsidian]]
[[contexto-persistente-em-llms]]

## Histórico

- 2026-04-02: Nota criada
- 2026-04-02: Reescrita como guia de integração
