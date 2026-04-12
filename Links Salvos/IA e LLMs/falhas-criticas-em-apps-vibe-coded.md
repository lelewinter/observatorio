---
tags: [segurança, backend, webdev, boas-práticas, vibe-coding, ai-generated-code]
source: https://x.com/Hartdrawss/status/2035378419278532928?s=20
date: 2026-04-02
tipo: aplicacao
---
# 20 Falhas Críticas em Apps Vibe Coded: Segurança até Observabilidade

## O que é

Vibe coding — desenvolvimento onde a aplicação inteira é gerada por LLM sem código manual — funciona em happy path (usuário válido, dados corretos, rede estável), mas falha sistematicamente em produção. Um relatório de Escape.tech (2026) escaneou 1.400+ apps vibe-coded em produção:

- **65% tinham vulnerabilidades de segurança**
- **58% continham pelo menos 1 CVE crítico**
- **400+ secrets expostos, 175 instâncias de PII exposto**

A análise de Tenzai (dezembro 2025) em 15 apps reais revelou **69 vulnerabilidades** entre eles:
- 100% sem CSRF protection
- 100% sem security headers configurados
- 100% com SSRF (Server-Side Request Forgery) vulnerabilidades

**Raiz do problema**: LLMs não compreendem "contexto de produção" — segurança em produção não é uma feature, é uma ausência de negligência. Modelos treinam em código open-source (que muitas vezes é exemplo/prototipo, não production-ready), então herdam esses padrões.

## Como Implementar: Checklist de Hardening Pré-Production

### 1. Autenticação e Armazenamento de Tokens

**Vulnerabilidade Comum**: Tokens armazenados em `localStorage` (acessível via XSS).

```javascript
// ❌ ERRADO
localStorage.setItem('auth_token', token);
const token = localStorage.getItem('auth_token'); // XSS vulnerability

// ✅ CORRETO
// Backend: set httpOnly, Secure, SameSite cookies
res.cookie('auth', token, {
  httpOnly: true,      // JS não consegue ler
  secure: true,        // HTTPS only
  sameSite: 'strict',  // CSRF protection
  maxAge: 3600000      // 1 hour
});

// Frontend: cookie é enviado automaticamente, nada a fazer
fetch('/api/protected', { credentials: 'include' })
```

**Implementação**:
```typescript
// express-session middleware
import session from 'express-session';
import RedisStore from 'connect-redis';
import { createClient } from 'redis';

const redisClient = createClient();
const store = new RedisStore({ client: redisClient });

app.use(session({
  store,
  secret: process.env.SESSION_SECRET,
  resave: false,
  saveUninitialized: false,
  cookie: {
    httpOnly: true,
    secure: process.env.NODE_ENV === 'production',
    sameSite: 'strict',
    maxAge: 1000 * 60 * 60 // 1h
  }
}));
```

### 2. Environment Variables e Secrets Management

**Vulnerabilidade**: Hardcoded API keys ou database URLs no código.

```python
# ❌ ERRADO
API_KEY = "sk-1234567890abcdef"  # Commited to git = permanently leaked
db_url = "postgres://user:password@prod.db.com:5432/main"

# ✅ CORRETO
import os
from dotenv import load_dotenv

load_dotenv()  # Load from .env.local (never commit)
api_key = os.getenv('ANTHROPIC_API_KEY')
if not api_key:
    raise ValueError("ANTHROPIC_API_KEY not set in environment")

# Validation on startup
required_vars = ['DATABASE_URL', 'REDIS_URL', 'JWT_SECRET']
for var in required_vars:
    if not os.getenv(var):
        raise ValueError(f"Missing required env var: {var}")
```

**Tooling para detectar secrets já commitados**:
```bash
# Install pre-commit hook
pip install detect-secrets

# Scan history
detect-secrets scan > .secrets.baseline

# Prevent future commits
detect-secrets install-hook --baseline .secrets.baseline
```

### 3. Input Validation e SQL Injection Prevention

**Vulnerabilidade**: Inputs não sanitizados concatenados direto em queries.

```python
# ❌ ERRADO
user_id = request.args.get('id')
query = f"SELECT * FROM users WHERE id = {user_id}"  # SQL injection
result = db.execute(query)

# ✅ CORRETO - Prepared Statements (parameterized)
from sqlalchemy import text

user_id = request.args.get('id')
query = text("SELECT * FROM users WHERE id = :id")
result = db.execute(query, {"id": user_id})
```

**Validação de Schema** (Zod em TypeScript):
```typescript
import { z } from 'zod';

const CreateUserSchema = z.object({
  email: z.string().email("Invalid email"),
  age: z.number().int().min(0).max(150),
  tags: z.array(z.string()).max(10, "Max 10 tags"),
  bio: z.string().max(500)
});

// Usage
try {
  const valid = CreateUserSchema.parse(req.body);
  // Process valid data
} catch (err) {
  res.status(400).json({ error: err.errors });
}
```

### 4. Rate Limiting

**Vulnerabilidade**: Sem rate limit, brute-force logins são triviais.

```typescript
import rateLimit from 'express-rate-limit';

const loginLimiter = rateLimit({
  windowMs: 15 * 60 * 1000,  // 15 minutes
  max: 5,                     // 5 requests per windowMs
  message: 'Too many login attempts, try again later',
  standardHeaders: true,
  legacyHeaders: false,
});

app.post('/login', loginLimiter, (req, res) => {
  // Handle login
});

// Stricter for auth endpoints
const authLimiter = rateLimit({
  windowMs: 1000,  // 1 second
  max: 1,          // 1 request per second
});
```

### 5. Database Query Pagination

**Vulnerabilidade**: `SELECT * FROM large_table` returns millions de rows, OOM/timeout.

```python
# ❌ ERRADO
posts = Post.query.all()  # Memory bomb

# ✅ CORRETO - Cursor-based pagination
from sqlalchemy.orm import Query

page = request.args.get('cursor', '0')
limit = min(int(request.args.get('limit', 20)), 100)  # cap at 100

query = Post.query.filter(Post.id > page).order_by(Post.id).limit(limit + 1)
posts = query.all()

# Next cursor is last post's ID
next_cursor = posts[-1].id if len(posts) > limit else None
posts = posts[:limit]

return {
  'posts': [p.to_dict() for p in posts],
  'next_cursor': next_cursor
}
```

### 6. Database Indexing

**Vulnerabilidade**: Queries lentas em tabelas grandes causam timeouts.

```sql
-- ❌ ERRADO - nenhum índice
SELECT * FROM orders WHERE user_id = ? AND status = 'pending'
-- Table scan de 10M+ linhas = 30+ segundos

-- ✅ CORRETO - índices em colunas frequentemente filtradas
CREATE INDEX idx_orders_user_status ON orders(user_id, status);
-- Same query = 5-10ms

-- Audit: check missing indexes
SELECT schemaname, tablename, indexname 
FROM pg_indexes 
WHERE schemaname NOT IN ('pg_catalog', 'information_schema');
```

### 7. File Upload Validation

**Vulnerabilidade**: Uploads sem validação permitem malware ou zip bombs.

```typescript
import multer from 'multer';
import fileType from 'file-type';

const upload = multer({
  limits: { fileSize: 10 * 1024 * 1024 }, // 10MB max
  fileFilter: async (req, file, cb) => {
    const type = await fileType.fromBuffer(file.buffer);
    
    const allowed = ['image/jpeg', 'image/png', 'application/pdf'];
    if (!type || !allowed.includes(type.mime)) {
      cb(new Error('Invalid file type'));
    }
    cb(null, true);
  }
});

app.post('/upload', upload.single('file'), (req, res) => {
  // File is validated
  res.json({ url: `/uploads/${req.file.filename}` });
});
```

### 8. CORS Configuration

**Vulnerabilidade**: CORS "*" permite qualquer site fazer requests no seu backend.

```typescript
// ❌ ERRADO
app.use(cors());  // Allows all origins

// ✅ CORRETO
import cors from 'cors';

app.use(cors({
  origin: [
    'https://yourdomain.com',
    'https://app.yourdomain.com'
  ],
  credentials: true,
  methods: ['GET', 'POST', 'PUT', 'DELETE'],
  allowedHeaders: ['Content-Type', 'Authorization']
}));
```

### 9. Error Handling e Logging

**Vulnerabilidade**: Stack traces expostos ao frontend revelam arquivos, versões, banco de dados.

```typescript
// ❌ ERRADO
try {
  // code
} catch (err) {
  res.status(500).json({ error: err.stack, message: err.message });
}

// ✅ CORRETO
try {
  // code
} catch (err) {
  // Log interno (só backend vê)
  logger.error('DB error', {
    message: err.message,
    stack: err.stack,
    userId: req.user?.id,
    path: req.path,
    timestamp: new Date().toISOString()
  });
  
  // Resposta genérica ao user
  res.status(500).json({
    error: 'Internal server error',
    requestId: req.id  // para rastrear em logs
  });
}
```

### 10-20. Checklist Rápido Adicional

| # | Issue | Fix |
|---|-------|-----|
| 10 | Sem security headers | `helmet()` middleware (Content-Security-Policy, X-Frame-Options, X-Content-Type-Options) |
| 11 | Webhooks sem assinatura | Verify HMAC: `crypto.timingSafeEqual(provided, computed)` |
| 12 | Tokens nunca expiram | JWT `exp` claim: `{ exp: Math.floor(Date.now() / 1000) + 3600 }` |
| 13 | Emails sincronos no request | Queue (Bull, RabbitMQ): `await emailQueue.add({ to, subject })` |
| 14 | Sem backups | Daily automated exports to S3 com retenção (7+ dias) |
| 15 | Sem health checks | `/health` endpoint que valida DB, Redis, caches |
| 16 | Env vars não validadas | Schema validation no startup: `z.object({ PORT: z.coerce.number() }).parse(process.env)` |
| 17 | Sem error boundaries (React/Vue) | `<ErrorBoundary fallback={...}>` envolvendo tudo |
| 18 | Imagens servidas direto | Usar CDN (CloudFront, Cloudflare) com cache headers |
| 19 | Sem request logging | Middleware: `(req, res, next) => logger.info({ method: req.method, path: req.path })` |
| 20 | Secrets commitados em git | Pre-commit hook com `detect-secrets`, audit histórico com `git log -p` |

## Stack e Requisitos

**Agnóstico linguagem/framework** — princípios aplicam a Node.js, Python, Go, Rust, Java.

**Ferramentas por categoria**:
- **Type Safety**: TypeScript, Mypy (Python), Rust
- **Testing**: Jest (JS), Pytest (Python), criterium (Rust)
- **Linting**: ESLint + Prettier, Ruff (Python), Clippy (Rust)
- **Scanning**: SonarQube, Snyk, GitHub CodeQL
- **Secrets Detection**: detect-secrets, GitGuardian, TruffleHog
- **Infrastructure**: Docker, Kubernetes, GitHub Actions (CI/CD)
- **Monitoring**: DataDog, Prometheus, ELK stack

**Tempo estimado**: 4-8 horas de hardening em app small-medium para passar cada item.

## Armadilhas e Limitações

### 1. Segurança é Moving Target

Novo CVE sai diariamente. Framework que era "seguro" em janeiro tem vulnerability em março.

**Mitigação**: 
- GitHub Dependabot automático (avisos de updates)
- Audit semanal: `npm audit`, `pip audit`
- Subscribe a advisories de linguagem (Node.js, Python, Go security mailing lists)

### 2. Performance vs Segurança Trade-off

Auth agressivo (2FA obrigatório, captcha toda request) aumenta churn e latência.

**Calibração**: Risk-based auth — 2FA apenas para ações sensíveis (withdraw, share, delete), não login.

### 3. Teste Caótico Requer Infraestrutura

Checklist de segurança é estático. Produção é dinâmica — chaos monkey (kill aleatório de instâncias) e load testing revelam bugs que static analysis não pega.

**Investimento**: Ferramentas como Gremlin ou Firecracker exigem setup, custo USD 500+/mês.

## Conexões

- [[deepagent-gerar-app-funcional-90-segundos|App generation com guardrails de segurança]]
- [[desafio_engenharia_performance_anthropic|Performance engineering em produção]]
- [[designmd-como-contrato-de-design-para-llms|Quality standards para LLMs]]

## Histórico

- 2026-04-02: Nota criada
- 2026-04-11: Reescrita com vulnerabilities reais (Escape.tech, Tenzai, Veracode), 10 items expandidos com código, checklist 20 items, tools, trade-offs
