---
tags: [conceito, computação-quantica, algoritmos, rsa, criptografia, ameaça-quântica]
date: 2026-04-02
tipo: conceito
aliases: [Algoritmo de Shor, Algoritmo de Grover, Quebra Quântica de RSA]
---
# Algoritmos de Shor e Grover: Ameaça Quântica à Criptografia

## O que e

Dois algoritmos quânticos que quebram segurança de sistemas criptográficos clássicos:

1. **Shor (1994)**: Fatoração de inteiros em tempo polinomial. Quebra RSA, ECDSA, Diffie-Hellman em horas se houver ~2000 qubits lógicos.
2. **Grover (1996)**: Busca em banco de dados sem estrutura em tempo sqrt(n). Reduz segurança efetiva de AES-256 para ~AES-128.

Relevância: Shor é ameaça crítica (todo RSA/ECC quebra). Grover é parcial (AES ainda seguro, mas margem menor).

## Como funciona

**Algoritmo de Shor**

Problema clássico: dado n = p*q (produto de dois primos grandes), encontre p e q. Melhor algoritmo clássico: number field sieve, O(2^n) sub-exponencial, infeasível para RSA-2048 (tempo de universo).

Shor resolve em O((log n)^3), tempo polinomial:

1. **Pick random a < n**
2. **Compute gcd(a, n)** — se > 1, achou fator (probabilidade ~0)
3. **Order-finding** (passo quântico):
   - Find menor r tal que a^r ≡ 1 (mod n)
   - Usa Quantum Phase Estimation
   - Classicamente: exponencial
   - Quanticamente: O(log^3 n)
4. **Extract factors**:
   - Se r é par: n = p*q onde p = gcd(a^(r/2) - 1, n), q = n/p
   - Se r é ímpar: retry

**Exemplo concreto (pequeno)**:
```
n = 15 = 3 * 5

Pick a = 7
Find r: 7^r ≡ 1 (mod 15)
  7^1 ≡ 7 (mod 15)
  7^2 ≡ 4 (mod 15)
  7^3 ≡ 13 (mod 15)
  7^4 ≡ 1 (mod 15)  → r = 4 (encontrado em O(log^3 15) no computador quântico)

7^(4/2) - 1 = 49 - 1 = 48
gcd(48, 15) = 3  → Fator encontrado!
15 / 3 = 5  → Outro fator
```

Para RSA-2048 (617 dígitos), computador quântico com ~2000 qubits lógicos quebra em horas.

**Algoritmo de Grover**

Busca em lista não-ordenada: classicamente O(n), Grover O(sqrt(n)).

Aplicação a criptografia de chave simétrica:

```
AES-256: espaço de chaves 2^256
Ataque clássico: brute force, O(2^256)
Ataque Grover: O(2^128)  → "efetivamente" AES-128

Não quebra AES-256 completamente, mas reduz margem de segurança
```

Solução simples: usar AES-512 (chave de 512 bits), então Grover → O(2^256), ainda exponencial.

Ou: usar algoritmos resistentes a Grover (nem RSA nem ECC tem proteção, mas PQC lattice-based tem).

## Pra que serve (entendimento)

**Entender por que RSA/ECC viram inseguros**: Shor não é ataque genérico — é específico para fatoração + discrete log. Esses dois problemas fundamentam toda criptografia de chave pública moderna.

**Definir urgência de PQC**: Shor em ~2000 qubits lógicos é 5–15 anos away (IBM, Google, China investem pesado). Quando isso chegar, RSA/ECC caem simultaneamente em escala global.

**Justificar "Harvest Now, Decrypt Later"**: Se adversário grava tráfego TLS hoje (criptografado com RSA), em 2030 executa Shor e decripta. Motivo urgente para PQC agora.

**Mitigar Grover**: AES-256 sobrevive Grover (torna-se AES-128 efetivamente, ainda seguro), mas margem é apertada. Usar AES com chave de 512 bits garante segurança mesmo contra Grover futuro.

## Exemplo pratico

**Simulação Clássica de Ordem-Finding (parte clássica de Shor)**

```python
import math
from math import gcd

def find_order_classical(a, n, max_iterations=1000):
    """
    Classicamente: find r tal que a^r ≡ 1 (mod n)
    Exponencial em bits de n
    """
    r = 1
    result = a % n
    while result != 1 and r < max_iterations:
        result = (result * a) % n
        r += 1
    return r if result == 1 else None

def shor_classical_simulation(n, max_iterations=100):
    """
    Simulação clássica de Shor (parte não-quântica)
    Lento, só funciona para números pequenos
    """
    for _ in range(max_iterations):
        a = random.randint(2, n - 1)
        factor = gcd(a, n)
        if factor != 1 and factor != n:
            return factor, n // factor

        r = find_order_classical(a, n)
        if r is None or r % 2 != 0:
            continue

        x = pow(a, r // 2, n)
        factor1 = gcd(x - 1, n)
        factor2 = gcd(x + 1, n)

        if factor1 != 1 and factor1 != n:
            return factor1, n // factor1
        if factor2 != 1 and factor2 != n:
            return factor2, n // factor2

    return None

# Teste
n = 15
p, q = shor_classical_simulation(n)
print(f"Fatores de {n}: {p} * {q}")  # Output: 3 * 5 (ou 5 * 3)

# Para RSA-2048, isso levaria bilhões de anos classicamente
# Com Shor quântico: ~1 hora em 2000 qubits lógicos
```

**Comparação de Segurança**:

```python
import hashlib

def grover_complexity(key_bits):
    """
    Redução de segurança via Grover
    Classicamente: 2^key_bits
    Com Grover: 2^(key_bits/2)
    """
    classical_ops = 2 ** key_bits
    grover_ops = 2 ** (key_bits / 2)
    return {"classical": classical_ops, "grover": grover_ops}

print(grover_complexity(256))
# classical: 2^256 ~ 10^77 ops
# grover: 2^128 ~ 10^39 ops (problema!)

print(grover_complexity(512))
# classical: 2^512 ~ 10^154 ops
# grover: 2^256 ~ 10^77 ops (seguro, AES-256 classicamente)
```

## Aparece em
- [[post-quantum-cryptography-pqc]] — solução a Shor
- [[quantum-key-distribution-qkd]] — solução ortogonal (física, não matemática)
- [[migrar-criptografia-para-resistencia-quantica]] — aplicação prática

---
*Conceito extraído em 2026-04-02*
