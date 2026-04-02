---
tags: [segurança, backend, webdev, boas-práticas, vibe-coding]
source: https://x.com/Hartdrawss/status/2035378419278532928?s=20
date: 2026-04-02
---
# Falhas Críticas em Apps Vibe Coded

## Resumo
Aplicações geradas com auxílio de IA ("vibe coded") frequentemente omitem camadas essenciais de segurança, performance e resiliência que desenvolvedores experientes aplicam por padrão. Essas lacunas transformam um MVP funcional em um sistema vulnerável e inescalável.

## Explicação
"Vibe coding" é o processo de construir aplicações inteiras guiado por LLMs, aceitando o código gerado com pouca revisão crítica. O resultado costuma ser um app que *funciona* em condições ideais, mas falha sistematicamente em cenários reais: picos de tráfego, usuários maliciosos, falhas de infraestrutura e crescimento de dados.

As falhas se agrupam em três categorias principais. **Segurança**: tokens de autenticação em localStorage (vulneráveis a XSS), chaves de API hardcoded no frontend, ausência de sanitização de inputs (SQL injection), falta de verificação de assinatura em webhooks, rotas de admin sem checagem de roles e sessões que nunca expiram. Cada um desses erros representa um vetor de ataque direto e exploitável. **Performance e escalabilidade**: sem paginação de queries, sem connection pooling no banco, sem indexação em campos consultados e imagens servidas direto do servidor sem CDN — o sistema colapsa na primeira onda real de usuários. **Observabilidade e resiliência**: sem logging em produção, sem health checks, sem estratégia de backup, sem validação de variáveis de ambiente e sem error boundaries na UI — quando algo quebra, o desenvolvedor não sabe onde, quando, nem como.

O ponto mais relevante é que IAs generativas produzem código *confidentemente incorreto* — sintaxe válida, lógica plausível, mas sem consciência de contexto de produção. TypeScript não resolve isso sozinho, mas força a superfície de erros a ser menor e mais visível. Rate limiting, CORS bem configurado e emails assíncronos são exemplos de decisões que exigem conhecimento arquitetural que o modelo não infere automaticamente do prompt.

A lista funciona como um checklist de hardening pré-lançamento: cada item é um vetor de falha independente, mas em conjunto descrevem o gap entre "código que roda no localhost" e "sistema que aguenta produção".

## Exemplos
1. **Stripe webhook sem verificação de assinatura**: um atacante envia um POST falso simulando pagamento aprovado e obtém acesso pago sem pagar — corrigido verificando `stripe.webhooks.constructEvent()` com o `STRIPE_WEBHOOK_SECRET`.
2. **Sem rate limiting na rota `/api/send-email`**: um bot dispara 10.000 requisições em minutos, gerando cobrança massiva no provedor de email e potencial blacklist do domínio — corrigido com middleware como `express-rate-limit` ou equivalente na edge.
3. **Query sem paginação em tabela de usuários**: `SELECT * FROM users` funciona com 500 registros, trava o servidor com 50.000 — corrigido com `LIMIT/OFFSET` ou cursor-based pagination desde o início.

## Relacionado
*(Nenhuma nota relacionada disponível no vault no momento.)*

## Perguntas de Revisão
1. Quais das 20 falhas listadas representam riscos de **segurança imediata** versus riscos de **degradação de performance gradual**? Como essa distinção muda a prioridade de correção?
2. Por que código gerado por IA tende a omitir sistematicamente as camadas de segurança e resiliência, mesmo quando o prompt não pede explicitamente para simplificar?

## Histórico de Atualizações
- 2026-04-02: Nota criada a partir de Telegram