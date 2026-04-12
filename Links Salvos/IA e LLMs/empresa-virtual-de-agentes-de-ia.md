---
tags: [agentes-ia, multi-agentes, orquestração, git-worktrees, autonomia, llm]
source: https://x.com/ihtesham2005/status/2038934452538319205?s=20
date: 2026-04-02
tipo: aplicacao
atualizado: 2026-04-11
---

# Empresa Virtual: Simulação de Organização com Múltiplos Agentes IA

## O que é

Framework open-source que simula empresa de software completa onde agentes IA (Claude, Gemini, etc.) atuam como "funcionários" em departamentos especializados: Frontend Engineer, Backend Engineer, QA, DevOps, Product Manager, etc. CEO humano envia direto ("implementar autenticação OAuth2") via Telegram/Slack, sistema quebra em subtarefas, distribui entre agentes, cada agente trabalha isolado em git worktree, pull request é revisado por CEO antes de merge. Roda 100% local com SQLite para auditoria.

**Diferencial chave:** não é "LLM gera código completo", é orquestração. Cada agente tem:
- Papel específico (com system prompt customizado)
- XP/level system (agente sênior tem mais autonomia)
- Skills mapeadas (~600 possíveis: "escrever teste", "revisar PR", "refatorar", etc)
- Memória de contexto (vê histórico de PRs, commits, problemas)
- Dashboard visual (mostra agentes "trabalhando")

Resultado: você vê empresa operando com divisão de trabalho, parallelismo, controle humano sobre merge.

## Como implementar

### Setup Inicial: Configurar Organização

```python
"""
Configuração de empresa virtual com Claw-Empire.
"""

import json
import sqlite3
from pathlib import Path
from typing import List, Dict

class VirtualCompany:
    def __init__(self, company_name: str, workspace_dir: str = "./company"):
        self.name = company_name
        self.workspace = Path(workspace_dir)
        self.workspace.mkdir(exist_ok=True)
        
        # DB para auditoria
        self.db_path = self.workspace / "company.db"
        self._init_db()
        
        # Config da empresa
        self.config_path = self.workspace / "company.json"
    
    def _init_db(self):
        """Cria tabelas para auditoria."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS agents (
            id INTEGER PRIMARY KEY,
            name TEXT UNIQUE,
            role TEXT,
            model TEXT,
            experience_level INTEGER DEFAULT 1,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        """)
        
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS tasks (
            id INTEGER PRIMARY KEY,
            title TEXT,
            description TEXT,
            assigned_to TEXT,
            status TEXT DEFAULT 'pending',
            pr_id TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            completed_at TIMESTAMP
        )
        """)
        
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS pull_requests (
            id TEXT PRIMARY KEY,
            branch TEXT,
            changes_count INTEGER,
            status TEXT DEFAULT 'pending_review',
            created_by TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        """)
        
        conn.commit()
        conn.close()
    
    def add_agent(self, name: str, role: str, model: str = "claude-3-5-sonnet-20241022", level: int = 1):
        """Registra novo agente na empresa."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        try:
            cursor.execute(
                "INSERT INTO agents (name, role, model, experience_level) VALUES (?, ?, ?, ?)",
                (name, role, model, level)
            )
            conn.commit()
            print(f"✓ Agent {name} ({role}) hired, level {level}")
        except sqlite3.IntegrityError:
            print(f"✗ Agent {name} already exists")
        finally:
            conn.close()
    
    def create_config(self, agents: List[Dict]):
        """Salva configuração de empresa em JSON."""
        config = {
            "company": self.name,
            "github_repo": "./project",  # Local git repo
            "telegram_bot_token": "YOUR_BOT_TOKEN",
            "telegram_group_id": "YOUR_GROUP_ID",
            "agents": agents,
            "model_provider": "anthropic",
            "vcs": "git"
        }
        
        with open(self.config_path, "w") as f:
            json.dump(config, f, indent=2)
        
        print(f"✓ Company config saved: {self.config_path}")

# Setup: Criar empresa com 5 agentes
company = VirtualCompany("TechStartup Inc")

# Contrata time
company.add_agent("Alice", "Senior Backend Engineer", level=3)
company.add_agent("Bob", "Frontend Engineer", level=2)
company.add_agent("Charlie", "QA Automation Engineer", level=2)
company.add_agent("Diana", "DevOps Engineer", level=3)
company.add_agent("Eve", "Product Manager", level=1)

# Config
agents_config = [
    {"name": "Alice", "role": "Backend", "skills": ["python", "database-design", "api", "security"]},
    {"name": "Bob", "role": "Frontend", "skills": ["react", "typescript", "css", "testing"]},
    {"name": "Charlie", "role": "QA", "skills": ["pytest", "selenium", "load-testing"]},
    {"name": "Diana", "role": "DevOps", "skills": ["docker", "kubernetes", "ci-cd", "monitoring"]},
    {"name": "Eve", "role": "PM", "skills": ["requirements", "roadmap", "user-stories"]}
]

company.create_config(agents_config)
```

### Orquestração: CEO → Tarefas → Agentes

```python
import anthropic
import subprocess
from datetime import datetime

class TaskOrchestrator:
    """
    Quebra diretiva do CEO em tarefas, distribui entre agentes.
    """
    
    def __init__(self, company: VirtualCompany):
        self.company = company
        self.client = anthropic.Anthropic()
        self.db_path = company.db_path
    
    def create_task_from_directive(self, directive: str) -> List[Dict]:
        """
        CEO diz: "Implementar autenticação OAuth2"
        Claude quebra em subtarefas específicas por role.
        """
        
        message = self.client.messages.create(
            model="claude-3-5-sonnet-20241022",
            max_tokens=2048,
            messages=[{
                "role": "user",
                "content": f"""
                Você é gerente de projeto em empresa ágil.
                CEO passou diretiva: "{directive}"
                
                Quebre em 4-5 subtarefas específicas, cada uma para um role:
                - Backend Engineer: código de API/lógica
                - Frontend Engineer: UI/componentes
                - QA Engineer: testes
                - DevOps: deployment/monitoring
                
                Retorne JSON com array de tasks. Cada task tem:
                - title: nome conciso
                - description: detalhes específicos
                - assigned_role: Backend/Frontend/QA/DevOps
                - estimated_hours: tempo estimado
                - dependencies: lista de tasks que deve fazer antes
                - acceptance_criteria: como saber que funcionou
                
                Retorne APENAS JSON válido.
                """
            }]
        )
        
        import json
        tasks_json = json.loads(message.content[0].text)
        return tasks_json["tasks"]
    
    def assign_tasks_to_agents(self, tasks: List[Dict]) -> Dict[str, List[Dict]]:
        """
        Mapeia tarefas para agentes específicos baseado em role.
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Busca agentes por role
        cursor.execute("SELECT name, role FROM agents")
        agents = {role: name for name, role in cursor.fetchall()}
        conn.close()
        
        assignments = {}
        
        for task in tasks:
            role_needed = task["assigned_role"]
            
            # Encontra agente com esse role
            agent_name = agents.get(role_needed)
            if not agent_name:
                print(f"✗ No agent found for role: {role_needed}")
                continue
            
            if agent_name not in assignments:
                assignments[agent_name] = []
            
            assignments[agent_name].append(task)
            print(f"✓ Assigned to {agent_name}: {task['title']}")
        
        return assignments
    
    def execute_agent_task(self, agent_name: str, task: Dict, branch_name: str) -> str:
        """
        Executa tarefa de um agente em git worktree isolado.
        """
        
        # Cria worktree
        worktree_path = self.company.workspace / "project" / "worktrees" / branch_name
        self._create_worktree(branch_name, worktree_path)
        
        # System prompt para agente
        system_prompt = self._get_agent_system_prompt(agent_name)
        
        # Pede ao Claude para fazer tarefa
        message = self.client.messages.create(
            model="claude-3-5-sonnet-20241022",
            max_tokens=4096,
            system=system_prompt,
            messages=[{
                "role": "user",
                "content": f"""
                Você precisa completar esta tarefa:
                
                Título: {task['title']}
                Descrição: {task['description']}
                
                Critérios de aceitação:
                {json.dumps(task['acceptance_criteria'], indent=2)}
                
                Seu worktree local está em: {worktree_path}
                
                Implemente a solução, faça commits, e prepare um PR.
                Retorne JSON com:
                - summary: resumo do que fez
                - files_changed: lista de arquivos modificados
                - test_results: resultados de testes (se rodou)
                - pr_description: descrição pro PR
                """
            }]
        )
        
        # Parse resultado
        import json
        response = json.loads(message.content[0].text)
        
        # Faz commit
        self._commit_changes(agent_name, branch_name, response["summary"])
        
        # Cria PR
        pr_id = self._create_pull_request(agent_name, branch_name, response["pr_description"])
        
        return pr_id
    
    def _create_worktree(self, branch: str, path: Path):
        """Cria git worktree isolado."""
        path.parent.mkdir(parents=True, exist_ok=True)
        subprocess.run(
            ["git", "worktree", "add", str(path), "-b", branch],
            cwd=self.company.workspace / "project",
            check=True
        )
    
    def _get_agent_system_prompt(self, agent_name: str) -> str:
        """Customiza system prompt por agente."""
        
        prompts = {
            "Alice": """Você é Senior Backend Engineer com 10+ anos experiência.
                        Especializado em Python, databases, APIs, segurança.
                        Código sempre é production-ready com error handling.
                        Escreva testes automaticamente.""",
            "Bob": """Você é Frontend Engineer, especialista em React/TypeScript.
                      UI sempre responsiva, acessível, testada.
                      Use componentes reutilizáveis.""",
            "Charlie": """Você é QA Engineer. Sempre escreve testes abrangentes.
                          Busca edge cases, race conditions, security issues.
                          Documenta casos de teste claramente.""",
            "Diana": """Você é DevOps Engineer. Kubernetes, Docker, CI/CD specialist.
                        Automação total. Sempre monitora performance e logs.
                        Security-first approach.""",
        }
        
        return prompts.get(agent_name, "You are a skilled software engineer.")
    
    def _commit_changes(self, agent_name: str, branch: str, message: str):
        """Faz commit dos trabalho do agente."""
        subprocess.run(
            ["git", "add", "-A"],
            cwd=self.company.workspace / "project",
            check=True
        )
        subprocess.run(
            ["git", "commit", "-m", f"[{agent_name}] {message}"],
            cwd=self.company.workspace / "project",
            check=True
        )
    
    def _create_pull_request(self, agent_name: str, branch: str, description: str) -> str:
        """Simula PR (em produção, usa GitHub API)."""
        import uuid
        pr_id = str(uuid.uuid4())[:8]
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute(
            """INSERT INTO pull_requests (id, branch, status, created_by, changes_count)
               VALUES (?, ?, ?, ?, ?)""",
            (pr_id, branch, "pending_review", agent_name, 5)  # Mock changes_count
        )
        conn.commit()
        conn.close()
        
        print(f"✓ PR created: {pr_id} by {agent_name}")
        return pr_id

# Uso: Fluxo completo
company = VirtualCompany("TechStartup Inc")
orchestrator = TaskOrchestrator(company)

# CEO manda diretiva
directive = "Implementar autenticação OAuth2 com Google e GitHub"

# Quebra em tarefas
tasks = orchestrator.create_task_from_directive(directive)
print(f"\n📋 CEO Directive: {directive}")
print(f"   Quebrado em {len(tasks)} subtarefas\n")

# Distribui
assignments = orchestrator.assign_tasks_to_agents(tasks)

# Executa em paralelo (simplificado: sequencial aqui)
prs = []
for agent_name, agent_tasks in assignments.items():
    for task in agent_tasks:
        branch_name = f"feature/{task['title'].lower().replace(' ', '-')}"
        pr_id = orchestrator.execute_agent_task(agent_name, task, branch_name)
        prs.append(pr_id)

print(f"\n✓ All agents completed! {len(prs)} PRs waiting for CEO review:")
for pr_id in prs:
    print(f"  - {pr_id}")
```

### Controle Humano: CEO Revisão + Merge

```python
class CEOApprovalProcess:
    """
    CEO revisa PRs antes de merge em main.
    """
    
    def __init__(self, company: VirtualCompany):
        self.company = company
        self.client = anthropic.Anthropic()
    
    def review_pr(self, pr_id: str, auto_check: bool = True) -> Dict:
        """
        Revisa PR. Se auto_check=True, Claude faz análise automática.
        CEO deve aprovar antes de merge.
        """
        
        pr_data = self._get_pr_details(pr_id)
        
        if auto_check:
            # Claude revisa código
            analysis = self._auto_review_code(pr_data)
            print(f"\n🤖 Auto-Review for {pr_id}:")
            print(f"   Code Quality: {analysis['quality_score']}/10")
            print(f"   Issues: {analysis['issues']}")
            print(f"   Recommendation: {analysis['recommendation']}")
        
        # CEO decision
        print(f"\n👨‍💼 CEO Decision:")
        decision = input(f"Approve PR {pr_id}? (approve/request-changes/reject): ").strip()
        
        if decision == "approve":
            self._merge_pr(pr_id)
            return {"status": "merged", "pr_id": pr_id}
        
        elif decision == "request-changes":
            feedback = input("Feedback for agent: ").strip()
            self._send_feedback_to_agent(pr_id, feedback)
            return {"status": "changes-requested", "feedback": feedback}
        
        else:
            self._reject_pr(pr_id)
            return {"status": "rejected"}
    
    def _get_pr_details(self, pr_id: str) -> Dict:
        """Busca detalhes do PR (mock)."""
        return {
            "id": pr_id,
            "branch": "feature/oauth2-google",
            "author": "Alice",
            "changes": ["src/auth.py", "tests/test_auth.py"],
            "diff_stats": "+450 -120 lines"
        }
    
    def _auto_review_code(self, pr_data: Dict) -> Dict:
        """Claude faz análise automática de código."""
        
        message = self.client.messages.create(
            model="claude-3-5-sonnet-20241022",
            max_tokens=1024,
            messages=[{
                "role": "user",
                "content": f"""
                Revise este PR como code reviewer sênior:
                
                Branch: {pr_data['branch']}
                Author: {pr_data['author']}
                Changes: {', '.join(pr_data['changes'])}
                Stats: {pr_data['diff_stats']}
                
                Retorne JSON:
                - quality_score: 1-10
                - issues: lista de problemas (ou vazio se nenhum)
                - recommendation: "approve", "request-changes", ou "reject"
                - comments: feedback específico
                """
            }]
        )
        
        import json
        return json.loads(message.content[0].text)
    
    def _merge_pr(self, pr_id: str):
        """Merge para main."""
        print(f"✅ PR {pr_id} approved and merged to main!")
        # Em produção: `gh pr merge` ou GitHub API
    
    def _send_feedback_to_agent(self, pr_id: str, feedback: str):
        """Envia feedback pro agente revisar."""
        print(f"📤 Feedback sent to agent: {feedback}")
    
    def _reject_pr(self, pr_id: str):
        """Rejeita PR, deleta branch."""
        print(f"❌ PR {pr_id} rejected and branch deleted")

# Uso
company = VirtualCompany("TechStartup Inc")
approval_process = CEOApprovalProcess(company)

# CEO revisa PRs
prs = ["abc123", "def456", "ghi789"]
for pr_id in prs:
    result = approval_process.review_pr(pr_id, auto_check=True)
    print(f"  Result: {result['status']}\n")
```

### Dashboard Visual (ASCII Art)

```python
def print_company_dashboard(company: VirtualCompany):
    """Mostra status da empresa."""
    
    conn = sqlite3.connect(company.db_path)
    cursor = conn.cursor()
    
    cursor.execute("SELECT COUNT(*) FROM tasks WHERE status = 'pending'")
    pending = cursor.fetchone()[0]
    
    cursor.execute("SELECT COUNT(*) FROM tasks WHERE status = 'completed'")
    completed = cursor.fetchone()[0]
    
    cursor.execute("SELECT COUNT(*) FROM pull_requests WHERE status = 'pending_review'")
    prs_pending = cursor.fetchone()[0]
    
    cursor.execute("SELECT name, role, experience_level FROM agents ORDER BY experience_level DESC")
    agents = cursor.fetchall()
    conn.close()
    
    # ASCII art dashboard
    print("""
    ╔════════════════════════════════════════════════════════╗
    ║           🏢 TechStartup Inc - Company Dashboard      ║
    ╚════════════════════════════════════════════════════════╝
    
    📊 Status:
       Pending Tasks: {pending}
       Completed: {completed}
       PRs Pending Review: {prs_pending}
    
    👥 Team:
    """.format(pending=pending, completed=completed, prs_pending=prs_pending))
    
    for name, role, level in agents:
        xp_bar = "⭐" * level
        print(f"       {name:12} | {role:15} | {xp_bar}")
    
    print("""
    
    ⚙️ Workflow:
       CEO Directive → Claude Breaks into Tasks → Agents Work in Parallel
       → Git Worktrees Isolation → PRs Created → CEO Reviews → Merge to Main
    """)

# Chama
print_company_dashboard(company)
```

## Stack e requisitos

**Infraestrutura:**
- Local: Python 3.10+, Git 2.40+, sqlite3 (padrão)
- LLM: Anthropic API key válida
- VCS: Git com múltiplos worktrees
- Optional: Docker para isolar agentes em containers

**Custo por Task:**
- 3-4 chamadas Claude por task (planning, execution, review)
- ~2000-3000 tokens por call
- Estimado USD 0.05-0.20 por task pequena
- Para 5 agentes trabalhando 8 horas: ~USD 2-5/dia em API costs

**Performance:**
- Orquestração (quebrar task): 30-60s
- Execução de task (coding): 2-5 minutos
- Code review auto: 10-30s
- Total por task: 3-6 minutos
- Parallelização com múltiplos agentes: N tasks em ~3-6min (não 3-6min × N)

## Armadilhas e limitações

**Agentes Não Têm Memória Longo-Prazo:**
Cada chamada é nova sessão. Agente "esquece" contexto de PRs anteriores. Solução:
```python
# Inclua histórico no system prompt
recent_context = fetch_agent_recent_commits(agent_name, limit=5)
system_prompt += f"\nRecent work:\n{recent_context}"
```

**Git Merge Conflicts Não Resolvem Automaticamente:**
Se dois agentes mexem no mesmo arquivo, merge pode quebrar. Mitigation:
- Arquitetura que reduz overlap (cada agente, domínio específico)
- Merge strategy manual: CEO resolve ou agente sênior refactora

**Agentes Podem Gerar Código Incorreto:**
Claude às vezes "alucina" imports, funções que não existem. Sempre:
- Testar código (QA agente roda testes)
- Code review (CEO aprova antes de merge)
- Não confie em "agente sênior" sem verificação

**Skill Mismatch:**
Agente pode tentar skill que não tem (ex: QA sem pytest experience). Solve:
- Mapear skills consolidados por agente
- Claude vê lista de skills no system prompt
- Reject task se requer skill desconhecida

**Alucinação de Funcionalidades:**
Agente pode implementar feature que não foi pedido. CEO deve:
- Revisar acceptance criteria
- Approve/reject conforme requisito exato

## Conexões

- [[construcao-de-llm-do-zero|LLM do zero]] — entender como Claude internamente
- [[geracao-de-video-local-com-agente-autonomo|Agentes autônomos]] — orquestração similar
- [[git-worktrees-para-agentes|Git worktrees isolation]] — garantir paralelismo seguro
- [[falhas-criticas-em-apps-vibe-coded|Code quality control]] — sempre revisar saída agente

## Histórico

- 2026-04-02: Nota criada com conceito básico
- 2026-04-11: Reescrita com código Python completo (VirtualCompany setup, TaskOrchestrator, CEOApprovalProcess, dashboard). Adicionadas estruturas reais (SQLite audit log, git worktree isolation, PR workflow). Cobertos armadilhas (hallucination, memory, merge conflicts). Fluxo completo: CEO directive → task breakdown → agent execution → PR review → merge.
