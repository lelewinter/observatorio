---
date: 2026-03-28
tags: [claude-code, ia, ferramentas, produtividade, best-practice, safe-execution, planning]
source: https://x.com/techNmak/status/2037788648691884207
autor: "@techNmak"
tipo: aplicacao
---

# Ativar Plan Mode no Claude Code para Revisão Prévia de Ações

## O que é

Plan mode é um padrão operacional estruturado no Claude Code que força uma etapa de planejamento e revisão ANTES de qualquer execução real (escrever arquivos, rodar comandos, modificar codebase). A analogia é um cirurgião que revisa o plano cirúrgico antes de fazer incisão — não durante a cirurgia. Em 2026, "plan first" é prática recomendada em 70%+ dos projetos pro de engenharia de software, porque reduz ciclos de correção em 80%.

## Por que importa

Sem plan mode, Claude Code executa por confiança (ou seu prompt ambíguo permite múltiplas interpretações). Resultado comum: escreve 5 arquivos, quebra 2 dependências, você nota depois 15 min, volta atrás. Com plan mode, você vê o plano (5-10 linhas), questiona em 10 segundos, corrige antes de execute, resultado = zero retrabalho. Para refatorações (toque 20+ arquivos), timing economizado é horas, não minutos.

## Como funciona / Como implementar

### Método 1: Instrução Explícita em Cada Sessão (Iniciante)

Ideal para tarefas pontuais. Ao iniciar sessão, escreva este prompt:

```markdown
Ative plan mode para esta tarefa:

1. ANTES de fazer qualquer coisa, revise o plano completo de ações
2. Liste quais arquivos você vai tocar (read, write, delete)
3. Liste a ordem das mudanças (dependências)
4. Questione suposições: tenho contexto completo? 
   existem edge cases? tests ainda passam após?
5. Mostre o plano em estrutura clara (árvore/checklist)
6. Aguarde meu "ok, execute" ou "muda tal passo" antes de fazer 
   qualquer FILE WRITE ou SHELL COMMAND

Você pode ler arquivos livremente para entender contexto. 
Quando plano estiver pronto, diga: "[PLAN READY] Esperando OK"
```

Claude responde com algo assim:

```
## Plan Mode Ativado

Entendi. Vou:
1. Ler arquivos relevantes
2. Montar plano de ações
3. Mostrar antes de executar
4. Aguardar aprovação

Lendo contexto do projeto...
```

Após ler codebase:

```
## [PLAN READY] Plano de Ações

Tarefa: Refatorar autenticação para suportar OAuth

**Arquivos a modificar:**
1. src/auth/config.ts — adicionar variáveis env
2. src/auth/strategies/oauth.ts — implementar fluxo
3. src/middleware/auth.ts — integrar novo provider
4. tests/auth.spec.ts — testes para novo fluxo
5. .env.example — documentar novas vars

**Ordem:**
- 1 → 2 → 3 → 4 → 5 (dependência linear)

**Riscos identificados:**
- Código antigo sem testes (auth.spec.ts tem gaps) 
  → Vou adicionar testes novos junto

**Estimativa:** 15-20 min

Aguardando seu "ok, execute" ou sugestões.
```

Você revisa, sugere ajustes, depois aprova:

```
Ok, execute. Mas antes de fazer spec.ts, mostra o código que vai 
adicionar no formato diff para eu revisar.
```

Claude então:
1. Escreve 1-4 completo
2. Mostra diff do spec.ts
3. Você aprova/ajusta
4. Claude finaliza

### Método 2: Plan Mode Persistente em `.claude.md` (Recomendado)

Para toda sessão no projeto, adicione ao `.claude.md` (ou crie em raiz):

```markdown
# Plan Mode - Default Behavior

Para TODA tarefa de código (refatoração, feature, fix, setup):

## Processo Padrão
1. NUNCA escreva arquivos sem mostrar plano primeiro
2. SEMPRE liste:
   - [ ] Arquivos que serão lidos (context)
   - [ ] Arquivos que serão modificados (escrita)
   - [ ] Ordem de mudanças (por dependência)
   - [ ] Testes que validam cada mudança
   - [ ] Possíveis regressões em outras partes
   - [ ] Rollback é seguro? (como reverter se quebrar)

3. QUESTIONE suposições:
   - Tenho contexto completo ou preciso ler mais?
   - Edge cases: usuário com 0 items? N itens? Input vazio?
   - Testes: passam antes? passam depois? coverage mantido?

4. Mostre estrutura visualmente:
   ```
   PLAN:
   ├─ [READ] src/types.ts (entender interfaces)
   ├─ [MODIFY] src/handlers/user.ts (adicionar campo)
   ├─ [MODIFY] tests/handlers.spec.ts (testes novo campo)
   └─ [RUN] npm run test (validar)
   ```

5. Aguarde confirmação explícita antes de:
   - `git add` / `git commit`
   - Escrever em arquivo (file write)
   - Rodar comando shell (bash/npm)
   - Deletar qualquer coisa

## Quando Pular Plan Mode
- Mudar uma variável simples (1 linha, sem deps)
- Renomear função + seus calls (automático com tooling)
- Tarefa é literalmente "copiar arquivo X para Y" (trivial)

Caso contrário, plan mode always.

## Status Signals
Use linguagem clara:
- "[PLAN READY]" — plano montado, aguardando OK
- "[EXECUTING]" — rodando ações aprovadas
- "[DONE]" — tarefa completa, testada
- "[ERROR]" — algo quebrou, need help
```

Agora, qualquer assistente Claude em seu projeto segue isso automaticamente.

### Método 3: Checklist Estruturado com Confirmação

Para tarefas complexas (20+ arquivos, refatoração arquitetural), use checklist explícito:

```markdown
## Plan Mode Checklist

Antes de executar, responda SIM a todos:

### Escopo & Dependências
- [ ] Identifiquei todos os arquivos que serão modificados?
- [ ] Verif dependências entre mudanças (ordem correta)?
- [ ] Há imports circulares potenciais?

### Testes & Validação
- [ ] Há testes que cobrem cada mudança?
- [ ] Testes passam ANTES da minha mudança?
- [ ] Testes vão passar DEPOIS?
- [ ] Coverage mantém acima de X% (seu threshold)?

### Regressão & Segurança
- [ ] Possíveis regressões em outras partes do código?
- [ ] Configs que podem afetar esta mudança?
- [ ] Variáveis env novo requisito? (documentar)
- [ ] Credenciais/secrets que não devem ser commitadas?

### Rollback
- [ ] Rollback é seguro/simples se algo der errado?
- [ ] Migrations de database (se houver) são reversíveis?
- [ ] Posso voltar em 1 git reset --hard se quebrar?

### Context
- [ ] Tenho arquivo README/docs relevante lido?
- [ ] Entendo padrões de código do projeto?
- [ ] Há comentários TODO/FIXME que afetam isto?

---

Se respondeu NÃO em qualquer item, faça:
1. Ler arquivo relevante
2. Esclarecer com você
3. Ajustar plano
4. Responder SIM

Só depois execute.
```

### Método 4: Auto Mode com Safety Rails (Avançado)

Se plan mode fica tedioso para tarefas rotineiras (renomear variável, adicionar log), use auto mode com permissões permitidas:

```markdown
## Auto Mode com Whitelist

Permita execução automática (sem plan show) para:
- [ ] Adicionar console.log/print (não muda lógica)
- [ ] Renomear variável consistentemente (regex replace)
- [ ] Formatação de código (prettier/black)
- [ ] Adicionar comentário
- [ ] Deletar arquivo comentado/obsoleto

Bloqueie sempre (plan mode obrigatório):
- [ ] Mudança em lógica de negócio
- [ ] Refatoração arquitetural
- [ ] Toque em auth/segurança
- [ ] Delete de arquivo ativo
- [ ] Mudança em database schema
```

Você usa:

```
Use auto mode para logging. Plan mode para lógica.
```

Claude segue: logging → execute direto; lógica → plan first.

## Stack técnico

```yaml
IDE: Claude Code (desktop ou web)
Versionamento: Git (para undo seguro)
Testing: Pytest, Jest, Vitest (validar antes/depois)
Linting: ESLint, Pylint (detectar issues auto)
Configuração: .claude.md na raiz do projeto
Tempo setup: ~5 minutos para escrever .claude.md robusto
```

## Código prático: Template de .claude.md para Seu Projeto

```markdown
# Claude Code Configuration

## Plan Mode Padrão
Para TODA tarefa não-trivial (lógica, refatoração, db schema):
1. Ler arquivos relevantes
2. Montar plano (arquivos lidos/escritos, ordem, riscos)
3. Mostrar plano estruturado
4. Aguardar "ok, execute"

## Estrutura do Projeto
- `src/` — código fonte (TypeScript)
- `tests/` — testes (Jest)
- `public/` — assets estáticos
- `.env.local` — variáveis locais (NÃO commitar)
- `package.json` — dependências

## Padrões de Código
- Naming: camelCase para funções/vars, PascalCase para classes
- Formatting: Prettier (prettier.config.js)
- Commits: Conventional Commits (feat:, fix:, refactor:)

## Segurança
- NUNCA exponha .env, tokens, API keys em arquivo
- NUNCA rode comando `rm -rf` sem plano prévio
- Type safety: usar TypeScript strict mode

## Testes
- Rodar `npm run test` antes de finalizar mudança
- Coverage target: >80%
- Testar edge cases: null, empty, muito grande

## Exemplo Plano Correto

```
[PLAN READY] 

Tarefa: Adicionar campo `email_verified` em User

ESTRUTURA:
├─ [READ] src/types/user.ts (entender User interface)
├─ [MODIFY] src/db/schema.ts (adicionar coluna)
├─ [MODIFY] src/api/users.ts (retornar novo campo)
├─ [MODIFY] tests/api.spec.ts (testes novo campo)
└─ [RUN] npm test (validar)

RISCOS:
- Se não fizer migration, versão velha quebra
  → Solução: criar migration file

ROLLBACK: git reset --hard HEAD (seguro, db em dev)

Aguardando "ok, execute"
```

## Armadilhas e limitações

1. **Overdoing plan mode em tarefas triviais cria friction.**
   Renomear uma variável, adicionar um log — não precisa plan. Restrinja plan mode a refatorações (5+ arquivos) e mudanças de lógica.
   
   **Solução:** Usa whitelist conforme Método 4 acima.

2. **Plano muito longo (>20 passos) é sinal de "quebra em partes".**
   Se plan tem 30 passos, é 1 tarefa gigante disfarçada. Divida em 3 sessões menores (cada com seu próprio plan).
   
   **Exemplo:** Em vez de "Refatorar toda autenticação em 30 passos", faça:
   - Sessão 1: Setup OAuth config
   - Sessão 2: Implementar OAuth flow
   - Sessão 3: Migrar users existentes
   
   Cada sessão tem seu próprio plan, validação, rollback.

3. **Plan mode não substitui testes automáticos.**
   Plano pode parecer perfeito, mas código quebra. Plan é complementar: previne classes óbvias de erros (esquecer de arquivo, ordem errada), não substitui teste.
   
   **Ação:** Sempre rodar `npm test` ou `pytest` no final. Plan é revisão humana, teste é automático.

4. **Instruções obscuras em .claude.md confundem o modelo.**
   Se seu .claude.md tem 50 linhas de regras conflitantes, Claude fica confuso. Mantenha claro e conciso.
   
   **Bom:** 10-15 linhas, lista clara, exemplos
   **Ruim:** 50 linhas, orações complexas, muitas exceções

5. **Plano é estático — realidade é dinâmica.**
   Meio caminho, descobrir que arquivo X não existe ou mudou. Plano fica obsoleto. Precisam ajustar on-the-fly.
   
   **Mitigação:** Plano é guia, não lei. Se descobre problema, avise: "Plano muda: arquivo X não existe, vou usar Y."

6. **Contexto incompleto invalida plano.**
   Se não leu arquivo Y que é dependência, plano pode estar errado. Releia tudo se incerto.
   
   **Ação:** No plano, liste explicitamente: "[READ] arquivo X porque é dependência de mudança Y"

## Conexões

- [[Claude Code Best Practices 2026]] — workflow completo
- [[Safe Execution Patterns in AI Coding]] — além de plan mode
- [[Testing Strategies for AI-Generated Code]] — validação
- [[Git Workflows for Solo Developers]] — versionamento seguro

## Histórico

- 2026-03-28: Nota criada
- 2026-04-02: Reescrita como guia de aplicação prática
- 2026-04-11: Expandida com 130+ linhas, template .claude.md pronto pra usar, 4 métodos diferentes, checklist e auto mode, armadilhas práticas
