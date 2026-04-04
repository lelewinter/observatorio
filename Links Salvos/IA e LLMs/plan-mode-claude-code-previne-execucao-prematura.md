---
date: 2026-03-28
tags: [claude-code, ia, ferramentas, produtividade, best-practice]
source: https://x.com/techNmak/status/2037788648691884207
autor: "@techNmak"
tipo: aplicacao
---

# Ativar Plan Mode no Claude Code para Revisão Prévia de Ações

## O que é

Plan mode é um padrão operacional no Claude Code que força uma etapa de planejamento e revisão ANTES de qualquer execução real (escrever arquivos, rodar comandos, modificar codebase). Analogia: cirurgião que revisa o plano cirúrgico antes de fazer incisão, não durante.

## Como implementar

**Método 1: Instrução explícita em cada sessão.** Ao iniciar uma tarefa, escreva:

```
Ative plan mode para esta tarefa:
1. Primeiro, revise o plano completo de ações (quais arquivos tocar, em que ordem)
2. Questione suposições (tenho contexto completo? existem edge cases?)
3. Proponha o plano antes de executar
4. Aguarde meu "ok, execute" antes de fazer mudanças reais
```

Claude então mostra um plano estruturado em passos antes de qualquer filesystem write.

**Método 2: Adicionar em `.claude.md` como preference persistente.**

```markdown
## Plan Mode Padrão

Para toda tarefa de código:
- SEMPRE revise o plano antes de executar
- Mostre estrutura de mudanças como árvore
- Questione suposições: contexto completo? tests passam após mudanças?
- Aguarde confirmação explícita antes de escrever arquivos
```

Isso torna plan mode comportamento default sem repetir instrução a cada conversa.

**Método 3: Estruturado com checklist.**

```
Plan Mode Checklist:
[ ] Identifiquei todos os arquivos que serão modificados?
[ ] Verificar dependências entre mudanças?
[ ] Há tests que validam cada mudança?
[ ] Possíveis regressões em outras partes do código?
[ ] Rollback é seguro se algo der errado?
[ ] Contexto é suficiente ou preciso carregar mais arquivos?

Executar apenas quando todos os itens estão preenchidos.
```

**Timing prático.** Plan mode típicamente adiciona 30-60 segundos para tarefas simples, 2-5 minutos para refatorações. Retorna em redução de ciclos de correção (80% menos volta atrás).

## Stack e requisitos

- Claude Code (desktop ou web)
- Projeto Git (para context manager)
- `.claude.md` com instruções (opcional mas recomendado)
- Sem custos adicionais
- Tempo: ~10 minutos setup inicial

## Armadilhas e limitações

Plan mode adiciona latência para tarefas triviais (ex: renomear variável). Overdoing plan mode em tarefas pequenas cria friction desnecessária — use selective para tarefas complexas. Se plan é muito longo (>20 passos), considere quebrar em múltiplas sessões. Plan mode não substitui testes automáticos — é complementar. Instruções obscuras no claude.md podem confundir o modelo — mantenha claro e conciso.

## Conexões

[[Simplificar Setup Claude Deletar Regras Extras]], [[Sistemas Multi-Agente para Engenharia de Software]], [[Spec-Driven Development]]

## Histórico

- 2026-03-28: Nota criada
- 2026-04-02: Reescrita como guia de aplicação prática
