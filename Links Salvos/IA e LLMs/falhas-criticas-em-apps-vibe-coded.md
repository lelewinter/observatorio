---
tags: [segurança, backend, webdev, boas-práticas, vibe-coding]
source: https://x.com/Hartdrawss/status/2035378419278532928?s=20
date: 2026-04-02
tipo: aplicacao
---
# 20 Falhas Críticas em Apps Vibe Coded: Segurança até Observabilidade

## O que e
Aplicações geradas integralmente por LLMs ("vibe coded") funcionam em happy path mas falham sistematicamente em produção. Lista de 20 vulnerabilidades e anti-patterns que agentes de código geram confidentemente porque não compreendem contexto de produção. Inclui segurança (auth, injection), performance (indexação, paginação), resiliência (logging, backups).

## Como implementar
**Checklist de hardening pré-production**: (1) tokens em localStorage → mover para httpOnly cookies; (2) API keys hardcoded → usar env vars com validação; (3) inputs não sanitizados → usar prepared statements + input validation lib; (4) webhooks sem assinatura → verificar HMAC/JWT antes de processar; (5) sem rate limiting → adicionar middleware (express-rate-limit, redis); (6) queries sem LIMIT → paginar sempre (cursor-based preferível); (7) sem índices em FK/search fields → audit schema; (8) uploads sem validação tamanho/tipo → rejeitar >10MB ou extensões suspeitas; (9) CORS muito permissivo → restringir a domínios específicos; (10) erros stacktrace expostos → log interno, mensagem genérica ao user; (11) sem validação de roles → check `user.role === 'admin'` em toda rota sensível; (12) session tokens nunca expiram → set maxAge: 1h em JWT; (13) emails síncronos no request → queue com Bull/RabbitMQ; (14) sem backup → automated daily backups com retenção; (15) sem health checks → endpoint /health que valida DB conectado; (16) variáveis de env não validadas → startup script checa todas obrigatórias; (17) sem error boundaries → React/Vue deve envolver tudo em <ErrorBoundary>; (18) imagens servidas direto do servidor → usar CDN (CloudFront, Cloudflare); (19) sem request logging → middleware que loga method/path/status/duration; (20) commit secrets em git → usar pre-commit hooks com detect-secrets.

Para cada item: implementar, validar com teste (ex: curl com JWT expirado deve retornar 401), documentar em DEPLOYMENT.md.

## Stack e requisitos
Checklist é agnóstico linguagem/framework. Ferramentas: TypeScript para adicionar type safety, testes (Jest, pytest), linting (ESLint, Ruff). Segurança: bibliotecas específicas conforme stack (bcrypt para hashing, helmet para headers, joi/zod para validação). Time: 4-8 horas de hardening por app small-medium.

## Armadilhas e limitacoes
Segurança é moving target — novo CVE sai a cada semana, monitorar advisories. Performance optimization é iterativo — profile em produção, não assuma. Resiliência requer testing caótico (chaos monkey, kill aleatório de instâncias) — simples checklist não suficiente. Trade-off entre UX e segurança — auth agressivo (2FA obrigatório) pode aumentar churn; calibrar por risk profile.

## Conexoes
[[deepagent-gerar-app-funcional-90-segundos|App generation seguro]]
[[desafio_engenharia_performance_anthropic|Performance engineering]]
[[designmd-como-contrato-de-design-para-llms|Quality standards]]

## Historico
- 2026-04-02: Nota criada
- 2026-04-02: Reescrita pelo pipeline
