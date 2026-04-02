---
name: obsidian-daily-review
description: Revisão diária do vault Obsidian da Leticia
---

Use o comando /obsidian para fazer a revisão diária do vault da Leticia.

Faça o seguinte:
1. Liste todas as notas modificadas nas últimas 24 horas via GET http://127.0.0.1:27123/vault/ com o header Authorization: Bearer bb5f96c3d6639b0db426877ed96c5fbec6d4eaf2a2b3f07b09a71815044176b2
2. Leia o conteúdo das notas da pasta raiz e subpastas relevantes
3. Extraia todos os todos, decisões e ideias pendentes
4. Crie uma nova nota chamada "Daily Review - YYYY-MM-DD" (com a data de hoje) via PUT http://127.0.0.1:27123/vault/Daily Reviews/Daily Review - YYYY-MM-DD.md contendo:
   - Resumo do que foi trabalhado ontem (3-5 frases)
   - Lista de todos pendentes agrupados por projeto
   - 3 prioridades sugeridas para hoje
   - Novas ideias ou descobertas capturadas
5. Use sempre frontmatter YAML com date e tags: [daily-review, auto-generated]