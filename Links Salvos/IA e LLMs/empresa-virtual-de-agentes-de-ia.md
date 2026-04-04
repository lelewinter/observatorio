---
tags: []
source: https://x.com/ihtesham2005/status/2038934452538319205?s=20
date: 2026-04-02
tipo: aplicacao
---
# Claw-Empire: Empresa Virtual Simulada com Múltiplos Agentes IA

## O que e
Framework open-source que simula empresa de software completa onde agentes de IA (Claude Code, Gemini, etc.) operam como funcionários em departamentos especializados. CEO humano envia diretivas via Telegram/Slack, sistema distribui trabalho entre agentes, cada agente trabalha isolado em git worktree, merge requer aprovação humana. Roda 100% localmente com SQLite.

## Como implementar
**Arquitetura**: agentes multifuncionais com ~600 skills configuráveis (cada skill é função que agente pode invocar: "gerar relatório", "escrever código", "revisar PR"). Cada agente tem departamento (frontend, backend, QA, DevOps), nível de experiência (XP system), e vê a "empresa" via dashboard. **Setup**: inicializar com `claw-empire init`, definir agentes por departamento, mapear skills, estruturar empresa em organigrama JSON. **Fluxo**: CEO posta diretiva ("implementar autenticação OAuth") no canal Telegram → sistema quebra em subtarefas → agentes recebem tarefas paralelas em worktrees isoladas → cada agente trabalha, testa localmente → resultado mergea em branch staging → CEO aprova merge → integra em main. **Observabilidade**: dashboard visual em pixel-art mostra agentes se movendo pelo escritório, atas de reunião são geradas automaticamente, trilha de auditoria completa de quem fez o quê.

Diferencial: isolamento via git worktree garante que múltiplos agentes nunca corrompem base de código; controle humano sobre merge previne mudanças indesejadas. Sistema é extensível — adicionar agente novo = registrar na config + mapear skills.

## Stack e requisitos
Python 3.10+, Git 2.40+, Docker (opcional para containers isolados por agente). SQLite para estado/auditoria. LLM providers: Anthropic (Claude), Google (Gemini), OpenAI (GPT). Requer local machine com suficiente CPU para múltiplos agentes paralelos (recomendado 8+ cores). Armazenamento: ~500MB para projeto typical (código + estado SQLite). Custo: zero infrastructure (roda localmente) + tokens LLM por agente (estimado USD 5-50/dia para 5 agentes contínuos).

## Armadilhas e limitacoes
Agentes não têm memória de longo prazo entre sessões — reiniciam do zero (use SQLite para persistir estado crítico). Git worktree merge conflicts não são auto-resolvidos — conflitos reais de código persistem. Agentes podem gerar código errado confidentemente; sempre revisar antes de merge. Alucinação de skills: agente pode chamar skill que não existe se mal configurado. Sincronização entre agentes é eventual (não transacional); race conditions possíveis em paralelo não sincronizado.

## Conexoes
[[estudio-de-games-com-multi-agentes-ia|Multi-agentes paralelos]]
[[git-worktrees-para-agentes|Git worktrees isolamento]]
[[git-worktrees-desenvolvimento-paralelo-claude-code|Desenvolvimento paralelo]]
[[falhas-criticas-em-apps-vibe-coded|Code quality control]]

## Historico
- 2026-04-02: Nota criada
- 2026-04-02: Reescrita pelo pipeline
