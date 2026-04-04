---
tags: []
source: https://x.com/Koukoumidis/status/2038994860582261145?s=20
date: 2026-04-02
tipo: aplicacao
---

# Construir Modelos Customizados via Oumi (No-Code Machine Learning)

## O que é

Plataforma Oumi abstrai ciclo completo de ML (dados → fine-tuning → eval → deploy) via interface natural-language. Descreva "preciso de modelo para triagem de radiografias" e a plataforma orquestra construção automática com seus dados.

## Como implementar

**Etapa 1: Setup de conta Oumi.** Acesse https://oumi.ai, crie conta, configure workspace. Conecte fonte de dados (CSV, banco de dados, Google Sheets, S3 bucket).

**Etapa 2: Descrevê intenção em linguagem natural.** No interface Oumi, descreva:
```
Preciso de modelo para:
- Entrada: descrição de imagem radiológica em texto
- Saída: classificação binária (normal / anormal)
- Mínimo 300 exemplos de treinamento
- Métrica crítica: recall > 0.95 (não perder positivos)
```

Oumi infere arquitetura, parâmetros e pipeline.

**Etapa 3: Upload ou sincronização de dados.** Oumi conecta diretamente à sua fonte e coleta dados. Formato esperado: CSV com colunas [input, output]. Exemplo:
```
input,output
"Consolidação bilateral no ápice",anormal
"Campos pulmonares claros",normal
```

Oumi faz validação automática (detecção de outliers, balanceamento de classes).

**Etapa 4: Fine-tuning automático.** Oumi seleciona modelo base apropriado (ex: MedBERT para textos médicos, Llama para textos genéricos). Configura parâmetros de treinamento e roda em infraestrutura Oumi. Tempo: 30 min a 2 horas dependendo tamanho dataset.

**Etapa 5: Avaliação e validação.** Oumi automaticamente:
- Separa 20% dos dados como test set
- Calcula métricas (precisão, recall, F1, confusion matrix)
- Gera relatório detalhado com recomendações
- Se performance insuficiente, sugere coletar mais dados de classe minoritária

**Etapa 6: Deploy e chamadas de API.** Modelo fica acessível via REST API com versioning automático:
```bash
curl -X POST https://api.oumi.ai/models/seu-modelo/predict \
  -H "Authorization: Bearer TOKEN" \
  -d '{"input": "Consolidação bilateral no ápice"}'

# Resposta:
# {"prediction": "anormal", "confidence": 0.94}
```

**Integração em pipeline existente.** Oumi fornece SDKs para Python, Node.js, que se integram em aplicações:
```python
from oumi import OumiClient

client = OumiClient(api_key="...", model="seu-modelo")
result = client.predict({"input": "texto radiologia aqui"})
print(result["prediction"])  # "anormal"
```

## Stack e requisitos

- Dados de treinamento: mínimo 100 exemplos (300+ recomendado)
- Oumi free tier: até 5 modelos, 10K predicções/mês
- Oumi paid: $99-999/mês dependendo volume
- Tempo: 1-2 horas setup + coleta de dados
- Sem conhecimento de ML necessário

## Armadilhas e limitações

Oumi opera melhor com dados bem estruturados — dados bagunçados prejudicam resultado. Modelos customizados é bom para domínios especializados, mas genéricos (ex: análise de sentimento geral) continuam perdendo para modelos de escala (GPT-4). Se dataset é <100 exemplos, fine-tuning pode overfit — Oumi avisa mas requer coleta de mais dados. Latência de API é ~200-500ms (não é real-time). Falta fine-grained control se você precisa customizar loss function ou arquitetura específica.

## Conexões

[[Modelos Locais e IA Privada]], [[Stack de IA Local Self-Hosted]], [[Skill Pack Financeiro para Agentes AI]]

## Histórico

- 2026-04-02: Nota criada
- 2026-04-02: Reescrita como guia prático de uso