---
tags: []
source: https://github.com/liquidslr/system-design-notes
date: 2026-04-03
tipo: aplicacao
---
# Implementar System Design de Ponta a Ponta com Padrões dos Gigantes da Tech

## O que é

Este repositório consolida as notas do livro *System Design Interview – An Insider's Guide* (Vol. 1, 2ª ed.) cobrindo 16 capítulos de design de sistemas distribuídos, desde escalar do zero até milhões de usuários até projetar sistemas como YouTube, Google Drive e Discord. O valor prático está em ter um framework replicável para tomar decisões arquiteturais reais — não apenas passar em entrevistas, mas construir sistemas que funcionam em produção. Importa porque cada capítulo resolve um problema concreto com trade-offs documentados por empresas como Amazon, Google e Discord.

## Como implementar

**Passo 1 — Dominar o framework de estimativas (Cap. 2)**
Antes de projetar qualquer sistema, calibre seus números. Use as estimativas back-of-the-envelope como ponto de partida obrigatório: 1 servidor commodity aguenta ~10 mil conexões simultâneas com Go ou Node; um SSD entrega ~500 MB/s de leitura sequencial; latência de rede dentro do mesmo datacenter fica em ~0,5 ms, cross-region ~150 ms. Para calcular capacidade de armazenamento, parta do DAU (Daily Active Users), multiplique pelo tamanho médio de payload por request e projete para 5 anos. Exemplo: 10 milhões de usuários, 1 post/dia, 1 KB por post = ~10 GB/dia = ~18 TB em 5 anos sem compressão. Documente esses números antes de qualquer discussão arquitetural.

**Passo 2 — Aplicar o framework de entrevista/design (Cap. 3) no seu processo de ADR**
O framework proposto tem quatro fases: (1) entender o problema e o escopo, (2) proposta de design de alto nível, (3) deep dive em componentes críticos, (4) wrap-up com trade-offs. Mapeie isso para Architecture Decision Records (ADRs) no seu projeto: cada ADR deve ter contexto, opções consideradas, decisão tomada e consequências. Use ferramentas como `adr-tools` (CLI) ou simplesmente um diretório `/docs/adr/` com arquivos Markdown numerados.

**Passo 3 — Implementar Rate Limiter com Token Bucket (Cap. 4)**
O algoritmo Token Bucket é o mais indicado para APIs REST. Implemente em Redis com o seguinte padrão:

```lua
-- script Lua atomico no Redis
local key = KEYS[1]
local capacity = tonumber(ARGV[1])
local refill_rate = tonumber(ARGV[2])
local now = tonumber(ARGV[3])
local requested = tonumber(ARGV[4])

local bucket = redis.call('HMGET', key, 'tokens', 'last_refill')
local tokens = tonumber(bucket[1]) or capacity
local last_refill = tonumber(bucket[2]) or now

local elapsed = now - last_refill
local new_tokens = math.min(capacity, tokens + (elapsed * refill_rate))

if new_tokens >= requested then
  redis.call('HMSET', key, 'tokens', new_tokens - requested, 'last_refill', now)
  return 1
else
  return 0
end
```

No API Gateway (ex: Kong, Nginx, ou middleware Express/FastAPI), execute esse script antes de processar a request. Para sistemas distribuídos, use Redis Cluster para evitar single point of failure no rate limiter. Considere também o algoritmo Sliding Window Log para casos onde precisão é mais crítica que performance.

**Passo 4 — Consistent Hashing para distribuição de carga (Cap. 5)**
Implemente um virtual node ring. A ideia central: cada servidor físico recebe N posições no anel (ex: N=150 virtual nodes), distribuídas via hash. Para encontrar o servidor responsável por uma chave, faça hash da chave e mova no sentido horário até o próximo nó. Em Python:

```python
import hashlib
import bisect

class ConsistentHashRing:
    def __init__(self, virtual_nodes=150):
        self.ring = {}
        self.sorted_keys = []
        self.virtual_nodes = virtual_nodes

    def add_node(self, node):
        for i in range(self.virtual_nodes):
            key = self._hash(f"{node}:{i}")
            self.ring[key] = node
            bisect.insort(self.sorted_keys, key)

    def remove_node(self, node):
        for i in range(self.virtual_nodes):
            key = self._hash(f"{node}:{i}")
            self.ring.pop(key, None)
            idx = bisect.bisect_left(self.sorted_keys, key)
            if idx < len(self.sorted_keys) and self.sorted_keys[idx] == key:
                self.sorted_keys.pop(idx)

    def get_node(self, data_key):
        if not self.ring:
            return None
        h = self._hash(data_key)
        idx = bisect.bisect(self.sorted_keys, h) % len(self.sorted_keys)
        return self.ring[self.sorted_keys[idx]]

    def _hash(self, key):
        return int(hashlib.md5(key.encode()).hexdigest(), 16)
```

Esse padrão é exatamente o que o Apache Cassandra usa internamente. Quando um nó cai ou é adicionado, apenas ~1/N das chaves precisam ser remapeadas.

**Passo 5 — Key-Value Store com replicação e quorum (Cap. 6)**
Baseado no Amazon Dynamo: implemente replicação com N=3 réplicas, W=2 (quorum de escrita), R=2 (quorum de leitura). A fórmula de consistência forte é W + R > N. Para consistência eventual tolerante a partições, use W=1, R=1. Implemente vector clocks para detecção de conflitos: cada escrita carrega um vetor `{node_id: counter}`. Na leitura, compare versões; se houver divergência, passe ao cliente para resolver (estratégia last-write-wins ou merge manual). Para implementação rápida em Go, avalie bibliotecas como `etcd` (para consistência forte via Raft) ou `riak` (para consistência eventual ao estilo Dynamo).

**Passo 6 — URL Shortener com geração de ID distribuída (Caps. 7 e 8)**
Combine dois capítulos na prática. Para gerar IDs únicos sem coordenação central, use o algoritmo Snowflake do Twitter: 64 bits = 1 bit sinal + 41 bits timestamp (ms) + 10 bits machine ID + 12 bits sequence. Isso garante ~4 mil IDs/ms por máquina sem colisões. Para o URL Shortener em si: hash o ID gerado com Base62 (caracteres `[0-9a-zA-Z]`), use 7 caracteres (62^7 ≈ 3,5 trilhões de URLs). Armazene no Redis com TTL para URLs temporárias e em PostgreSQL para persistência. O redirect deve ser HTTP 301 (cache permanente no browser) para short URLs imutáveis ou 302 (sem cache) se precisar rastrear cliques.

**Passo 7 — News Feed com fan-out e cache em camadas (Cap. 11)**
Implemente fan-out on write para usuários com poucos seguidores (< 10 mil): ao postar, escreva o post ID no feed cache de todos os seguidores em Redis (lista ordenada por timestamp). Para celebrities (> 10 mil seguidores), use fan-out on read: não pré-computa, busca dinamicamente na leitura. Combine os dois: fetch do feed = posts pré-computados dos amigos normais + posts on-demand dos celebrities. Use Redis Sorted Set com score = timestamp Unix para ordenação eficiente: `ZADD feed:{user_id} {timestamp} {post_id}`. Mantenha apenas os últimos 1000 posts no cache; para histórico, caia no banco relacional.

**Passo 8 — Chat System com WebSocket e presença (Cap. 12)**
A arquitetura Discord/Slack escala assim: clientes conectam via WebSocket a Chat Servers stateful. Cada Chat Server mantém conexões ativas em memória. Para roteamento de mensagens entre servidores, use um message broker (Kafka ou RabbitMQ) — quando o Chat Server A recebe uma mensagem para um usuário conectado ao Chat Server B, publica no broker, B consome e entrega. Serviço de presença (online/offline) usa heartbeat: cliente envia ping a cada 5 segundos; se o servidor não receber em 30 segundos, marca como offline. Persista mensagens no Cassandra (escolha do Discord): partition key = `channel_id`, clustering key = `message_id` descendente, permitindo paginação eficiente pelo histórico.

## Stack e requisitos

- **Linguagens recomendadas para implementação**: Go (alta concorrência, WebSocket), Python (prototipagem rápida, scripts Lua/Redis), Java (ecossistema enterprise, Cassandra drivers maduros)
- **Redis**: versão 7.x, modo Cluster para produção; biblioteca `redis-py` (Python) ou `go-redis` (Go)
- **Apache Cassandra**: versão 4.x; driver oficial `cassandra-driver` (Python) ou `gocql` (Go)
- **Kafka**: versão 3.x para message broker do chat system;