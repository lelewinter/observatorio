---
tags: [entrevistas, algoritmos, leetcode, preparacao, engenharia, system-design, behavioral]
source: https://medium.com/@kp9810113/system-design-interviews-in-2026-leetcode-still-gets-you-in-this-gets-you-hired-02dc6e85fb54
date: 2026-04-11
tipo: aplicacao
---
# Preparar para 50% de Entrevistas com LeetCode: O Que Falta

## O que é

LeetCode cobre apenas ~50% das perguntas técnicas em entrevistas FAANG em 2026. Enquanto problemas de Data Structures & Algorithms (DSA) são base, o custo de negligenciar System Design (30%), Behavioral (20%) e Communication Skills é aumentar drasticamente a chance de rejeição mesmo com ótimo score em DSA. Candidatos que dominam apenas algoritmos são comuns: "passes coding, fails hiring decision."

**A realidade**: passar em todas as rodadas de coding é prerequisito, não suficiente. Em 2026, a distribuição de peso em entrevistas é:
- **Coding/LeetCode**: 50% → testa capacidade de transformar ideias em código correto e eficiente
- **System Design**: 30% → testa julgamento arquitetural, trade-offs, escalabilidade
- **Behavioral**: 20% → testa soft skills, ownership, collaboration, growth mindset
- **Communication**: Transversal em todas as rodas → capacidade de explicar pensamento sob pressão

Problemas: LeetCode otimiza para velocidade de resolução (memorizar padrões). System Design exige reasoning sob ambiguidade. Behavioral é storytelling + STAR method (Situation-Task-Action-Result). São músculos diferentes.

## Como implementar

### Fase 1: Dominar LeetCode (6-8 semanas, 1-2 horas/dia)

**Semana 1-2: Arrays & Strings (25 easy problems)**
- Foco: two pointers, sliding window, prefix sums
- Exemplo: "Two Sum", "Best Time to Buy and Sell Stock", "Container With Most Water"
- Estratégia: não pule para ler solução; tente 30min antes. Se travar, read explain, repeat day 2.

```python
# Padrão sliding window (máxima janela com produto < k)
def maxProduct(nums, k):
    left, product = 0, 1
    max_length = 0
    for right in range(len(nums)):
        product *= nums[right]
        while product >= k:
            product //= nums[left]
            left += 1
        max_length = max(max_length, right - left + 1)
    return max_length
```

**Semana 3-4: Trees & Graphs (20 medium problems)**
- Foco: DFS/BFS, tree traversal, connected components
- Exemplo: "Binary Tree Level Order", "Number of Islands", "Course Schedule"
- Padrão crítico: quando usar DFS vs BFS? Quando precisa de memoization?

```python
# DFS com memoization (problema clássico)
class Solution:
    def maxPathSum(self, root):
        self.max_sum = float('-inf')
        
        def dfs(node):
            if not node:
                return 0
            left = max(dfs(node.left), 0)
            right = max(dfs(node.right), 0)
            self.max_sum = max(self.max_sum, node.val + left + right)
            return node.val + max(left, right)
        
        dfs(root)
        return self.max_sum
```

**Semana 5-6: Dynamic Programming (15 hard problems)**
- Foco: reconhecer subproblemas, definir estado, escrever transição
- Exemplo: "Longest Increasing Subsequence", "Word Break II", "Edit Distance"
- Trap: memorizar fórmulas erradas. Teste estado diferente, veja qual converge.

```python
# DP com space optimization
def coinChange(coins, amount):
    dp = [float('inf')] * (amount + 1)
    dp[0] = 0
    for coin in coins:
        for i in range(coin, amount + 1):
            dp[i] = min(dp[i], dp[i - coin] + 1)
    return dp[amount] if dp[amount] != float('inf') else -1
```

**Semana 7-8: Mock Interviews + Speed Run**
- LeetCode contests (medium difficulty, 1h30, 2-3x/semana)
- Pramp ou LeetCode Live Sessions (simular pressão)
- Goal: resolver medium em <25min, hard em <40min (simulando room)

### Fase 2: Dominar System Design (4-6 semanas, 1-2 horas/dia)

**Semana 1: Fundamentos (load balancing, caching, databases)**
- Leia: "Designing Data-Intensive Applications" (Kleppmann) cap 1-5
- Atividade: desenhe arquitetura do Twitter em um papel A4, explicar 5min

```
Arquitetura Twitter (simplified):
- Client (web/mobile) → load balancer (AWS ELB)
- API servers (horizontal scale, stateless)
- Cache layer (Redis: tweets recentes, follows)
- Primary DB (write): PostgreSQL ou Cassandra
- Read replicas: distributed across regions
- Message queue (Kafka): assync tweet propagation
- Search: Elasticsearch index
```

**Semana 2-3: Estudar 5-7 designs profundos**
- YouTube (video storage, encoding, recommendation)
- Instagram (scale to billions of users, image storage, feed generation)
- Uber (location, matching, payments)
- Discord (millions concurrent users, low latency)
- Netflix (content delivery, personalization)

Para cada: estude a real architecture (blog posts da empresa), depois redesenha no quadro.

**Semana 4-5: Practice na entrevista**
- Usar SystemDesignSchool ou Alex Xu's course
- Simulação: 45min design, 10min Q&A
- Foco: não decorar respostas. Explicar tradeoffs ("se escolho Cassandra vs PostgreSQL, ganho throughput mas perco ACID transactions")

```
Roteiro durante entrevista:
1. Clarify requirements (40% do tempo!)
   - Scale: 1M DAU, 100k queries/sec?
   - Read:write ratio? 100:1?
   - Latency SLA? (e.g., p99 < 100ms)
   
2. API design (10 min)
   - GET /tweets?user_id=123&limit=20
   - POST /tweets with {text, images[]}
   
3. Data model (15 min)
   - Users table, Tweets table, Follows table
   - Indices? (user_id, created_at para feed)
   
4. Scale (10 min)
   - Shard by user_id? By timestamp?
   - Cache hot tweets
   - CDN para imagens
   
5. Deep dive 1 topic (10 min)
   - Interviewer escolhe: "tell me more about feed generation"
   - Você explica: fanout-on-read vs fanout-on-write tradeoff
```

### Fase 3: Dominar Behavioral (2-3 semanas)

**STAR Method + storytelling**
- **S** (Situation): contexto, escala, restrição
- **T** (Task): o que você foi assignado?
- **A** (Action): exatamente qual ação você tomou?
- **R** (Result): métrica concreta (reduzeu latência 40%, shipped 2 weeks early)

**Stories pré-preparadas (5-7 mínimo):**
1. Um projeto onde você liderou (ownership)
2. Um projeto onde falhou (learnings)
3. Um projeto com conflito de team (collaboration)
4. Um projeto com deadline apertado (time management)
5. Um projeto técnico duro (problem solving)
6. Um projeto onde você ensinou alguém (mentorship)
7. Um projeto onde você rejeitou uma abordagem (judgment)

```
Exemplo ruim:
Q: "Tell me about a time you showed ownership"
A: "I owned a project that was really cool. We used microservices 
   and it was deployed to the cloud."
Problem: genérico, sem números, sem learnings

Exemplo bom:
A: "When I joined the team, the search service was handling 1K 
   queries/sec but had 500ms latency. I profiled, found the issue 
   was N+1 queries in recommendation loop. Rewrote with batch fetch 
   + caching (Redis), cut latency to 100ms. Throughput increased 
   5x without infra cost increase. The team adopted the pattern 
   for 3 other services. What I learned: always profile before 
   optimizing."
```

**Questions que vão fazer:**
- Walk me through your resume, project X in detail
- Most complex technical challenge you've faced?
- Tell me about a time you disagreed with a decision
- Describe a time you failed
- How do you handle ambiguity?
- What do you do when you don't know something?

## Stack e requisitos

### Recursos LeetCode
- **LeetCode Premium**: $159/ano (essencial para solution explanations + mock interviews)
- **Alternative gratuita**: NeetCode.io (vídeos explicativos detalhados para ~150 problemas comuns)
- **Language**: Python recomendado (sintaxe rápida, 30% mais rápido que Java em entrevista)

### Recursos System Design
- **"Designing Data-Intensive Applications"** (Kleppmann, ~700 páginas, $50)
- **"System Design Interview"** (Alex Xu, Udemy ~$15)
- **SystemDesignSchool.io**: mock interviews, $50
- **Blogs**: High Scalability, Instagram Engineering, Uber Engineering

### Recursos Behavioral
- Não precisa de resources. Prepara stories mentalmente, pratica em Pramp

### Hardware/Setup
- **Ambiente coding**: VS Code + Python 3.10+
- **Whiteboard**: físico ou Miro.com
- **Recording**: Loom (grabar mock interviews, review seu desempenho)

### Timeline estimada
- **6 semanas: LeetCode + System Design + Behavioral = interview-ready**
- Aplicar depois que passar em online assessment (OA) de LeetCode

## Armadilhas e limitacoes

### Armadilha 1: Memorizar soluções, não entender padrões
Sintoma: resolve "Two Sum" em 5min, mas "3Sum Closest" trava. 
Root cause: memorizou código, não entendeu two pointer technique.
Fix: depois cada problema, explique padrão em voz alta. Resolve novamente dias depois sem ver solution.

### Armadilha 2: Negligenciar System Design até 1 semana antes
Sintoma: passa todas as rodas coding, falha system design round.
Root cause: sistema design é habilidade diferente, precisa 4-6 semanas.
Fix: estude em paralelo. Semanas 1-4 são 50% coding, 50% system design. Semana 5-6 mais design.

### Armadilha 3: Behavioral answers soam ensaiados/robôticos
Sintoma: "one time I showed leadership was when I delegated tasks"
Root cause: memorizou answer genérica, não tem story real.
Fix: escreva 3-4 versões por story, com diferentes ângulos (technical depth, leadership, failure). Pratica até soar natural.

### Armadilha 4: LeetCode-only = rejeição sênior
Sintoma: mid-level passa em coding, falha em design + behavioral (pesa 50% em Senior+)
Root cause: FAANG calibração: junior pesa coding 70%, senior pesa design+behavior 50%+
Fix: se candidatando a senior, gaste 40% tempo em design deep dives.

### Armadilha 5: "Decorei 200 problemas, ainda erro"
Sintoma: fez 200 LeetCode, aceita ~70%, durante entrevista trava em variação
Root cause: reconhecimento de padrão fraco. Problema é variação que força pensar.
Fix: foque em 100 core problems (NeetCode 100 curated list), domine profundamente. Resolutivas por pattern (arrays: 25, trees: 20, graphs: 15, DP: 20, etc.)

### Armadilha 6: Communication breakdown durante coding
Sintoma: escreve código certo, mas interviewer acha que tá confuso
Root cause: não explica pensamento. Código é output, não input.
Fix: durante entrevista, fale em voz alta antes de escrever. "I'll iterate 2 pointers from ends..." antes digita. Interviewer acompanha.

## Conexoes

[[construcao-de-llm-do-zero|LLM do zero (system design de redes neurais)]]
[[entrevistas-tecnicas-2026|Framework completo de entrevistas]]
[[design-patterns-engenharia|Padrões de design em produção]]

## Historico
- 2026-04-11: Nota reescrita com pesquisa aprofundada, 3 fases, código, armadilhas específicas
- 2026-04-02: Nota original criada
