---
tags: []
source: https://x.com/jasondoesstuff/status/2039444150743867561?s=20
date: 2026-04-02
---
# Motion Graphics Gerados por IA com Design System

## Resumo
É possível usar um agente de código (como Claude Code) para extrair automaticamente o design system de um projeto existente e, a partir dele, gerar motion graphics programáticos com Remotion, mantendo consistência visual total.

## Explicação
O fluxo consiste em três etapas encadeadas: primeiro, um agente de IA analisa o projeto/app atual e documenta seu design system em um arquivo markdown (`design-system.md`), capturando tokens de cor, tipografia, espaçamento e componentes. Em seguida, instala-se o Remotion — uma biblioteca que permite criar vídeos e animações usando React e código JavaScript. Por fim, o agente utiliza o design system extraído como contexto para gerar animações de interações do próprio app, produzindo motion graphics programaticamente coerentes com a identidade visual existente.

O que torna essa abordagem relevante é a eliminação do gargalo criativo-técnico entre design e produção de vídeo. Tradicionalmente, criar b-roll animado ou demos de produto exigiria um designer de motion graphics trabalhando manualmente em ferramentas como After Effects. Aqui, a IA age como uma ponte entre o artefato de código existente e a produção audiovisual, sem intervenção humana especializada em cada etapa.

A capacidade de mockar apps populares (como Slack) sugere que o agente pode trabalhar não apenas com projetos próprios, mas também recriar interfaces conhecidas como referência — útil para estudos comparativos, apresentações ou conteúdo educativo. O formato 16:9 mencionado indica uso direto como b-roll para YouTube, mostrando aplicação imediata em produção de conteúdo.

## Exemplos
1. **B-roll para YouTube**: Gerar animações de fluxos do próprio SaaS em 16:9 para usar como material de apoio em vídeos explicativos, sem contratar motion designer.
2. **Demo de produto**: Criar animações das interações principais de um app para landing pages ou pitch decks, garantindo que os tokens visuais sejam fiéis ao produto real.
3. **Mockup de referência**: Recriar interfaces de apps conhecidos (Slack, Notion) animadas para comparações de UX ou tutoriais.

## Relacionado
*(Nenhuma nota relacionada disponível no vault no momento.)*

## Perguntas de Revisão
1. Quais são os limites do que um agente de IA consegue extrair automaticamente como "design system" de um projeto — ele captura apenas CSS/tokens ou também padrões de interação?
2. De que forma o uso de Remotion (React-based) facilita a integração com o design system extraído em comparação com ferramentas de vídeo tradicionais?

## Histórico de Atualizações
- 2026-04-02: Nota criada a partir de Telegram