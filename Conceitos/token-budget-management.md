---
tags: [conceito, llm, context-engineering, otimizacao, arquitetura]
date: 2026-04-03
tipo: conceito
aliases: [Token Budget Management]
---
# Token Budget Management

## O que é

Token Budget Management é o conjunto de técnicas e decisões arquiteturais voltadas a controlar, monitorar e otimizar o número de tokens consumidos dentro da janela de contexto de um LLM. O objetivo central é manter o consumo abaixo dos limites físicos do modelo — evitando truncamentos, erros e degradação de qualidade — enquanto se reduz o custo de inferência, que em provedores como Anthropic e OpenAI é diretamente proporcional ao volume de tokens processados. Na prática, trata-se de decidir *o que entra no contexto*, *quando entra* e *com qual granularidade*.

## Como funciona

O princípio fundamental é tratar o contexto como um recurso escasso e gerenciado, não como um buffer ilimitado onde tudo é carregado de uma vez. Isso exige uma classificação explícita das informações por prioridade e frequência de uso, resultando em camadas de carregamento com custos diferentes em tokens.

Uma arquitetura típica de três camadas ilustra bem o mecanismo. A **Camada 1 (Main Context)** é carregada sempre e contém apenas configurações essenciais e invariantes do sistema — o overhead é fixo e previsível. A **Camada 2 (Skill Metadata)** carrega somente metadados leves, como cabeçalhos YAML com 2–3 linhas e menos de 200 tokens por item, suficientes para o modelo saber *que* recursos existem sem precisar conhecer seu conteúdo completo. A **Camada 3 (Active Skill Context)** carrega o conteúdo completo de um recurso — arquivos `.md`, documentação, templates — apenas quando aquele recurso é efetivamente ativado na sessão.

Arquivos de suporte como scripts e templates permanecem fora do contexto por padrão e são acessados diretamente sob demanda, consumindo zero tokens até o momento de uso. Esse padrão é análogo ao [[lazy-loading-contexto]], onde o carregamento é postergado até que a necessidade seja confirmada. O resultado é que centenas de skills ou ferramentas podem coexistir no sistema sem que o contexto seja saturado, pois o custo de tokens de cada uma é quase nulo enquanto inativa.

Tecnicamente, o orçamento de tokens precisa ser monitorado em tempo de execução ou de configuração. Isso pode envolver contadores explícitos, limites por camada, heurísticas de eviction (remover do contexto itens menos usados) e compressão seletiva de histórico de conversação.

## Pra que serve

Token Budget Management é essencial em qualquer sistema que combine múltiplos agentes, ferramentas, skills ou documentos extensos numa única sessão de LLM. Sem ele, o contexto atinge seu limite rapidamente, forçando truncamentos silenciosos que degradam a qualidade das respostas ou erros explícitos que interrompem o fluxo.

**Quando usar:** sistemas multi-skill ou multi-agente; pipelines com documentação extensa; aplicações de longa duração com histórico de conversação acumulado; cenários onde o custo de inferência é relevante em escala.

**Quando não usar (ou simplificar):** tarefas únicas e curtas onde o contexto jamais se aproxima do limite; protótipos onde a otimização ainda não é prioritária.

**Trade-offs principais:** a estratégia de carregamento sob demanda reduz tokens mas aumenta a complexidade de orquestração — é preciso lógica para detectar quando ativar cada camada. Além disso, metadados muito enxutos podem ser insuficientes para o modelo tomar boas decisões de roteamento, exigindo calibração do tamanho mínimo viável dos sumários.

Conecta-se diretamente com [[context-engineering]], que trata do design mais amplo do que compõe o contexto, e com [[layered-context-management]], que formaliza a estratégia de camadas. A eficiência pode ser amplificada por mecanismos como [[kv-cache-quantization]], que reduz o custo computacional de tokens repetidos entre chamadas.

## Exemplo prático

Considere um sistema Claude com 300 skills registradas. Sem Token Budget Management, carregar todas as skills no contexto consumiria facilmente 300 × 500 tokens = **150.000 tokens** só de documentação — inviável para a maioria dos modelos e caro em qualquer provedor.

Com a arquitetura de 3 camadas:

```yaml
# Camada 2: Metadado de skill (< 200 tokens por skill)
skill: refactor-python
description: Refatora código Python para padrões modernos
trigger: [refactor, clean code, pep8]
```

```
Contexto total estimado com 300 skills:
  Camada 1 (config global):         ~500 tokens   [sempre]
  Camada 2 (300 × 150 tokens):    ~45.000 tokens  [sempre, só metadados]
  Camada 3 (1 skill ativa × 800): ~800 tokens     [sob demanda]
  ─────────────────────────────────────────────
  Total efetivo:                  ~46.300 tokens  [vs 150.000+ sem gestão]
```

Somente a skill ativada na sessão atual tem seu arquivo `.md` completo carregado. Scripts auxiliares da skill (ex.: `lint_runner.sh`) só entram no contexto se forem explicitamente invocados durante a execução. O orçamento permanece controlado independentemente do número total de skills cadastradas no sistema.

## Aparece em

- [[implementar-sistema-de-3-camadas-de-context-engineering-com-claude-skills]] - A arquitetura de 3 camadas descrita é justificada explicitamente pela necessidade de suportar centenas de skills sem ultrapassar os limites de tokens do contexto.

---
*Conceito extraído automaticamente em 2026-04-03*