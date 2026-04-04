---
date: 2026-03-28
tags: [claude-code, workflow, comunicacao, multitasking, produtividade]
source: https://x.com/techNmak/status/2037788648691884207
author: "@techNmak"
tipo: aplicacao
---

# Usar /btw para Conversa Paralela com Claude Trabalhando

## O que é
Comando `/btw` (by the way) no Claude Code que permite manter conversa lateral enquanto agente executa tarefa de fundo, sem bloquear execução principal. Sincroniza ritmos humano (ms) e computacional (s), eliminando ineficiência de espera sequencial.

## Como implementar
**1. Entender a mudança de paradigma**:

```
Sequencial (sem /btw):
User: "Build API"
Claude: [Roda, toma 5 minutos]
User esperando...
Claude termina.
User: "By the way, teste também?"

Paralelo (com /btw):
User: "Build API"
Claude: [Roda 30s]
User usa /btw: "By the way, teste também?"
Claude: Responde rápido, volta pro build
Claude continua [Roda mais 4min30s]
User não perdeu tempo de espera.
```

**2. Mecânica técnica**:

```python
class ClaudeCodeWithBTW:
    def __init__(self):
        self.main_task_thread = None
        self.message_queue = Queue()

    def start_main_task(self, task: str):
        """Inicia tarefa principal em thread."""
        self.main_task_thread = Thread(
            target=self._execute_main_loop,
            args=(task,),
            daemon=False
        )
        self.main_task_thread.start()

    def btw_message(self, message: str) -> str:
        """Envia mensagem /btw sem bloquear main loop."""
        # Processar message em context separado, rápido
        response = self._quick_response(message)

        # Não interrompe main task
        # Apenas responde e retorna

        return response

    def _execute_main_loop(self, task: str):
        """Loop principal da tarefa (pode levar minutos)."""
        # Executa tarefa ...
        # A qualquer momento, /btw pode ser injetado
        # Sem prejudicar progresso de main_task
        pass

    def _quick_response(self, message: str) -> str:
        """Responde /btw rapidamente sem contexto full."""
        # Processa pergunta rápida
        # Usa apenas estado compartilhado, não contexto da main task
        return "Quick response"
```

**3. Casos de uso práticos**:

```python
class BTWUseCases:
    def debugging_while_working(self):
        """Debug de build enquanto Claude trabalha."""
        # Claude Code está: compilando projeto (2 min)

        # User vê erro no console
        # /btw "Why is module X failing?"

        # Claude responde em 2-3 segundos
        # Volta à compilação

    def planning_next_phase(self):
        """Planejar próxima fase enquanto current roda."""
        # Claude Code está: escrevendo testes (1 min)

        # /btw "Após testes, qual é a ordem de features seguinte?"

        # Claude responde com sugestões
        # Continua testes

    def gathering_context(self):
        """Coletar informações para iterar melhor."""
        # Claude Code está: refatorando código (3 min)

        # /btw "Qual é nosso padrão de error handling?"

        # Claude responde baseado em CLAUDE.md
        # User aproveita essa info depois

    def course_correction(self):
        """Corrigir direção sem esperar término."""
        # Claude Code está: implementar feature A (5 min)

        # /btw "Na verdade, priorize feature B primeiro"

        # Claude reconsidera, pode pivotar plano
        # Ou aceita e continua (depende da situação)
```

**4. Diferença com `/loop`**:

```
/loop: Tarefa repetida automaticamente (cron-like)
       "Execute testes a cada 5 min por 1 hora"

/btw:  Conversa lateral durante tarefa ativa
       "Enquanto testes rodam, dúvida: como fazer X?"

Combinados:
User: /loop "run tests every 5 min"
     [Tests iniciam em background]
User: /btw "Como otimizo esse query?"
     [Resposta rápida, sem interromper testes]
```

**5. Implementação real em Claude Code**:

```markdown
# Workflow com /btw

## Session 1: Build fase

```
/plan "Construir API REST completa com autenticação"
→ Claude cria plano estruturado

[Claude começa implementação - 5 min de trabalho]
```

## Mid-session: Pergunta rápida via /btw

```
/btw "qual é a melhor forma de hashar senhas? bcrypt ou argon2?"
→ Resposta em ~3s

Claude continua a implementação que já está em progresso
```

## Session 2: Testes

```
[Claude roda testes - 2 min]

/btw "quantos testes passaram até agora?"
→ "3 de 5. Erro em auth_test.py linha 45"

User lê erro, aproveita tempo
Claude continua testes
```

## Session 3: Review

```
[Claude refatora - 3 min]

/btw "você tem feito refactoring incremental ou vai fazer 1x no final?"
→ "Incremental. Cada função é testada após refactor."

User entende estratégia
Claude continua
```
```

**6. Benefícios mensuráveis**:

```python
def measure_btw_efficiency():
    """Quantifica ganho de /btw."""

    # Sem /btw:
    time_waiting = 15 * 60  # 15 min esperando Claude terminar
    time_thinking = 5 * 60  # 5 min pensando enquanto espera
    total_wall_time = 20 * 60  # 20 min total

    # Com /btw:
    time_claude_working = 15 * 60  # Claude roda 15 min
    time_user_thinking = 10 * 60   # User pensa DURANTE execução, não depois
    questions_asked = 3  # 3 /btw queries rápidas

    # Resultado:
    wall_time_saved = 5 * 60  # ~5 min economizado
    cognitive_flow_improvement = "Contínuo, sem quebras"  # Qualitativo

    return {
        "wall_time_saved_sec": wall_time_saved,
        "questions_answered_during": questions_asked,
        "context_continuity": "Mantida"
    }
```

## Stack e requisitos
- **Claude Code**: versão que suporta `/btw` (já nativa)
- **Console**: acesso simultâneo para visualizar ambos fluxos
- **Disciplina**: decidir quando usar /btw vs deixar Claude terminar

## Armadilhas e limitações
- **Distrações**: /btw pode quebrar foco if overused
- **Context mixing**: se /btw questão for muito complexa, tira tempo do main task
- **Timing**: /btw melhor durante tarefas longas (>1min), não útil para ciclos rápidos
- **Limite**: Claude não pode fazer /btw queries se já no máximo de contexto

## Conexões
[[Claude Code - Melhores Práticas]], [[Plan Mode Claude]], [[Loop Agenda Tarefas]], [[Multitasking com Agentes]]

## Histórico
- 2026-03-28: Nota criada
- 2026-04-02: Reescrita em padrão aplicacao
