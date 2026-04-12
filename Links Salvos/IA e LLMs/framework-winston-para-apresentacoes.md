---
tags: [apresentações, prompting, frameworks, comunicação, claude, ai, retórica, winston]
source: https://x.com/godofprompt/status/2039258111543046403?s=20
date: 2026-04-02
tipo: aplicacao
---

# Framework Winston: Estrutura de Apresentação Oral via Prompts no Claude

## O que é

Patrick Henry Winston, lendário professor de Ciência da Computação do MIT, desenvolveu framework de comunicação oral ensinado por 40+ anos que estrutura apresentações memoráveis em **elementos psicológicos comprovados**. O método Winston é baseado em retórica oral (oralidade = diferente de escrita), e não em design de slides.

Quando codificado em sequência de prompts estruturados, Claude consegue transformar conteúdo bruto em apresentação profissional seguindo os **6 pilares de Winston**: VSNC (Vision, Steps, News, Contributions) + elementos de comunicação como abertura impactante, "fence" (delimitação de escopo), exemplos progressivos, tema central repetido estrategicamente, fechamento membrável.

A inovação é **usar IA como assistente de retórica**: você fornece ideias brutas, Claude estrutura seguindo método comprovado de 40 anos em vez de deixar slides "vibe coded".

## Por que importa

Apresentações fracassam porque:
1. Falta **promise clara** — audiência não sabe para onde vai
2. Escopo nebuloso — você toca em 10 temas, audiência entende nenhum
3. Exemplos fora de ordem — começa complexo, nunca passa pelos casos simples
4. Repetição amadora — repete a mesma frase idêntica 3x (óbvio e chato)
5. Fechamento fraco — termina com "perguntas?" e audiência esqueceu por que importava

Winston resolve tudo isso com **estrutura sistemática**. Seu curso "How to Speak" é tradicional no MIT exatamente porque funciona.

Para quem consome muito conteúdo (Leticia): aprender a estruturar suas próprias apresentações (estudos em grupo, defesa de projeto, pitch de ideia) torna você **exponencialmente mais persuasivo**.

## Como funciona / Como implementar

### Entender os 6 elementos de Winston

#### 1. **Vision (Visão)**
Responda: "Por que isso importa?" Não é "técnico", é **emocional/prático**.

Exemplo fraco: "Vou falar sobre RAG"
Exemplo forte: "RAG é como dar ao seu modelo de IA acesso a um livro inteiro em tempo real — em vez de decorar tudo no treinamento, ele consulta quando precisa. Isso muda tudo em produção."

#### 2. **Steps (Passos)**
Qual é a **ordem lógica** para alguém entender?
- Para ensinar RAG: começa em "o que é embeddings?", depois "retrieval", depois "augmented generation"
- NÃO começa em "FAISS e HNSW" (agentes avançados)

#### 3. **News (Novidade/Contribuição)**
O que há de **novo** que você traz?
- Não é "RAG existe"
- É "RAG + streaming + multi-agent = pipeline que escala"

#### 4. **Contributions (Contribuições)**
Deixa **explícito** qual é a sua descoberta/método/framework.

### 6-Prompt Sequence prática

Crie uma sessão no Claude com seu outline bruto. Rode estes prompts em sequência:

**Prompt 1: Abertura (Hook)**
```
Tópico: Como implementar RAG em produção
Audiência: Engenheiros de software sem experiência com LLMs
Duração: 30 minutos

Gere uma abertura impactante que:
- NÃO usa piadas
- Estabelece por que RAG importa agora
- Deixa claro qual é a promise ("ao final você vai poder implementar RAG do zero")
- Máximo 3 minutos para ler em voz alta
```

Claude vai gerar algo como:
```
"Em 2025, a maioria dos LLMs ainda alucinam quando perguntados sobre dados privados da sua empresa. RAG (Retrieval-Augmented Generation) resolve isso: em vez de decorar tudo no treinamento, o modelo consulta seus dados em tempo real. Em 30 minutos, você vai entender como implementar isso, do zero, num projeto real. Vamos começar com uma pergunta: quantos de vocês já viram um chatbot inventar respostas com confiança total?"
```

**Prompt 2: Fence (Cerca de Escopo)**
```
Mantendo a mesma apresentação, defina explicitamente:
- O que SERÁ coberto (ex: embeddings via OpenAI, retrieval com FAISS, augmented prompt)
- O que NÃO será coberto (ex: fine-tuning, training custom embeddings, distributed RAG)

Deixe a audiência saber exatamente os limites.
```

**Prompt 3: Estrutura de Exemplos**
```
Crie uma progressão de 3 exemplos do simples ao complexo para RAG:
1. Exemplo simples: RAG com um único PDF, OpenAI embeddings, prompt único
2. Exemplo médio: RAG com múltiplos documentos, reranking, caching
3. Exemplo avançado: RAG com streaming, múltiplos LLMs, multi-step retrieval

Para cada exemplo: código mínimo funcional + explicação de 1-2 minutos
```

**Prompt 4: Tema Central Repetido**
```
Identifique a ideia central de toda a apresentação (ex: "Dados privados em tempo real = credibilidade + controle").
Gere 4-5 formas DIFERENTES de repetir esse tema ao longo da apresentação sem ser repetitivo:
- Abertura: tema como promise
- Exemplo 1: tema como benefício prático
- Transição meio: tema como contexto histórico
- Fechamento: tema como oportunidade futura
```

**Prompt 5: Transições e Estrutura**
```
Organize a apresentação em blocos com transições explícitas:
- Bloco 1: Fundamentals (3 min)
- Bloco 2: Exemplo simples (7 min)
- Bloco 3: Exemplo real em produção (10 min)
- Bloco 4: Próximos passos (5 min)
- Bloco 5: Q&A (5 min)

Cada bloco deve ter:
- 1 frase de abertura que conecta ao anterior
- Objetivo específico do bloco
- Transição para próximo bloco
```

**Prompt 6: Fechamento Memorável**
```
Gere um fechamento que:
- Resume a ideia central (tema repetido) em 1 frase marcante
- NÃO termina com "perguntas?"
- Deixa audiência com sensação de "eu posso fazer isso"
- Aponta próximos passos concretos
- Máximo 2 minutos
```

Exemplo:
```
"Hoje vocês aprenderam que RAG é essencialmente 'dar ao seu modelo acesso a biblioteca privada'. Não é magia. É pipeline. E é implementável em uma tarde. Vocês agora têm as ferramentas para fazer isso hoje. Meu último conselho: comece pequeno — um documento, um prompt, uma query. Depois escala. Qual é o seu primeiro caso de uso?"
```

### Fluxo prático completo (CLI)

```bash
# 1. Escrever outline bruto em txt
cat > presentation-outline.txt << 'EOF'
- RAG é retrieval-augmented generation
- Embeddings convertem texto em números
- Retrieval busca documentos similares
- Augmented prompt injeta contexto
- Exemplo com OpenAI + FAISS
- Considerações em produção
EOF

# 2. Iniciar sessão Claude
claude --with presentation-outline.txt

# 3. Rodar sequência de 6 prompts (vide acima)
# 4. Copiar saídas estruturadas para PowerPoint/Keynote
# 5. Praticar lendo em voz alta (40% do trabalho)
```

## Stack técnico

- **Modelo**: Claude 3.5 Sonnet ou superior
- **Input**: Outline texto/Markdown, detalhes de audiência e contexto
- **Output**: Markdown estruturado com notas de speaker
- **Conversão**: Copy para PowerPoint/Keynote/Google Slides (IA não faz design de slides, faz estrutura)
- **Prática**: Gravar áudio ou fazer ensaio com amigos para validar fluxo oral
- **Ferramentas de integração**:
  - [Obsidian + Templater](https://github.com/SilentVoid13/Templater) — pode automatizar seção de perguntas de revisão
  - [Whisper](https://github.com/openai/whisper) — transcrever sua prática para refinar
  - [Slides API](https://developers.google.com/slides/api) — gerar slides via API (futura automação)

## Código prático

### Template de Prompt Base (reutilizável)

```markdown
# Winston Presentation Framework

## Input
- **Tópico**: [seu tópico]
- **Audiência**: [profissão/nível técnico]
- **Duração**: [minutos]
- **Objetivo Primário**: [o que audiência vai fazer após?]

## Output Structure (use isso como prompt)

### 1. VISION
Responda: Por que isso importa agora?
- Contexto histórico (1-2 sentences)
- Por que agora (1-2 sentences)
- Promise explícita (1 sentence)

### 2. FENCE
- Será coberto: [3-4 tópicos]
- NÃO será coberto: [3-4 tópicos]

### 3. EXEMPLO PROGRESSIVO
- Simples: [código mínimo funcional]
- Médio: [com complicações reais]
- Avançado: [produção scale]

### 4. TEMA CENTRAL REPETIDO
- Identificar: [1 ideia que resume tudo]
- Variações: [4-5 formas de dizer]

### 5. ESTRUTURA EM BLOCOS
- Bloco 1: [tópico] (tempo)
  - Abertura: [transição]
  - Objetivo: [o que audiência aprende]
  - Fechamento: [ponte para próximo]

### 6. FECHAMENTO
- Restatement: [tema central]
- Call-to-action: [próximo passo concreto]
- Tone: [confiante, não questionador]
```

### Script Node.js para gerar apresentação estruturada

```javascript
// winston-presenter.js
const Anthropic = require('@anthropic-ai/sdk');

const client = new Anthropic.default();

const winstonPrompts = [
  {
    name: 'Vision',
    prompt: (topic, audience) => `
Para a apresentação sobre "${topic}" para ${audience}:
1. Escreva abertura impactante (não piadas)
2. Estabeleça promise clara
3. Máximo 3 minutos para ler em voz alta
    `,
  },
  {
    name: 'Fence',
    prompt: (topic) => `
Para "${topic}":
- Liste 3-4 tópicos que SERÁ coberto
- Liste 3-4 que NÃO será coberto
Deixe audiência saber exatamente os limites.
    `,
  },
  {
    name: 'Exemplos Progressivos',
    prompt: (topic) => `
Para "${topic}", crie 3 exemplos do simples ao complexo:
1. Exemplo simples (código mínimo)
2. Exemplo médio (complicações reais)
3. Exemplo avançado (produção)
    `,
  },
];

async function generatePresentation(topic, audience, duration) {
  console.log(`Generating Winston-structured presentation for: ${topic}`);
  console.log(`Audience: ${audience}, Duration: ${duration}min\n`);

  for (const promptConfig of winstonPrompts) {
    const systemPrompt = `You are a presentation coach trained in Patrick Winston's framework from MIT.
Your job is to structure presentations for maximum clarity and memorability.
Rules:
- Speak to oralidade (words to be said aloud), not written text
- No piadas (Winston hates jokes in opening)
- Theme must be repeated 3-5x in different ways
- Every section must serve the central promise
- Closing must NOT end with "Questions?"`;

    const userPrompt = promptConfig.prompt(topic, audience);

    const response = await client.messages.create({
      model: 'claude-3-5-sonnet-20241022',
      max_tokens: 1024,
      system: systemPrompt,
      messages: [{ role: 'user', content: userPrompt }],
    });

    console.log(`\n=== ${promptConfig.name.toUpperCase()} ===`);
    console.log(response.content[0].type === 'text' ? response.content[0].text : '');
  }
}

generatePresentation('How to Implement RAG in Production', 'Software Engineers', 30);
```

## Armadilhas e limitações

### 1. **Framework é para ORALIDADE, não leitura de slides**

Winston foi feito para palestras faladas. Se você ler slides escritos, perde 60% do efeito.

Problema: Gerar presentation text e copiar para slides Google sem praticar leitura em voz alta.
Resultado: Você lê slides, audiência fica entediada, estrutura não funciona.

Mitigação:
- **Sempre pratique em voz alta** (gravando no Whisper/telefone)
- **Slides devem ter mínimo de texto** (máximo 3 linhas por slide)
- **Use slides para visual** (diagrama, código, imagem), não para ler
- **Seu roteiro falado é o conteúdo**, slides são suporte visual

### 2. **"Fence" genérica não delimita**

IA pode gerar "vamos cobrir RAG, implementação, best practices" (duh, é óbvio).

Problema: Audiência ainda não sabe o que vai realmente aprender.
Resultado: Expectativa mismatch, frustraçãoao final.

Mitigação:
- **Seja específico no input**: "Vamos cobrir embeddings com OpenAI (não fine-tuning), retrieval com FAISS (não Elasticsearch), prompt augmentation (não reranking)"
- **Diga o que NÃO entra**: "Não vamos treinar embeddings custom, não vamos fazer distributed RAG, não vamos debugar alucinações avançadas"
- **Repita a fence** no meio da apresentação: "Como prometi, estamos aqui focados em X, não em Y"

### 3. **Repetição do tema central pode virar óbvia**

Winston ensina "repetir tema 3-5x de formas diferentes", mas amadores repetem a MESMA frase.

Exemplo ruim:
```
Abertura: "RAG dá ao modelo acesso a dados privados"
Minuto 10: "Como eu disse, RAG dá ao modelo acesso a dados privados"
Minuto 20: "Lembrem que RAG dá ao modelo acesso a dados privados"
```
Audiência: 😑

Exemplo bom:
```
Abertura: "RAG é como dar ao seu modelo um livro inteiro"
Exemplo 1: "Sem RAG, o modelo decora. Com RAG, consulta em tempo real"
Transição: "Veem só — o modelo que consulta é mais preciso que o que decora"
Fechamento: "Seu modelo agora tem biblioteca privada. Use bem."
```

Mitigação:
- **Gravar sua apresentação** e revisar com amigos — se soar óbvio, é porque é
- **Usar diferentes ângulos** (analógias, exemplos concretos, dados, imagens)
- **Variar estrutura de sentence** (não sempre "RAG é X")

### 4. **Promise não honrada destrói credibilidade**

Se você abre com "vocês vão implementar RAG em 30 min" mas gasta 25 minutos em teoria, não cumpre promise.

Problema: Audiência sai frustrada, acredita menos no seu conhecimento.

Mitigação:
- **Estruturar blocos de tempo com precisão** — reserve 10 minutos mínimo para prático se promise é implementar
- **Praticar timing** — rodar a apresentação completa 2-3x para bater o tempo
- **Reduzir promise se preciso** — "vocês vão ENTENDER como implementar" é mais honesto que "vocês vão IMPLEMENTAR"

### 5. **Closings fracos perdem audiência**

"Perguntas?" não deixa ninguém inspirado. Encerramentos membreáveis requerem esforço.

Exemplo fraco:
```
"Pronto, era isso. Vocês entendem RAG agora. Perguntas?"
```

Exemplo bom:
```
"Então resumindo: dados privados em tempo real muda tudo. Hoje vocês têm ferramentas. Meu desafio pra vocês é pegar um documento real que importa pra vocês e rodar RAG nele esta semana. Vocês conseguem. Vou ficar aqui se tiverem dúvidas."
```

Mitigação:
- **Acabar com frase afirmativa** ("vocês conseguem") não interrogativa ("alguma pergunta?")
- **Dejar próximo passo concreto** ("esta semana", "depois de hoje")
- **Sair da posição de palco** — descer, aproximar, mudar postura física

### 6. **Contexto insuficiente gera estrutura genérica**

Se você apenas disser "tópico: RAG", IA gera estrutura que serve pra qualquer RAG.

Problema: Não é adaptada ao seu contexto específico (sua empresa, seu time, seu caso de uso).

Mitigação:
- **Fornecer contexto máximo** no primeiro prompt:
  - Audiência (nível técnico, conhecimento previsto, pain point específico)
  - Contexto histórico (por que RAG agora para ELES?)
  - Objetivo comportamental (o que você quer que façam após?)
  - Restrições (não pode usar ferramenta X, precisa usar tech stack Y)

## Conexões

[[geracao-automatizada-de-prompts|Prompt engineering — técnica para usar sequência de prompts efetivamente]]
[[contexto-persistente-em-llms|Contexto estruturado — Winston é essencialmente structure that persists across 6 prompts]]
[[explicabilidade-como-medida-de-compreensao|Clareza conceitual — a promise clara é parte do framework]]
[[persuasao-em-comunicacao|Psicologia da persuasão — base teórica de Winston]]
[[pratica-deliberada|Deliberate practice — você precisa praticar em voz alta, não só gerar]]

## Histórico

- 2026-04-02: Nota criada
- 2026-04-11: Expandida com framework completo, exemplos de prompts, código prático, armadilhas técnicas
