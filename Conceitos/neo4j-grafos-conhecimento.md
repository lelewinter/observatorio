---
tags: [conceito, banco-de-dados, grafos, neo4j, conhecimento, persistência, aprendizado]
date: 2026-04-02
tipo: conceito
aliases: [Grafos de Conhecimento, Knowledge Graphs, Neo4j]
---
# Neo4j e Grafos de Conhecimento Persistente

## O que e

Neo4j é um banco de dados otimizado para armazenar e consultar grafos — estruturas onde dados são nós (entidades) conectados por relações com propriedades. Um grafo de conhecimento é a aplicação: mapeando conceitos (CVEs, alvos, técnicas, ferramentas) e suas relações, permitindo reutilização automática de conhecimento entre execuções.

Diferencia-se de bancos relacionais (PostgreSQL) porque consultas de relacionamento são O(1) em grafos vs O(n) em JOINs.

## Como funciona

**Estrutura de Nó**: Cada conceito é nó com propriedades.

```cypher
// CVE é nó
(:CVE {
  id: "CVE-2021-12345",
  description: "RCE em Apache Struts",
  cvss_score: 9.1,
  published_date: "2021-03-15",
  exploitable: true
})

// Alvo é nó
(:Target {
  domain: "acme.com",
  ip: "203.0.113.1",
  last_scanned: "2026-04-02",
  technologies: ["Apache 2.4.41", "OpenSSL 1.1.1"]
})

// Relacionamento entre nós
(target)-[:VULNERABLE_TO]->(cve)
(cve)-[:EXPLOITABLE_WITH]->(technique)
```

**Query para Reutilização**: Quando novo alvo entra com "Apache 2.4.41", consultamos:

```cypher
MATCH (target:Target {domain: "novo.com"})-[:USES_TECHNOLOGY]->(tech),
      (tech)-[:VULNERABILITY]->(cve:CVE),
      (cve)-[:EXPLOITABLE_WITH]->(technique)
WHERE target.technologies CONTAINS "Apache 2.4.41"
RETURN cve, technique
ORDER BY cve.cvss_score DESC
```

Resultado: lista de CVEs conhecidas + técnicas já bem-sucedidas, sem rescanning.

**Atualização Incremental**: Cada engajamento alimenta o grafo:

```python
from neo4j import GraphDatabase

driver = GraphDatabase.driver("bolt://localhost:7687")

def record_vulnerability(session, target_ip, cve_id, technique):
    session.run("""
        MATCH (t:Target {ip: $target_ip}), (c:CVE {id: $cve_id})
        CREATE (t)-[:VULNERABLE_TO {discovered_date: date()}]->(c)
        CREATE (c)-[:EXPLOITABLE_WITH]->(tech:Technique {name: $technique})
    """, target_ip=target_ip, cve_id=cve_id, technique=technique)

# Na execução de pentagi:
with driver.session() as session:
    record_vulnerability(session, "10.0.0.5", "CVE-2021-12345", "SQLi+RCE")
```

**Memória Organizacional**: Grafo cresce com tempo. Após 50 engajamentos, tem 10K+ nós. Cada novo engajamento começa com ~80% das vulnerabilidades já mapeadas (reuso).

## Pra que serve

**Red Team Automatizado**: Principal aplicação. Acelera reconhecimento consultando CVEs conhecidas de infraestrutura similar. Sem grafo: cada engajamento rescanneia tudo. Com grafo: pula direto para exploração.

**Compliance e Auditoria**: Rastreia vulnerabilidades encontradas ao longo do tempo, mudanças de risco, técnicas bem-sucedidas. Responde: "Qual % de vulnerabilidades críticas foi remediado em 6 meses?".

**Detecção de Anomalias em Segurança**: Correlaciona eventos — se técnica X foi usada com sucesso em alvo Y, e agora aparece tráfego suspeito emulando técnica X, dispara alerta.

**Recomendação e Navegação**: Busca semântica. Dado um CVE, recomenda técnicas similares, alvos com padrão similar, ferramentas relacionadas.

**Quando usar**: Sistema tem múltiplas execuções com oportunidade de aprender. Quando NOT usar: dados são altamente dinâmicos (ex: preços de ações — grafo fica obsoleto em minutos), ou é one-off (sem reuso).

## Exemplo pratico

Setup Neo4j local + alimentação via Python:

```bash
# Instalar Neo4j (Docker)
docker run -d \
  --name neo4j \
  -p 7687:7687 \
  -p 7474:7474 \
  -e NEO4J_AUTH=neo4j/password123 \
  neo4j:latest

# Conectar e criar schema
python -m neo4j.admin create-indexes
```

```python
from neo4j import GraphDatabase

class SecurityKnowledgeGraph:
    def __init__(self, uri, user, password):
        self.driver = GraphDatabase.driver(uri, auth=(user, password))

    def record_target(self, domain, ip, technologies):
        """Add target to graph"""
        with self.driver.session() as session:
            session.run("""
                CREATE (t:Target {domain: $domain, ip: $ip, scanned_at: datetime()})
                WITH t
                UNWIND $techs AS tech
                CREATE (t)-[:USES_TECHNOLOGY]->(t2:Technology {name: tech})
            """, domain=domain, ip=ip, techs=technologies)

    def record_vulnerability(self, target_ip, cve_id, cvss, exploited):
        """Log discovered vulnerability"""
        with self.driver.session() as session:
            session.run("""
                MATCH (t:Target {ip: $ip})
                CREATE (c:CVE {id: $cve, cvss: $cvss, exploited: $exploited})
                CREATE (t)-[:VULNERABLE_TO]->(c)
            """, ip=target_ip, cve=cve_id, cvss=cvss, exploited=exploited)

    def get_similar_targets(self, technologies):
        """Find targets with same tech stack"""
        with self.driver.session() as session:
            return session.run("""
                UNWIND $techs AS tech
                MATCH (t:Target)-[:USES_TECHNOLOGY]->(te:Technology {name: tech})
                RETURN t, COUNT(*) as match_count
                ORDER BY match_count DESC
            """, techs=technologies).data()

    def get_vulnerabilities_for_tech(self, tech_name):
        """Fetch known vulnerabilities for a technology"""
        with self.driver.session() as session:
            return session.run("""
                MATCH (te:Technology {name: $tech})<-[:USES_TECHNOLOGY]-(t:Target)
                    -[:VULNERABLE_TO]->(c:CVE)
                WHERE c.exploited = true
                RETURN DISTINCT c.id, c.cvss
                ORDER BY c.cvss DESC
            """, tech=tech_name).data()

# Uso em pentagi
kgraph = SecurityKnowledgeGraph("bolt://localhost:7687", "neo4j", "password123")

# Fase 1: Record target
kgraph.record_target("acme.com", "203.0.113.1", ["Apache 2.4.41", "OpenSSL 1.1.1"])

# Fase 2: Check similarities
similar = kgraph.get_similar_targets(["Apache 2.4.41"])
# Retorna: [{"t": Target {domain: "other.com"}, "match_count": 2}, ...]

# Fase 3: Get known CVEs
cves = kgraph.get_vulnerabilities_for_tech("Apache 2.4.41")
# Retorna: [{"id": "CVE-2021-12345", "cvss": 9.1}, ...]
# → Pula direto pra exploração, sem rescanning
```

**Resultado prático**: Primeiro engajamento: 2 horas (scan + pesquisa + exploração). Quinto engajamento com infraestrutura similar: 20 minutos (grafo fornece 80% das informações).

## Aparece em
- [[red-team-autonomo]] — PentAGI usa Neo4j como memória de agentes
- [[arquitetura-multi-agente-sistema-distribuído]] — como compartilhar conhecimento entre agentes

---
*Conceito extraído em 2026-04-02*
