---
date: 2026-03-28
tags: [claude-code, git, desenvolvimento, workflow, paralelo]
source: https://x.com/techNmak/status/2037788648691884207
tipo: aplicacao
autor: "@techNmak"
---
# Git Worktrees: Desenvolvimento Paralelo com Múltiplos Claudes sem Context Loss

## O que e
Git Worktrees permite múltiplos checkouts isolados do mesmo repositório em diretórios diferentes. Para Claude Code: rodar 2+ sessões em paralelo, cada uma em branch diferente, sem perder contexto via checkout. Equivale a ter clones do projeto em "mesas diferentes" — cada Claude trabalha sua mesa, depois merge-eia tudo centralmente.

## Como implementar
**Setup inicial**: `git worktree add ../project-feature-a origin/feature-a` cria novo diretório `project-feature-a/` com checkout de `feature-a` branch. Mesma operação cria `project-main/` para main branch. **Sessão Claude 1**: abre primeira pasta, trabalha em feature A. **Sessão Claude 2**: abre segunda pasta, trabalha em feature B. **Sync**: cada sessão trabalha isoladamente — sem checkout repetido que perde contexto. Quando feature A está pronta, Claude 1 commita, push em feature-a branch. Main não é afetado. Depois merge é feito centralmente (via PR, manual, conforme workflow). Worktree também permite uma Claude trabalhar em main enquanto outra testa em branch — sem conflito.

Cleanup: `git worktree remove ../project-feature-a` deleta worktree.

## Stack e requisitos
Git 2.40+. Bash ou PowerShell. Requer espaço disco para múltiplas cópias da pasta (cada worktree ~2x tamanho repo). Tempo: 30 segundos para criar worktree.

## Armadilhas e limitacoes
Worktrees compartilham Git object store, mas cada tem seu HEAD independente — merge conflicts ainda ocorrem se branches divergem. Se deletar worktree eroneamente, commits não são perdidos (estão em object store), apenas referência local desaparece. Algumas operações Git globais (rebase, amend ao main) podem impactar todas worktrees — coordenar. IDEs (vscode) podem confundir worktrees com submodulos; confirmar que reconhece como git worktree, não sub-folder.

## Conexoes
[[git-worktrees-para-agentes|Worktrees para multi-agentes]]
[[empresa-virtual-de-agentes-de-ia|Agentes paralelos]]
[[estudio-de-games-com-multi-agentes-ia|Desenvolvimento paralelo]]

## Historico
- 2026-03-28: Referência original
- 2026-04-02: Reescrita pelo pipeline
