---
date: 2026-03-24
tags: [ia, automacao, orquestrador, agentes, claude-code, produtividade]
source: https://x.com/glaucia_lemos86/status/2036246906347655325?s=20
autor: "@glaucia_lemos86"
tipo: aplicacao
---

# Configurar Maestri para Orquestração Visual de Múltiplos Agentes IA

## O que é

Interface visual (Canvas 2D) que coordena múltiplos agentes de IA (Claude Code, Codex, GPT) trabalhando simultaneamente em um projeto, com visibilidade total de estado, dependências e fluxo de dados. Elimina context-switching e ineficiência de coordenação manual entre agentes.

## Como implementar

### Fase 1: Download e Setup Inicial

Maestri roda em macOS/Linux (Windows: use WSL2).

```bash
# Clone repositório
git clone https://github.com/EvertJr/maestri.git
cd maestri

# Instale dependências
npm install
# ou
pip install -r requirements.txt

# Inicie a aplicação
npm start  # Abre interface web em http://localhost:3000
```

### Fase 2: Configurar Agentes

Na interface Maestri, adicione seus agentes disponíveis:

```
Painel "Agentes":
  + Novo Agente
    Nome: Claude-CodeGeneration
    Tipo: Claude Code
    API Key: [sua chave Anthropic]
    Modelo: claude-opus-4-1
    Papel: "Escreve código novo e refactora"

  + Novo Agente
    Nome: Claude-Testing
    Tipo: Claude Code
    Modelo: claude-opus-4-1
    Papel: "Escreve testes e valida"

  + Novo Agente
    Nome: Qwen-Local
    Tipo: Ollama (local)
    Endpoint: http://localhost:11434
    Modelo: qwen2.5-32b
    Papel: "Testes rápidos, documentação"
```

### Fase 3: Definir Workflow no Canvas

Arraste agentes no canvas e conecte com fluxos de dados:

```
[Canvas 2D]

┌─────────────────────────────────────────────┐
│  Entrada: "Implementar função X"             │
└────────────┬────────────────────────────────┘
             │
             ▼
┌─────────────────────────────────────────────┐
│  Claude-CodeGeneration                       │
│  Prompt: "Implemente a função X segundo...   │
│  Output: code_generated.py                   │
└────────────┬────────────────────────────────┘
             │
             ▼
┌─────────────────────────────────────────────┐
│  Claude-Testing                              │
│  Prompt: "Escreva testes para..."            │
│  Wait-for: code_generated.py                 │
│  Output: test_generated.py                   │
└────────────┬────────────────────────────────┘
             │
             ▼
┌─────────────────────────────────────────────┐
│  Qwen-Local                                  │
│  Prompt: "Gere documentação para..."         │
│  Input: code_generated.py, test_generated.py│
│  Output: README_generated.md                 │
└────────────┬────────────────────────────────┘
             │
             ▼
    [Aprovação Humana]
```

No Maestri, clique e arraste para criar essas conexões visualmente.

### Fase 4: Configurar Transições e Regras

Defina quando um agente começa com base no output de outro:

```json
{
  "workflow": "code-to-test-to-docs",
  "agents": [
    {
      "id": "codegen",
      "name": "Claude-CodeGeneration",
      "trigger": "manual",
      "on_complete": "notify:testing"
    },
    {
      "id": "testing",
      "name": "Claude-Testing",
      "trigger": "on_file_generated",
      "watch_file": "code_generated.py",
      "on_complete": "notify:docs"
    },
    {
      "id": "docs",
      "name": "Qwen-Local",
      "trigger": "on_files_ready",
      "require_files": ["code_generated.py", "test_generated.py"],
      "on_complete": "wait_approval"
    }
  ]
}
```

### Fase 5: Monitoramento e Feedback

Visualize em tempo real no Canvas:

- Verde: Agente completou tarefa
- Amarelo: Agente trabalhando
- Vermelho: Agente falhou ou esperando input
- Azul: Agente aguardando output de outro

Clique em qualquer agente para ver:
- Prompt enviado
- Output gerado
- Tempo decorrido
- Tokens usados (se disponível)

### Fase 6: Integração com seu Fluxo de Trabalho

Execute workflows via CLI:

```bash
maestri run --workflow code-to-test-to-docs \
  --input "Implemente algoritmo de busca binária em Python" \
  --output-dir ./generated
```

Ou via API REST:

```bash
curl -X POST http://localhost:3000/api/workflows/run \
  -H "Content-Type: application/json" \
  -d '{
    "workflow_id": "code-to-test-to-docs",
    "initial_prompt": "Implemente X"
  }'
```

## Stack e requisitos

- **Plataforma**: macOS 11+, Linux (Ubuntu 20+); Windows via WSL2
- **Node.js**: 16+
- **Python**: 3.9+ (para agentes que exigem Python)
- **RAM**: 4GB mínimo (8GB+ recomendado se rodar agentes locais)
- **APIs**: Anthropic key (Claude), OpenAI key (GPT, opcional), Ollama local (opcional)
- **Custo**: Maestri é free/open-source; custos vêm de tokens dos agentes premium
- **Escalabilidade**: Até ~5-10 agentes paralelos sem degradação visível

## Armadilhas e limitações

1. **Windows não suportado nativamente**: Use WSL2 ou aguarde port oficial.

2. **Overhead de coordenação**: Se agentes são muito interdependentes, o overhead de passing outputs entre eles pode superar ganho de parallelização. Melhor para workflows com etapas independentes.

3. **Visualização pode ficar confusa**: Em workflows com >8 agentes, canvas fica denso. Use agrupamento e subgrafos.

4. **Falha em cascata**: Se um agente falha, downstream pode ficar esperando. Defina timeouts e fallback claros.

5. **Custo não-óbvio**: Fácil deixar agentes premium rodando em paralelo desnecessariamente. Monitore uso.

## Conexões

- [[Claude Code - Melhores Práticas]] — integração com Claude Code
- [[Indexacao de Codebase para Agentes IA]] — cada agente deve ter acesso ao índice
- [[Otimizar Uso Rate Limit Claude Pro Max]] — coordenar rate limits entre agentes
- [[mcp-unity-integracao-ia-editor-nativo]] — padrão similar para Unity

## Histórico

- 2026-03-24: Nota original sobre Maestri
- 2026-04-02: Guia de setup e configuração

## Exemplos

Casos de uso incluem aumentar produtividade como desenvolvedor, compartilhar soluções com a comunidade, demonstrar viabilidade de orquestração visual de agentes. Próximas etapas esperadas: possível suporte para Windows, expansão para outros agentes de IA, melhorias na interface de Canvas, integrações com mais ferramentas de desenvolvimento, possível marketplace de workflows.

## Relacionado

- [[Indexacao de Codebase para Agentes IA]]
- [[Otimizar Uso Rate Limit Claude Pro Max]]
- [[crucix_agente_inteligencia_pessoal]]
- [[Claude Peers Multiplas Instancias Coordenadas]]
- [[ComfyUI Posicionamento Agent Wave]]

## Perguntas de Revisão

1. Como interface visual em Canvas 2D muda a coordenação de múltiplos agentes?
2. Por que ver estado de cada agente em tempo real importa para eficiência de time?
3. Qual é a diferença entre Claude Peers (automático) e Maestri (visual/centralizado)?
