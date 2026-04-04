---
date: 2026-03-24
tags: [claude, rate-limits, otimizacao, api, automacao]
source: https://x.com/aaronjmars/status/2036230574822580675?s=20
autor: "@aaronjmars"
tipo: aplicacao
---

# Automatizar Uso de Rate Limits Claude Pro/Max em Janelas de 5 Horas

## O que é

Sistema que monitora a janela deslizante de 5 horas dos rate limits do Claude Pro/Max e dispara automaticamente tarefas agendadas quando faltam 30 minutos, garantindo uso de 100% da cota antes da reset. Implementado no projeto Aeon.

## Como implementar

### Fase 1: Setup Inicial

Clone e configure o projeto Aeon:

```bash
git clone https://github.com/aaronjmars/aeon.git
cd aeon
pip install -r requirements.txt

# Configure credenciais
cp .env.example .env
# Edite .env com:
ANTHROPIC_API_KEY=your_key
SLACK_WEBHOOK_URL=optional_webhook  # para notificações
```

### Fase 2: Entender Rate Limits do Claude

O Claude Pro/Max opera com **janelas deslizantes de 5 horas**, não límites diários ou mensais.

```
Exemplo de comportamento:

10:00 - Você começa a usar Claude (limite de 5h começa)
11:00 - Você usou 30% da cota na última hora
12:00 - Você usou 50% no total
14:00 - Faltam 60 minutos na janela (4 horas já passaram)
14:30 - ⚠️ GATILHO: Faltam 30 min. Dispara tarefas agendadas.
14:45 - Tarefas rodando, consumindo os últimos 25% da cota
15:00 - Janela reseta. Nova janela de 5 horas começa.
```

### Fase 3: Configurar Monitoramento de Uso

Criar script que consulta API de uso:

```python
# monitor_rate_limit.py
import os
import time
from anthropic import Anthropic
from datetime import datetime, timedelta

client = Anthropic()

def check_rate_limit_status():
    """Retorna % de uso e tempo restante na janela"""
    # Nota: Anthropic fornece endpoint de usage; veja documentação
    # Aqui é um exemplo de como estruturar a lógica

    # Você pode também usar monitoring via headers da response
    # client.messages.create() retorna headers com rate limit info

    response = client.messages.create(
        model="claude-opus-4-1",
        max_tokens=10,
        messages=[{
            "role": "user",
            "content": "test"
        }]
    )

    # Headers indicam:
    # x-ratelimit-limit-requests: limite de requests
    # x-ratelimit-limit-tokens: limite de tokens
    # x-ratelimit-remaining-requests: restante de requests
    # x-ratelimit-remaining-tokens: restante de tokens
    # x-ratelimit-reset-requests: quando reseta em segundos
    # x-ratelimit-reset-tokens: quando reseta em segundos

    headers = response.response.headers  # Verificar sintaxe exata
    tokens_remaining = headers.get('x-ratelimit-remaining-tokens')
    reset_at = headers.get('x-ratelimit-reset-tokens')

    return {
        "tokens_remaining": int(tokens_remaining),
        "reset_in_seconds": int(reset_at),
        "percent_used": (1 - int(tokens_remaining) / 1000000) * 100  # ajustar limite real
    }

def should_trigger_tasks(status):
    """Retorna True se deve disparar tarefas (menos de 30min restantes)"""
    reset_in_minutes = status["reset_in_seconds"] / 60
    return reset_in_minutes < 30

status = check_rate_limit_status()
print(f"Cota usada: {status['percent_used']:.1f}%")
print(f"Reset em: {status['reset_in_seconds']} segundos")
```

### Fase 4: Criar Fila de Tarefas

Defina tarefas que aguardam execução:

```yaml
# tasks.yaml
tasks:
  - name: "fix-prs"
    description: "Review e fix PRs pendentes"
    skill: "pr_reviewer"
    priority: 1
    max_tokens: 50000

  - name: "refactor-codebase"
    description: "Refactor modules marcados"
    skill: "code_refactorer"
    priority: 2
    max_tokens: 100000

  - name: "write-documentation"
    description: "Documentar funções não-documentadas"
    skill: "doc_writer"
    priority: 3
    max_tokens: 30000

  - name: "research-libraries"
    description: "Investigar biblioteca X para alternativas"
    skill: "research"
    priority: 4
    max_tokens: 40000

  - name: "code-quality-audit"
    description: "Auditoria de qualidade em projeto Y"
    skill: "quality_checker"
    priority: 5
    max_tokens: 80000
```

### Fase 5: Implementar Dispatcher Automático

```python
# dispatcher.py
import yaml
from monitor_rate_limit import check_rate_limit_status, should_trigger_tasks
import subprocess
import time

def load_tasks():
    with open("tasks.yaml") as f:
        return yaml.safe_load(f)["tasks"]

def run_task(task):
    """Executa uma skill/tarefa"""
    print(f"[{task['name']}] Iniciando...")

    # Executar via Claude Code ou script direto
    result = subprocess.run(
        ["claude", "run", task["skill"], f"--max-tokens={task['max_tokens']}"],
        capture_output=True,
        text=True
    )

    print(f"[{task['name']}] Completo")
    return result.returncode == 0

def main():
    tasks = load_tasks()
    tasks_sorted = sorted(tasks, key=lambda x: x["priority"])

    while True:
        status = check_rate_limit_status()

        if should_trigger_tasks(status):
            print(f"⚠️  GATILHO: {status['reset_in_seconds']/60:.0f}min restantes!")
            print("Disparando tarefas agendadas...")

            for task in tasks_sorted:
                if status["percent_used"] < 95:  # Reserve margem
                    success = run_task(task)
                    if not success:
                        print(f"Falha em {task['name']}, continuando...")
                else:
                    print(f"Atingido 95% de uso, parando para segurança")
                    break

            print("Ciclo de tarefas completado")

        # Verificar a cada 5 minutos
        time.sleep(300)

if __name__ == "__main__":
    main()
```

### Fase 6: Agendamento via Cron ou Systemd

```bash
# Cron: rodar a cada minuto
* * * * * cd /path/to/aeon && python dispatcher.py >> dispatcher.log 2>&1

# Ou via systemd service (melhor prática)
# Crie /etc/systemd/system/aeon-dispatcher.service:

[Unit]
Description=Aeon Rate Limit Dispatcher for Claude
After=network.target

[Service]
Type=simple
User=your_user
ExecStart=/usr/bin/python3 /path/to/aeon/dispatcher.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

### Fase 7: Notificações (Slack)

```python
# Adicione ao dispatcher.py
import requests

def notify_slack(message):
    webhook_url = os.getenv("SLACK_WEBHOOK_URL")
    if not webhook_url:
        return

    requests.post(webhook_url, json={
        "text": message,
        "blocks": [{
            "type": "section",
            "text": {"type": "mrkdwn", "text": message}
        }]
    })

# Usar:
notify_slack("⚠️  Gatilho de rate limit! Disparando 5 tarefas...")
```

## Stack e requisitos

- **Python 3.9+**
- **anthropic**: `pip install anthropic`
- **pyyaml**: `pip install pyyaml`
- **requests**: `pip install requests` (para notificações Slack)
- **Subscription**: Claude Pro ou Max (necessário para rate limits altos)
- **API Key**: Anthropic API Key com permissões de uso
- **Custo**: zero (usa cota já adquirida)

## Armadilhas e limitações

1. **Rate limits mudam**: Anthropic pode ajustar limites sem aviso. Monitore headers da API constantemente.

2. **Overshooting**: Tarefas podem ser muito grandes e exceder janela. Implemente checkpoints e resumição.

3. **Falhas de task**: Se uma skill falha no meio, tokens já foram consumidos. Adicione idempotência (tarefas podem reexecutar).

4. **Notificações barulhentas**: Sistema pode disparar múltiplos alertas. Implemente deduplicação.

5. **Custo não-óbvio**: Apesar de ser "automático", cada token custa. Não deixe sistema rodando com tarefas infinitas.

## Conexões

- [[Maestri Orquestrador Agentes IA Canvas 2D]] — coordenação visual de múltiplas tarefas
- [[Claude Code - Melhores Práticas]] — otimização de prompts para economizar tokens
- [[otimizacao-de-tokens-em-llms]] — técnicas de token compression

## Histórico

- 2026-03-24: Conceito original de Aaron Mars
- 2026-04-02: Guia de implementação com Aeon

Vantagens incluem: nenhuma cota desperdiçada, uso de 100% do que você paga, completamente automático sem intervenção manual, flexibilidade para configurar quaisquer skills (correção de código, research, documentação, refatoração, testes, qualquer tarefa que aceite automação), sem custo extra (usa apenas cota já adquirida, nenhuma API adicional, nenhuma cobrança extra).

Em vez de ver rate limits como limitação, tornam-se: oportunidade de planejamento, janela previsível de oportunidade, gatilho para automação inteligente.

## Exemplos

Stack técnico necessário: Claude Code com API key ativo, projeto Aeon (ou reimplementação), skills configuradas para tarefas desejadas, agendamento do monitoramento.

Monitoramento programático: Polling `GET /api/oauth/usage` → Parse JSON → Verificar threshold → Executar lógica.

Casos de uso em desenvolvimento: revisar e corrigir automaticamente PRs quando há tempo disponível, refatorar código em background, melhorar documentação. Em pesquisa: executar análises extensas de código, fazer research de bibliotecas e dependências, gerar relatórios. Em manutenção: update dependencies, security audits, code quality improvements.

## Relacionado

- [[Maestri Orquestrador Agentes IA Canvas 2D]]
- [[Claude Code Subconscious Letta Memory Layer]]
- [[Claude Code - Melhores Práticas]]
- [[450_skills_workflows_claude]]

## Perguntas de Revisão

1. Como janelas deslizantes de 5 horas mudam estratégia de otimização comparado a limites mensais?
2. Por que automação de rate limits é mais eficiente que gerenciamento manual?
3. Qual é o synergy entre múltiplos agentes coordenados e maximização de rate limits?
