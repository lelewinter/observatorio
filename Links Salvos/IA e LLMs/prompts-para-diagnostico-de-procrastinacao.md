---
tags: [procrastinacao, prompts, produtividade, llm, claude]
source: https://x.com/alex_prompter/status/2038962632536068573?s=20
date: 2026-04-02
tipo: aplicacao
---

# Usar Claude como Coach Cognitivo-Comportamental para Diagnóstico de Procrastinação

## O que é

Padrão de prompt que simula role de coach/terapeuta, conduzindo diagnóstico socrático da procrastinação identificando causa raiz (medo, perfeccionismo, indefinição, baixa autoeficácia) e gerando plano de ação via implementation intentions.

## Como implementar

**Padrão 1: Diagnóstico de resistência.**
```
Identifique PORQUE eu procrastino na tarefa: "[TAREFA VAGA]"

Análise:
1. Minha melhor hipótese sobre a causa raiz (medo, perfeccionismo, indefinição, desgaste?)
2. Pergunte: "O que exatamente você teme se começar?"
3. Pergunte: "Como você mediria 'sucesso' nesta tarefa?"
4. Pergunte: "Qual é o MENOR primeiro passo possível (2-5 minutos)?"

Com base nas respostas, liste 5 possíveis razões em ordem de probabilidade:
- [Razão 1]: X% chance
- [Razão 2]: Y% chance
...

Finalize com: "De longe, a causa mais provável é: [X]. Para testá-la, você poderia: [ação concreta de 5 minutos]"
```

Usado assim:
```
[Claude me responde com diagnóstico]

Eu respondo com respostas às perguntas do Claude.

[Claude refina hipótese e propõe experimento de 5 minutos]
```

**Padrão 2: Reformulação com implementation intentions.**
```
Redesenhe a tarefa "[TAREFA]" usando implementation intentions.

Template:
TAREFA ORIGINAL: [descreva como está agora]

MICROTAREFAS (quebre em <5 minutos cada):
- Micro 1: [Que exatamente você faz, com critério de conclusão claro]
- Micro 2: ...

TRIGGERS e AÇÕES (formato: "Quando X, eu faço Y"):
- Quando eu sentar no computador, eu abro [arquivo específico]
- Quando terminar Micro 1, eu tiro 2min de break e faço Micro 2
- Quando atingir 3 microtarefas, eu celebro com [recompensa concreta]

RESISTÊNCIAS ESPERADAS:
- Se sentir [emoção], eu faço [ação alternativa] (ex: se ansiedade, eu respiro 3x profundo)

Comece com Micro 1 AGORA. Timer: 5 minutos. Vou?
```

**Padrão 3: Diagnóstico + Plano Integrado (Tudo-em-um).**
```
Sou seu coach. Vamos resolver a procrastinação em "[TAREFA]" em 10 minutos.

Passo 1: DIAGNÓSTICO
Responda rapidamente (sem filtro):
- Por que você evita isto?
- O que você teme que aconteça se começar?
- Qual é a primeira coisa que você precisaria fazer?

Passo 2: REFORMULAÇÃO
[Sistema analisa respostas e reformula usando implementation intentions]
Tarefa original = [mapeado para microtarefas]

Passo 3: AÇÃO
Micro 1 [x minutos] começa AGORA. Você faz, eu espero aqui.
[Quando você voltar, continuamos.]
```

**Padrão 4: ACT (Aceitação e Compromisso).**
```
Procrastinação = evitação de emoção incômoda.

Vamos usar ACT em lugar de força bruta.

1. Nomeie a emoção que evita: [medo, ansiedade, tédio, vergonha?]
2. Acei tela emoção como normal: "É OK sentir [emoção]. Todos sentem."
3. Compromisso: O que você QUER fazer mesmo com essa emoção? [valor pessoal]
4. Ação: Qual é UM passo pequeno que alinha com seu valor?

Exemplo:
- Emoção evitada: Medo de rejeição no feedback
- Aceitação: "Medo é sinal que importa. Normal."
- Valor: Quero crescer, quero ser bom no que faço
- Ação: Enviar para feedback MESMO com medo. Medo não impede isso.
```

## Stack e requisitos

- Claude (web, desktop, ou API)
- 10-20 minutos por sessão de diagnóstico
- Sem requisitos técnicos adicionais
- Tempo de implementação: ação deve começar mesma sessão

## Armadilhas e limitações

LLM não substitui terapeuta de verdade para procrastinação crónica/clínica. Pacientes que "enrolam" respondendo perguntas do LLM continuam procrastinando (meta-procrastinação). Padrão de implementation intentions funciona bem para tarefas bem definidas; funciona mal para tarefas nebulosas ("escrever livro") — quebrar em micro menores primeiro. ACT requer disposição interna para mudança; LLM não força isso. Auto-diagnóstico é enviesado — pode não identificar verdadeira causa raiz.

## Conexões

[[Prompt First Principles para LLMs]], [[Simplificar Setup Claude Deletar Regras Extras]], [[Plan Mode Claude Code]]

## Histórico

- 2026-04-02: Nota criada
- 2026-04-02: Reescrita como guia estruturado