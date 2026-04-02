---
tags: []
source: https://x.com/namcios/status/2037956753812328761?s=20
date: 2026-04-02
---
# Layout de Texto Sem DOM

## Resumo
Pretext é uma biblioteca TypeScript que realiza medição e layout de texto inteiramente em aritmética pura, sem tocar no DOM, eliminando o reflow do browser e sendo ~500x mais rápida que a abordagem tradicional via CSS.

## Explicação
O reflow do browser é o processo pelo qual o motor de renderização recalcula posições e dimensões de elementos após qualquer mudança no DOM ou no CSS. Toda vez que uma aplicação precisa saber a altura ou largura de um bloco de texto — algo trivial em UIs modernas — o browser precisa pausar a thread principal, executar esse cálculo e devolver o resultado. Em interfaces complexas como dashboards, chats ou layouts responsivos, isso acontece centenas de vezes e é uma das principais causas de travamento perceptível ao usuário.

O CSS foi arquitetado nos anos 1990 para servir documentos estáticos. Sua pipeline de layout nunca foi redesenhada para aplicações interativas em tempo real. A abordagem do Pretext é radical: substituir essa pipeline por aritmética pura em TypeScript, rodando inteiramente no userland, sem qualquer interação com o DOM. Isso torna o layout de texto determinístico, previsível e executável fora do contexto do browser — inclusive em workers, servidores ou ambientes de renderização headless.

O aspecto mais significativo do processo de desenvolvimento é metodológico: Cheng Lou utilizou Claude Code e Codex para construir a biblioteca, alimentando os modelos com o "ground truth" do comportamento real do browser e iterando até convergir em precisão. Isso representa um padrão emergente de engenharia onde um especialista humano define as invariantes e o critério de correção, e a IA executa a exploração do espaço de solução. O resultado suporta CJK, árabe RTL, emojis e clusters de grafemas — cobrindo a complexidade tipográfica global.

## Exemplos
- **Chat em tempo real**: renderizar bolhas de mensagem com altura calculada antes de inserir no DOM, eliminando o salto visual causado por reflows tardios.
- **Editores de layout tipo revista**: calcular quebras de coluna e posicionamento de blocos de texto sem depender do ciclo de renderização do browser.
- **Renderização server-side de UI**: gerar layouts de texto precisos em Node.js ou Deno sem instanciar um browser headless como Puppeteer.

## Relacionado
*(Nenhuma nota relacionada disponível no vault no momento.)*

## Perguntas de Revisão
1. Por que o reflow do browser é inerentemente bloqueante, e o que na arquitetura do CSS torna esse problema difícil de resolver incrementalmente?
2. Qual é a diferença entre calcular layout de texto no userland versus delegar ao motor de renderização, e quais são os trade-offs de precisão e manutenção a longo prazo?

## Histórico de Atualizações
- 2026-04-02: Nota criada a partir de Telegram