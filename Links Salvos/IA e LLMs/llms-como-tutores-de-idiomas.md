---
tags: [ia, aprendizado-de-idiomas, prompts, llm]
source: https://x.com/FelpsCrypto/status/2039546795387154446?s=20
date: 2026-04-02
tipo: aplicacao
---
# Configurar Claude como Tutor de Idiomas Personalizado

## O que é

Prompt estruturado + hook de conversa que transforma Claude em tutor de idiomas imersivo, oferecendo conversação 24/7, correção gramatical com explicações, ajuste progressivo de dificuldade e feedback contextualizado — sem custo.

## Como implementar

### Fase 1: Criar Prompt de Tutor

Salve em arquivo `language_tutor_system.md`:

```markdown
# Sistema de Tutoria de Idiomas

## Seu Papel
Você é um tutor de idioma especializado. Seu objetivo é ensinar [IDIOMA] de forma conversacional e engajante.

## Nível do Aluno
Nível atual: [PROFICIÊNCIA: A1/A2/B1/B2/C1]
Objetivo: Atingir [PROFICIÊNCIA ALVO]

## Estratégia de Ensino

### 1. Conversação Imersiva
- Sempre responda em [IDIOMA] PRIMEIRO
- Use estruturas do nível do aluno (não salte para complexidade)
- Inclua um padrão novo a cada 3 mensagens

### 2. Correção e Feedback
Quando o aluno escrever algo incorreto:

\`\`\`
[RESPOSTA DO ALUNO]

✓ CORREÇÃO:
[Versão corrigida]

📝 EXPLICAÇÃO:
[Por que estava errado e regra gramatical]

💡 DICA:
[Padrão similar ou regra conexa]
\`\`\`

### 3. Contextos Pedagógicos
Varie entre:
- Conversas casuais (conhecer amigos)
- Situações práticas (restaurante, estação)
- Entrevistas de emprego
- Discussões sobre hobbies/interesses
- Storytelling (histórias curtas para leitura)

### 4. Ajuste Dinâmico
- Se aluno entender 100%: aumente dificuldade
- Se aluno entender <50%: volte ao nível anterior
- Sempre mencione: "Seu nível está agora: [novo nível]"

### 5. Revisão Spaced Repetition
A cada 5 mensagens: "Vamos revisar os 5 padrões principais desta conversa?"

## Materiais Proibidos
- Explicação em inglês (fale apenas em [IDIOMA])
- Diálogos muito complexos no início
- Vocabulário fora do escopo do nível
```

### Fase 2: Conversa com Tutor

Copie o prompt acima e adapte:

```
# No Claude, comece com:

Cole isto como system message:

[Seu prompt adaptado de language_tutor_system.md]

Depois, mensagem do usuário:

"Quero aprender português. Sou iniciante (A1).
Comece com conversa natural sobre meu dia."
```

### Fase 3: Estrutura de Aula

**Primeira conversa (15 min):**
- Simples apresentação
- 3 palavras novas
- Padrão: "Oi, meu nome é X"

**Próximas 5 conversas:**
- Expansão gradual
- Novos vocabulários +5 por aula
- Introdução de tempos verbais

**Após 10 sessões:**
- Mini diálogo (você lê descrição, responde em idioma)
- Correção detalhada
- Reflexão sobre progresso

### Fase 4: Prompt Específico por Idioma

**Para Português:**

```
Você é especialista em português brasileiro e europeu.
Ensine [ALUNO] começando com:

Aula 1: Cumprimentos (Oi, Olá, Como vai?)
Aula 2: Apresentação (Meu nome é..., Eu sou...)
Aula 3: Profissões (Sou engenheiro, advogado...)
Aula 4: Hobbies (Gosto de..., Adoro...)
Aula 5: Família (Tenho pai, mãe, irmão...)

Para cada resposta do aluno:
1. Responda como colega (naturalemente)
2. Se houver erro: Corrija com "✓ Forma correta: ..."
3. Inclua 1 padrão novo
4. Pergunte de volta para manter conversa
```

**Para Inglês:**

```
Teaching method: Conversational English, starting at A1

Progression:
- Lesson 1-5: Present simple, basic vocabulary
- Lesson 6-10: Present continuous, past simple
- Lesson 11+: More complex tenses, idioms

Always:
1. Respond naturally
2. Correct gently
3. Explain one grammar point per lesson
4. Ask follow-up questions
```

### Fase 5: Tracking de Progresso

Mantenha arquivo `progress.md`:

```markdown
# Meu Progresso em [IDIOMA]

## Estatísticas
- Aulas completadas: 15
- Horas conversando: 12
- Palavras aprendidas: 150
- Nível atual: A2

## Pontos Fortes
- Conversas casuais
- Números e datas
- Cumprimentos

## Áreas de Melhoria
- Tempos verbais (ainda confundo past tense)
- Pronúncia (não testada)
- Vocabulário técnico

## Próximas Metas
- [ ] Conversa de 5 min inteira em idioma
- [ ] Ler mini-conto e responder perguntas
- [ ] Passar para B1
```

### Fase 6: Integração com Ferramentas Externas

**Usar com Anki para Vocabulary:**

```python
# export_vocab.py - automaticamente cria cards Anki com vocab novo

vocab_learned = [
    {"pt": "gato", "en": "cat"},
    {"pt": "casa", "en": "house"},
    # ...
]

# Formato Anki (TSV): frente \t verso
for word in vocab_learned:
    print(f"{word['pt']}\t{word['en']}")
```

## Stack e requisitos

- **Claude**: Acesso a claude.ai ou Claude Code (Free tier funciona)
- **Tempo**: 30 min/dia, mínimo 5 dias/semana para progresso
- **Suplementos** (opcionais):
  - Anki para vocabulário
  - Forvo.com para pronúncia
  - LingQ para leitura estruturada
- **Custo**: Grátis (Claude Pro maximiza, mas Free funciona)

## Armadilhas e limitações

1. **Sem pronúncia**: Claude não avalia som. Use Forvo.com ou Google Translate para áudio.

2. **Alucinação de regras**: Ocasionalmente Claude cria "regras" que não existem. Verifique em fontes como Duolingo.

3. **Falta de imersão total**: Você pode "voltar" ao inglês. Para imersão real, deabilite traduções automáticas no browser.

4. **Conversa pode ficar repetitiva**: O modelo pode ciclar padrões. Mude contextos frequentemente ("Agora estamos em restaurante...").

5. **Não é substituto de professor real**: Para pronúncia avançada e sotaque nativo, professor humano é necessário.

## Conexões

- [[obsidian-com-ia-como-segundo-cerebro]] — vault para rastrear progresso
- [[Otimizar Preferencias Claude Chief of Staff]] — otimizar tom do tutor
- [[Claude Code - Melhores Práticas]] — automação de aulas

## Histórico

- 2026-04-02: Nota criada
- 2026-04-02: Guia prático de setup

## Exemplos
1. **Simulação de diálogo**: Prompt instrui o Claude a conversar apenas em japonês e corrigir cada erro com explicação gramatical em PT-BR ao final de cada resposta.
2. **Modo imersivo progressivo**: Prompt define que o modelo deve começar com frases simples e aumentar a complexidade a cada 5 trocas de mensagem, simulando uma progressão de curso.
3. **Preparação para situações reais**: Prompt cria um roleplay de entrevista de emprego em inglês, com o modelo avaliando vocabulário profissional e sugerindo expressões mais naturais.

## Relacionado
*(Nenhuma nota relacionada no vault no momento.)*

## Perguntas de Revisao
1. Quais elementos de um prompt tornam um LLM mais eficaz como tutor de idiomas do que uma conversa genérica?
2. Em que cenários específicos de aprendizado um LLM seria insuficiente e precisaria ser combinado com outros métodos?

## Historico de Atualizacoes
- 2026-04-02: Nota criada a partir de Telegram