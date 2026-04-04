---
date: 2026-03-24
tags: [claude, preferencias-pessoais, chief-of-staff, writing, automacao]
source: https://www.linkedin.com/posts/clarama_if-youre-a-chief-of-staff-switching-to-claude-share-7441832145192472576-d926
autor: "@clarama"
tipo: aplicacao
---

# Configurar Preferências Pessoais do Claude para Conversas Eficientes

## O que é

Sistema de 7 preferências configuráveis no Claude que transformam o tom de conversação, eliminando padrões óbvios de IA e criando interlocução mais natural e parceira para roles executivas (Chief of Staff, estratégia, escrita de alto impacto).

## Como implementar

### Fase 1: Acessar Configurações

1. Abra Claude (web ou app)
2. Clique em seu avatar no canto superior direito
3. Selecione "Settings" → "Personal Preferences" (ou "Profile" → "Preferences")

### Fase 2: Configurar as 7 Preferências

**Preferência 1: Desabilitar Contrast Framing**

Adicione na seção "Writing Style":

```
IMPORTANTE: Nunca use estruturas de "contrast framing" como:
- "This isn't X, it's Y"
- "Rather than doing X, you should do Y"
- "While many people X, the truth is Y"

Essas construções são sinalizadores óbvios de texto gerado por IA.
Use estruturas diretas e naturais em vez disso.
```

**Preferência 2: Evitar Engagement Bait**

```
Evite completamente:
- "But here's the thing"
- "Here's what most people get wrong"
- "You won't believe this"
- "The truth is"
- Qualquer frase que tente dramatizar ou criar urgência artificial

Vá direto ao ponto. Seja honesto sobre incerteza.
```

**Preferência 3: Eliminar Em Dashes**

```
NUNCA use em dashes (—) em respostas.
Substitua por:
- Vírgulas para pauses curtos
- Períodos para pauses longos
- Reestruture a sentença para maior clareza

Exemplo ERRADO:
"Claude é poderoso — em certos contextos — mas tem limitações."

Exemplo CORRETO:
"Claude é poderoso em certos contextos, mas tem limitações."
```

**Preferência 4: English Spelling Americano** (se aplicável)

```
Use sempre variações americanas:
- "organization" (não "organisation")
- "optimize" (não "optimise")
- "color" (não "colour")

Consistência de estilo é sinal de profissionalismo.
```

**Preferência 5: Eliminar Therapy Speak**

```
Proibido:
- "That sounds really hard"
- "Let's unpack that"
- "I hear you"
- Linguagem infantilizante ou de validação emocional

Você é parceiro técnico, não terapeuta.
Seja direto sobre dificuldades e soluções.
```

**Preferência 6: Não Pular para Deliverables**

```
Comportamento esperado:
1. Você faz pergunta exploratória
2. Claude pergunta de volta: "Qual é o contexto? Por quê?..."
3. Vocês pensam JUNTOS antes de gerar output grande
4. Quando estiver pronto: "Quer que eu escreva um draft agora?"

NÃO: responder imediatamente com documento de 2 páginas sem validar.
SIM: conversa primeiro, entregável depois.
```

**Preferência 7: Manter no Trilho**

```
Protocolo:
- Na primeira mensagem de novo chat, defina escopo: "Este chat é sobre: [X]"
- Se eu derivar ou não entender a direção: avise
- Se pergunta muda de assunto significativamente: confirme se quer mudar tópico

Exemplo:
"Nota: Começamos falando sobre estratégia de pricing, agora estou falando de posicionamento. Quer continuar com essas duas conexadas, ou focar em uma?"
```

### Fase 3: Criar Arquivo PREFERÊNCIAS.md Privado

Mantenha no seu vault um arquivo com suas preferências:

```markdown
# Minhas Preferências de Conversa com Claude

## Tone
- Parceiro técnico, não assistente
- Questionar antes de implementar
- Direto sobre incerteza

## Escrita
- Sem contrast framing
- Sem engagement bait
- Sem em dashes, sem therapy speak
- Americano spelling

## Fluxo
- Pense comigo antes de entregar
- Fique no assunto definido
- Me questione se estiver perdido
```

Compartilhe com Claude ao iniciar chats críticos:

```
Cole isto no chat:

Você tem acesso às minhas preferências pessoais.
Sigamos meu estilo documentado em PREFERÊNCIAS.md
```

### Fase 4: Teste e Refine

**Primeira semana**: Note quando Claude não segue uma preferência. Adicione novo refinement:

```
"Percebi que você ainda usa XX. Por favor, reescreva evitando
essa construção. Aqui está um exemplo melhor: YY"
```

Claude aprende com feedback. Cada especificação torna futuras respostas melhores.

### Fase 5: Integração em Workflows

Para tarefas críticas (prezentações, comunicações executivas):

```
Prompt de setup:

"Vou compartilhar um documento. Atualize-o mantendo:
1. Minhas preferências de tom (parceiro técnico)
2. Estrutura clara SEM contrast framing
3. Direto, sem engagement bait
4. Pronto para compartilhar com [stakeholder específico]"
```

## Stack e requisitos

- **Acesso Claude**: Web (claude.ai) ou App
- **Dedicação**: ~20 min para configuração inicial, 5 min/mês para refine
- **Documentação**: Arquivo de preferências em seu vault
- **Custo**: Grátis (funciona em qualquer tier de acesso)

## Armadilhas e limitações

1. **Claude não é determinístico**: Mesmo com preferências, ocasionalmente gerará respostas que violam regras. Feedback corrige para futuro, não retroativamente.

2. **Preferências não se propagam entre chats**: Cada conversa é independente. Para aplicar sempre, salve em arquivo separado e compartilhe no início de chats críticos.

3. **Conflito de preferências**: Às vezes "direto e conciso" conflita com "parceiro questionador". Priorize: para exploração, seja questionador; para entrega, seja direto.

4. **Customização Demais Cria Inflexibilidade**: Se adicionar 50 regras, Claude pode ficar paralizado. Mantenha ~7-10 preferências principais.

5. **Impacto é 80% Conversa, 20% Preferências**: As melhores conversas vêm de prompts de qualidade, não de preferências. Use preferências para limpeza, não para salvação.

## Conexões

- [[Livro You and Your Research Richard Hamming]] — pensamento de qualidade em conversas
- [[Claude Code - Melhores Práticas]] — aplicar preferências no desenvolvimento
- [[otimizacao-de-tokens-em-llms]] — preferências também economizam tokens

## Histórico

- 2026-03-24: Conceito original de Clara Ma
- 2026-04-02: Guia prático de configuração

Como implementar: Settings → Profile → Personal Preferences, adicione cada preferência, teste em conversas, refine conforme trabalhar.

## Exemplos

Usar trigger words: "Do not proceed with creating anything until I say 'proceed'" permite Claude saber quando realmente quer output versus apenas explorando ideias.

Automação de branding: criar brand guide abrangente em Claude, exportar como documento, adicionar como arquivo para referência contínua, todos documentos criados automaticamente se encaixam no estilo. Unlock: apresentações e documentos profissionais e consistentes em minutos.

Usar skills para consistência: criar skill e ao completar tarefa para líder/cliente/organização específica, pedir a Claude para se referir à skill primeiro.

Para Chief of Staffs especificamente, essas preferências fazem diferença dramática em: qualidade das sugestões estratégicas, tom das comunicações preparadas, eficiência das sessões de brainstorming, naturalidade do output para compartilhar com stakeholders.

## Relacionado

- [[Livro You and Your Research Richard Hamming]]
- [[Claude Code - Ativar Resumo de Pensamentos]]
- [[Simplificar Setup Claude Deletar Regras Extras]]
- [[Claude Code - Melhores Práticas]]

## Perguntas de Revisão

1. Por que "contrast framing" é o sinalizador #1 de texto gerado por IA?
2. Como 7 preferências simples transformam Claude de "yes-man" para verdadeiro parceiro?
3. Qual é o padrão emergente em otimização: removação de patterns vs adição de features?
