---
tags: [prompt-engineering, llm-agents, claude, arquitetura-de-agentes, multi-agent, engenharia-de-software]
source: https://x.com/NieceOfAnton/status/2039277883127103501?s=20
date: 2026-04-01
---
# Claude Code opera com 26 prompts especializados organizados em camadas funcionais distintas, revelando uma arquitetura modular de agentes como padrão para ferramentas de IA de produção

## Resumo
O Claude Code, ferramenta de codificação da Anthropic, utiliza 26 prompts distintos organizados em categorias funcionais (sistema, ferramentas, agentes, memória, coordenação e utilidades). Essa arquitetura foi reconstruída a partir do código-fonte npm publicado acidentalmente e disponibilizada sob licença MIT.

## Explicação
A arquitetura do Claude Code revela que ferramentas de IA sofisticadas não operam com um único prompt monolítico, mas com um sistema hierárquico de prompts especializados. O prompt de sistema define identidade, segurança e roteamento de ferramentas — a "constituição" do agente. Abaixo dele, 11 prompts de ferramentas cobrem operações atômicas como shell, manipulação de arquivos e busca, enquanto 5 prompts de agentes encapsulam papéis cognitivos distintos: explorador, arquiteto, verificador e documentador.

Um padrão arquitetural especialmente relevante é a presença de um agente dedicado exclusivamente a tentar quebrar o código antes do deploy — um "red team" automatizado embutido no pipeline. Isso materializa o princípio de que segurança e verificação não são etapas externas, mas componentes de primeira classe dentro do sistema. Complementarmente, há regras anti-over-engineering explicitamente codificadas nos prompts ("não adicione features além do solicitado"), o que demonstra que restrições comportamentais podem e devem ser injetadas via prompt, não apenas via treinamento.

O subsistema de memória merece atenção especial: 4 prompts gerenciam compressão de sessão em 9 seções estruturadas, preservando obrigatoriamente todas as mensagens do usuário. Isso resolve um problema clássico de agentes de longa duração — a perda de contexto — através de sumarização estruturada em vez de simples truncamento. O prompt coordenador de multi-agentes funciona como orquestrador, delegando tarefas entre os demais agentes, o que é o padrão arquitetural central em sistemas como AutoGen e similares.

O sistema de risco em camadas é outro padrão exportável: o agente edita arquivos livremente (baixo risco), mas solicita permissão explícita antes de operações destrutivas como force-push (alto risco). Isso implementa o princípio do menor privilégio de forma dinâmica e contextual, adaptada ao domínio de desenvolvimento de software.

## Exemplos
1. **Construção de agente próprio**: Usar a mesma separação de camadas — um prompt de sistema para identidade, prompts de ferramenta para ações atômicas, e um prompt coordenador para orquestração — ao construir qualquer agente de automação de tarefas complexas.
2. **Pipeline de revisão de código com red team embutido**: Implementar um sub-agente cujo único papel é tentar invalidar, encontrar bugs ou quebrar o output do agente principal antes de entregar o resultado ao usuário.
3. **Gestão de contexto em sessões longas**: Adotar o padrão de compressão em seções fixas (ex: objetivos, decisões tomadas, próximos passos, mensagens do usuário) para manter coerência em conversas que ultrapassam a janela de contexto.

## Relacionado
*(Nenhuma nota existente no vault para conectar neste momento.)*

## Perguntas de Revisão
1. Quais são as seis categorias funcionais de prompts no Claude Code e qual é a responsabilidade específica de cada uma?
2. Por que separar a lógica de um agente em múltiplos prompts especializados é preferível a um único prompt monolítico em sistemas de produção?

## Histórico de Atualizações
- 2026-04-01: Nota criada a partir de Telegram