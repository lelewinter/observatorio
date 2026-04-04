---
tags: [conceito, data-engineering, pipelines, arquitetura-dados]
date: 2026-04-02
tipo: conceito
aliases: [ETL, ELT]
---

# ETL e ELT: Padrões de Pipeline de Dados

## O que é

ETL (Extract, Transform, Load) e ELT (Extract, Load, Transform) são os dois padrões dominantes de processamento de dados. A diferença reside em *onde* e *quando* a transformação ocorre no pipeline.

- **ETL**: Extrai dados da fonte, transforma-os em um sistema intermediário, depois carrega no destino final. A transformação ocorre antes do warehouse/lake.
- **ELT**: Extrai dados da fonte, carrega-os no destino bruto, transforma *depois* no warehouse usando power de query nativa. Mais moderno.

## Como funciona

**ETL Clássico (1990s-2010s):**
```
Source DB → Extract → Transform (Talend/Informatica) → Load → Data Warehouse
            (aplicativo            (aplicativo           (aplicativo
             externo)               externo)              externo)
```
Cada etapa é separada. Transformações complexas rodam em servidores dedicados. Lento, custoso em infraestrutura.

**ELT Moderno (2015+):**
```
Source DB → Extract → Load → Transform (Spark/Redshift/BigQuery nativo)
            (rápido,        (dados
             bulk)          brutos)
```
Dados brutos chegam rápido no warehouse. Transformações usam SQL nativo do warehouse — muito mais rápido porque a computação está perto dos dados.

Teknicamente:
- **ETL** tipicamente usa Apache NiFi, Talend, ou custom Java/Python
- **ELT** usa Spark SQL, dbt (Dataform), ou queries nativas (Snowflake, BigQuery, Redshift)

## Para que serve

- **ETL**: Dados sensíveis que devem ser transformados antes de sair da rede corporativa. Pipelines heterogêneos (múltiplas fontes, formatos incompatíveis). Sistemas legacy sem warehouse nativo.

- **ELT**: Startups e times pequenos com datasets < 10TB. Data lakes em S3/GCS. Speed to insight é prioritário sobre compliance estrito. Elasticidade de computação (pay per query).

## Exemplo prático

**ETL com Airflow + Spark (tradicional):**
```python
from pyspark.sql import SparkSession

spark = SparkSession.builder.appName("ETL").getOrCreate()

# Extract
raw_df = spark.read.csv("s3://bucket/raw/orders.csv")

# Transform
clean_df = raw_df.filter(raw_df.amount > 0) \
                  .withColumn("date", to_date(raw_df.order_date))

# Load
clean_df.write.parquet("s3://bucket/warehouse/orders_clean")
```

**ELT com dbt (moderno):**
```sql
-- models/staging/stg_orders.sql
{{ config(materialized='table') }}

select
    order_id,
    customer_id,
    amount,
    cast(order_date as date) as order_date
from {{ source('raw', 'orders') }}
where amount > 0
```

O dbt roda como queries nativas no Redshift/BigQuery — sem orquestração externa.

## Aparece em

- [[10-repositorios-github-data-engineering-essenciais]] - Fundamento de pipelines
- [[spec-driven-ai-coding]] - Geração de código de pipeline com IA

---
*Conceito extraído em 2026-04-02*
