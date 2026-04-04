---
tags: []
source: https://x.com/DavidOndrej1/status/2034755841530769712?s=20
date: 2026-04-02
tipo: aplicacao
---
# Git Worktrees para Agentes: Isolamento de Filesystem para Execução Paralela

## O que e
Git Worktrees criam múltiplos checkouts independentes do mesmo repositório em diretórios separados, eliminando conflito de estado compartilhado. Ideal para sistemas multi-agente: cada agente recebe worktree isolada, trabalha em paralelo sem race conditions, merge centralizado após conclusão.

## Como implementar
**Arquitetura de agentes**: (1) agente orquestrador mantém repo principal, (2) para cada tarefa/agente, cria worktree: `git worktree add ./agent-1-branch branch-name`, (3) agente 1 trabalha em `./agent-1-branch/`, (4) agente 2 trabalha em `./agent-2-branch/` simultaneamente — zero conflito de arquivo porque são diretórios separados, (5) cada agente commita em sua branch isolada, (6) orquestrador merge branches após validação. **Escalabilidade**: N agentes = N worktrees, cada operação é O(1) em relação a N.

Alternativa (menos eficiente): clonar repo N vezes — usa 2x mais espaço disco, perde conexão com objeto store compartilhado, merge é mais complexo. Worktrees resolvem esses problemas nativamente.

## Stack e requisitos
Git 2.40+. Suporta qualquer VCS que use Git (GitHub, GitLab, Gitea). Sistema de arquivos POSIX (Linux, Mac) ou Windows com Git Bash. Overhead: ~500MB por worktree (compartilha objects, só duplica working tree). Sem custo.

## Armadilhas e limitacoes
Worktree não é perfeito isolamento — shared Git config pode causar race conditions se agentes fazem global git config simultaneamente; usar local `--local` config. Deletion acidental: `git worktree remove` sem backup causa perda (mitigar com sempre push antes de deletar). Rebase complexo envolvendo worktrees pode causar problemas se não coordenar; evitar operações globais durante execução paralela.

## Conexoes
[[empresa-virtual-de-agentes-de-ia|Orquestração de agentes]]
[[estudio-de-games-com-multi-agentes-ia|Multi-agentes paralelos]]
[[git-worktrees-desenvolvimento-paralelo-claude-code|Desenvolvimento paralelo Claude]]

## Historico
- 2026-04-02: Nota criada
- 2026-04-02: Reescrita pelo pipeline
