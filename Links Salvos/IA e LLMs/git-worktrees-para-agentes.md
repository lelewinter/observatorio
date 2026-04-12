---
tags: [git, agentes-ia, parallelization, multi-agent, orchestration]
source: https://x.com/DavidOndrej1/status/2034755841530769712?s=20
date: 2026-04-02
tipo: aplicacao
---
# Git Worktrees para Agentes: Isolamento de Filesystem para Execução Paralela

## O que é

Git Worktrees criam múltiplos checkouts independentes do **mesmo repositório** em diretórios separados, compartilhando o mesmo `.git` object store mas com working trees isoladas. Para sistemas multi-agente, isso é crítico: cada agente recebe sua própria worktree, trabalha em paralelo sem race conditions, commita em sua branch isolada, e depois a orquestra centralizada faz merge após validação.

Diferença crucial vs "clonar N vezes":
- **Clones N vezes**: Cada clone é ~300MB (duplica .git), refs separados, merge é custoso
- **Worktrees N vezes**: Cada worktree é ~2MB (compartilha .git), refs vivos, merge é operação sobre mesmo objeto store

No Augment Code e DEV Community em 2026, Git worktrees emergiram como padrão de facto para orquestração multi-agente em produção. JetBrains adicionou first-class support em 2026.1 (março 2026), VS Code em julho 2025.

**Aplicação prática**: 3 agentes especializados (frontend, backend, tests) trabalham em paralelo em branches diferentes. Sem worktrees, um agente espera o outro terminar. Com worktrees: 3x throughput.

## Como Implementar

### Setup Básico: Orchestrator + N Agentes

```bash
# Assumindo repo limpo com main branch
cd /project
git status
# On branch main, working tree clean

# === ORCHESTRATOR ===
# Cria 3 worktrees isoladas para 3 agentes
git worktree add ./agent-frontend frontend-branch
git worktree add ./agent-backend backend-branch
git worktree add ./agent-tests tests-branch

# Resultado: filesystem agora tem
# /project/
#   .git/                    (compartilhado)
#   ./agent-frontend/        (branch isolada)
#   ./agent-backend/         (branch isolada)
#   ./agent-tests/           (branch isolada)
#   ./
```

Cada worktree está em uma **branch diferente**, com seu próprio `HEAD`, `index`, e working tree. Ao mesmo tempo, todas compartilham `.git/objects`, `.git/refs` (leitura), reduzindo overhead.

### Integração Python: Orchestrator para Multi-Agent

```python
# orchestrator.py
import subprocess
import json
from pathlib import Path
from datetime import datetime
from typing import Optional
import asyncio

class GitWorktreeOrchestrator:
    def __init__(self, repo_path: str, num_agents: int = 3):
        self.repo_path = Path(repo_path)
        self.num_agents = num_agents
        self.worktrees = {}
        self.agent_tasks = {}
        self.execution_log = []
    
    def setup_worktrees(self, task_list: list[dict]) -> None:
        """
        Create N worktrees, one per agent task.
        task_list = [
            {"agent_id": "frontend", "branch": "feat/ui-refactor"},
            {"agent_id": "backend", "branch": "feat/api-v2"},
            {"agent_id": "tests", "branch": "feat/test-coverage"}
        ]
        """
        print(f"Setting up {len(task_list)} worktrees...")
        
        for task in task_list:
            agent_id = task["agent_id"]
            branch = task["branch"]
            worktree_path = self.repo_path / f"agent-{agent_id}"
            
            try:
                # Cria branch se não existir (tracking main)
                self._run_git(["checkout", "-b", branch, "origin/main"],
                             cwd=str(self.repo_path))
            except subprocess.CalledProcessError:
                # Branch já existe
                pass
            
            # Cria worktree
            result = self._run_git(
                ["worktree", "add", str(worktree_path), branch],
                cwd=str(self.repo_path)
            )
            
            self.worktrees[agent_id] = {
                "path": str(worktree_path),
                "branch": branch,
                "status": "ready",
                "created_at": datetime.now().isoformat(),
                "task": task
            }
            
            print(f"  ✓ {agent_id}: {worktree_path} on {branch}")
    
    async def execute_parallel_tasks(self, commands: dict[str, list[str]]) -> dict:
        """
        Execute N commands in parallel (one per agent/worktree).
        commands = {
            "frontend": ["npm install && npm run build"],
            "backend": ["poetry install && poetry run migrate"],
            "tests": ["pytest tests/"]
        }
        """
        print("\nExecuting tasks in parallel...")
        
        tasks = []
        for agent_id, cmd_list in commands.items():
            if agent_id not in self.worktrees:
                print(f"  ✗ Agent {agent_id} not found in worktrees")
                continue
            
            worktree_path = self.worktrees[agent_id]["path"]
            
            # Cada agente executa sua tarefa na sua worktree
            task = asyncio.create_task(
                self._execute_in_worktree(agent_id, worktree_path, cmd_list)
            )
            tasks.append(task)
        
        # Aguarda todas as tarefas em paralelo
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        execution_summary = {}
        for agent_id, result in zip(commands.keys(), results):
            if isinstance(result, Exception):
                execution_summary[agent_id] = {
                    "status": "failed",
                    "error": str(result)
                }
            else:
                execution_summary[agent_id] = result
        
        return execution_summary
    
    async def _execute_in_worktree(self, agent_id: str, worktree_path: str,
                                   commands: list[str]) -> dict:
        """Execute commands in agent's worktree (async)."""
        
        print(f"  → {agent_id} starting...")
        
        start_time = datetime.now()
        outputs = []
        
        for cmd in commands:
            try:
                result = subprocess.run(
                    cmd,
                    shell=True,
                    cwd=worktree_path,
                    capture_output=True,
                    text=True,
                    timeout=300  # 5 min per command
                )
                
                if result.returncode != 0:
                    raise RuntimeError(f"Command failed: {result.stderr}")
                
                outputs.append(result.stdout)
            
            except subprocess.TimeoutExpired:
                raise RuntimeError(f"Command timeout in {agent_id}")
        
        end_time = datetime.now()
        duration = (end_time - start_time).total_seconds()
        
        print(f"  ✓ {agent_id} completed in {duration:.1f}s")
        
        return {
            "agent_id": agent_id,
            "status": "success",
            "duration_seconds": duration,
            "outputs": outputs
        }
    
    def commit_and_push_all(self, commit_msg: str) -> dict:
        """Cada agente faz commit em sua branch e push."""
        
        print(f"\nCommitting changes across all worktrees...")
        results = {}
        
        for agent_id, wt_info in self.worktrees.items():
            worktree_path = wt_info["path"]
            branch = wt_info["branch"]
            
            try:
                # Check status
                status = self._run_git(
                    ["status", "--porcelain"],
                    cwd=worktree_path
                )
                
                if not status.strip():
                    print(f"  - {agent_id}: no changes")
                    results[agent_id] = {"status": "no_changes"}
                    continue
                
                # Stage all
                self._run_git(["add", "-A"], cwd=worktree_path)
                
                # Commit
                self._run_git(
                    ["commit", "-m", f"{commit_msg} ({agent_id})"],
                    cwd=worktree_path
                )
                
                # Push
                self._run_git(
                    ["push", "origin", branch],
                    cwd=worktree_path
                )
                
                results[agent_id] = {"status": "pushed"}
                print(f"  ✓ {agent_id} pushed to {branch}")
            
            except Exception as e:
                results[agent_id] = {"status": "error", "error": str(e)}
                print(f"  ✗ {agent_id} failed: {e}")
        
        return results
    
    def merge_and_cleanup(self) -> dict:
        """Merge all branches de volta para main (orchestrator faz isso)."""
        
        print(f"\nMerging branches back to main...")
        
        # Volta para main
        self._run_git(["checkout", "main"], cwd=str(self.repo_path))
        self._run_git(["pull"], cwd=str(self.repo_path))
        
        merge_results = {}
        
        for agent_id, wt_info in self.worktrees.items():
            branch = wt_info["branch"]
            
            try:
                # Merge branch
                output = self._run_git(
                    ["merge", "--no-ff", branch, "-m", f"Merge {agent_id}"],
                    cwd=str(self.repo_path)
                )
                
                merge_results[agent_id] = {
                    "status": "merged",
                    "output": output
                }
                print(f"  ✓ {agent_id} merged to main")
            
            except subprocess.CalledProcessError as e:
                # Possível conflito
                merge_results[agent_id] = {
                    "status": "conflict",
                    "error": str(e),
                    "action": f"resolve manually: git merge --abort then fix {branch}"
                }
                print(f"  ⚠ {agent_id} has conflicts (resolve manually)")
        
        # Cleanup worktrees
        self.cleanup_worktrees()
        
        return merge_results
    
    def cleanup_worktrees(self) -> None:
        """Remove all worktrees após merge."""
        
        print(f"\nCleaning up worktrees...")
        
        for agent_id, wt_info in self.worktrees.items():
            try:
                self._run_git(
                    ["worktree", "remove", wt_info["path"]],
                    cwd=str(self.repo_path)
                )
                print(f"  ✓ Removed {agent_id} worktree")
            except Exception as e:
                print(f"  ✗ Error removing {agent_id}: {e}")
    
    def _run_git(self, args: list[str], cwd: Optional[str] = None) -> str:
        """Helper para executar comando git."""
        cmd = ["git"] + args
        result = subprocess.run(cmd, cwd=cwd or str(self.repo_path),
                              capture_output=True, text=True)
        if result.returncode != 0:
            raise subprocess.CalledProcessError(
                result.returncode, cmd, result.stderr
            )
        return result.stdout.strip()

# === MAIN EXECUTION ===
async def main():
    orchestrator = GitWorktreeOrchestrator("/project", num_agents=3)
    
    # 1. Setup worktrees
    tasks = [
        {"agent_id": "frontend", "branch": "feat/ui-refactor"},
        {"agent_id": "backend", "branch": "feat/api-v2"},
        {"agent_id": "tests", "branch": "feat/test-coverage"}
    ]
    orchestrator.setup_worktrees(tasks)
    
    # 2. Execute tasks in parallel
    commands = {
        "frontend": ["npm install", "npm run lint", "npm run build"],
        "backend": ["poetry install", "poetry run lint", "poetry run test"],
        "tests": ["pytest tests/ --cov"]
    }
    results = await orchestrator.execute_parallel_tasks(commands)
    print(f"\nExecution results:\n{json.dumps(results, indent=2)}")
    
    # 3. Commit changes
    orchestrator.commit_and_push_all("feat: multi-agent execution")
    
    # 4. Merge and cleanup
    merge_results = orchestrator.merge_and_cleanup()

if __name__ == "__main__":
    asyncio.run(main())
```

## Stack e Requisitos

### Essencial
- **Git 2.40+** (worktrees adicionado em 2.14, mas v2.40+ é recomendado para estabilidade)
- Repositório Git existente (GitHub, GitLab, Gitea)
- Sistema de arquivos POSIX (Linux, Mac) ou Windows com Git Bash
- Python 3.8+ para orchestrator

### Overhead Técnico
- Cada worktree ocupa ~500MB (compartilha .git, duplica working tree)
- 10 worktrees = ~5GB extra (tolerável)
- Operações não são thread-safe — usar locks em shared refs (`.git/config`)

### Compatibilidade IDE
- **VS Code**: Git Worktrees (extension by Amodio, built-in desde v1.85)
- **JetBrains**: Native support desde 2026.1 (March 2026)
- **Cursor**: Suporta (Git integration via Command Palette)
- **Vim/Neovim**: Manual (CLI)

## Armadilhas e Limitações

### 1. Worktrees Não Isolam Git Config

**Problema**: Se dois agentes executam `git config --global core.ignoreCase true` simultaneamente, há race condition no `.git/config` compartilhado.

**Mitigação**:
```python
# Usar --local, não --global
def setup_agent_config(worktree_path: str):
    subprocess.run(
        ["git", "config", "--local", "user.name", "Agent-Frontend"],
        cwd=worktree_path
    )
    # Agora config é local a essa worktree
```

### 2. Sem Warning se Múltiplas Worktrees Modificam Mesmo Arquivo

**Problema**: Agente Frontend e Backend ambos modificam `package.json`. Quando mergeam:
```
Agent Frontend: "scripts": {"build": "..."}
Agent Backend: "scripts": {"start": "..."}
Result: Merge conflict
```

Git Worktrees não avisa sobre essa sobreposição **antes** de merge.

**Mitigação**:
- Pré-análise: escanear which files cada agente vai tocar
- Owner mapping: arquivo `.git/CODEOWNERS` lista owner de cada path
- Pre-merge validation: `git diff --name-only main..branch` em cada branch antes de merge

```python
def validate_no_overlapping_changes(branches: list[str]) -> bool:
    """Check if branches modify overlapping files."""
    touched_files = {}
    
    for branch in branches:
        files = subprocess.check_output(
            ["git", "diff", "--name-only", "main.."+branch]
        ).decode().split("\n")
        
        for file in files:
            if file in touched_files:
                print(f"CONFLICT: {file} modified in both {touched_files[file]} and {branch}")
                return False
            touched_files[file] = branch
    
    return True
```

### 3. Runtime Não É Isolado (Ports, DBs, Caches)

**Problema**: Agente Backend em worktree 1 inicia servidor em `localhost:5000`. Agente Backend em worktree 2 tenta iniciar no mesmo port → conflict.

Worktrees isolam **filesystem**, não runtime.

**Mitigação**:
- Assinar ports dinamicamente por agente:
```python
PORT = 5000 + agent_id_hash % 100  # Cada agente get unique port range
```
- Database: use in-memory (SQLite `:memory:`) ou múltiplas instâncias
- Cache: Redis keys scoped by agent: `agent-1:cache:key`

### 4. Deletion Acidental = Perda de Trabalho

**Problema**: 
```bash
git worktree remove ./agent-frontend --force
# Poof, todo trabalho uncommitted desaparece
```

**Mitigação**:
- Sempre push antes de remover: `git push origin branch` primeiro
- Pre-remove check: verificar uncommitted changes
```python
def safe_remove_worktree(worktree_path: str):
    # Check for uncommitted changes
    status = subprocess.run(
        ["git", "status", "--porcelain"],
        cwd=worktree_path,
        capture_output=True, text=True
    ).stdout
    
    if status.strip():
        raise RuntimeError(f"Uncommitted changes in {worktree_path}")
    
    # Safe to remove
    subprocess.run(["git", "worktree", "remove", worktree_path])
```

### 5. Rebase Complexo em Múltiplas Worktrees Causa Problemas

**Problema**: Após 3 agentes terminarem, branches têm históricos divergentes. Rebase interativo de todos é complicado.

**Mitigação**: Evitar operações globais durante execução paralela. Usar squash merge:
```bash
git merge --squash feat/frontend  # Combina todos commits em 1
git commit -m "Feature: Frontend refactor"
```

### 6. Merge Conflicts Requerem Resolução Manual

Git worktrees não resolvem conflitos automaticamente.

**Mitigação**: 
- Conflict detection antes de merge
- Human-in-the-loop: escalona para dev revisar se houver conflict
- Abortar merge (`git merge --abort`) e notificar orquestrador

## Conexões

- [[empresa-virtual-de-agentes-de-ia|Orquestração de agentes especializados]]
- [[estudio-de-games-com-multi-agentes-ia|Multi-agentes trabalhando em paralelo (assets, código, tests)]]
- [[git-worktrees-desenvolvimento-paralelo-claude-code|Desenvolvimento paralelo integrado em Claude Code]]
- [[orchestrator-central-para-multi-agentes|Coordenação centralizada de agentes]]

## Histórico

- 2026-04-02: Nota criada
- 2026-04-11: Reescrita com orchestrator Python funcional, async execution, merge strategy, 6 armadilhas detalhadas, runtime isolation challenges, JetBrains/VS Code compatibility
