---
tags: []
source: https://x.com/heyshrutimishra/status/2038126459450171860?s=20
date: 2026-04-02
tipo: aplicacao
---
# Implementar Loop de Auto-Aperfeiçoamento em Agentes

## O que é
Agente que registra erros, correções humanas e padrões bem-sucedidos em banco estruturado, promovendo insights valiosos para memória persistente que é consultada a cada nova requisição. Cria vantagem composta exponencial: menos erros novos, maior alinhamento ao usuário, melhoria não-linear.

## Como implementar
**1. Arquitetura de logging + RAG**: mantenha banco de erros e correções:

```python
import sqlite3
from datetime import datetime
from typing import Optional

class AdaptiveAgentMemory:
    def __init__(self, db_path: str = "agent_memory.db"):
        self.db = sqlite3.connect(db_path)
        self._init_tables()

    def _init_tables(self):
        """Cria tabelas de logging e memória."""
        self.db.execute("""
            CREATE TABLE IF NOT EXISTS errors (
                id INTEGER PRIMARY KEY,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                context TEXT,
                error_type TEXT,
                agent_response TEXT,
                human_correction TEXT,
                pattern_identified TEXT,
                resolved BOOLEAN DEFAULT FALSE,
                confidence FLOAT DEFAULT 0.5
            )
        """)

        self.db.execute("""
            CREATE TABLE IF NOT EXISTS learned_patterns (
                id INTEGER PRIMARY KEY,
                pattern TEXT UNIQUE,
                solution TEXT,
                frequency INTEGER DEFAULT 1,
                confidence FLOAT,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                last_applied DATETIME
            )
        """)

        self.db.execute("""
            CREATE TABLE IF NOT EXISTS user_preferences (
                id INTEGER PRIMARY KEY,
                preference_key TEXT UNIQUE,
                preference_value TEXT,
                strength FLOAT DEFAULT 0.8,
                learned_from TEXT
            )
        """)

        self.db.commit()

    def log_error(self, context: str, agent_response: str, human_correction: str, error_type: str = "general"):
        """Registra erro com contexto completo."""
        self.db.execute("""
            INSERT INTO errors (context, error_type, agent_response, human_correction)
            VALUES (?, ?, ?, ?)
        """, (context, error_type, agent_response, human_correction))
        self.db.commit()

    def promote_pattern(self, pattern: str, solution: str, confidence: float = 0.7):
        """Move aprendizado para memória permanente."""
        try:
            self.db.execute("""
                INSERT INTO learned_patterns (pattern, solution, confidence)
                VALUES (?, ?, ?)
            """, (pattern, solution, confidence))
        except sqlite3.IntegrityError:
            # Padrão já existe; aumentar frequency
            self.db.execute("""
                UPDATE learned_patterns
                SET frequency = frequency + 1,
                    confidence = MAX(confidence, ?)
                WHERE pattern = ?
            """, (confidence, pattern))

        self.db.commit()

    def retrieve_relevant_patterns(self, context: str, top_k: int = 5) -> list:
        """Recupera padrões relevantes via BM25 ou similaridade."""
        # Implementação simples; em produção usar embedding
        results = self.db.execute("""
            SELECT pattern, solution, confidence, frequency
            FROM learned_patterns
            WHERE pattern LIKE ?
            ORDER BY (confidence * frequency) DESC
            LIMIT ?
        """, (f"%{context[:20]}%", top_k)).fetchall()
        return results

    def save_preference(self, key: str, value: str, learned_from: str):
        """Registra preferência do usuário."""
        try:
            self.db.execute("""
                INSERT INTO user_preferences (preference_key, preference_value, learned_from)
                VALUES (?, ?, ?)
            """, (key, value, learned_from))
        except sqlite3.IntegrityError:
            self.db.execute("""
                UPDATE user_preferences
                SET preference_value = ?, learned_from = ?
                WHERE preference_key = ?
            """, (value, learned_from, key))
        self.db.commit()

    def get_user_context(self) -> dict:
        """Recupera preferências para injetar no prompt."""
        prefs = self.db.execute("""
            SELECT preference_key, preference_value
            FROM user_preferences
            ORDER BY strength DESC
        """).fetchall()
        return {k: v for k, v in prefs}
```

**2. Integração com agente**: injeta padrões aprendidos no contexto:

```python
from anthropic import Anthropic

class AdaptiveAgent:
    def __init__(self, memory: AdaptiveAgentMemory):
        self.memory = memory
        self.client = Anthropic()

    def process_request(self, user_prompt: str) -> str:
        """Processa requisição com contexto de aprendizados."""

        # Recuperar padrões relevantes
        patterns = self.memory.retrieve_relevant_patterns(user_prompt)
        user_prefs = self.memory.get_user_context()

        # Montar prompt com contexto aprendido
        enhanced_prompt = self._build_enhanced_prompt(
            user_prompt, patterns, user_prefs
        )

        response = self.client.messages.create(
            model="claude-3-5-sonnet-20241022",
            max_tokens=2000,
            messages=[{"role": "user", "content": enhanced_prompt}]
        )

        return response.content[0].text

    def _build_enhanced_prompt(self, user_prompt: str, patterns: list, prefs: dict) -> str:
        """Constrói prompt com memória contextual."""
        prompt = f"""Você está processando a seguinte requisição:
{user_prompt}

Aqui estão aprendizados de interações anteriores que podem ser relevantes:

Padrões de erro evitados:
{chr(10).join([f'- Se encontrar "{p[0]}", usar "{p[1]}" (confiança: {p[2]:.1%})' for p in patterns])}

Preferências do usuário:
{chr(10).join([f'- {k}: {v}' for k, v in prefs.items()])}

Aplique esses aprendizados ao responder."""

        return prompt

    def get_feedback(self, original_response: str, user_feedback: str) -> bool:
        """Processa feedback para melhorar agente."""
        # Detectar se feedback é positivo ou negativo
        if "errado" in user_feedback.lower() or "não" in user_feedback.lower():
            # Extrair padrão do erro
            pattern = self._extract_error_pattern(original_response, user_feedback)
            solution = user_feedback

            # Log + promoção
            self.memory.log_error(
                context=original_response[:200],
                agent_response=original_response,
                human_correction=user_feedback,
                error_type="user_feedback"
            )

            # Promover se confiança alta
            self.memory.promote_pattern(pattern, solution, confidence=0.85)

        elif any(word in user_feedback.lower() for word in ["perfeito", "obrigado", "exato"]):
            # Feedback positivo: aprender preferência
            pref_key = self._extract_preference(original_response)
            self.memory.save_preference(pref_key, original_response, "positive_feedback")

        return True

    def _extract_error_pattern(self, response: str, feedback: str) -> str:
        """Extrai padrão de erro para memorizar."""
        # Simplicidade: usar primeiras 30 chars do erro
        return feedback[:30]

    def _extract_preference(self, response: str) -> str:
        """Extrai preferência aprendida da resposta."""
        return f"format_{hash(response[:50])}"
```

**3. Validação de aprendizados**: evite poisoning de memória:

```python
class PatternValidator:
    def __init__(self, memory: AdaptiveAgentMemory):
        self.memory = memory

    def validate_pattern_before_promotion(self, pattern: str, solution: str) -> bool:
        """Valida antes de mover para memória permanente."""

        # Verificação 1: padrão muito genérico?
        if len(pattern) < 5:
            return False

        # Verificação 2: solução muito genérica?
        if len(solution) < 10:
            return False

        # Verificação 3: conflita com padrões existentes?
        conflicts = self.memory.db.execute("""
            SELECT pattern, solution FROM learned_patterns
            WHERE pattern SIMILAR TO ?
        """, (pattern,)).fetchall()

        if conflicts:
            for existing_pattern, existing_solution in conflicts:
                if existing_solution != solution:
                    print(f"Conflito detectado: {pattern} com {existing_pattern}")
                    return False  # Requer revisão manual

        # Verificação 4: confiança mínima
        # (Poderia incluir histórico de acertos/erros do padrão)

        return True

    def audit_memory(self):
        """Auditoria periódica da memória."""
        patterns = self.memory.db.execute("""
            SELECT pattern, frequency, confidence FROM learned_patterns
            ORDER BY frequency DESC
        """).fetchall()

        print("=== Top Patterns ===")
        for pattern, freq, conf in patterns[:10]:
            print(f"{pattern}: freq={freq}, conf={conf:.1%}")
```

**4. CLI para administração**: interface humana de supervisão:

```bash
# Ver aprendizados atuais
python adaptive_agent.py memory --view

# Deletar padrão específico (se errado)
python adaptive_agent.py memory --delete "padrão_id_123"

# Audit de qualidade
python adaptive_agent.py memory --audit

# Limpar padrões com confiança < 60%
python adaptive_agent.py memory --cleanup --min-confidence 0.6
```

## Stack e requisitos
- **BD**: SQLite (local) ou PostgreSQL (multi-usuário)
- **Embedding/Similaridade**: sentence-transformers ou Anthropic embeddings para BM25 avançado
- **Modelo base**: Claude 3.5 Sonnet (excellent em contextualização)
- **Armazenamento**: 1GB por ~1 million de registros de erro
- **Latência**: +200-500ms por consulta de memória (RAG)

## Armadilhas e limitações
- **Feedback poisoning**: usuário pode intencionalmente dar feedback errado para degradar agente. Implemente aprovações antes de promoção.
- **Derivas de confiança**: sistema de "confidence decay" importante — padrões antigos perdem relevância. Use `last_applied` para atualizar.
- **Ambiguidade**: mesmo padrão pode ter múltiplas soluções válidas (contexto-dependente). Inclua contexto na chave de padrão.
- **Escalabilidade de memória**: com 100k padrões, busca fica lenta. Use índices ou embedding vectors.

## Conexões
[[Auto-Evolução em Agentes de Código]], [[RAG com LLMs]], [[Claude Code - Melhores Práticas]], [[Memória Persistente em Agentes]], [[Meta-Aprendizado]]

## Histórico
- 2026-04-02: Nota criada
- 2026-04-02: Reescrita em padrão aplicação