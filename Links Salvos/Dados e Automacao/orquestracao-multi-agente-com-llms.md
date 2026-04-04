---
tags: [claude-code, llm-agents, produtividade, automacao, multi-agent, paralelo]
source: https://x.com/dennizor/status/2039489726370164789?s=20
date: 2026-04-02
tipo: aplicacao
---
# Orquestração Multi-Agente LLM em Paralelo: Desenvolvimento Distribuído com Loops de Validação

## O que é
Arquitetura de 6-10 instâncias paralelas de Claude Code (via tmux/sessionmanager) cada uma com escopo bem definido (auth service, API, UI, tests, infra, docs), comunicando via message passing (conversation IDs) e compartilhando "living documents" (change-philosophy, problem-space, solution-space). Transforma agente único e sequencial em sistema de desenvolvimento distribuído que itera, testa e debugga autonomamente.

## Como implementar

**Arquitetura de Orquestração:**

```
[Master Coordinator Agent]
├─ Mantém estado global (roadmap, decision log)
├─ Distribui tasks pra 6 sub-agentes
├─ Monitora progresso
└─ Escala para 10+ agentes se necessário

[Sub-Agentes Paralelos (cada um é Claude Code session)]
├── AUTH-Agent (autenticação, JWT, OAuth)
├── API-Agent (endpoints REST, lógica de negócio)
├── UI-Agent (frontend, componentes, estilo)
├── TEST-Agent (testes unitários, integração, E2E)
├── INFRA-Agent (deployment, CI/CD, observabilidade)
└── DOCS-Agent (README, API docs, tutorials)

[Shared State Layer]
├── change-philosophy.md (como pensar sobre mudanças)
├── problem-space.md (o quê está quebrado/ineficiente)
├── solution-space.md (arquitetura proposta)
├── decision-log.json (quem decidiu o quê, quando)
├── arch-diagram.md (visual da arquitetura)
└── progress-tracker.json (% completo por módulo)
```

**Passo 1: Setup e Context Distribution**

Cada agente começa com:

```
System Prompt Base:
"""
Você é um especialista em [AUTH|API|UI|TESTS|INFRA|DOCS].
Seu projeto: [description]

Contexto Global:
{shared_change_philosophy}
{current_arch_diagram}
{decision_log}

Seu Escopo:
- Responsável por: [módulo específico]
- NÃO mexer em: [outros módulos]
- Interface com: [quais agentes]

Se precisar coordenar com outro agente:
1. Descreva o problema no shared problem-space.md
2. Passe Conversation ID pra referência
3. Aguarde resposta do agente responsável

Quando terminar uma task:
1. Commit de código (se aplicável)
2. Update de progress-tracker.json
3. Notificação no shared-log
"""
```

**Passo 2: Change Philosophy (Modo de Pensar Estruturado)**

Criar arquivo `change-philosophy.md`:

```markdown
# Change Philosophy

## Princípio: "Design Fundacional"
Quando fazer mudança X, pergunte:
"Se X fosse requisito desde o início, como eu redesenharia tudo?"

Não: "Como patchear X no sistema atual?"
Sim: "Como X se integra na visão arquitetural?"

## Exemplo:
Se mudar de JWT para OAuth:
- Não: "Adicionar OAuth handler num arquivo novo"
- Sim: "Redesenhar toda auth layer como plugin system onde JWT é 1 provider, OAuth é outro"

## Guideline de Refactor
1. Se > 50% do código toca em mudança, considere refactor
2. Se mudança quebra coesão, redesenhe
3. Manter backward compat quando possível; caso contrário, migration path claro

## Comunicação Inter-Agentes
- AUTH passa token format pra API
- API passes schema changes pra TEST
- TEST reports regressions para todos
- INFRA monitora performance de mudanças
```

**Passo 3: Loop de Desenvolvimento (Dia Típico)**

```
08:00 - Todos agentes acordam
├─ Master: "Hoje vamos implementar [feature X]"
├─ Distribui tasks em Kanban
└─ Cada agente recebe task assignment + context

08:15 - Work in Parallel
├─ AUTH-Agent: Implementa endpoints de auth
├─ API-Agent: Schema de dados + business logic
├─ UI-Agent: Componentes + integração (mock API)
├─ TEST-Agent: Escreve testes (fixture-first approach)
├─ INFRA-Agent: Setup CI/CD pra branch
└─ DOCS-Agent: Escreve docs

09:00 - First Integration Check
├─ TEST-Agent spawns: /loop every 30 minutes: Run full test suite
└─ Reporta failures → problem-space.md

09:30 - Async Problem-Solving
├─ Failure: "API response malformed"
├─ TEST → API: "PUT problem-space.md + Conversation ID"
│  "Expected {id, token}, got {data: [{id, token}]}"
├─ API-Agent: Lê problem-space, identifica issue
├─ API-Agent: Fix schema → code fix → commit
├─ TEST-Agent: Re-run tests → passe
└─ API → TEST: Update decision-log

12:00 - Sub-Agent (Chrome Browser Testing)
├─ TEST-Agent spawns: /loop --chrome: Simulate user clicking buttons
└─ Capture screenshot + session recording

12:30 - Human Testing Fallback
└─ Se erro não pode ser diagnosticado automaticamente:
   "Session ID: abc123def456"
   Human cola no Master Agent:
   "Debugar session abc123def456"
   → Agent acessa logs, trace requests, propõe fix

17:00 - Daily Standup (via Shared Docs)
├─ progress-tracker.json atualizado
├─ decision-log com decisões do dia
├─ Known issues documentados
└─ Tech debt registry (o que vai ficar pra depois)

18:00 - End of Day
└─ Resumo automático: "76% completo, 3 bloqueadores, 0 regressions"
```

**Passo 4: Implementação Técnica (Session Management)**

```python
import subprocess
import json
from datetime import datetime
from pathlib import Path

class MultiAgentOrchestrator:
    def __init__(self, project_root: str):
        self.root = Path(project_root)
        self.agents = {
            "auth": {"color": "red", "session_id": None},
            "api": {"color": "green", "session_id": None},
            "ui": {"color": "blue", "session_id": None},
            "tests": {"color": "yellow", "session_id": None},
            "infra": {"color": "magenta", "session_id": None},
            "docs": {"color": "cyan", "session_id": None}
        }

    def spawn_agent(self, agent_name: str, initial_task: str):
        """Spawn Claude Code session para agente"""
        session_id = self._create_unique_session_id(agent_name)

        cmd = f"""
        claude code \
          --session-name "{agent_name}" \
          --context-file {self.root}/shared/change-philosophy.md \
          --context-file {self.root}/shared/progress-tracker.json \
          --initial-prompt "{initial_task}"
        """

        # Rodar em tmux pane (visual + paralelo)
        tmux_cmd = f"""
        tmux new-window -t dev -n {agent_name} -c {self.root}
        tmux send-keys -t dev:{agent_name} "{cmd}" Enter
        """

        subprocess.run(tmux_cmd, shell=True)
        self.agents[agent_name]["session_id"] = session_id
        print(f"✓ {agent_name} spawned (session: {session_id})")

    def coordinate_between_agents(self, from_agent: str, to_agent: str, message: str):
        """Passar mensagem entre agentes via shared files"""
        problem_space_file = self.root / "shared" / "problem-space.md"

        entry = {
            "timestamp": datetime.now().isoformat(),
            "from": from_agent,
            "to": to_agent,
            "conversation_id": self.agents[from_agent]["session_id"],
            "message": message
        }

        with open(problem_space_file, "a") as f:
            f.write(f"\n\n## [{from_agent}→{to_agent}] {entry['timestamp']}\n")
            f.write(f"Conv ID: {entry['conversation_id']}\n")
            f.write(f"{message}\n")

    def wait_for_all_agents(self, timeout_minutes: int = 480):
        """Aguardar até que todos agentes finalizem"""
        # Poll progress-tracker.json até todos report 100%
        while True:
            tracker = json.load(open(self.root / "shared" / "progress-tracker.json"))
            progress = {agent: tracker[agent].get("percent_complete", 0) for agent in tracker}

            total_progress = sum(progress.values()) / len(progress)
            print(f"Overall progress: {total_progress:.1f}%")

            if total_progress >= 100:
                break

            time.sleep(30)  # Poll a cada 30s

    def auto_debug_failure(self, session_id: str):
        """Se agente falha, Master diagnostica automaticamente"""
        master_prompt = f"""
        Agente falhou. Session ID: {session_id}
        Logs e contexto:
        {self._fetch_session_logs(session_id)}

        Diagnostique:
        1. Qual foi o erro?
        2. Raiz causa?
        3. Solução proposta?
        4. Quem precisa fazer o quê?

        Registre em problem-space.md
        """

        # Master Agent analisa e coordena fix
        pass

# Uso
orchestrator = MultiAgentOrchestrator("/path/to/project")

initial_tasks = {
    "auth": "Implementar JWT auth com refresh tokens",
    "api": "Criar endpoints CRUD de usuários",
    "ui": "Build login form + dashboard",
    "tests": "Write tests para auth flow",
    "infra": "Setup GitHub Actions CI/CD",
    "docs": "Document auth API + setup guide"
}

for agent, task in initial_tasks.items():
    orchestrator.spawn_agent(agent, task)

orchestrator.wait_for_all_agents(timeout_minutes=480)
print("✓ All agents completed!")
```

**Passo 5: Instrumentation para Debug Autônomo**

Adicionar ao app:

```javascript
// Em app index.js / main entry point
// Tecla de atalho para capturar session
window.addEventListener('keydown', (e) => {
  if (e.ctrlKey && e.shiftKey && e.keyCode === 68) { // Ctrl+Shift+D
    captureSessionDebugInfo();
  }
});

function captureSessionDebugInfo() {
  const sessionData = {
    timestamp: new Date().toISOString(),
    url: window.location.href,
    userAgent: navigator.userAgent,
    localStorageState: localStorage,
    consoleErrors: window.__CONSOLE_ERRORS__ || [],
    networkRequests: window.__NETWORK_LOG__ || [],
    componentState: window.__APP_STATE__ || {},
    screenshots: window.__SCREENSHOTS__ || []
  };

  const sessionId = 'DEBUG_' + Date.now();
  localStorage.setItem('DEBUG_SESSION_ID', sessionId);

  // Upload pra backend ou file
  fetch('/api/debug/upload', {
    method: 'POST',
    body: JSON.stringify(sessionData),
    headers: { 'Content-Type': 'application/json' }
  });

  console.log(`Debug session captured: ${sessionId}. Paste to Agent.`);
  return sessionId;
}
```

Agent recebe:

```
User: "Debug session DEBUG_1712145600"

Master Agent:
→ Fetch session data
→ Analyze logs + network requests
→ Identify stack trace
→ Propose fix
→ Coordinate com API-Agent: "Fix endpoint /api/users (500 error)"
→ TEST-Agent: "Verify fix with session replay"
```

## Stack e requisitos

**Infraestrutura:**
- Claude Code (IDE web ou CLI)
- tmux ou screen (multiplexing de sessões)
- Git (versionamento código + branching por agente)
- Shared filesystem (acesso a change-philosophy.md, problem-space.md)

**Habilidades:**
- Prompt engineering (estruturar system prompts pra cada agente)
- Arquitetura de software (desenhar contratos entre módulos)
- Versionamento e merge strategies

**Custo:**
- Claude API usage (6+ sessões paralelas rodando, ~$50-200/dia dependendo volume)

## Armadilhas e limitações

**Coordination Overhead:** Se agentes não conseguem comunicar bem, degenera em chaos. **Mitigação:**
- change-philosophy.md muito clara (não ambígua)
- problem-space.md atualizado em tempo real
- Definir "interface contracts" entre agentes (o quê cada módulo expõe/espera)

**Context Explosion:** Cada agente recebe ~50KB de contexto. Com 6 agentes, é 300KB de leitura repetida. **Mitigação:**
- Comprimir contexto (sumarizar docs longos)
- Usar referências em vez de copiar ("see shared/auth-spec.md" vs. copiar inteiro)

**Debugging Falhas Correlacionadas:** Se auth-agent e api-agent ambos erram, qual é o culpado? **Mitigação:**
- Testes de integração rodando continuamente (TEST-Agent)
- Session recording sempre disponível pra replay

**Explosão de Mudanças:** Se todos agentes commitam simultaneamente, merge conflicts. **Mitigação:**
- Usar feature branches isolados
- Cada agente responsável por seu próprio namespace (auth/* , api/*, etc.)
- Master coordena merge strategy (squash vs. rebase)

## Conexões

- [[agentes-autonomos-multi-agente]] - padrões de coordenação
- [[orquestracao-multi-agente-com-llms]] - aplicação específica com Claude Code
- [[prompt-engineering-agentes]] - estruturação de system prompts

## Histórico
- 2026-04-02: Nota criada
- 2026-04-02: Nota reescrita e enriquecida pelo pipeline de curadoria
