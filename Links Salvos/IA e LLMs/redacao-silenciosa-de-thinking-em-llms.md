---
tags: []
source: https://x.com/Butanium_/status/2037575095569269201?s=20
date: 2026-04-02
---
# Redação Silenciosa de Thinking em LLMs

## Resumo
A partir da versão 2.1.69 do Claude Code, os "pensamentos" (thinking/reasoning tokens) do modelo são suprimidos silenciosamente por padrão, sem menção no changelog. É possível restaurá-los via configuração não documentada.

## Explicação
Modelos de linguagem com capacidade de raciocínio estendido (extended thinking) geram tokens intermediários que representam o processo de "pensamento" antes da resposta final. Esses tokens são valiosos para depuração, auditoria e compreensão do comportamento do modelo. No Claude Code v2.1.69, a Anthropic passou a suprimir silenciosamente esses tokens por padrão — sem anunciar a mudança no changelog oficial.

Essa decisão tem implicações diretas para transparência e observabilidade de sistemas baseados em LLMs. Usuários e desenvolvedores que dependem do thinking para inspecionar o raciocínio do modelo ou para fins de debug foram afetados sem aviso prévio. O comportamento silencioso — sem comunicação clara — é particularmente relevante em contextos onde a auditabilidade do modelo é requisito.

A configuração `"showThinkingSummaries": true` no arquivo `settings.json` restaura a exibição dos pensamentos, mas essa opção não está documentada oficialmente. Isso exemplifica um padrão recorrente em ferramentas de IA: funcionalidades críticas para poder avançado de usuário ficam ocultas em configurações não documentadas, acessíveis apenas via descoberta comunitária.

Do ponto de vista de segurança e controle, a supressão padrão pode ser justificada pela Anthropic como redução de ruído ou custo de contexto — mas a ausência de comunicação transparente levanta questões sobre governança de produto em ferramentas de IA voltadas a desenvolvedores.

## Exemplos
1. **Debug de comportamento inesperado**: Um desenvolvedor nota que o Claude Code parou de exibir seu raciocínio após atualização; adiciona `"showThinkingSummaries": true` ao `settings.json` para restaurar visibilidade.
2. **Auditoria de decisões do modelo**: Equipes que usam Claude Code em pipelines automatizados e precisam logar o raciocínio do modelo para compliance precisam ativar manualmente essa configuração.
3. **Descoberta comunitária como documentação alternativa**: A configuração foi descoberta e divulgada por usuários, não pela Anthropic — padrão comum em ecossistemas de ferramentas de IA em rápida evolução.

## Relacionado
*(Nenhuma nota relacionada disponível no vault no momento.)*

## Perguntas de Revisão
1. Por que a supressão silenciosa de thinking tokens é problemática do ponto de vista de transparência em ferramentas de IA para desenvolvedores?
2. Qual a diferença entre "thinking tokens" e a resposta final de um LLM com raciocínio estendido, e por que essa distinção importa para observabilidade?

## Histórico de Atualizações
- 2026-04-02: Nota criada a partir de Telegram