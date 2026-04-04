---
tags: [memoria, agentes, claude-code, letta, persistencia]
source: https://x.com/ihtesham2005/status/2037484864090644653?s=20
date: 2026-04-02
tipo: aplicacao
---

# Implementar Memória Persistente em Agentes de Código com Letta

## O que e

Claude Subconscious (arquitetura baseada em Letta framework) adiciona memória de longo prazo a Claude Code rastreando contexto de projeto em 8 blocos persistentes entre sessões. Elimina amnésia de agentes ao injetar resumos automaticamente antes de novas interações.

## Como implementar

**Arquitetura central**: Agente secundário (Letta) roda em background após cada resposta de Claude Code, coleta transcript da sessão, indexa codebase, e atualiza 8 blocos de memória estruturados. Antes de prompt seguinte, agente busca fragmentos relevantes e injeta-os no contexto de Claude Code sem latência perceptível (assíncrono).

**Blocos de memória**:
1. **Preferências de estilo** — lingüística e estrutural (indentação, camelCase vs snake_case, comments verbosos vs sucintos)
2. **Padrões arquiteturais** — decisões de design recorrentes (MVC vs MVVM, monolith vs microserviços)
3. **Stack tecnológico** — frameworks, libraries e versões em uso
4. **TODOs e refactorings** — itens em progresso (não conclusos em sessão anterior)
5. **Funções frecuentes** — utilities reutilizáveis (logging, error handling)
6. **Decisões de API** — contratos de endpoints, nomeação de recursos
7. **Contexto do projeto** — goals, constraints, timelines
8. **Padrões de teste** — frameworks e abordagens de testing observadas

**Instalar Letta e integrar com Claude Code**:
```bash
pip install letta
letta start  # Inicia daemon
```

**Configurar Claude Code com hook de memória**:
```json
{
  "memoryAgent": {
    "enabled": true,
    "backend": "letta",
    "indexCodebase": true,
    "updateFrequency": "after-response",
    "blockCount": 8,
    "injectionStrategy": "relevance-based"
  }
}
```

**Exemplo de fluxo**:
1. Usuário pede: "refactor this component"
2. Claude Code gera solução
3. **Pós-resposta**: Letta lê transcript, detecta padrão (ex: "preferencia por functional components"), atualiza bloco 1
4. **Próxima sessão**: Usuário abre projeto, Claude injeta "hint" do bloco 1 antes de qualquer interação

**Indexar codebase** (setup inicial):
```python
from letta import MemoryAgent

agent = MemoryAgent(project_path="/path/to/project")
agent.index_codebase()  # Escaneia todos os arquivos
agent.extract_blocks()  # Extrai os 8 blocos automaticamente
```

**Injetar memória manualmente** (debug):
```python
memory = agent.get_memory()
print(memory.blocks[0])  # Preferências de estilo
print(memory.blocks[4])  # Funções frecuentes

# Atualizar um bloco específico
agent.update_block(index=2, content="Now using FastAPI instead of Flask")
```

**Compartilhamento entre repositórios**: Configurar agente global em lugar central:
```bash
letta config --global-memory-path=/path/to/shared/memory.db
# Todos os projetos acessam mesma base de memória
```

## Stack e requisitos

- **Letta**: 0.4.0+ (MIT license, Python 3.8+)
- **Claude Code**: versão com suporte a hooks (2026.01+)
- **Persistência**: SQLite por padrão, PostgreSQL para produção
- **Armazenamento**: 10-100MB por projeto (índices de codebase)
- **Overhead**: <5% latência adicional (operações assíncronas)
- **RAM**: +50MB para daemon Letta

## Armadilhas e limitacoes

- **Bloat de contexto**: Se codebase cresce rapidamente, índice fica enorme; usar filtering para reduzir relevância (ex: ignorar node_modules).
- **Inconsistência**: Blocos podem ficar desincronizados se múltiplas sessões rodam em paralelo; usar locks.
- **Privacy**: Memória persistente contém decisões/padrões do projeto; garantir acesso restrito se código é sensível.
- **Relevance ranking**: Injetar todos 8 blocos pode causar "context pollution"; Letta tenta ser inteligente mas nem sempre acerta.
- **Descontinuidade**: Se mudar radicalmente tecnologia (ex: Python → Rust), blocos antigos viram noise.

## Conexoes

[[Memory Stack para Agentes de Codigo]] [[Claude Code Melhores Praticas]] [[Orquestracao Hibrida de LLMs]]

## Historico

- 2026-04-02: Nota criada
- 2026-04-02: Reescrita para template aplicacao