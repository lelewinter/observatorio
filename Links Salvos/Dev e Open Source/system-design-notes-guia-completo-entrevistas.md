---
tags: [system-design, entrevistas, arquitetura, distribuidos, backend]
source: https://github.com/liquidslr/system-design-notes
date: 2026-04-03
tipo: aplicacao
---
# System Design Interview Notes: Guia Completo com Recursos Reais

## O que é
System Design Interview Notes é um repositório GitHub que traduz os conceitos dos livros "System Design Interview" (Vol 1 e 2) em notas estruturadas com referências a sistemas reais (Amazon Dynamo, Cassandra, Discord, Netflix, Slack). Cobre desde escalar de zero até milhões de usuários, com capítulos dedicados a padrões como rate limiting, consistent hashing, caches distribuídos e muito mais. Acessível em pagefy.io/system-design-interview com recursos práticos para preparação de entrevistas em Big Tech.

## Como implementar

### Estrutura Básica: Rate Limiter
Um dos padrões mais críticos é rate limiting. Aqui está implementação prática usando Token Bucket:

```python
import time
from collections import defaultdict

class TokenBucketRateLimiter:
    def __init__(self, capacity: int, refill_rate: float):
        """
        capacity: tokens máximos no bucket
        refill_rate: tokens adicionados por segundo
        """
        self.capacity = capacity
        self.refill_rate = refill_rate
        self.buckets = defaultdict(lambda: {"tokens": capacity, "last_refill": time.time()})
    
    def allow_request(self, user_id: str) -> bool:
        """Verifica se usuário pode fazer requisição"""
        bucket = self.buckets[user_id]
        now = time.time()
        
        # Calcular tokens desde último refill
        time_passed = now - bucket["last_refill"]
        tokens_added = time_passed * self.refill_rate
        bucket["tokens"] = min(self.capacity, bucket["tokens"] + tokens_added)
        bucket["last_refill"] = now
        
        if bucket["tokens"] >= 1:
            bucket["tokens"] -= 1
            return True
        return False

# Uso prático
limiter = TokenBucketRateLimiter(capacity=100, refill_rate=10)  # 100 req, 10 req/seg

# Simular requisições
for user_id in ["user1", "user2", "user3"]:
    for _ in range(5):
        if limiter.allow_request(user_id):
            print(f"✓ {user_id} - requisição permitida")
        else:
            print(f"✗ {user_id} - limite atingido")
```

### Consistent Hashing: Distribuir Dados em Nós
Problema: como distribuir dados entre servidores mantendo rebalanceamento mínimo quando nós entram/saem?

```python
import hashlib
from sortedcontainers import SortedDict

class ConsistentHash:
    def __init__(self, num_virtual_nodes: int = 150):
        """
        num_virtual_nodes: aumenta para melhor distribuição
        Real-world: Discord usa ~150, Cassandra ~256
        """
        self.ring = SortedDict()  # hash_value -> node_id
        self.num_virtual_nodes = num_virtual_nodes
        self.nodes = set()
    
    def _hash(self, key: str) -> int:
        """Hash consistente (não randomizado)"""
        return int(hashlib.md5(key.encode()).hexdigest(), 16)
    
    def add_node(self, node_id: str):
        """Adiciona nó com múltiplos replicas no ring"""
        self.nodes.add(node_id)
        for i in range(self.num_virtual_nodes):
            virtual_key = f"{node_id}:{i}"
            hash_value = self._hash(virtual_key)
            self.ring[hash_value] = node_id
    
    def remove_node(self, node_id: str):
        """Remove nó do ring"""
        self.nodes.discard(node_id)
        keys_to_delete = [
            h for h, n in self.ring.items() if n == node_id
        ]
        for k in keys_to_delete:
            del self.ring[k]
    
    def get_node(self, key: str) -> str:
        """Encontra nó responsável pela chave"""
        hash_value = self._hash(key)
        
        # Achar primeiro nó >= hash_value (o anel é circular)
        index = self.ring.bisect_left(hash_value)
        if index == len(self.ring):
            index = 0
        
        return list(self.ring.values())[index]
    
    def get_replicas(self, key: str, replica_count: int = 3) -> list:
        """Retorna N nós para replicação"""
        hash_value = self._hash(key)
        index = self.ring.bisect_left(hash_value)
        if index == len(self.ring):
            index = 0
        
        replicas = []
        seen = set()
        for _ in range(len(self.ring)):
            node = list(self.ring.values())[index]
            if node not in seen:
                replicas.append(node)
                seen.add(node)
            if len(replicas) == replica_count:
                break
            index = (index + 1) % len(self.ring)
        
        return replicas

# Uso: cache distribuído tipo Memcached
hash_ring = ConsistentHash(num_virtual_nodes=150)
hash_ring.add_node("cache-1")
hash_ring.add_node("cache-2")
hash_ring.add_node("cache-3")

# Distribuir keys
keys = [f"user:{i}" for i in range(1000)]
distribution = {node: 0 for node in ["cache-1", "cache-2", "cache-3"]}

for key in keys:
    node = hash_ring.get_node(key)
    distribution[node] += 1

print("Distribuição de keys:", distribution)  # Esperado: ~333 cada

# Adicionar nó - apenas ~1/4 das keys precisam rebalancear
hash_ring.add_node("cache-4")
print("Após adicionar cache-4: Apenas ~25% das keys mudam de nó")
```

### Key-Value Store Distribuído: Inspirado em Dynamo (AWS)
Implementação simplificada do padrão Dynamo usado por Amazon, Cassandra, etc:

```python
import json
from datetime import datetime
from typing import Optional, List, Dict
from dataclasses import dataclass

@dataclass
class Version:
    """Vector clock para resolver conflitos"""
    vector: Dict[str, int]
    value: any
    timestamp: float
    
    def is_newer_than(self, other: 'Version') -> bool:
        """Comparação Lamport timestamp + vector clock"""
        # Simplificado para exemplo
        return self.timestamp > other.timestamp

class DynamoStyleKV:
    def __init__(self, node_id: str, replica_count: int = 3):
        self.node_id = node_id
        self.replica_count = replica_count
        self.store: Dict[str, List[Version]] = {}
        self.hash_ring = ConsistentHash()
    
    def put(self, key: str, value: any) -> bool:
        """
        Write com replicação e vector clocks
        Real-world: Dynamo necessita W (write quorum) acks
        """
        replicas = self.hash_ring.get_replicas(key, self.replica_count)
        
        version = Version(
            vector={replica: 1 for replica in replicas},
            value=value,
            timestamp=time.time()
        )
        
        if key not in self.store:
            self.store[key] = []
        
        self.store[key].append(version)
        
        # Cleanup: manter apenas versão mais recente ou versões concorrentes
        self.store[key] = self._resolve_conflicts(self.store[key])
        
        return True
    
    def get(self, key: str) -> Optional[any]:
        """
        Read com quorum - se houver conflitos, retorna todos (application resolve)
        """
        if key not in self.store or not self.store[key]:
            return None
        
        versions = self.store[key]
        if len(versions) == 1:
            return versions[0].value
        
        # Conflito detectado - application deve resolver
        # Em produção, retornar para client decidir (read repair)
        newest = max(versions, key=lambda v: v.timestamp)
        return newest.value
    
    def _resolve_conflicts(self, versions: List[Version]) -> List[Version]:
        """Remove versões claramente antigas, mantém concorrentes"""
        if not versions:
            return []
        
        # Manter apenas versões que não têm predecessor
        keep = []
        for v in versions:
            has_predecessor = any(
                other.timestamp < v.timestamp and 
                all(other.vector.get(k, 0) >= v.vector.get(k, 0) for k in v.vector)
                for other in versions
            )
            if not has_predecessor:
                keep.append(v)
        
        return keep if keep else [max(versions, key=lambda v: v.timestamp)]

# Teste
store = DynamoStyleKV("node-1", replica_count=3)
store.put("user:123:profile", {"name": "Leticia", "role": "engineer"})
print(store.get("user:123:profile"))
```

### Unique ID Generator: Inspirado em Snowflake (Twitter)
Para sistemas que precisam gerar billions de IDs únicos, monotônicos e distribuídos:

```python
import time
import threading

class SnowflakeIDGenerator:
    """
    ID format (64 bits):
    | sign (1) | timestamp (41) | datacenter (5) | worker (5) | sequence (12) |
    
    Timestamps: 41 bits = 69 anos (desde epoch)
    Datacenters: 5 bits = 32 centros
    Workers: 5 bits = 32 workers por datacenter
    Sequence: 12 bits = 4096 ids/ms por worker
    
    Real-world: Twitter, Discord, Instagram usam variações
    """
    
    EPOCH = 1609459200000  # 2021-01-01
    TIMESTAMP_BITS = 41
    DATACENTER_BITS = 5
    WORKER_BITS = 5
    SEQUENCE_BITS = 12
    
    WORKER_ID_SHIFT = SEQUENCE_BITS
    DATACENTER_ID_SHIFT = SEQUENCE_BITS + WORKER_BITS
    TIMESTAMP_SHIFT = SEQUENCE_BITS + WORKER_BITS + DATACENTER_BITS
    
    SEQUENCE_MASK = (1 << SEQUENCE_BITS) - 1
    MAX_WORKER_ID = (1 << WORKER_BITS) - 1
    MAX_DATACENTER_ID = (1 << DATACENTER_BITS) - 1
    
    def __init__(self, datacenter_id: int, worker_id: int):
        if datacenter_id > self.MAX_DATACENTER_ID or datacenter_id < 0:
            raise ValueError(f"Invalid datacenter_id: {datacenter_id}")
        if worker_id > self.MAX_WORKER_ID or worker_id < 0:
            raise ValueError(f"Invalid worker_id: {worker_id}")
        
        self.datacenter_id = datacenter_id
        self.worker_id = worker_id
        self.sequence = 0
        self.last_timestamp = -1
        self.lock = threading.Lock()
    
    def next_id(self) -> int:
        with self.lock:
            timestamp = int(time.time() * 1000)
            
            if timestamp == self.last_timestamp:
                self.sequence = (self.sequence + 1) & self.SEQUENCE_MASK
                if self.sequence == 0:
                    # Sequence overflow - esperar próximo ms
                    timestamp = self._wait_until(timestamp + 1)
            else:
                self.sequence = 0
            
            if timestamp < self.last_timestamp:
                raise ValueError("Clock went backwards!")
            
            self.last_timestamp = timestamp
            
            # Montar ID
            id_value = (
                ((timestamp - self.EPOCH) << self.TIMESTAMP_SHIFT) |
                (self.datacenter_id << self.DATACENTER_ID_SHIFT) |
                (self.worker_id << self.WORKER_ID_SHIFT) |
                self.sequence
            )
            
            return id_value
    
    def _wait_until(self, target_timestamp: int) -> int:
        while True:
            ts = int(time.time() * 1000)
            if ts >= target_timestamp:
                return ts

# Teste: gerar 10M ids em 1 segundo
generator = SnowflakeIDGenerator(datacenter_id=1, worker_id=5)
start = time.time()
ids = [generator.next_id() for _ in range(10_000_000)]
elapsed = time.time() - start
print(f"Gerou 10M ids em {elapsed:.2f}s ({10_000_000/elapsed/1e6:.1f}M ids/seg)")
print(f"Amostra de IDs: {ids[:5]}")
```

## Stack e Requisitos

### Tecnologias Reais Mencionadas
- **Distributed Consensus**: Raft (etcd, Consul), Paxos (Google), PBFT
- **Databases**: 
  - **DynamoDB** (AWS) - NoSQL, sharding automático, global tables
  - **Cassandra** (Apache) - Column-family, eventual consistency, peer-to-peer
  - **HBase** - BigTable clone, batch processing massive
  - **MongoDB** - Document-based, replica sets
- **Caches**: Redis, Memcached, DynamoDB TTL
- **Message Queues**: Kafka (billions/day - LinkedIn), RabbitMQ, AWS SQS/SNS
- **Search**: Elasticsearch (Netflix, Uber), Solr
- **Rate Limiting**: Redis counters, Token Bucket (upstream)
- **APIs**: REST vs gRPC vs GraphQL tradeoffs

### Recursos Disponíveis
- **Repositório GitHub**: github.com/liquidslr/system-design-notes (código + markdown)
- **Website**: pagefy.io/system-design-interview (versão web)
- **Livros referência**: "System Design Interview" Vol 1 & 2 (Alex Xu)
- **Real-world case studies**: 
  - Discord - 8.5M concurrent users, Go + Rust
  - Netflix - 200M subscribers, multiple region failover
  - Slack - message consistency, read receipts
  - Uber - location-based sharding, ETA prediction

### Custo para Estudar
- Totalmente grátis (repositório open source)
- Livros recomendados: ~$40-50 cada (opcional, as notas cobrem 80%)
- Infraestrutura pra praticar: Docker + PostgreSQL/Redis = free

## Armadilhas e Limitações

### 1. Teoria vs Prática em Entrevista
As notas cobrem conceitos corretamente mas entrevistas em Big Tech focam em trade-offs específicos e decisões em tempo real. Você pode conhecer Consistent Hashing perfeitamente mas falhar em explicar quando NÃO usar.

**Mitigação**:
- Após estudar cada tópico, praticar 2-3 design problems por semana
- Simular entrevistas com alguém (ou grava você mesmo)
- Focar em: "Por quê essa escolha? Alternativas? Trade-offs?"

```python
# Checklist para cada design:
design_checklist = {
    "escalabilidade": "Quantos usuários? Read/write ratio?",
    "latencia": "P99? P50? Aceitável pra user experience?",
    "consistencia": "Eventual vs Strong? Conflitos toleráveis?",
    "custo": "Infraestrutura estimada?",
    "operacional": "Fácil de monitorar? Alertas? Runbooks?",
}
```

### 2. Exemplos Simplificados vs Realidade
O rate limiter Token Bucket acima é single-machine. Produção em escala precisa:
- Rate limiter distribuído (Redis)
- Sincronização entre servidores
- Handling de race conditions
- Cascading failures

**Mitigação**:
- Implementar em Redis de verdade:
```python
import redis

class DistributedTokenBucket:
    def __init__(self, redis_client, key_prefix: str, capacity: int, refill_rate: float):
        self.redis = redis_client
        self.key_prefix = key_prefix
        self.capacity = capacity
        self.refill_rate = refill_rate
    
    def allow_request(self, user_id: str) -> bool:
        """Atomic operation via Lua script"""
        script = """
        local bucket = KEYS[1]
        local now = tonumber(ARGV[1])
        local capacity = tonumber(ARGV[2])
        local refill_rate = tonumber(ARGV[3])
        
        local data = redis.call('HGETALL', bucket)
        local tokens = tonumber(data[2]) or capacity
        local last_refill = tonumber(data[4]) or now
        
        local time_passed = now - last_refill
        tokens = math.min(capacity, tokens + time_passed * refill_rate)
        
        if tokens >= 1 then
            tokens = tokens - 1
            redis.call('HSET', bucket, 'tokens', tokens, 'last_refill', now)
            return 1
        end
        return 0
        """
        
        key = f"{self.key_prefix}:{user_id}"
        return self.redis.eval(script, 1, key, time.time(), self.capacity, self.refill_rate)
```

### 3. Confundir Escalabilidade Horizontal vs Vertical
Notas mencionam sharding (horizontal) mas muitos confundem com simplesmente adicionar RAM (vertical). Máquinas cada vez maiores = limite físico.

**Mitigação**:
- Sempre pensar em "E se crescer 10x?". Vertical não escala indefinidamente.
- Sharding strategy desde o início: hash(user_id) % num_shards
- Planar rebalanceamento consistente (Consistent Hash)

### 4. Falta de Prática com Números Reais
Entrevistas pedem estimativas: "Quantos reads por segundo? Storage estimado? Bandwidth?"

**Mitigação**:
```python
# Ferramenta de estimation
def estimate_system_size(
    monthly_active_users: int,
    posts_per_user_per_month: int,
    avg_post_size_kb: float,
    read_write_ratio: int = 100
):
    """Estima escala (útil pra entrevistas)"""
    daily_active = monthly_active_users / 30
    daily_writes = daily_active * (posts_per_user_per_month / 30)
    daily_reads = daily_writes * read_write_ratio
    
    daily_storage = daily_writes * avg_post_size_kb
    yearly_storage = daily_storage * 365
    
    writes_per_sec = daily_writes / 86400
    reads_per_sec = daily_reads / 86400
    
    return {
        "rps_writes": writes_per_sec,
        "rps_reads": reads_per_sec,
        "storage_yearly_gb": yearly_storage / 1024,
        "bandwidth_mbps": (reads_per_sec * avg_post_size_kb * 8) / 1000
    }

# Exemplo: Twitter scale
twitter_estimate = estimate_system_size(
    monthly_active_users=300_000_000,
    posts_per_user_per_month=10,
    avg_post_size_kb=1.0
)
print(f"Tweets/seg: {twitter_estimate['rps_writes']:.0f}")
print(f"Reads/seg: {twitter_estimate['rps_reads']:.0f}")
print(f"Storage/ano: {twitter_estimate['storage_yearly_gb']:.0f} GB")
```

## Conexões
- [[rate-limiting-algoritmos]] - Deep dive em Token Bucket, Sliding Window, Leaky Bucket
- [[consistent-hashing-distribuido]] - Aplicações práticas em cache/sharding
- [[cap-theorem-entrevistas]] - Tradeoffs Consistency/Availability/Partition tolerance
- [[database-sharding-estrategias]] - Quando e como fazer sharding
- [[nosql-vs-sql-escolhas]] - Comparação para cada use case
- [[kafka-message-streaming]] - Event sourcing, distributed logs

## Histórico
- 2026-04-03: Nota criada com implementações práticas de Rate Limiter, Consistent Hashing, Dynamo-style KV, Snowflake IDs
