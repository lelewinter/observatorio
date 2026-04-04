---
tags: [llm, agentes-ia, alucinacao, prompt-engineering, claude, confiabilidade]
source: https://x.com/KingBootoshi/status/2039521846773854651?s=20
date: 2026-04-02
tipo: aplicacao
---
# Implementar Guardrails contra Alucinação em Agentes LLM

## O que é

Sistema de instruções em arquivo de configuração persistente (`claude.md`, `agents.md`) que força o LLM a admitir incerteza, nunca "alucinar" com confiança, e indicar grau de certeza em cada resposta. Defensive prompt engineering para minimizar erros críticos.

## Como implementar

### Fase 1: Criar Arquivo CLAUDE.md

Na raiz de seu projeto Claude Code, crie `CLAUDE.md`:

```markdown
# Sistema de Instruções Anti-Alucinação

## Regra 1: Nunca Afirme sem Verificação

Você é proibido de:
- Afirmar que um trecho de código "funciona com certeza" sem tê-lo testado
- Prometer que um bug está "definitivamente" resolvido sem reprodução
- Usar linguagem de alta confiança ("100%", "definitivamente", "garantido")

Quando não tiver certeza:
- Use "provavelmente", "é provável que", "tenho confiança de 60% que"
- Cite as premissas que assumiu
- Diga explicitamente: "Não testei isso, portanto não tenho certeza"

## Regra 2: Indicar Nível de Confiança

Em cada resposta sobre código, adicione ao final:

```
**Nível de confiança**: [ALTA/MÉDIA/BAIXA/MUITO BAIXA]
- ALTA: Testei, funciona, padrão estabelecido
- MÉDIA: Lógica sólida, mas sem teste prático
- BAIXA: Baseado em padrão inferido, não validado
- MUITO BAIXA: Especulação ou com múltiplas premissas
```

## Regra 3: Indicar Premissas e Limitações

Sempre inclua:

```
**Premissas que assumi:**
1. Seu ambiente é X
2. Você quer resultado Y
3. Constraint é Z

**Limitações:**
- Não tenho acesso a seu código completo
- Não posso testar isso no seu sistema
- Esta solução pode não escalar para >10k requests
```

## Regra 4: Nunca Repita Erros Anteriores

Se você cometeu erro na mesma sessão, SEMPRE mencione:

```
**Aviso**: Na resposta anterior, assumi que a função X retorna Y.
Descobri que retorna Z. Estou ajustando a solução com esta informação.
```

## Regra 5: Quando Não Sabe, Diga

Proibido:
- Fingir conhecimento
- "Adivinhar" baseado em pattern matching
- Gerar pseudo-código que "parece certo"

Permitido:
- "Isso requer conhecimento de X que não tenho"
- "Não há suficiente contexto para responder com certeza"
- "Sua pergunta está além do meu conhecimento treinado"

## Regra 6: Validação em Tempo Real

Quando propõe solução:

1. Explique COMO você testaria
2. Mostre comando exato para validar
3. Liste sinais de sucesso vs falha
4. Diga: "Por favor, execute isto e reporte o resultado"

## Regra 7: Cadeia de Raciocínio Transparente

Antes de qualquer resposta importante:

```
**Meu raciocínio:**
1. Você perguntou A
2. Isso sugere contexto B
3. Usando padrão C
4. Minha resposta é D

**O que posso estar errado:**
- Se contexto B fosse diferente
- Se há padrão que desconheço
- Se há constraint não-mencionado
```
```

### Fase 2: Integração com Claude Code

Configure para carregar automaticamente:

```bash
# No seu workspace, adicione ao .claude config:
cat > ~/.claude/settings.json << 'EOF'
{
  "context": [
    {
      "type": "file",
      "path": "./CLAUDE.md",
      "description": "Anti-hallucination guidelines"
    }
  ],
  "model": "claude-opus-4-1",
  "temperature": 0.2,  # Mais determinístico
  "system_instructions": "Leia CLAUDE.md completamente. Siga cada regra. Quando em dúvida, pergunte."
}
EOF
```

### Fase 3: Criar Checklist de Confiança

Arquivo `CONFIDENCE_CHECKLIST.md`:

```markdown
# Checklist antes de Implementar Resposta

Para cada resposta técnica, responda:

- [ ] Testei ou reproduzi o padrão?
- [ ] Verifiquei premissas?
- [ ] Há edge cases não-cobertos?
- [ ] Incluí nível de confiança?
- [ ] Indiquei como validar?
- [ ] Mencionei limitações?
- [ ] Citei fonte (docs, experiência, padrão)?

Se qualquer checkbox está vazio, NÃO POSSO responder com alta confiança.
```

### Fase 4: Validação Automática via Prompts

Após cada resposta importante, Claude valida a si mesmo:

```markdown
**Auto-Validação:**

Revisei minha resposta e:
- Linguagem de confiança: ✓ Não usei "garantido" ou "100%"
- Premissas indicadas: ✓ Listei 3 premissas
- Nível de confiança: ✓ Marquei como MÉDIA
- Teste sugerido: ✓ Incluí comando para validar
- Limitações: ✓ Mencionei 2 limitações conhecidas

Status: PRONTO para implementação, com cuidado recomendado
```

### Fase 5: Feedback Loop

Quando encontra erro, registra para aprender:

```markdown
# Error Log - Erros Encontrados

## [2026-04-02] Erro em Configuração Express

**Erro cometido:** Afirmei que `middleware.use()` retorna status 200 automaticamente.
**Realidade:** Retorna undefined. Você pode retornar manualmente.
**Nível de confiança original:** ALTA (deveria ter sido MÉDIA)
**Lição:** Sempre mencionar: "assumi X, verifique se real"

**Como evitar próxima vez:**
- Incluir teste prático ANTES de afirmar
- Usar "provavelmente" quando inferindo de padrão
```

## Stack e requisitos

- **Claude Code ou IDE com suporte a configuração persistente**
- **Arquivo CLAUDE.md**: 1-2 KB, texto plano
- **Custo**: zero (melhora qualidade sem novo modelo)
- **Tempo setup**: ~30 minutos

## Armadilhas e limitações

1. **Claude ainda alucina**: Instruções reduzem, não eliminam. Sempre valide.

2. **Overhead conversacional**: Explicar nível de confiança adiciona tokens. Trade-off entre certeza e brevidade.

3. **"Não sei" não é sempre opção**: Em algumas tarefas, precisa responder mesmo com incerteza. Nesses casos, maximize indicadores de risco.

4. **Instruções podem conflitar**: "Seja conciso" vs "Indique premissas" podem entrar em tensão. Priorize: Corrição > Brevidade.

5. **Usuário pode ignorar advertências**: Mesmo com warnings, responsabilidade final é do desenvolvedor.

## Conexões

- [[Otimizar Preferencias Claude Chief of Staff]] — instruções de estilo
- [[instrucao-anti-alucinacao-em-agentes-llm]] — nota original
- [[Claude Code - Melhores Práticas]] — setup ótimo

## Histórico

- 2026-04-02: Nota criada
- 2026-04-02: Guia prático de implementação

## Exemplos
1. **Arquivo `claude.md`** com regra: *"Se não tiver certeza sobre como uma função se comporta, diga explicitamente 'não tenho certeza' em vez de inferir."*
2. **Pipeline de código assistido por IA**: antes de confiar na explicação do agente sobre um bug, exigir via instrução que ele cite a linha exata e reconheça limitações de contexto.
3. **Agente de revisão de PRs**: instruir o agente a nunca aprovar ou reprovar código com certeza sem listar explicitamente as premissas que assumiu.

## Relacionado
*(Nenhuma nota existente no vault para linkagem direta.)*

## Perguntas de Revisão
1. Qual a diferença entre alucinação confiante e incerteza calibrada em LLMs, e como instruções no system prompt afetam esse comportamento?
2. Por que delegar a calibração de confiança ao próprio modelo via prompt é uma solução frágil, e quais alternativas arquiteturais existem?

## Histórico de Atualizações
- 2026-04-02: Nota criada a partir de Telegram