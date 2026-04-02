---
tags: []
source: https://x.com/om_patel5/status/2039165508910813264?s=20
date: 2026-04-02
---
# Ancoragem de Janela de Uso em APIs

## Resumo
Serviços com janelas de uso baseadas em tempo podem ser manipulados ao ancorar o início da janela em um horário estratégico, antes do expediente real, maximizando a disponibilidade durante as horas produtivas.

## Explicação
O Claude (Anthropic) nos planos pagos (Pro, Max 5x, Max 20x) implementa um sistema de rate limiting baseado em janelas deslizantes de 5 horas. A janela é fixada ao horário da primeira mensagem enviada, truncada para a hora cheia (floor). Isso significa que o ponto de ancoragem é controlável pelo usuário — não é fixo nem determinístico a partir do momento exato do envio, mas sim do início da hora em que ocorreu.

O hack explorado aqui é simples: ao enviar uma mensagem trivial ("hi") usando um modelo barato como Haiku às 6h da manhã, a janela 6h–11h é estabelecida. Quando o usuário começa a trabalhar de verdade às 8h30 e esgota o limite por volta das 11h, uma nova janela já está disponível — em vez de esperar até as 13h como aconteceria se a primeira mensagem tivesse sido enviada às 8h.

A automação desse comportamento via GitHub Actions (cron job diário) ou via tarefas agendadas nativas do próprio Claude torna o processo completamente transparente. O token OAuth do usuário é usado para autenticar a requisição automatizada, sem intervenção manual. Isso transforma um comportamento intencional e repetível em infraestrutura passiva de produtividade.

Do ponto de vista técnico, isso é um exemplo de **exploração de implementação de rate limiting por janela fixa ancorada em evento**, distinto de algoritmos como token bucket ou sliding window contínuo. Janelas fixas ancoradas têm essa vulnerabilidade intrínseca: o ponto de início pode ser deslocado por quem controla o primeiro evento.

## Exemplos
1. **GitHub Actions cron job**: configurar um workflow que roda às 6h00 diariamente, autentica com OAuth token do Claude e envia uma mensagem com Haiku para ancorar a janela.
2. **Tarefas agendadas nativas do Claude**: usar o recurso interno de scheduled tasks do próprio Claude para disparar a mensagem âncora automaticamente sem infraestrutura externa.
3. **Generalização para outras APIs**: qualquer API que use janelas fixas baseadas no primeiro evento (ex.: alguns sistemas de quota diária) pode ser manipulada da mesma forma, deslocando o primeiro uso para fora do pico de trabalho.

## Relacionado
*(Nenhuma nota relacionada disponível no vault no momento.)*

## Perguntas de Revisão
1. Qual é a diferença entre rate limiting por janela fixa ancorada em evento e sliding window contínuo, e por que o primeiro é vulnerável a esse tipo de manipulação?
2. Em quais outros contextos (além de APIs de LLM) o conceito de ancoragem de janela de uso poderia ser explorado para otimizar disponibilidade?

## Histórico de Atualizações
- 2026-04-02: Nota criada a partir de Telegram