---
tags: [celonis, process-mining, business-intelligence, data-analysis, saas]
source: https://academy.celonis.com/learn/video/navigate-the-celonis-platform
date: 2026-04-02
tipo: aplicacao
---
# Masterizar Celonis: Navegação e Estrutura da Plataforma de Process Mining

## O que é
Plataforma SaaS de Process Mining e Business Intelligence que captura, modela e otimiza processos de negócio em tempo real através de análise de event logs de ERPs (SAP, Salesforce, Oracle) e sistemas transacionais. Navegação eficiente é essencial porque a interface organiza-se em múltiplas dimensões: dados (connectors), análises (PQL queries), dashboards (apps) e artefatos (packages).

## Como implementar

**Arquitetura Hierárquica da Plataforma:**

```
Organization (nivel raiz)
  ↓
Team (múltiplos times)
  ↓
Workspace (sandbox isolado pra projeto/cliente)
  ├── Data Integration
  │   ├── Connectors (SAP, Salesforce, etc.)
  │   ├── Data Jobs (ETL pipelines)
  │   └── Snapshots (cópias históricas)
  ├── Studio
  │   ├── Process Definitions (modelos de processos)
  │   ├── PQL Queries (análises customizadas)
  │   ├── Objects & Attributes (data model)
  │   └── KPI Definitions
  ├── Apps (dashboards pré-construídos)
  │   ├── Capacity Benchmark
  │   ├── Compliance Dashboard
  │   ├── Order-to-Cash Analysis
  │   └── Custom Apps (usando Power BI, Tableau)
  └── Explore
      ├── Process Viz (visualização interativa)
      ├── Bottleneck Analysis (gargalos)
      └── Variance Analysis (desvios)
```

**Passo 1: Acesso e Autenticação**

```
https://celonis.cloud/login
→ SSO (Okta, Azure AD) ou credenciais Celonis
→ Acesso a Organization Dashboard
```

Após login:

```
Organization Dashboard
├── Recent Workspaces (atalhos)
├── Create New Workspace (+ Workspace)
├── Team Management (administração)
└── Usage & Billing (consumo)
```

**Passo 2: Explorar Workspace**

```
Dentro de Workspace:

[Left Sidebar]
├── Data Integration (ícone banco de dados)
│   Clicar → gerenciar conectores de dados
├── Studio (ícone código/análise)
│   Clicar → construir análises customizadas
├── Apps (ícone dashboard)
│   Clicar → visualizar/usar dashboards
├── Explore (ícone mapa)
│   Clicar → exploração interativa de processos
└── Admin (ícone engrenagem)
    Clicar → configurar workspace
```

**Passo 3: Data Integration (Conectar Dados)**

Sequência típica:

```
1. Clique em "Data Integration"
   → Vê lista de conectores pré-configurados
   → Ou clique "+ Add Connector" pra novo

2. Configure Connector SAP (exemplo)
   ├── Host/Port (sistema SAP)
   ├── Credenciais (usuário SAP)
   ├── Tabelas a replicar (EKKO, EKPO para P2P)
   └── Schedule (daily sync às 2am)

3. Execute "Data Job" inicial
   → Celonis puxa histórico completo
   → Cria snapshots (versões de dados)

4. Valide dados
   ├── Quantas linhas?
   ├── Qual período cobre?
   ├── Há gaps/anomalias?
```

**Passo 4: Studio (Construir Análises)**

Onde a "magia" acontece. Três conceitos:

**4a. Process Definitions (Modelo de Processo)**

Descrever sequência de eventos/atividades:

```
P2P (Procure-to-Pay) Workflow:

Create Purchase Requisition
  ↓
Create PO
  ↓
Send to Vendor
  ↓
Receive Goods
  ↓
Receive Invoice
  ↓
3-Way Match Check
  ↓
Payment
  ↓
Close
```

Mapeamento em Celonis via "Event Columns":

```
Table: EKKO (PO header)
Key Events:
- "PO Created" → quando EKKO.ERDAT preenche
- "PO Sent" → quando EKKO.BEDAT preenchido
- "PO Closed" → quando EKKO.LOEKZ = 'X'
```

**4b. PQL Queries (Análise Customizada)**

Process Query Language = SQL + semântica de processos.

```pql
-- Exemplo: Casos que levam > 10 dias de PO a Pagamento

SELECT
    CASE_KEY,
    REWORK_COUNT,
    TOTAL_DURATION_DAYS
FROM
    DEFAULT (
        PROCESS_VARIANT_PERCENTAGE >= 0.5
    )
WHERE
    CASE_DURATION > '10d'
    AND PROCESS_NAME = 'P2P'
ORDER BY
    TOTAL_DURATION_DAYS DESC
```

Acesso via Studio → PQL Editor:

```
[Toolbox Esquerda]
├── Event Types (selecionar tabelas/eventos)
├── Functions (agregação, cálculo)
└── Templates (queries pré-construídas)

[Query Editor Centro]
├── Escrever ou arrastar para construir
└── Execute (botão azul)

[Results Direita]
├── Tabela de resultados
├── Visualização (gráfico)
└── Export (CSV/Excel)
```

**4c. Objects & Attributes (Data Model)**

Definir dimensões/características dos casos:

```
Object: Purchase Order
├── Attributes
│   ├── Vendor (fornecedor)
│   ├── Amount (valor)
│   ├── Category (categoria de compra)
│   ├── Plant (unidade fabril)
│   └── Procurement Officer (responsável)

Usado em análises:
- Filtrar casos por Vendor
- Agrupar por Category
- Colorir gráficos por Plant
```

**Passo 5: Apps (Dashboards Prontos)**

Celonis oferece Apps pré-construídas (muito usado):

```
Clique em "Apps"
├── Workbench (visão geral)
├── Capacity Benchmark (volume/capacidade)
├── Compliance Dashboard (conformidade)
│   ├── 3-way match compliance %
│   ├── Invoices matched on time %
│   └── Duplicate POs detected
├── Cycle Time Dashboard (duração)
│   ├── P2O (PO creation)
│   ├── O2I (invoice receipt)
│   └── I2P (payment)
├── Order-to-Cash (O2C)
├── Procure-to-Pay (P2P)
└── Finance Analytics

Cada app = múltiplos gráficos + filtros interativos
```

**Uso Prático de App:**

```
Abrir "Compliance Dashboard"
→ Top KPI cards
  - Compliance Rate: 87%
  - Outliers: 23 cases
  - Cycle Time: 8.2 days

→ Filtrar por Period (últimos 30 dias)
→ Filtrar por Plant (apenas Curitiba)
→ Ver casos não-compliant (botão "Drill Down")
  → Clique em caso específico (PO#12345)
    → Histórico detalhado de eventos
    → Timeline de 7 atividades
    → Por quê demorou? (bottleneck apontado)
```

**Passo 6: Explore (Análise Interativa)**

Ferramenta visual para explorar processos sem código:

```
Clique em "Explore"
→ Process Viz (mapa de processos)
  ├── Nós = atividades
  ├── Arestas = fluxos
  └── Espessura arestas = volume
  → Clique em nó → vê casos dessa atividade
  → Clique em aresta → vê casos que seguem esse fluxo

→ Bottleneck Analysis
  ├── Identifica atividades lentas
  ├── Casos que "quedam" mais tempo
  └── Sugestões de melhoria

→ Variance Analysis
  ├── Quais casos desviaram do caminho ideal?
  ├── Por que?
  └── Impacto financeiro
```

**Passo 7: Administração (Workspace Config)**

```
Clique em "Admin"
├── User Management (quem acessa o que)
├── Workspace Settings (nome, timezone, integrations)
├── Data Sources (conectores, schedules)
├── Capacity & Billing (consumo)
└── Audit Log (quem fez o quê, quando)
```

## Stack e requisitos

**Infraestrutura:**
- SaaS cloud-hosted (Celonis gerencia)
- Acesso via navegador moderno (Chrome, Safari, Firefox)
- VPN se conectando a sistemas on-premise (SAP, Oracle)

**Integrações:**
- ERP: SAP, Salesforce, Oracle, NetSuite, Dynamics 365
- Data Warehouse: Snowflake, Redshift, BigQuery
- BI Tools: Tableau, Power BI (exportar dados via API)
- Workflow: Zapier, Make (automação baseada em insights)

**Custo:**
- Modelo de consumo (não-seat-based)
- Baseado em: volume de dados, computação, usage
- Típicamente: $10K-$100K/ano dependendo escala

**Habilidades Necessárias:**
- Compreensão de processos de negócio (P2P, O2C, etc.)
- Familiaridade com dados ERP/transacionais
- SQL básico (se usar PQL)
- BI/dashboard literacy (interpretar KPIs)

## Armadilhas e limitações

**Curva de Aprendizado Acentuada:** Celonis é poderoso mas não intuitivo. Primeiras 2-3 semanas de ramp-up são necessárias. **Mitigação:**
- Usar Celonis Academy (vídeos, labs)
- Começar com Apps pré-construídas (não PQL)
- Contratar consultor Celonis pra first engagement

**Data Quality Issues:** Se dados ERP estão sujos (eventos faltando, timestamps errados), análises saem erradas. **Mitigação:**
- Auditar dados antes de análise ("data profiling")
- Implementar data quality checks em connector
- Trabalhar com DBA/ERP owner pra corrigir fonte

**PQL Complexity:** PQL é poderosa mas tem curva. Queries complexas podem ser lentas. **Mitigação:**
- Começar com templates/exemplos
- Usar Celonis PQL documentation + community
- Considerar usar Apps pré-construídas em vez de custom PQL

**Volume de Dados:** Se processos tem milhões de eventos/dia, Celonis pode ficar lento. **Mitigação:**
- Filtrar por período (últimos 6 meses, não 5 anos)
- Agregar eventos se possível
- Contactar Celonis pra otimização

**Integrações Limitadas:** Nem todo sistema ERP tem connector nativo. **Mitigação:**
- Usar connector genérico (HTTP API, DB connector)
- Ou pipeline intermediário (extrair pra CSV, importar em Celonis)

## Conexões

- [[neo4j-grafos-conhecimento]] - mapeamento de processos complexos
- [[metricas-de-engagement-ecommerce]] - KPI definition e monitoramento
- [[producao-criativa-como-processo-estatistico]] - otimização iterativa de processos

## Histórico
- 2026-04-02: Nota criada
- 2026-04-02: Nota reescrita e enriquecida pelo pipeline de curadoria
