---
tags: [projeto, pipeline, obsidian, qualidade, reprocessamento, automacao]
date: 2026-04-11
tipo: projeto
status: pendente
prioridade: media
tempo-estimado: 1-2 horas
---
# Projeto 4: Reprocessar Notas Fracas do Vault

## Objetivo

Rodar o script `reprocess_weak_notes.py` para identificar e melhorar as 77 notas fracas do vault. Transformar notas com pouco conteudo em notas ricas, com codigo, armadilhas e conexoes.

## Por que fazer isso agora

A analise de qualidade mostrou que 77 de 278 notas (28%) estao abaixo do threshold de qualidade. Dessas, 63 tem URL de origem e podem ser reprocessadas automaticamente. O prompt do pipeline ja foi reescrito com regras de qualidade minima (80+ linhas, codigo obrigatorio, 3+ armadilhas). Basta rodar o script quando os creditos voltarem.

## Pre-requisitos

- Creditos na API Anthropic (custo estimado: ~$2.83 para todas as 63 notas)
- Python 3.14 (ja instalado)
- Acesso ao vault: `C:\Users\leeew\Documentos\Vaults Obsidian\Claude\`
- Script ja pronto: `Projects/second-brain-pipeline/reprocess_weak_notes.py`

## Passo a Passo

### Etapa 1: Scan Inicial (5 min)

```powershell
cd "C:\Users\leeew\Documentos\Vaults Obsidian\Claude\Projects\second-brain-pipeline"

# Ver todas as notas fracas
python reprocess_weak_notes.py --scan
```

Output esperado: lista de ~77 notas com score de qualidade (0-100), ordenadas da pior para a melhor. Scoring:
- Tamanho (40pts): baseado em numero de linhas
- Secoes (25pts): quantas secoes a nota tem
- Blocos de codigo (20pts): presenca de exemplos praticos
- URL de origem (15pts): se tem link para reprocessar

### Etapa 2: Teste com 1 Nota (10 min)

```powershell
# Escolher uma nota fraca e testar reprocessamento
python reprocess_weak_notes.py --test "nome-da-nota-fraca"
```

Isso reprocessa UMA nota e mostra o resultado sem salvar. Verificar:
- A nota nova tem 80+ linhas?
- Tem blocos de codigo?
- Tem 3+ armadilhas especificas?
- O conteudo e mais rico que o original?

### Etapa 3: Reprocessar em Batches (30-60 min)

```powershell
# Primeiro batch: 10 piores notas
python reprocess_weak_notes.py --reprocess --limit 10

# Se qualidade OK, proximo batch
python reprocess_weak_notes.py --reprocess --limit 20

# Se tudo bem, rodar o resto
python reprocess_weak_notes.py --reprocess
```

O script faz backup automatico de cada nota antes de sobrescrever (salva em `_backups/`). Se algo der errado, o original esta preservado.

### Etapa 4: Verificacao de Qualidade (15 min)

```powershell
# Rodar scan novamente para ver melhoria
python reprocess_weak_notes.py --scan

# Comparar: quantas notas ainda estao abaixo do threshold?
```

Meta: reduzir de 77 notas fracas para <20.

### Etapa 5: Dry Run Antes de Gastar (Opcional)

```powershell
# Ver o que seria reprocessado sem gastar tokens
python reprocess_weak_notes.py --reprocess --dry-run
```

Mostra lista de notas que seriam afetadas, custo estimado, e preview do prompt que seria enviado.

## Metricas de Qualidade

| Metrica | Threshold Minimo | Peso |
|---------|-----------------|------|
| Linhas de conteudo | 60+ | 40% |
| Secoes estruturadas | 4+ | 25% |
| Blocos de codigo | 1+ | 20% |
| URL de origem | presente | 15% |
| Score total | 50+ de 100 | - |

## Estimativa de Custo

- 63 notas reprocessaveis
- ~4000 tokens output por nota (max_tokens configurado)
- ~1500 tokens input por nota (URL + prompt)
- Total: ~350K tokens
- Custo estimado: ~$2.83 (Claude Sonnet)
- Tempo de processamento: ~30-45 min (sequencial)

## Checklist de Conclusao

- [ ] Scan inicial rodou, confirmou 77 notas fracas
- [ ] Teste com 1 nota, qualidade verificada
- [ ] Batch de 10 notas reprocessado
- [ ] Scan pos-reprocessamento mostra melhoria
- [ ] Restante reprocessado (ou decisao de parar)
- [ ] Backups verificados (pasta _backups/ existe)
- [ ] Score medio do vault melhorou

## Riscos e Mitigacoes

**Risco**: API fora do ar ou rate limit. **Mitigacao**: script tem retry com backoff exponencial.

**Risco**: nota reprocessada fica pior que original. **Mitigacao**: backup automatico, pode reverter.

**Risco**: URL de origem retorna 404. **Mitigacao**: script pula notas com URL inacessivel.

**Risco**: custo excede estimativa. **Mitigacao**: usar --limit para controlar batches.

## Notas Relacionadas

- [[construir-base-de-conhecimento-pessoal-com-llm-obsidian-e-markdown]]
- [[obsidian-com-ia-como-segundo-cerebro]]
- [[otimizacao-de-tokens-via-claudemd]]

## Criterios de Sucesso

Minimo: Scan rodou, teste com 1 nota feito, backup funciona.
Ideal: 63 notas reprocessadas, score medio subiu de ~45 para ~70+.
Bonus: zero notas abaixo do threshold apos reprocessamento.

## Historico

- 2026-04-11: Projeto criado
- 2026-04-10: Script reprocess_weak_notes.py criado e validado
- 2026-04-10: Scan inicial: 253 notas total, 77 fracas, 63 reprocessaveis
