---
tags: [conceito, ia-generativa, prompt-engineering, marketing, criatividade]
date: 2026-04-02
tipo: conceito
aliases: [Engenharia de Prompt para Roteiros de UGC]
---
# Engenharia de Prompt para Roteiros de UGC

## O que é

Técnica estruturada de elaboração de prompts para LLMs que transformam dados estruturados de um produto (nome, preço, proposta de valor) em roteiros persuasivos e variados, otimizados para hooks específicos (dor, curiosidade, prova social, FOMO). Diferencia-se de prompt genérico por incluir placeholders parametrizados, especificação explícita de restrições (duração, tom, CTA) e estrutura de output em formato máquina-processável (JSON).

## Como funciona

O prompt funciona como um template com três camadas:

**Camada 1 — Contexto de Persona:** Define o LLM como especialista em um domínio específico ("você é especialista em UGC para TikTok Shop de moda feminina"). Isso direciona o modelo para padrões lingüísticos adequados ao contexto.

**Camada 2 — Placeholders e Variáveis:** Em vez de escrever um novo prompt a cada geração, use placeholders: [HOOK_TYPE], [PRODUTO], [PUBLICO], [PRECO], [VALOR_PROPOSTO]. Isso permite automatizar geração em lote: loop 50 vezes, alterando apenas essas variáveis. Cada iteração custa ~USD 0,001-0,005.

**Camada 3 — Restrições e Formato:** Especifique explicitamente: duração em segundos (15-30s), tom (casual, entusiasmado, crítico), estrutura esperada (hook + corpo + CTA) e formato de saída (JSON). Sem restrições, LLMs geram outputs inconsistentes ou muito longos.

Exemplo técnico:

```
Contexto: "Você é especialista em roteiros UGC para TikTok Shop. Crie roteiros que geram alto engagement."

Entrada estruturada:
- Hook Type: [HOOK_TYPE] (opcoes: dor | curiosidade | prova_social | fomo)
- Produto: [PRODUTO]
- Preço: [PRECO]
- Público: [PUBLICO]
- Proposta: [PROPOSTA]

Restrição: "Máximo 30 segundos. Tom [TONE]. Sem menção a preço se hook for dor."

Output esperado (JSON):
{
  "hook": "...",
  "corpo": "...",
  "cta": "...",
  "duracao_segundos": 25,
  "tom": "casual"
}
```

Quando você executa este prompt com 10 diferentes HOOK_TYPEs mantendo PRODUTO constante, gera 10 variações do mesmo produto com ângulos emocionais diferentes — e é essa variação em massa que permite teste estatístico de qual hook perfurma melhor.

## Pra que serve

**Uso principal — Teste em lote de hipóteses criativas:**
Agências tradicionais testam 3-5 hooks por semana (uma criadora gera 1-2 variações/dia). Com engenharia de prompt, teste 50 hooks em 10 minutos (custo: ~USD 0,10). Isso coloca a criação em regime estatístico: gere muito, meça qual perfurma, escale vencedor.

**Trade-offs:**
- **Vantagem:** velocidade, custo marginal próximo de zero, escalabilidade
- **Desvantagem:** roteiros tendem a convergir para padrões; criatividade é mais mecânica, menos "genuína"
- **Quando usar:** produtos commoditizados (beleza, moda rápida, e-commerce) onde margem vem de volume e teste rápido
- **Quando NÃO usar:** produtos de nicho/premium que exigem narrativa única autêntica; categorias reguladas (saúde, finanças)

Também serve como "rascunho criativo" — gere 20 roteiros, envie para criador humano refinar os 3 melhores. Acelera fluxo de criador em 60-80%.

## Exemplo prático

**Cenário:** Loja TikTok Shop de esmaltes. Produto: "Esmalte Rouge Luxe, R$ 45".

**Execução:**

```
Hook_type = "dor"
Produto = "Esmalte Rouge Luxe"
Preco = "R$ 45"
Publico = "mulheres 18-35 com interesse em beleza"
Proposta = "acabamento premium + durabilidade 21 dias"

[Envia prompt ao Claude]

Output:
{
  "hook": "Cansei de esmalte que descasca em 3 dias...",
  "corpo": "Rouge Luxe dura até 21 dias sem lascar. Acabamento espelhado, à prova de água.",
  "cta": "TikTok Shop: @minhaloja (link na bio)"
}
```

Em seguida, mesmo produto, Hook_type = "curiosidade":

```
Output:
{
  "hook": "Vcs ja testaram um esmalte que brilha diferente no escuro?",
  "corpo": "Rouge Luxe tem pigmento que ativa sob luz UV. Preto que fica vermelho...",
  "cta": "Testa no meu shop!"
}
```

Gera dois roteiros completamente diferentes, mesmo produto, em <2 segundos. Publica ambos, mede engagement. Se "curiosidade" ganha 3x em CTR, gera 10 mais variações de "curiosidade" na próxima semana.

## Aparece em
- [[producao-de-ugc-em-escala-com-ia]] — camada 1 da implementação técnica
- [[llm-para-automacao-criativa]] — aplicação de APIs de LLM

---
*Conceito extraído em 2026-04-02*
