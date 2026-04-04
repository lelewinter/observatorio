---
tags: []
source: https://www.linkedin.com/posts/clarama_if-youre-a-chief-of-staff-switching-to-claude-share-7441832145192472576-d926?utm_source=share&utm_medium=member_android&rcm=ACoAAAgQrLIB4LHRfm8oNhRCsOv9i7wGJSYJXQs
date: 2026-04-02
tipo: aplicacao
---

# Configurar Preferências Globais do Claude para Modo Socrático Persistente

## O que é

Personal Preferences no Claude funcionam como um system prompt global, aplicado a todas as conversas sem necessidade de repetição. Diferente de project system prompts (escopo limitado), as preferências atuam como camada de pré-conditioning que condiciona o comportamento do modelo antes de qualquer prompt inicial.

## Como implementar

Acesse Settings → Profile → Personal Preferences no Claude web ou desktop. Estruture as preferências em três camadas.

**Camada 1: Modo de operação.** Adicione: "Não crie entregáveis finalizados até eu passar um sinal explícito (como 'proceder', 'executar', ou 'gerar documento'). Até então, mantenha modo exploratório: questione suposições, ofereça alternativas e peça esclarecimentos." Isso força o LLM a permanecer em decomposição analítica em vez de colapsar prematuramente em output. O gatilho explícito ("proceed") atua como separator entre brainstorming e execução.

**Camada 2: Eliminação de ruído linguístico.** Remova marcadores de "IA-ness": "Não use em dashes para separar ideias. Não use frases como 'but here's the thing', 'so basically', 'at the end of the day'. Não ofereça múltiplas opções numeradas como default. Escreva em tom direto, como alguém que já conhece o contexto." Reduz friction cognitiva ao revisar outputs — texto chega mais próximo do estilo humano desde a primeira geração.

**Camada 3: Ancoragem contextual.** Se tiver tema recorrente (ex: você é Chief of Staff com foco em operações), adicione: "Contexto: você atua como [seu papel]. Todas as respostas devem se alinhar com [seu objetivo específico]." Isso reduz desvios e cria um "north star" que o modelo usa internamente para redirecionar respostas fora do escopo.

**Integração com brand guide.** Crie um guia de marca usando Claude, exporte como markdown ou PDF. Anexe em um projeto do Claude Code. Todos os documentos gerados naquele contexto (relatórios, apresentações, copy) seguirão automaticamente tom, vocabulário e estética definidos — sem precisar repetir instruções a cada novo documento.

Teste com uma conversa trivial. Verificar se: modelo não oferece soluções pré-cocinadas, linguagem soa humana, mantém foco no tema definido.

## Stack e requisitos

- Claude (web ou desktop, versão 2.1+)
- Notebook/desktop com acesso ao navegador
- Sem custo adicional
- Tempo de setup: 10-15 minutos

## Armadilhas e limitações

Preferências globais aplicam a TODAS as conversas — se adicionar restrição muito rígida, afeta uso casual. Preferências não substituem project system prompts; ambas funcionam em camadas. Overload de preferências (>500 palavras) dilui atenção do modelo — mantenha mínimo viável. Updates em preferências não afetam conversas já iniciadas.

## Conexões

[[Simplificar Setup Claude Deletar Regras Extras]], [[Claude Code - Melhores Práticas]], [[Prompt First Principles para LLMs]]

## Histórico

- 2026-04-02: Nota criada
- 2026-04-02: Reescrita como guia de aplicação prática