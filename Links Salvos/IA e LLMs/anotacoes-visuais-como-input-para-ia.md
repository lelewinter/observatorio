---
tags: []
source: https://x.com/om_patel5/status/2036599662665249060?s=20
date: 2026-04-02
---
# Anotações Visuais como Input para IA

## Resumo
Ferramenta open source que permite desenhar diretamente sobre a tela — círculos, setas e textos — para comunicar problemas de UI a um agente de IA, substituindo descrições textuais ambíguas por feedback visual direto.

## Explicação
A comunicação entre humano e agente de IA via texto puro sofre de um problema fundamental: linguagem natural é inerentemente ambígua para descrever elementos visuais. Dizer "o botão está mal alinhado" ou "essa seção parece estranha" obriga o modelo a inferir o que o usuário está vendo, gerando múltiplos ciclos de tentativa e erro. A ferramenta descrita resolve isso ao tornar a tela um canvas de anotações: o usuário circula o problema, adiciona uma seta, escreve uma nota cursiva diretamente sobre o que precisa ser corrigido.

O mecanismo central é a conversão dessas anotações em input multimodal para o modelo. O Claude Code (ou qualquer modelo com visão) recebe a imagem anotada como contexto, eliminando a lacuna semântica entre "o que o usuário vê" e "o que o modelo entende". Isso reduz drasticamente a quantidade de turnos necessários para convergir em uma solução.

Do ponto de vista de design de sistemas de IA, isso representa uma mudança de paradigma na interface humano-agente: ao invés de adaptar o humano para comunicar em linguagem que o modelo entenda bem, adapta-se a interface para que o humano use sua forma natural de comunicação (apontar, circular, desenhar). Ferramentas como esta são exemplos práticos de como o gargalo de produtividade em agentic workflows não está na capacidade do modelo, mas na qualidade e forma do input fornecido.

O fato de ser free e open source também sinaliza uma tendência de tooling comunitário emergindo ao redor de agentes de código, onde desenvolvedores constroem suas próprias extensões de interface para suprir limitações de UX dos produtos principais.

## Exemplos
1. **Debug de UI com Claude Code**: Após o agente renderizar um componente React com espaçamento errado, o desenvolvedor circula o elemento problemático e escreve "padding errado aqui" — o modelo recebe a imagem anotada e corrige diretamente.
2. **Revisão de design iterativo**: Designer usa a ferramenta para marcar múltiplos elementos em uma única screenshot, enviando feedback consolidado ao invés de descrever cada problema em mensagens separadas.
3. **Pair programming visual**: Em sessões de desenvolvimento front-end, o programador anota a diferença entre o mockup esperado e o resultado renderizado, usando setas para comparar regiões específicas.

## Relacionado
*(Nenhuma nota relacionada disponível no vault no momento.)*

## Perguntas de Revisão
1. Por que anotações visuais reduzem o número de turnos em um ciclo de feedback com agentes de IA comparado a descrições textuais?
2. Quais outros gargalos de input humano-agente poderiam ser resolvidos com abordagens similares de interface multimodal?

## Histórico de Atualizações
- 2026-04-02: Nota criada a partir de Telegram