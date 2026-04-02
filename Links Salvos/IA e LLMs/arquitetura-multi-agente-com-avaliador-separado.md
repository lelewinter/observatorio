---
tags: []
source: https://x.com/0xCVYH/status/2036485891250635248?s=20
date: 2026-04-02
---
# Arquitetura Multi-Agente com Avaliador Separado

## Resumo
Sistemas multi-agente com papéis separados de geração e avaliação superam agentes solo em qualidade e criatividade, porque eliminam o viés de auto-avaliação inerente a um único modelo avaliando seu próprio output.

## Explicação
A arquitetura publicada pela Anthropic no Engineering Blog é inspirada em GANs (Generative Adversarial Networks): a ideia central é que separar quem gera de quem avalia cria uma tensão produtiva. Quando o mesmo agente gera e avalia seu próprio trabalho, ele tende a aprovar outputs mediocres — um problema análogo ao colapso de modo em GANs, onde o gerador aprende a enganar o discriminador em vez de melhorar genuinamente.

O sistema completo opera com três agentes especializados: um **Planner** que transforma um prompt curto em uma especificação detalhada de produto; um **Generator** que implementa a especificação em sprints incrementais, feature por feature; e um **Evaluator** que testa a aplicação real via Playwright (navegação, cliques, interações), reprovando o sprint se os critérios não forem atendidos. Antes de cada sprint, Planner e Generator negociam um contrato explícito do que "pronto" significa — apenas após esse acordo o Generator começa a implementar. Isso externaliza e formaliza o critério de aceitação, tornando-o auditável.

Um resultado particularmente relevante é o comportamento emergente na 10ª iteração: o agente descartou o trabalho acumulado e reimaginou a solução completamente, algo que modelos em single-pass não fazem. Isso sugere que iterações longas com feedback externo desbloqueiam espaços criativos inacessíveis em uma única passagem. O custo é alto ($200, 6 horas) comparado ao agente solo ($9, 20 minutos), mas o delta de qualidade é proporcional — o agente solo produziu um jogo quebrado; o harness completo entregou 16 features funcionais com editor de sprites e IA generativa de níveis.

Um dado técnico crítico: o modelo **Opus 4.5** não apresenta "context anxiety" (degradação de desempenho conforme o contexto cresce), enquanto o Sonnet 4.5 sim. Isso significa que sessões longas e contínuas sem resets de contexto só são viáveis com Opus, o que tem implicação direta em custos e escolha de modelo para pipelines de longa duração.

## Exemplos
1. **Geração de software complexo**: prompt "crie um game maker 2D retro" → Planner expande em spec, Generator implementa em 10 sprints, Evaluator testa cada sprint com Playwright, resultando em editor funcional com 16 features.
2. **Design iterativo com salto criativo**: site de museu após múltiplas iterações é completamente reimaginado como espaço 3D com perspectiva CSS e navegação por portas — emergência impossível em single-pass.
3. **Pipelines de produção de produto**: qualquer sistema onde "pronto" precisa ser verificável objetivamente (testes automatizados, critérios de aceitação contratuais entre agentes) se beneficia diretamente dessa separação de papéis.

## Relacionado
Nenhuma nota relacionada disponível no vault no momento.

## Perguntas de Revisão
1. Por que separar o agente gerador do avaliador elimina o viés de auto-avaliação, e qual é o paralelo com a arquitetura GAN?
2. Qual a implicação prática da "context anxiety" do Sonnet 4.5 versus Opus 4.5 para a escolha de modelo em pipelines multi-agente de longa duração?

## Histórico de Atualizações
- 2026-04-02: Nota criada a partir de Telegram