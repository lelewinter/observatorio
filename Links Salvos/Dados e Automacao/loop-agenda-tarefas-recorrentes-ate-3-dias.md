---
date: 2026-03-28
tags: [claude-code, automacao, tarefas, agendamento, workflow, loop-scheduling]
source: https://x.com/techNmak/status/2037788648691884207
autor: "@techNmak"
tipo: aplicacao
---
# Agendamento Autônomo de Tarefas Recorrentes: /loop + Padrão Temporal até 3 Dias

## O que é
Comando `/loop` no Claude Code que permite descrever tarefa em linguagem natural + padrão de recorrência (a cada X minutos/horas), e a executa automaticamente até 3 dias seguidos sem intervenção humana. Transforma "lembrar de rodar teste manualmente cada 30min por 72h" em "descrever o padrão uma vez, Claude faz".

## Como implementar

**Sintaxe Básica:**

```
/loop [PADRÃO_TEMPORAL] [DESCRIÇÃO_TAREFA]

Exemplos:
/loop every 30 minutes: Run test suite and report failures
/loop every 2 hours: Check API health endpoints and alert if down
/loop daily at 9am: Generate report and email to team
/loop every 15 minutes for 3 days: Monitor queue depth and auto-scale workers
```

**Padrões Suportados:**

- `every X minutes` (X = 5, 10, 15, 30, 60)
- `every X hours` (X = 1, 2, 4, 8, 12, 24)
- `daily at HH:mm`
- `every weekday`
- `custom cron: <expression>`

**Fluxo Interno de Execução:**

```
Usuário descreve /loop
  ↓
Claude interpreta tarefa + padrão
  ↓
Cria "loop session" com duração máx 3 dias
  ↓
A cada intervalo X:
  - Executa tarefa (código, script, query, etc.)
  - Captura output
  - Avalia sucesso/falha
  - Se falha: gera diagnóstico automático
  - Se sucesso: registra resultado
  ↓
Após 3 dias ou conclusão:
  - Resume final com estatísticas
  - Opção de continuar, modificar ou parar
```

**Exemplo 1: Teste Repetido (30min por 72h)**

```
/loop every 30 minutes:
Run pytest tests/ -v
Report any failures with stack trace
If > 50% tests fail, investigate root cause and fix
```

Claude vai:
1. Executar `pytest tests/` a cada 30min
2. Parsear output (passou/falhou)
3. Se > 50% falham: usar ferramentas (code search, git log) pra investigar
4. Sugerir/aplicar fix automaticamente
5. Rerun tests pra validar

**Exemplo 2: Monitoramento de Sistema (15min por 72h)**

```
/loop every 15 minutes:
Check API health: curl http://api.example.com/health
If status != 200: Trigger auto-recovery script
Log latency percentiles (p50, p95, p99)
Alert if p99 > 500ms
```

Claude vai:
1. HTTP GET ao endpoint
2. Parse JSON response
3. Se error: SSH → run recovery script
4. Calcular latências
5. Enviar alertas (Slack/email) se threshold violado

**Exemplo 3: Data Pipeline Recorrente (2 horas por 72h)**

```
/loop every 2 hours:
Run dbt run --select models/daily_reports
Test data quality (null checks, uniqueness)
Load results to Redshift
Email stakeholders with summary
```

Claude vai:
1. Executar dbt (modelos de transformação de dados)
2. Rodar testes (validar dados)
3. Fazer INSERT/MERGE em warehouse
4. Enviar email formatado com estatísticas

**Implementação Técnica (PT que Claude Interpreta):**

```python
# Pseudocódigo do que Claude faz internamente

import asyncio
from datetime import datetime, timedelta
from dateutil import parser as date_parser

class LoopScheduler:
    def __init__(self, interval_str: str, task_description: str, max_duration_hours: int = 72):
        self.interval = self.parse_interval(interval_str)  # "every 30 minutes" → 30*60 sec
        self.task_desc = task_description
        self.max_duration = timedelta(hours=max_duration_hours)
        self.start_time = datetime.now()
        self.execution_log = []

    def parse_interval(self, interval_str: str) -> int:
        """Converter descrição pra segundos"""
        if "every" in interval_str and "minutes" in interval_str:
            mins = int(interval_str.split()[1])
            return mins * 60
        elif "every" in interval_str and "hours" in interval_str:
            hours = int(interval_str.split()[1])
            return hours * 3600
        # ... outros patterns

    async def run_loop(self):
        """Loop principal"""
        iteration = 0
        while True:
            elapsed = datetime.now() - self.start_time

            if elapsed > self.max_duration:
                print(f"Loop completado após 3 dias. Total de {iteration} execuções.")
                break

            iteration += 1
            print(f"[Iteração {iteration}] Executando: {self.task_desc}")

            try:
                # Executar tarefa (Claude interpreta e executa)
                result = await self.execute_task(self.task_desc)
                self.execution_log.append({
                    "iteration": iteration,
                    "timestamp": datetime.now().isoformat(),
                    "status": "success",
                    "result": result
                })
            except Exception as e:
                self.execution_log.append({
                    "iteration": iteration,
                    "timestamp": datetime.now().isoformat(),
                    "status": "error",
                    "error": str(e),
                    "diagnosis": await self.auto_diagnose(e, self.task_desc)
                })

            # Aguardar próxima execução
            await asyncio.sleep(self.interval)

    async def execute_task(self, task_desc: str):
        """Claude executa tarefa descrita em linguagem natural"""
        # Pseudocódigo: Claude interpreta task_desc e escolhe ação
        # Ex: "Run pytest" → subprocess.run("pytest")
        # Ex: "Check API health" → HTTP GET + parse
        # Ex: "Load to Redshift" → SQL INSERT
        pass

    async def auto_diagnose(self, error: Exception, context: str):
        """Se falha, Claude investigar raiz causa"""
        # Pseudocódigo
        # 1. Procurar logs recentes
        # 2. Analisar mudanças recentes (git log)
        # 3. Testar isoladamente cada componente
        # 4. Sugerir/aplicar fix
        pass

    def get_summary(self):
        """Retorna resumo após conclusão"""
        total_runs = len(self.execution_log)
        successes = sum(1 for log in self.execution_log if log["status"] == "success")
        failures = total_runs - successes
        success_rate = (successes / total_runs * 100) if total_runs > 0 else 0

        return {
            "total_executions": total_runs,
            "successes": successes,
            "failures": failures,
            "success_rate": success_rate,
            "duration": datetime.now() - self.start_time,
            "execution_log": self.execution_log
        }
```

**Interface do Usuário (Claude Code):**

```
User: /loop every 30 minutes:
Run all tests, fix failures automatically, report status

Claude:
✓ Loop iniciado
  Interval: 30 minutos
  Duração máxima: 72 horas
  Tarefa: [test suite + auto-fix + report]

[Loop rodando...]

Iteração 1 [00:00]: ✓ 156/156 testes passando
Iteração 2 [00:30]: ✓ 156/156 testes passando
Iteração 3 [01:00]: ✗ 4/156 testes falhando
  → Investigando...
  → Encontrado: bug em models/customer_segmentation.py linha 23
  → Aplicando fix automático
  → Rerodando testes... ✓ Corrigido!
Iteração 4 [01:30]: ✓ 156/156 testes passando
...

[Após 72h]
✓ Loop completado
  Total de 144 iterações
  Taxa de sucesso: 98.6% (143/144)
  Tempo total: 72h

  Falhas investigadas: 1
  Fixes automáticos aplicados: 1
  Manual interventions needed: 0

  Próximas ações:
  /continue (roda mais 3 dias)
  /modify (alterar padrão/tarefa)
  /stop (encerrar)
```

## Stack e requisitos

**Ambiente:**
- Claude Code (web IDE com acesso a shell, git, databases)
- Acesso a stdin/stdout de processos
- Integração com ferramentas: pytest, dbt, git, SSH, HTTP clients, email

**Limitações técnicas:**
- Máximo 3 dias de execução contínua (by design)
- Não suporta muito alto volume (ex: milhões de eventos/min; use streaming em vez)
- Requer tarefas bem-definidas (ambigüidade = timeout)
- Human-in-the-loop necessário pra decisões críticas (ex: "delete prod data")

**Custo:**
- Claude Code = subscriçao (parte do plano)
- Recursos consumidos (CPU, API calls) = billing normal

## Armadilhas e limitações

**Limite de 3 Dias:** Se necessário monitoramento > 3 dias, precisa:
- Chamar `/loop` novamente (será uma "nova sessão")
- Ou usar scheduled task no OS (cron, Windows Task Scheduler) em vez

**Ambigüidade de Tarefa:** Se descrição é vaga, Claude pode interpretar errado. **Mitigação:**
- Ser específico: "Run pytest with -v flag, report failures with stack trace" (não "run tests")
- Incluir formatos esperados: "Output JSON com campos: timestamp, success, message"

**Falta de Contexto Histórico Between Loops:** Cada `/loop` é sessão independente. Se loop 1 faz descoberta importante, loop 2 (próximas 3 dias) não sabe. **Mitigação:**
- Escrever findings em arquivo/DB acessível entre loops
- Passar histórico explicitamente no prompt de `/loop` seguinte

**Gestão de Estado:** Tarefas que precisam manter estado (ex: "processar apenas pedidos novos desde última execução") requerem coordination. **Mitigação:**
- Armazenar "last processed timestamp" em arquivo/DB
- Fazer query com `WHERE created_at > last_checkpoint`

**Timeouts:** Se tarefa leva > X segundos em alguma iteração, timeout pode ativar. **Mitigação:**
- Testar tarefa manualmente primeiro pra medir tempo
- Aumentar timeout se legítimo (ex: query grande)
- Quebrar em sub-tarefas paralelas

## Conexões

- [[orquestracao-multi-agente-com-llms]] - escalabilidade com múltiplos loops paralelos
- [[deteccao-mudanca-anomalia]] - usar loop pra monitoramento contínuo
- [[monitoramento-distribuido-inteligencia]] - padrão análogo com 27 feeds

## Histórico
- 2026-03-28: Nota criada
- 2026-04-02: Nota reescrita e enriquecida pelo pipeline de curadoria
