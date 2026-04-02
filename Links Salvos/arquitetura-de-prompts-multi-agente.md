---
tags: []
source: https://x.com/NieceOfAnton/status/2039277883127103501?s=20
date: 2026-04-02
---
# Arquitetura de Prompts Multi-Agente

## Resumo
Sistemas de IA complexos como o Claude Code operam por meio de uma arquitetura modular com múltiplos prompts especializados, cada um responsável por uma função distinta — identidade, execução de ferramentas, memória, orquestração e verificação.

## Explicação
A engenharia reversa do Claude Code revelou que a ferramenta não funciona com um único prompt monolítico, mas com 26 prompts distintos organizados em camadas funcionais: um prompt de sistema central (identidade, segurança, roteamento de ferramentas), 11 prompts de ferramentas (shell, operações de arquivo, busca, planejamento), 5 prompts de agentes especializados, 4 prompts de memória, 1 prompt coordenador para orquestração multi-agente e 4 prompts utilitários.

Essa arquitetura revela um princípio de design fundamental em sistemas de IA de produção: a decomposição funcional. Cada agente possui responsabilidade única e bem definida — há, por exemplo, um agente dedicado exclusivamente a tentar quebrar o código antes do deploy (equivalente a um QA automatizado). Há também regras explícitas contra over-engineering baked nos prompts: "não adicione funcionalidades além do que foi pedido", o que demonstra que restrições de comportamento são injetadas diretamente na camada de instrução, não apenas no treinamento do modelo.

O sistema de memória utiliza compressão em 9 seções que preserva todas as mensagens do usuário, indicando uma estratégia deliberada de retenção de contexto sem perda de intent. O sistema de risco em camadas — editar arquivos livremente, mas pedir permissão antes de force-push — mostra como gradações de autonomia são codificadas explicitamente em prompts, não inferidas pelo modelo. Isso é relevante para qualquer desenvolvedor construindo agentes: o comportamento confiável emerge de instruções estruturadas, não apenas de capacidades do modelo base.

Para estudos de prompt engineering e design de agentes, esse repositório funciona como um caso real de referência: demonstra como um produto de $200/mês estrutura seu "cérebro" em termos puramente de texto e instrução.

## Exemplos
1. **Agente verificador de código**: Um agente cujo único job é tentar quebrar o código antes do ship — equivalente a um red-team automatizado embutido no pipeline de desenvolvimento.
2. **Compressão de memória de sessão**: 9 seções de sumarização que preservam o histórico de mensagens do usuário para manter contexto em sessões longas sem estourar a janela de contexto.
3. **Sistema de risco graduado**: Edições de arquivo ocorrem de forma autônoma, mas operações destrutivas (force-push) disparam uma camada de confirmação — autonomia calibrada por nível de risco da ação.

## Relacionado
*(Nenhuma nota relacionada disponível no vault no momento.)*

## Perguntas de Revisão
1. Quais são as seis camadas funcionais de prompts identificadas no Claude Code e qual é o papel de cada uma?
2. Por que separar responsabilidades em múltiplos prompts especializados é preferível a um único prompt longo em sistemas de agentes de produção?

## Histórico de Atualizações
- 2026-04-02: Nota criada a partir de Telegram