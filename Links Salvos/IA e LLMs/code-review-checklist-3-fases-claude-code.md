---
date: 2026-03-12
tags: [code-review, Claude-Code, checklist, qualidade, bugs, segurança, performance]
source: https://x.com/adriano_viana/status/2032074818783256668
autor: "Adriano Viana"
tipo: aplicacao
---

# Metodologia Code Review em 3 Fases com Claude Code

## O que é

Checklist estruturado com 3 fases para revisar código usando Claude Code, sem depender só de testes. Encontra ~11 categorias de bugs (estrutura, lógica, segurança, performance). Reduz bugs em produção em 80%+.

## Como implementar

**1. Fase 1: Estrutura (O código faz o que deveria?)**

Prompt para Claude Code:

```
Revise este código e responda:

1. Estrutura lógica:
   - Faz exatamente o que deveria fazer?
   - Há ramos de código não-testados?
   - Variáveis são inicializadas antes do uso?

2. Nomes & Clareza:
   - Nomes de variáveis são descritivos?
   - Nomes de funções descrevem a ação?
   - Código precisa de comentários? (ruim sign)

3. Duplicação:
   - Há código repetido?
   - Funções poderiam ser extraídas?

Para cada problema:
   Linha #: [linha no arquivo]
   Problema: [descrição]
   Sugestão: [como corrigir]
```

Exemplo de output:
```
Linha 42: Variable `d` nunca é usado após atribuição
Problema: Dead code ou lógica incompleta?
Sugestão: Remova ou complete lógica

Linha 58: Função `process_user()` duplica lógica em `handle_request()`
Problema: Duplicação (DRY violation)
Sugestão: Extrair função comum `extract_name()` e reutilizar
```

**2. Fase 2: Lógica & Segurança (O código é correto e seguro?)**

```
Revise este código para problemas de lógica e segurança:

1. Lógica de negócio:
   - Casos edge-case são tratados?
   - Qual é o comportamento se input for null/undefined/empty?
   - Há race conditions possíveis?
   - Off-by-one errors (loops, slices)?

2. Segurança:
   - SQL injection possível? (se usar banco)
   - Input validation existe?
   - Autenticação/autorização checada?
   - Dados sensíveis logados ou expostos?
   - Rate limiting necessário?

3. Dependências externas:
   - Timeout definido para chamadas externas?
   - Erro handling para APIs que falham?
   - Retry logic com exponential backoff?

Para cada risco:
   Linha: [linha]
   Risco: [tipo: logic/security/performance]
   Severidade: [critical/high/medium]
   Sugestão: [como mitigar]
```

Exemplo output:
```
Linha 15: Input `user_id` não é validado antes de query
Risco: SQL injection
Severidade: CRITICAL
Sugestão: Use parameterized queries: db.query("SELECT * FROM users WHERE id = ?", [user_id])

Linha 89: Se externa_api.fetch() falha, app explode sem retry
Risco: Availability
Severidade: HIGH
Sugestão: Implementar retry com exponential backoff (max 3 tentativas)
```

**3. Fase 3: Performance & Observabilidade**

```
Revise este código para performance e observabilidade:

1. Performance:
   - Há loops aninhados que podem ser O(n²) ou pior?
   - Cálculos pesados rodando em loop?
   - Possível fazer caching?
   - Database queries otimizadas (índices, JOINs)?

2. Observabilidade:
   - Logging é estruturado e informativo?
   - Métricas críticas estão sendo reportadas?
   - Erros têm contexto suficiente para debug?
   - Performance é monitorável (latency, throughput)?

3. Escalabilidade:
   - Código aguenta 10x carga?
   - Há limites explícitos (max connections, queue size)?
   - Pode-se fazer horizontal scaling?

Para cada achado:
   Linha: [linha]
   Categoria: [performance/observability/scalability]
   Impacto: [estimado em latência ou throughput]
   Sugestão: [como otimizar]
```

**4. Fluxo prático (3-fase integration)**

```bash
# 1. Criar arquivo de checklist
cat > code_review_checklist.md << 'EOF'
# Code Review — 3 Fases

## Arquivo: [nome_arquivo.py]
EOF

# 2. Fase 1: Estrutura
claude code "[Fase 1 prompt]" > fase1_output.txt

# 3. Fase 2: Lógica & Segurança
claude code "[Fase 2 prompt]" > fase2_output.txt

# 4. Fase 3: Performance
claude code "[Fase 3 prompt]" > fase3_output.txt

# 5. Consolidar achados
cat fase{1,2,3}_output.txt > combined_review.txt

# 6. Priorizar por severidade
grep "CRITICAL" combined_review.txt  # Fix first
grep "HIGH" combined_review.txt      # Fix second
```

**5. Template de execução automática**

```python
# automated_code_review.py
import anthropic

class CodeReviewAgent:
    def __init__(self, file_path):
        self.file_path = file_path
        self.client = anthropic.Anthropic()

    def phase1_structure(self):
        with open(self.file_path) as f:
            code = f.read()

        response = self.client.messages.create(
            model="claude-opus-4-1",
            max_tokens=2000,
            messages=[{
                "role": "user",
                "content": f"[PHASE 1 PROMPT]\n\n{code}"
            }]
        )
        return response.content[0].text

    def phase2_logic_security(self):
        # Similar para Phase 2

    def phase3_performance(self):
        # Similar para Phase 3

    def run_full_review(self):
        print("=== PHASE 1: Structure ===")
        print(self.phase1_structure())

        print("\n=== PHASE 2: Logic & Security ===")
        print(self.phase2_logic_security())

        print("\n=== PHASE 3: Performance ===")
        print(self.phase3_performance())

# Uso
if __name__ == "__main__":
    review = CodeReviewAgent("app.py")
    review.run_full_review()
```

## Stack e requisitos

- Claude Code (ou Claude API)
- Arquivo de código para revisar
- Estrutura de checklist (3 prompts especializados)
- Opcional: integração com GitHub CI/CD

## Armadilhas e limitações

- **Requer leitura**: Output é texto verboso. Processamento manual necessário
- **False positives**: Claude às vezes marca "problema" que é intencional
- **Contexto limitado**: Muito código (>10k linhas) pode não caber em uma request
- **Não substitui testes**: Encontra issues, mas não prova correção. Testes ainda necessários
- **Custo**: 3 calls de API por arquivo. Para 100 arquivos = $10-30

## Conexões

[[CLAUDE-md-template-plan-mode-self-improvement]]
[[code-review-contexto-novo-encontra-bugs]]

## Histórico

- 2026-03-12: Nota criada
- 2026-04-02: Reescrita como guia de implementação
