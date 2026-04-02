---
tags: [claude, produtividade, rate-limit, automacao, llm]
source: https://x.com/om_patel5/status/2039165508910813264?s=20
date: 2026-04-01
---
# Ancorar a janela de uso do Claude Code cedo evita dead time por rate limit

## Resumo
O Claude Code usa uma janela deslizante de 5 horas que começa no momento do primeiro uso (arredondado para a hora cheia). Enviar uma mensagem barata antes do horário de trabalho real desloca essa janela e evita o bloqueio no meio do expediente.

## Explicação
O Claude Code (planos Pro, Max 5x e Max 20x) aplica rate limit com base em uma **janela de 5 horas** que é ancorada à hora cheia do primeiro uso do dia. Se o primeiro uso ocorre às 8h, a janela vai de 8h às 13h — e quem trabalha intensamente pode esgotar o limite por volta das 11h, ficando bloqueado por até 2 horas no meio do expediente.

O truque explora o mecanismo de ancoragem: ao enviar uma mensagem trivial (ex.: "hi") via modelo barato como Claude Haiku às 6h, a janela é fixada em 6h–11h. Quando o usuário começa a trabalhar de verdade às 8h–8h30, já está no meio de uma janela que se renova às 11h — exatamente quando o trabalho pesado começa. O resultado é que às 11h, em vez de bloqueio, há uma janela nova disponível.

A automação recomendada usa um **GitHub Actions cron job** que envia esse "ping" matinal automaticamente, exigindo apenas o OAuth token do usuário. Alternativamente, as **scheduled tasks nativas do Claude** podem fazer o mesmo sem infra externa. O custo da mensagem via Haiku é negligenciável comparado ao benefício de 2 horas recuperadas.

Este conceito é relevante para qualquer fluxo de trabalho que depende de LLMs com cotas por janela de tempo: entender *quando* a janela começa é tão importante quanto *quanto* se consome dentro dela.

## Exemplos
1. **GitHub Actions cron**: configurar um workflow com `cron: '0 6 * * 1-5'` que envia "hi" via API usando Claude Haiku, ancorando a janela às 6h em dias úteis.
2. **Claude Scheduled Tasks**: criar uma tarefa recorrente diária às 6h com instrução mínima, usando o próprio ecosistema Claude sem código externo.
3. **Script local com cron do sistema**: um simples `curl` para a API do Claude agendado via `crontab -e` no macOS/Linux, disparado antes do início do expediente.

## Relacionado
*(Nenhuma nota relacionada disponível no vault no momento.)*

## Perguntas de Revisão
1. Por que usar o modelo Haiku especificamente para a mensagem de ancoragem, e não o Sonnet ou Opus?
2. O que acontece se o cron job falhar em um dia — a janela volta ao comportamento padrão ou existe algum fallback?

## Histórico de Atualizações
- 2026-04-01: Nota criada a partir de Telegram