---
tags: []
source: https://x.com/PrajwalTomar_/status/2038292355095335406?s=20
date: 2026-04-02
---
# Separação de Responsabilidades em Workflow de IA

## Resumo
Claude Code é eficiente para lógica e código, mas fraco em design visual. Combinar Google Stitch 2.0 (design) com Claude Code via MCP (lógica) resolve o problema de apps com aparência genérica gerada por IA.

## Explicação
Ferramentas de IA generativa para código tendem a produzir interfaces funcionais, mas visualmente pobres — o chamado "AI slop": resultados padronizados, sem identidade visual, que denunciam geração automática. Claude Code, da Anthropic, se enquadra nesse perfil: excelente para raciocínio lógico, estrutura de código e resolução de problemas, mas não foi otimizado para tomar decisões estéticas de interface.

O Google Stitch 2.0 surge como ferramenta especializada em geração de UI/UX, capaz de produzir designs coerentes e visualmente consistentes. A proposta do workflow é usar cada ferramenta dentro de sua competência: Stitch 2.0 gera o design e os componentes visuais, enquanto Claude Code, conectado via MCP (Model Context Protocol), implementa a lógica de negócio e a integração funcional.

MCP (Model Context Protocol) é o protocolo que permite que modelos como Claude interajam com ferramentas externas, APIs e contextos de forma estruturada. Nesse pipeline, ele atua como ponte entre o output do Stitch 2.0 e a capacidade de codificação do Claude, permitindo que os dois sistemas colaborem sem intervenção manual excessiva.

Esse padrão reflete um princípio mais amplo de engenharia de software: separação de responsabilidades. Aplicado a workflows de IA, significa orquestrar modelos especializados em vez de exigir que um único modelo genérico execute todas as tarefas com qualidade uniforme.

## Exemplos
1. **Desenvolvimento de SaaS**: usar Stitch 2.0 para gerar telas e design system, depois conectar via MCP ao Claude Code para implementar autenticação, lógica de negócio e chamadas de API.
2. **Prototipagem rápida**: gerar um protótipo visual fiel no Stitch 2.0 e automaticamente transformar em código funcional via Claude Code, reduzindo o ciclo design→código.
3. **Correção de "AI slop"**: reprocessar interfaces geradas apenas por LLMs de código através do Stitch 2.0 para elevar a qualidade visual antes da entrega.

## Relacionado
*(Nenhuma nota relacionada disponível no vault no momento.)*

## Perguntas de Revisão
1. Por que delegar design visual a um LLM de código como Claude tende a produzir resultados de baixa qualidade estética?
2. Qual é o papel do MCP nesse workflow e por que ele é necessário para conectar Stitch 2.0 ao Claude Code?

## Histórico de Atualizações
- 2026-04-02: Nota criada a partir de Telegram