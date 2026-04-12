---
tags: []
source: https://x.com/i/status/2039978114655441141
date: 2026-04-03
tipo: aplicacao
---
# Implementar Sistema de 3 Camadas de Context Engineering com Claude Skills

## O que e

Claude Skills é uma arquitetura de gerenciamento de contexto em três camadas que permite ao Claude Code operar com centenas de habilidades especializadas sem estourar o limite de tokens da janela de contexto. A inteligência do sistema está em carregar apenas o mínimo necessário em cada momento, mantendo o restante em disco e acessando sob demanda. Isso importa porque resolve um dos maiores gargalos práticos no uso de agentes com LLMs: quanto mais capacidades você adiciona, mais tokens você consome antes mesmo de começar a tarefa.

## Como implementar

**Pré-requisitos e estrutura de diretórios**

Para replicar essa arquitetura hoje, você precisa do Claude Code (CLI da Anthropic, instalável via `npm install -g @anthropic-ai/claude-code`) e de um projeto com a seguinte estrutura mínima:

```
projeto/
├── CLAUDE.md                  ← Camada 1: contexto principal
├── .claude/
│   └── skills/
│       ├── escrever-testes.md     ← Skill completa
│       ├── revisar-pr.md
│       ├── deploy-staging.md
│       └── gerar-migrations.md
├── scripts/                   ← Arquivos de suporte (não pré-carregados)
│   ├── run_tests.sh
│   └── deploy.py
└── templates/
    └── pr_template.md
```

---

**Camada 1 — Main Context (`CLAUDE.md`)**

Este arquivo é carregado automaticamente pelo Claude Code em toda sessão. Deve ser enxuto e conter apenas: configuração do projeto, stack tecnológica, convenções de código, e o mapa de skills disponíveis com suas descrições de uma linha. Exemplo real:

```markdown
# Projeto: API de Pagamentos

## Stack
- Python 3.12, FastAPI, PostgreSQL 16, Redis
- Testes: pytest + testcontainers
- CI: GitHub Actions

## Skills disponíveis
- `escrever-testes`: Gera testes de integração com testcontainers
- `revisar-pr`: Checklist de revisão seguindo nossos padrões
- `deploy-staging`: Pipeline completo de deploy no ambiente de staging
- `gerar-migrations`: Alembic migrations a partir de mudanças nos models

## Convenções
- Snake_case para variáveis, PascalCase para classes
- Toda função pública precisa de docstring no padrão Google
```

O objetivo é manter este arquivo abaixo de 500 tokens. Não inclua documentação detalhada aqui.

---

**Camada 2 — Skill Metadata (YAML frontmatter)**

Cada arquivo de skill começa com um frontmatter YAML mínimo — entre 2 e 3 linhas, menos de 200 tokens. Esse metadata é o que o Claude lê para decidir qual skill ativar, sem carregar o conteúdo completo do arquivo:

```yaml
---
name: escrever-testes
trigger: "quando precisar criar testes de integração ou unitários"
requires: [pytest, testcontainers, docker]
---
```

A lógica aqui é análoga a um índice de livro: você lê os títulos dos capítulos para saber onde ir, sem ler o capítulo inteiro. O Claude Code faz exatamente isso — varre os frontmatters de todas as skills para construir um mapa de capacidades com custo mínimo de tokens.

---

**Camada 3 — Active Skill Context (corpo do arquivo `.md`)**

O conteúdo completo da skill é carregado apenas quando ativada. Este é o lugar para ser detalhado: passo a passo, exemplos de código, edge cases, comandos exatos. Exemplo para a skill `escrever-testes`:

```markdown
---
name: escrever-testes
trigger: "quando precisar criar testes de integração ou unitários"
requires: [pytest, testcontainers, docker]
---

# Skill: Escrever Testes

## Padrão de estrutura
Sempre use o padrão Arrange-Act-Assert explícito com comentários.

## Setup do testcontainer
```python
@pytest.fixture(scope="session")
def postgres_container():
    with PostgresContainer("postgres:16") as pg:
        yield pg.get_connection_url()
```

## Regras deste projeto
1. Nunca mockar a camada de banco em testes de integração
2. Cada teste deve limpar seu próprio estado com `TRUNCATE ... CASCADE`
3. Fixtures de dados ficam em `tests/fixtures/`

## Comandos
- Rodar suite completa: `pytest tests/ -v --tb=short`
- Rodar apenas integração: `pytest tests/integration/ -m integration`
```

---

**Arquivos de suporte — zero tokens**

Scripts em `scripts/`, templates em `templates/`, e arquivos de configuração não são referenciados no contexto. Eles são acessados diretamente pelo sistema de arquivos quando a skill ativa precisa deles — o Claude Code os lê via tool use (`read_file`) apenas no momento de uso. Isso significa que você pode ter dezenas de scripts auxiliares sem custo nenhum de tokens até o exato momento em que são necessários.

---

**Ativando skills na prática**

Com esta estrutura, o fluxo de uso é:
1. Abrir uma sessão Claude Code no diretório do projeto
2. O Claude carrega automaticamente `CLAUDE.md` (Camada 1) e os frontmatters de todas as skills (Camada 2)
3. Ao receber uma tarefa como "crie testes para o endpoint `/payments`", o Claude identifica pelo metadata que `escrever-testes` é a skill relevante
4. Carrega o arquivo completo `escrever-testes.md` (Camada 3)
5. Executa a tarefa usando o contexto específico daquela skill

Para forçar uma skill explicitamente: `use a skill escrever-testes para criar testes do PaymentService`.

---

**Escalando para centenas de skills**

Com frontmatters de ~150 tokens cada, 200 skills custam apenas ~30.000 tokens de metadata — viável dentro das janelas de contexto atuais. O conteúdo completo das skills (que pode somar centenas de milhares de tokens) nunca é carregado de uma vez. Organize skills em subdiretórios temáticos para projetos grandes:

```
.claude/skills/
├── backend/
├── frontend/
├── infra/
└── qualidade/
```

## Stack e requisitos

- **Claude Code CLI**: `npm install -g @anthropic-ai/claude-code` (Node.js 18+)
- **Conta Anthropic**: API key com acesso ao Claude 3.5 Sonnet ou Claude 3 Opus
- **Custo estimado**: Claude 3.5 Sonnet custa ~$3/MTok input; uma sessão típica com 3 camadas carregadas fica em torno de 5.000–15.000 tokens de contexto de sistema, o que representa menos de $0.05 por sessão
- **Formato dos skills**: Markdown com YAML frontmatter (sem dependências externas)
- **Sistema operacional**: macOS, Linux ou WSL2 no Windows
- **Hardware**: Nenhum requisito especial — processamento ocorre na API da Anthropic
- **Sem framework adicional**: A arquitetura é implementada em arquivos de texto puro, sem bibliotecas

## Armadilhas e limitacoes

**`CLAUDE.md` inflado invalida a Camada 1**: Se o arquivo principal crescer sem controle (documentação inline, exemplos longos, histórico de decisões), você derrota o propósito do sistema. Mantenha-o como um índice, não como uma wiki. Separe documentação extensa em arquivos referenciados pelas skills.

**Frontmatter mal escrito quebra a seleção de skills**: Se o campo `trigger` for vago ou ambíguo entre múltiplas skills, o Claude pode ativar a skill errada ou não ativar nenhuma. Escreva triggers descritivos e distintos. Teste com prompts reais e veja qual skill é selecionada.

**Dependências circulares entre skills**: Se a skill A referencia a skill B que referencia documentação que duplica conteúdo da skill A, você cria redundância e inconsistência. Mantenha cada skill auto-suficiente ou use arquivos de suporte compartilhados acessados via tool use.

**Não é adequado para contexto altamente dinâmico**: Se as regras e padrões do projeto mudam com frequência, manter múltiplos arquivos `.md` sincronizados vira overhead. Nesse caso, um único `CLAUDE.md` mais completo pode ser mais pragmático.

**Sem versionamento explícito das skills**: Esta arquitetura não tem mecanismo nativo de versionar skills. Se você mudar a skill `deploy-staging` enquanto um agente está em execução longa, pode haver inconsistência. Em pipelines críticos, versione os arquivos de skills com git e use tags.

**Não substitui RAG para bases de conhecimento grandes**: Para documentação com dezenas de milhares de páginas, a arquitetura de 3 camadas ainda não é suficiente. Nesse caso, combine com um sistema de RAG que alimenta as skills com chunks relevantes sob demanda.

**Custo invisível de tool calls**: Cada acesso a arquivo de suporte via `read_file` é uma tool call com latência e eventual custo de tokens no output. Em workflows que a