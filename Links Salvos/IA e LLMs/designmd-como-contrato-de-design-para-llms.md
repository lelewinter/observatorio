---
tags: []
source: https://x.com/GithubProjects/status/2039274093657325783?s=20
date: 2026-04-02
tipo: aplicacao
---
# DESIGN.md: Contrato Explícito de Sistema de Design para Agentes de Código

## O que e
Arquivo Markdown na raiz do projeto que documenta design system em linguagem natural (paleta de cores, tipografia, spacing, componentes, tom de voz). Funciona como contrato que LLMs leem antes de gerar UI, reduzindo inconsistências visuais e alucinações de design. Estende convenção de README.md para domínio de design.

## Como implementar
Estrutura típica de DESIGN.md: **Colors** (lista hex com semântica: primary=#007AFF, success=#34C759), **Typography** (fonte base, tamanhos: H1=32px, body=16px, mono=12px), **Spacing** (escala: 4px, 8px, 16px, 24px), **Components** (buttons: primary/secondary/tertiary estilos, inputs com estados), **Tone & Voice** (padrões de escrita, quando usar "por favor" vs imperativo), **Princípios** (acessibilidade WCAG, dark mode support, mobile-first). Formato Markdown mantém arquivo leve, versionável via Git, legível por humanos e facilmente ingerido por LLMs. Tamanho ideal: 2-5KB. Injectar em contexto de agente de código via prompt ou upload no Claude/Cursor/Copilot, permitindo que modelo gere UI coerente sem needing clonar styles do repositório inteiro.

Padrão emergente: coleções de DESIGN.md inspirados em empresas (Stripe, Vercel, Linear, Figma patterns) publicados open-source como referência. Criar seu próprio: copiar template, adaptar para brand, versionar, atualizar a cada mudança de design system.

## Stack e requisitos
Editor de texto puro (vscode, vim, github.com editor). Git para versionamento. Nenhuma dependência técnica. Requer effort inicial de documentação (1-2h para sistema de design existente), depois manutenção incremental. Validação manual: comparar UI gerada por agente contra DESIGN.md, verificar aderência.

## Armadilhas e limitacoes
Maior risco: DESIGN.md desatualizado — se design system evolve e arquivo não é atualizado, agente gera UI baseado em spec velha. Cria novo tipo de "débito de contexto de IA" que não existia antes. Mitigar: code review de UI gerada, integração contínua que valida conformidade com DESIGN.md. Arquivo muito genérico ("seja bonito") não adiciona valor; especificidade é crítica. Mudanças frequentes em design requerem atualizações frequentes do DESIGN.md.

## Conexoes
[[estrutura-claude-md-menos-200-linhas|Documentação concisa]]
[[falhas-criticas-em-apps-vibe-coded|Qualidade em vibe coding]]
[[geracao-automatizada-de-prompts|Prompts estruturados]]

## Historico
- 2026-04-02: Nota criada
- 2026-04-02: Reescrita pelo pipeline
