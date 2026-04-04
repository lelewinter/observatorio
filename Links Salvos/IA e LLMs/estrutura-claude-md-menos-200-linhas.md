---
date: 2026-03-28
tags: [claude-code, claude.md, configuracao, prompt-engineering, setup]
source: https://x.com/techNmak/status/2037788648691884207
tipo: aplicacao
autor: "@techNmak"
---
# CLAUDE.md Compacto: Máximo 200 Linhas para Máxima Aderência

## O que e
Arquivo CLAUDE.md de instruções que excede 200 linhas sofre degradação de qualidade — Claude ignora partes, contradições surgem, conformidade geral cai. Arquivo conciso (<200L) com instruções prioritizadas garante que TODAS as regras sejam lidas e seguidas corretamente. Metáfora: mente humana tem "span de atenção para leitura de regras"; além de 200 linhas, retenção cai dramaticamente.

## Como implementar
**Auditoria**: lista todas regras atuais de CLAUDE.md, marca por frequência de uso (crítico/importante/nice-to-have). **Consolidação**: combina regras redundantes (3 formas diferentes de "cite fontes" vira 1). **Abstração**: "Siga [[referência-de-style-guide-existente]]" em vez de repetir 20 linhas de detalhes. **Priorização**: mantém 5-10 regras críticas, delegua resto a documentação linkedada. Estrutura eficiente: 20L (meta), 30L (core behaviors), 50L (constraints), 50L (examples), 50L (tools/context). Revisar a cada 2 semanas, remover instruções que não impactam output. Teste: rode mesma tarefa com CLAUDE.md antigo vs. novo, valida se qualidade permanece.

Padrão: "menos é mais" em prompt engineering. Cada linha adicional custa atenção no modelo; você pensa "estou adicionando instrução útil" mas na verdade você está diluindo força de instruções existentes. Matemática: atenção é soma zero.

## Stack e requisitos
Editor de texto + Git para versionamento. Sem dependências técnicas. Requer disciplina de manutenção. Validação: usar mesmo test set antes/depois de redução, medir mudanças em qualidade (subjetivamente ou com evals automatizados).

## Armadilhas e limitacoes
Remover regra que parecia redundante mas é na verdade crítica em contexto específico. Mitigar: antes de deletar, testar prompt com tarefa que depende daquela regra. Abstrair muito ("sejam excelentes") perde especificidade. Manter arquivo em sync com tooling real — se adiciona nova tool, adiciona 1 linha ao CLAUDE.md (sem remover outra), senão contexto desatualiza.

## Conexoes
[[contexto-persistente-em-llms|Contexto estruturado]]
[[designmd-como-contrato-de-design-para-llms|Especificações de design]]
[[geracao-automatizada-de-prompts|Otimização de prompts]]

## Historico
- 2026-03-28: Referência original
- 2026-04-02: Reescrita pelo pipeline
