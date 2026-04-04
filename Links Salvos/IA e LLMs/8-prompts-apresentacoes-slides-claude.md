---
tags: [Claude, prompts, apresentações, slides, storytelling, design visual, narrativa]
source: https://x.com/MartinsJoa_/status/2031538066410672285
date: 2026-03-10
tipo: aplicacao
---

# Estruturar Apresentações Impactantes com 8 Prompts Sequenciais

## O que é

Sequência de 8 prompts estruturados que transformam ideia vaga em apresentação persuasiva: objetivo, arco narrativo, roteiro slide-a-slide, visuais recomendados, notas de apresentador, revisão, personalização para público, abertura impactante.

## Como implementar

### Prompt 1: Definir Objetivo Final

```
Tarefa: Qual é o ÚNICO resultado que preciso alcançar com esta apresentação?

Seu objetivo é DECISÃO (eles decidem algo?) ou AÇÃO (eles fazem algo?) ou PERSPECTIVA (eles entendem diferente)?

Tema: [TEMA]
Público: [TIPO DE PÚBLICO]
Duração: [MINUTOS]

Retorne:
1. Objetivo em 1 frase
2. A ideia central que devem lembrar 1 semana depois
3. Qual sentimento devem sair (confiante? Urgente? Inspirado?)
4. Métrica de sucesso ("se X acontece após apresentação, ganho")

Exemplo output:
"Objetivo: Conseguir aprovação de $2M em funding
Ideia-chave: Mercado de IA está fragmentado, nós unificamos
Sentimento: Confiança que tem produto pronto
Métrica: 3+ VCs agendarem next meeting na semana seguinte"
```

### Prompt 2: Construir Arco Narrativo

```
Crie estrutura narrativa para: [TEMA]

Estrutura recomendada:
1. Problema (o que está quebrado?)
2. Obstáculo (por que ninguém resolveu?)
3. Insight (a descoberta que muda tudo)
4. Solução (como você resolve)
5. Resultado (que mundo novo abre)

Parâmetros:
- Público-alvo: [TIPO]
- Tempo: [X] minutos
- Contexto: [SITUAÇÃO DO PÚBLICO]

Retorne markdown com 5-7 seções principais, cada uma com:
- Título da seção
- 2-3 frases de conteúdo
- Transição para próxima seção

Exemplo:
## 1. Problema (1 min)
"Em 2025, 92% das empresas usam 7+ ferramentas de IA desconectadas..."
Transição: "Mas por que isso ainda não foi resolvido?"
```

### Prompt 3: Roteiro Slide-a-Slide

```
Baseado nesta narrativa:
[COLAR RESULTADO PROMPT 2]

Crie roteiro completo de slides:

Para CADA slide, retorne em tabela:
| # | Título | Ideia Central | Elemento Apoio | Notas Técnicas |
|----|--------|--------------|----------------|----------------|
| 1 | [título] | 1 frase chave | Tipo visual | Layout sugerido |
| 2 | ... | ... | ... | ... |

Requisitos:
- Máximo 1 ideia por slide
- Elimine tudo não-essencial
- Slide final = Call-to-Action
- Máximo [X] slides
```

### Prompt 4: Visuais Recomendados

```
Para cada slide deste roteiro:
[COLAR TABELA PROMPT 3]

Recomende o melhor formato visual:
- Gráfico (linha, barra, pie)
- Diagrama (fluxo, ciclo, matriz)
- Imagem (foto, ilustração, screenshot)
- Ícones + Texto
- Texto + Citação
- Vídeo curto

Para CADA slide retorne:
"Slide [#]: [Visual Type]
Razão: [1 linha justificando por que funciona]
Exemplo: [Descreva o que colocar]"

Exemplo:
"Slide 2: Gráfico de barras
Razão: Dados numéricos de fragmentação são mais persuasivos como comparação visual
Exemplo: 7 barras (tool A, B, C...) com altura de integração/custo, mostrando que nenhuma resolve tudo"
```

### Prompt 5: Notas para Apresentador

```
Escreva notas naturais para cada slide (como se falasse em voz alta):

Para CADA slide:
## Slide [#]: [Título]

**O que dizer:** [2-3 frases naturais, conversacional]
**Não fale:** [Evite repetir literalmente o que está no slide]
**Pausa/Ênfase:** [Onde pausar, o que enfatizar]
**Transição:** [Como sair para próximo slide]

Exemplo:
"## Slide 2: O Problema

**O que dizer:** 'Aqui está algo interessante — a maioria das empresas que conhecemos usa entre 5 e 10 ferramentas diferentes de IA. Isso significa que cada equipe está em seu próprio silo, sem visibilidade do que outro time está fazendo. Resultado? Redundância, ineficiência, custos altos.'

**Não fale:** 'Como mostra o gráfico, 92% usam 7+ ferramentas' (repetição chata)

**Pausa/Ênfase:** Pause após 'cada equipe em seu próprio silo' — deixe afundar
Enfatizar a palavra 'redundância'

**Transição:** 'Mas você pode estar pensando...'
"
```

### Prompt 6: Revisão Final

```
Revise esta apresentação COMPLETA:

[COLAR: Roteiro Prompt 3 + Visuais Prompt 4 + Notas Prompt 5]

Checklist de revisão:
1. Clareza: Cada slide traz 1 ideia só?
2. Progressão: Faz sentido de A para B para C?
3. Persuasão: Argumentos são fortes ou frágeis?
4. Visual: Visuais sugerem engajamento?
5. Tempo: Acha que cabe em [X] minutos?
6. Memória: A ideia-chave é reforçada 3+ vezes?

Retorne:
- Lista de mudanças recomendadas (priorizado)
- Slides a combinar / split
- Slides frágeis (onde a lógica falha)
- Sugestões de reforço (o que adicionar)

Formato: Markdown com seção por issue
```

### Prompt 7: Adaptar para Público

```
Esta apresentação será feita para: [TIPO PÚBLICO]

Exemplos: VCs/Investidores, C-level executivos, Engenheiros técnicos, Jornalistas, Estudantes

Para ESTE público específico, identifique:
1. **Prioridades principais:** O que eles se importam?
2. **Preocupações/Objeções:** Que dúvidas têm?
3. **Nível técnico:** Quanto precisam entender em profundidade?
4. **Linguagem:** Que jargão funciona? O que evitar?
5. **Provas sociais:** Qual tipo de evidência os convence? (dados, stories, referências?)

Depois recomende:
- Slides a reordernar
- Linguagem a mudar
- Exemplos a adicionar/remover
- Métricas a enfatizar
- Comparações/Benchmarks relevantes

Exemplo output:
"Para VCs:
- Reordenar: Colocar 'Tamanho de Mercado' ANTES de 'Produto' (TAM é prioridade #1 para VCs)
- Linguagem: Usar 'Unit Economics', 'CAC/LTV ratio', 'Churn' (VC speak)
- Adicionar: Traction concreta (users, MRR, growth rate)
- Remover: Detalhes técnicos de como funciona (eles não se importam)"
```

### Prompt 8: Abertura Impactante

```
Crie uma abertura (primeiros 30 segundos) para:
"[TEMA]"

A abertura deve:
1. Prender atenção IMEDIATAMENTE
2. Estabelecer Stakes (por que devo ouvir?)
3. Teaser da solução (sem revelar tudo)

Opções de abertura (escolha 1):
A) Estatística surpreendente: "Em [YEAR], [X]% de [POPULAÇÃO] ainda [PROBLEMA]"
B) Pergunta provocativa: "Você já parou para pensar que [INSIGHT]?"
C) Story pessoal: "Há 6 meses eu [SITUAÇÃO], e descobri que [DESCOBERTA]"
D) Contraste: "Antes: [mundo ruim]. Depois: [mundo bom]. A diferença? [1 coisa]"
E) Demonstração: [Ação visual ou demonstração rápida]

Retorne 3 opções, cada uma com:
- Texto exato (30 segundos de fala)
- Visual que acompanha
- Como conecta ao resto da apresentação
- Por que funciona para ESTE público

Exemplo:
"Opção A: Estatística
Fala: 'Sabe quantas ferramentas sua empresa usa para IA? A média é 7. Sete. Isso significa que cada time está em seu próprio mundo. Hoje, vamos mostrar como unificar tudo em uma plataforma.'
Visual: Montagem rápida de 7 logos (Slack, OpenAI, Notion, etc.) vindo em direção à câmera, depois todas convergindo em 1 logo
Conexão: Leva direto ao Slide 2 (O Problema)
Por que: VCs entendem fragmentação como problema de mercado — statistics ressoam"
```

## Stack e requisitos

**Ferramentas recomendadas:**
- Claude 3.5 para structure/outline (prompts)
- Figma/PowerPoint para design visual
- Teleprompter (Speaker Notes em app)

**Workflow recomendado:**
1. Prompts 1-2 no Claude (estratégia)
2. Prompt 3-4 gera outline (exportar para markdown/CSV)
3. Importar em PowerPoint/Figma
4. Designer usa recomendações visuais (Prompt 4)
5. Voltar Prompt 6 (revisão)
6. Prompt 7 adapta (se switch de público)
7. Ensaiar com notas (Prompt 5)

**Custo:**
- Prompts 1-8 = ~$0.20 em API Claude
- Total tempo: 2-3 horas (vs. 8-10 horas manual)

## Armadilhas e limitações

**Sequência:**
- Não pule Prompt 1 (objetivo). Sem objetivo claro, tudo que segue é vago
- Não reordenar fora de Prompt 2-3. Ordem importa para narrativa

**Adaptação:**
- Prompt 7 (público) é CRÍTICO. Mesma apresentação não funciona para VC vs. técnicos
- Errar aqui = apresentação fracassa mesmo sendo bem-estruturada

**Visuais:**
- Prompt 4 recomenda tipo, não design exato. Designer ainda precisa criar
- Evite slides com >5 elementos visuais (noise)

**Tempo:**
- Roteiro (Prompt 3) deve combinar com duração real
- Não compactar muito (parece rushado) nem inflacionar (perdem foco)

## Conexões

[[claude-code-superpowers]]
[[30_prompts_claude_fp_a_analise]] - Similar templating approach
[[framework-winston-para-apresentacoes]]
[[nothing-style-ui-prompting]]

## Histórico

- 2026-03-10: Nota criada
- 2026-04-02: Reescrita como guia prático com 8 prompts executáveis
