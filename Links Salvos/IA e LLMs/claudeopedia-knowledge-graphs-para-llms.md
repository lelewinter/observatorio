---
tags: [knowledge-graph, llm, claudeopedia, neo4j, rag]
source: https://x.com/alliekmiller/status/2040884878229565816
date: 2026-04-11
tipo: aplicacao
---
# Claudeopedia: Knowledge Graphs para LLMs

## O que e

Claudeopedia é um projeto inovador de base de conhecimento desenvolvido por Allie K. Miller que combina a ideia 'llm-wiki' de Andrej Karpathy com a habilidade /last30days e adiciona um /wiki skill customizado com argumentos de screenshot e download para transferir inputs crus mais rapidamente. O diferencial é uma visualização interativa que permite pesquisar uma base de conhecimento com filtros de data, possibilitando comparar evolução do conhecimento ao longo do tempo.

O projeto foi construído em um fim de semana inteiro e roda nativamente no Obsidian, funcionando como um sistema de recuperação aumentado (RAG) que aproveita grafos de conhecimento para melhorar significativamente a qualidade das respostas geradas por LLMs. A arquitetura combina busca semântica (via embeddings) com raciocínio simbólico (via grafos), reduzindo alucinações e melhorando precisão em queries multi-hop.

Diferentemente de sistemas RAG tradicionais que dependem apenas de similaridade vetorial, Claudeopedia extrai entidades nomeadas e relacionamentos entre elas, estruturando tudo em um grafo que permite traversal inteligente para responder perguntas que requerem múltiplos saltos lógicos. O sistema também inclui um cron job "question your assumptions" que roda escritas recentes e emails contra as wikis, com enterprise AI como tema principal sendo construído.

## Como implementar

### Arquitetura Core

A implementação envolve três componentes principais: extração de entidades, construção do grafo, e retrieval inteligente.

```python
# Exemplo de pipeline de extração usando Claude API
from anthropic import Anthropic

client = Anthropic()

def extract_entities_and_relations(text: str) -> dict:
    """Extrai entidades e relacionamentos de um texto"""
    message = client.messages.create(
        model="claude-opus-4",
        max_tokens=2048,
        messages=[
            {
                "role": "user",
                "content": f"""
Analise o seguinte texto e extraia:
1. Entidades nomeadas (pessoas, organizações, conceitos, tecnologias)
2. Relacionamentos entre essas entidades
3. Contexto temporal e importância

Formato de saída em JSON:
{{
    "entities": [
        {{"id": "e1", "name": "Nome", "type": "Tipo", "description": "..."}}
    ],
    "relationships": [
        {{"source": "e1", "target": "e2", "relation": "tipo_relacao", "strength": 0.9}}
    ],
    "temporal_markers": ["2026-04-10", ...],
    "importance": "high|medium|low"
}}

Texto:
{text}
"""
            }
        ]
    )
    return message.content[0].text
```

### Integração com Neo4j

O Neo4j 5.x oferece suporte nativo a grafos com capacidades de multi-database e paralelismo, ideal para escalar Claudeopedia.

```python
from neo4j import GraphDatabase

class KnowledgeGraphBuilder:
    def __init__(self, uri: str, user: str, password: str):
        self.driver = GraphDatabase.driver(uri, auth=(user, password))
    
    def create_entity(self, entity_id: str, name: str, entity_type: str):
        """Cria nó de entidade no grafo"""
        with self.driver.session() as session:
            session.run(
                "CREATE (n:Entity {id: $id, name: $name, type: $type})",
                id=entity_id,
                name=name,
                type=entity_type
            )
    
    def create_relationship(self, source_id: str, target_id: str, relation: str, strength: float):
        """Cria relacionamento entre entidades"""
        with self.driver.session() as session:
            session.run(
                """
                MATCH (a:Entity {id: $source}), (b:Entity {id: $target})
                CREATE (a)-[r:RELATES_TO {type: $relation, strength: $strength}]->(b)
                """,
                source=source_id,
                target=target_id,
                relation=relation,
                strength=strength
            )
    
    def query_with_graph(self, query: str) -> list:
        """Executa query que aproveita a estrutura do grafo"""
        with self.driver.session() as session:
            result = session.run(
                """
                MATCH (n:Entity)-[r:RELATES_TO*1..3]->(m:Entity)
                WHERE n.name CONTAINS $query
                RETURN DISTINCT m, r
                LIMIT 10
                """,
                query=query
            )
            return result.data()
```

### Integração no Obsidian

Usando a obsidian-local-rest-api, é possível criar notas automaticamente:

```python
import requests
import json
from datetime import datetime

class ObsidianIntegration:
    def __init__(self, vault_path: str, api_url: str = "http://localhost:27123"):
        self.vault_path = vault_path
        self.api_url = api_url
    
    def create_knowledge_note(self, title: str, content: dict, folder: str):
        """Cria nota no Obsidian via REST API"""
        
        frontmatter = f"""---
tags: [knowledge-graph, {', '.join(content.get('tags', []))}]
source: {content.get('source', '')}
date: {datetime.now().strftime('%Y-%m-%d')}
entities: {json.dumps(content.get('entities', []))}
---
"""
        
        body = f"""# {title}

## Resumo
{content.get('summary', '')}

## Entidades Principais
"""
        
        for entity in content.get('entities', []):
            body += f"- [[{entity['name']}]]: {entity['description']}\n"
        
        body += "\n## Conexões\n"
        for rel in content.get('relationships', []):
            body += f"- [[{rel['source']}]] -> {rel['relation']} -> [[{rel['target']}]]\n"
        
        payload = {
            "vault": "Claude",
            "path": f"{folder}/{title}",
            "content": frontmatter + body
        }
        
        response = requests.post(
            f"{self.api_url}/vault/create",
            json=payload
        )
        return response.json()
```

### GraphRAG Pipeline Completo

```python
class GraphRAGPipeline:
    def __init__(self, claude_client, neo4j_driver, obsidian_api):
        self.claude = claude_client
        self.neo4j = neo4j_driver
        self.obsidian = obsidian_api
    
    def process_document(self, doc: str, source: str):
        # 1. Extração de entidades
        entities = self._extract_entities(doc)
        
        # 2. Construção do grafo
        for entity in entities:
            self._add_to_graph(entity)
        
        # 3. Enriquecimento via Claude
        enriched = self._enrich_with_llm(doc, entities)
        
        # 4. Salvar no Obsidian
        self.obsidian.create_knowledge_note(
            title=enriched['title'],
            content=enriched,
            folder="Knowledge/GraphRAG"
        )
        
        return enriched
    
    def query_knowledge(self, question: str) -> str:
        # 1. Buscar no grafo
        graph_results = self._query_graph(question)
        
        # 2. Converter para contexto
        context = self._format_graph_context(graph_results)
        
        # 3. Passcar para Claude com RAG
        response = self.claude.messages.create(
            model="claude-opus-4",
            max_tokens=2048,
            messages=[
                {
                    "role": "user",
                    "content": f"""
Com base no seguinte conhecimento estruturado:
{context}

Responda a pergunta: {question}

Cite as entidades e relacionamentos que suportam sua resposta.
"""
                }
            ]
        )
        return response.content[0].text
```

## Stack e requisitos

### Infraestrutura

- **Neo4j 5.x ou superior** (Community Edition ou paid): banco de dados grafo nativo
  - Requisitos: Java 11+, 4GB RAM mínimo recomendado
  - Custa: Community (grátis), Enterprise (sob demanda)
- **Obsidian** (v1.5+): vault para armazenar notas
  - Plugin: obsidian-local-rest-api (permite acesso programático)
- **Claude API** (Anthropic): modelo base para extração e raciocínio
  - Custa: $0.003 / 1K tokens input, $0.015 / 1K tokens output

### Dependências Python

```
neo4j==5.15.0
anthropic==0.21.0
requests==2.31.0
python-dotenv==1.0.0
```

### Configuração Recomendada

Para uso pessoal (como Leticia):
- **Neo4j**: 4GB RAM, grafo com até 1M nós é gerenciável
- **Batch**: processar links em lotes de 5-10 por execução
- **Custo mensal estimado**: ~$15 USD em chamadas à API Claude (assumindo ~500 chamadas/mês)

Para escala maior (100+ usuários):
- **Neo4j Enterprise** ou **Neo4j Aura** (cloud)
- **Load balancing**: múltiplas instâncias Claude
- **Cache**: Redis para queries frequentes

## Armadilhas e limitacoes

### 1. Explosão Combinatória em Grafos Densos

Quando um grafo de conhecimento atinge milhões de nós, queries multi-hop podem explodir em complexidade exponencial. Uma traversal de 3 saltos em um grafo com média de 100 vizinhos por nó resulta em 100³ = 1 milhão de possibilidades.

**Solução**: Implementar pruning por relevância (usar embeddings para filtrar) e limitar profundidade de busca a 2-3 saltos máximo. Adicionar índices de similaridade semântica pré-computados.

### 2. Desalinhamento entre Estrutura do Grafo e Consultas Semânticas

LLMs extraem relações nem sempre formalizadas consistentemente. "Influenciado por", "baseado em" e "derivado de" podem ser conceitualmente similares mas estruturalmente diferentes no grafo. Isso causa misses em queries que deveriam retornar resultados.

**Solução**: Normalizar tipos de relações durante extração, usando uma ontologia restrita. Implementar equivalências ("INFLUENCED_BY" = "BASED_ON" para certos tipos de entidades). Validar extrações com um segundo pass de Claude antes de comittar ao grafo.

### 3. Alucinações em Extração de Entidades

Claude pode inventar relações que não existem no texto original. Exemplo: texto menciona "Python e JavaScript", modelo extrai relação "Python_COMPETES_WITH_JavaScript" quando o texto apenas listava ambas as opções.

**Solução**: Implementar validação por citação - exigir que cada relação venha com um span do texto original. Usar function calls estruturadas do Claude para limitar saída a campos predefinidos. Fazer spot-check manual de ~5% das extrações.

### 4. Colapso de Memória em Grafos com Muito Histórico

Conforme notas são adicionadas cronicamente, o grafo cresce sem limite. Entidades antigas podem ter baixa relevância mas continuam consumindo recursos e afetando query performance.

**Solução**: Implementar time-decay no ranking de relevanância (entidades/relações acessadas há 6+ meses têm peso reduzido). Arquivar periodicamente (ex: trimestral) subgrafos antigos em Neo4j backup. Usar TTL (time-to-live) em cache de embeddings.

### 5. Custo Operacional em Escala

Cada nova nota requer chamada ao Claude para extração (custo $0.01-0.05). Com 20 links/dia, isso dá ~$6-15/mês. Em escala (1000 usuários), o custo de API pode escalar para $6-15K/mês, inviabilizando economicamente.

**Solução**: Implementar batching inteligente (agrupar 5 documentos em uma chamada). Usar cache agressivo de extrações similares. Para escala, considerar fine-tuning de modelo menor em GPT-2 ou open-source equivalente, reduzindo custo por 90%.

## Conexoes

[[neo4j-graph-database|Banco de dados grafo nativo com 5.x melhorias]]
[[rag-retrieval-augmented-generation|Padrão de recuperação aumentada para LLMs]]
[[embeddings-semantic-search|Busca semântica com embeddings para filtragem]]
[[obsidian-rest-api|Integração programática com Obsidian via REST]]
[[claude-api-structured-output|Extrair dados estruturados com Claude API]]

## Historico

- 2026-04-11: Nota criada com implementação completa, GraphRAG pipeline, e stack recomendado
- Baseado em: Allie K. Miller's Claudeopedia announcement, Neo4j GraphRAG patterns, research em knowledge graphs + LLMs 2026