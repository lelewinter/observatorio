---
tags: []
source: https://x.com/rubenhassid/status/2034999221703581818?s=20
date: 2026-04-02
tipo: aplicacao
---
# Contexto Persistente: Arquivos de Configuração Pessoal para LLMs

## O que e
Em vez de refazer instruções a cada sessão, centraliza representação do usuário em arquivos .md estruturados — identidade, estilo, exemplos, restrições — carregados automaticamente antes de cada interação. O modelo tem acesso instantâneo a uma "biografia do usuário" sem gastar tokens reescrevendo contexto manualmente. Transforma prompting isolado em sistema de memória externa.

## Como implementar
Cria pasta de contexto pessoal com arquivos como: `about-me.md` (quem é, nível técnico, objetivos), `writing-style.md` (tom preferido, patterns, antipadrões), `examples-work.md` (3-5 amostras de saídas aprovadas), `constraints.md` (absolutamente não faça X, Y, Z), `preferences.md` (tecnologias favoritas, preferências de código). No Claude, upload a pasta via "Cowork" — o modelo lê todos antes de responder. Patterns úteis: um meta-prompt inicial pedindo esclarecimentos antes de agir ("pergunte 3 coisas antes de começar"); outro meta-prompt para redirecionar conversas fora do trilho sem perder contexto ("resumo objetivo, liste assumptions, peça confirmação"). Implementação paralela: integra RAG (Retrieval-Augmented Generation) ao nível pessoal em vez de base de conhecimento — "retrieval" é total (lê tudo) não seletivo.

Workflow de manutenção: revisa contexto a cada 2-4 semanas, adiciona padrões novos conforme o gosto evolui. Usar [[obsidian]] ou [[vscode]] para versionar os arquivos, garantindo histórico de mudanças no contexto pessoal.

## Stack e requisitos
Editor de texto (vscode, obsidian) + acesso a Claude web ou aplicação desktop. Tamanho recomendado: ~20-40KB total (5-10 arquivos, 2-5KB cada). Se exceder 200KB, o modelo começa a ignorar partes (similar ao problema de CLAUDE.md muito longo). Upload via filepicker ou drag-drop. Sem custo adicional — apenas tokens gastos na leitura do contexto na primeira requisição de cada sessão.

## Armadilhas e limitacoes
Contexto desatualizado = modelo gera outputs baseado em informação velha; revisa regularmente. Se arquivos forem contraditórios (about-me diz "detesto Python" mas examples-work mostra código Python), modelo segue as contradições gerando outputs confusos. Arquivo muito genérico ("seja criativo") não adiciona valor; ser específico é mais útil ("use estrutura de 3 partes, máx 500 palavras"). Não inclua dados sensíveis (senhas, chaves API) — contexto pode ser capturado.

## Conexoes
[[estrutura-claude-md-menos-200-linhas|CLAUDE.md compacto]]
[[embeddings-multimodais-em-espaco-vetorial-unificado|RAG e recuperação]]
[[geracao-automatizada-de-prompts|Prompts otimizados]]

## Historico
- 2026-04-02: Nota criada
- 2026-04-02: Reescrita pelo pipeline
