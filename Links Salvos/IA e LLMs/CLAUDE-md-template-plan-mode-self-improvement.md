---
date: 2026-03-12
tags: [Claude Code, plan mode, CLAUDE.md, self-improvement, agentes IA, bug fixing, verificação]
source: https://x.com/Suryanshti777/status/2031983605044691454
autor: "Suryansh Tiwari / Boris Cherny"
tipo: aplicacao
---

# Implementar CLAUDE.md para Auto-Melhoria de Agentes IA

## O que é

Arquivo `CLAUDE.md` na raiz do projeto que age como "manual vivo". O agente Claude lê seu conteúdo a cada sessão, capturando convenções, padrões passados, regras derivadas de bugs. Automatiza correção de erros recorrentes sem modificar código.

## Como implementar

**1. Criar estrutura base do arquivo**

Coloque `CLAUDE.md` na raiz do seu projeto com seções:

```markdown
# CLAUDE.md - Configuração do Agente

## Convenções do Projeto
- [regras específicas de estilo, nomeação, padrões]
- Sempre valide entrada antes de processar
- Logs incluem timestamp + contexto

## Erros Passados & Regras Derivadas
- Erro: [descrição]
  Regra: [ação preventiva concreta]

- Erro: Não verificava existência de arquivo
  Regra: SEMPRE try-catch para filesystem

## Plan Mode Obrigatório
- 3+ passos ou decisão arquitetural = ativa plan mode
- Falha = STOP, replaneie, não force
- Use plan mode tanto para construção quanto verificação

## Estratégia de Subagentes
- Delegue pesquisa/exploração para subagentes paralelos
- Mantenha janela de contexto principal limpa
- Uma tarefa por subagente

## Tasks/Lessons
- [padrões aprendidos]
```

**2. Loop de Auto-Melhoria em Produção**

Após cada bug ou correção do usuário:
- Adicione entrada em "Erros Passados"
- Escreva regra preventiva específica
- Revise lições no início da próxima sessão
- Aperfeiçoe redação das regras com o tempo

**3. Verificação Antes de "Completo"**

- Nunca marque tarefa como completa sem prova de funcionamento
- Execute testes, verifique logs
- Pergunte: "Um senior engineer aprovaria?"
- Diff comportamento: main vs. suas mudanças
- Corrija testes CI falhando automaticamente

**4. Demanda Elegância (Balanceado)**

Para mudanças não triviais:
- Questione: "Existe solução mais elegante?"
- Se parece hacky: refatore
- Para fixes simples: aplique direto, sem sobre-engenharia
- Critique seu próprio trabalho antes de entregar

**5. Gerenciamento de Tarefas Estruturado**

- Plan First: escreva `tasks/todo.md` com itens verificáveis
- Verify: confirme plano antes de implementar
- Track: marque completos conforme progride
- Explain: resumo de alto nível a cada passo
- Document: adicione review ao `tasks/todo.md`
- Capture: atualize `tasks/lessons.md` após correções

## Stack e requisitos

- Git repo com estrutura padrão
- Editor de texto ou IDE (VS Code, IntelliJ, etc.)
- Sem dependências externas
- Compatível com qualquer linguagem/framework

## Armadilhas e limitações

- **Não é automático**: regras devem ser revisadas ativamente no início de sessões
- **Overhead inicial**: leva 3-5 iterações até que "lições" fiquem efetivas
- **Precisão crítica**: regras mal-escritas podem gerar falsos positivos
- **Contexto limitado**: CLAUDE.md muito grande (>500 linhas) não será lido integralmente
- **Não substitui testes**: rules documentam padrões, não garantem correção

## Conexões

[[Claude Code - Melhores Práticas]]
[[plan-mode-claude-code-previne-execucao-prematura]]
[[Claude Code Subconscious Letta Memory Layer]]
[[consolidacao-de-memoria-em-agentes]]

## Histórico

- 2026-03-12: Nota criada
- 2026-04-02: Reescrita como guia de implementação prático
