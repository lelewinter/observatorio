---
tags: [conceito, criptografia, computação-quantica, segurança, algoritmos, nist-fips]
date: 2026-04-02
tipo: conceito
aliases: [PQC, Criptografia Pós-Quântica, Lattice-Based Crypto]
---
# Post-Quantum Cryptography (PQC)

## O que e

Conjunto de algoritmos criptográficos que rodam em computadores clássicos (não quânticos) mas resistem a ataques por computadores quânticos. Contrasta com RSA e ECC que quebram via algoritmo de Shor em poucos segundos uma vez qubit lógicos suficientes existam.

NIST finalizou três padrões em 2024: ML-KEM (key encapsulation), ML-DSA (assinaturas), SLH-DSA (hash-based). Baseado em problemas matemáticos que permanecem difíceis mesmo com computadores quânticos: lattices, códigos corretores de erro, funções hash.

## Como funciona

**Lattice-Based (ML-KEM, ML-DSA)**

Lattice é grade n-dimensional. Problema hard: dado ponto y, encontre ponto mais próximo em lattice. Computadores clássicos não conseguem em tempo polinomial; quânticos também não têm algoritmo conhecido (Shor não funciona em lattices).

```
Visualização 2D (real é 256-1024D):
  •                      y (ponto aleatório)

  ●---●---●           ● = pontos do lattice
  |   |   |           • = alvo, encontre ●
  ●---●---●

Operação de key encapsulation (ML-KEM):
1. Gere matriz A (pública)
2. Gere vetor secreto s (privado)
3. Compute e = A*s + erro (erro pequeno = trapdoor)
4. e é chave pública, s é chave privada

Se adversário tem e e A, precisa resolver LWE (Learning With Errors):
  e = A*s + erro (mod q)

  Sem erro: trivial (álgebra linear)
  Com erro: hard até em computador quântico
```

**Hash-Based (SLH-DSA)**

Sem dependência em problemas matemáticos. Usa apenas segurança de função hash criptográfica (SHA-256, SHAKE). Mais robusto porque hash é mais bem compreendido que lattices, mas mais lento.

Assinatura: árvore de hashes. Cada folha é assinatura única. Validar = verificar caminho na árvore. Problema: 2^h assinaturas por chave (h~20), chave é grande.

## Pra que serve

**Substituição de RSA em TLS**: Google + Cloudflare já testam ML-KEM em TLS 1.3 em produção. Em vez de ECDH para key exchange, usa ML-KEM. Handshake fica ~1.5x maior (overhead de chaves maiores) mas seguro contra quântico.

**Certificados de Longa Vida**: Dados que precisam ser confidenciais por 50+ anos (segredos de Estado, IP industrial) já estão em risco via "harvest now, decrypt later". PQC mitiga porque dados criptografados com ML-KEM/ML-DSA não são quebráveis mesmo futuramente.

**Assinaturas de Código e Updates**: Assinar executáveis/patches com ML-DSA garante que futuras alterações não sejam falsificadas por adversário com computador quântico.

**Mitigação de "Harvest Now, Decrypt Later"**: Adversários já coletam hoje dados TLS de você. Se seu certificado é RSA 2048-bit, decriptam em 2027–2030 quando qubit lógicos existem. Mudando para PQC agora, dados coletados hoje viram indecifrável.

## Exemplo pratico

Migrar certificado de RSA para ML-DSA:

```bash
# Gerar CA ML-DSA (em vez de RSA)
openssl genrsa -out old-ca.key 4096  # Old way
oqs-openssl genkey dilithium3 ca-key.pem  # New way (ML-DSA)

# Criar certificado raiz PQC
oqs-openssl req -new -x509 -newkey mlDSA87 \
  -keyout ca-mlkem-key.pem \
  -out ca-mlkem-cert.pem \
  -days 3650 \
  -subj "/CN=Quantum-Safe-Root-CA"

# Assinar certificado de servidor com CA PQC
oqs-openssl req -new -newkey mlKEM768 \
  -keyout server-key.pem \
  -out server.csr \
  -subj "/CN=api.acme.com"

oqs-openssl x509 -req \
  -in server.csr \
  -CA ca-mlkem-cert.pem \
  -CAkey ca-mlkem-key.pem \
  -out server-mlkem-cert.pem \
  -days 365 \
  -CAcreateserial

# Configurar nginx/apache
# server {
#   listen 443 ssl;
#   ssl_certificate server-mlkem-cert.pem;
#   ssl_certificate_key server-key.pem;
#   ssl_ciphers "TLS_ML_KEM_768_RSA_PSS_RSAE_SHA256:TLS_ECDHE_RSA_WITH_AES_256_GCM_SHA384";  # Hybrid
# }
```

**Benchmark de performance**:

```python
import timeit
from cryptography.hazmat.primitives.asymmetric import rsa, ec
from oqs import Sig

# RSA ECDSA
ecdsa_key = ec.generate_private_key(ec.SECP256R1())
ecdsa_sig = timeit.timeit(
    lambda: ecdsa_key.sign(b"test", ec.ECDSA(hashes.SHA256())),
    number=1000
) / 1000  # ~0.5ms per sign

# ML-DSA
mldsa = Sig("ML-DSA-87")
pubkey = mldsa.generate_keypair()
mldsa_sig = timeit.timeit(
    lambda: mldsa.sign(b"test"),
    number=100
) / 100  # ~20ms per sign (40x mais lento)

# Mas verificação é quase igual
# Trade: assinatura é 2–3x maior (2.4KB vs 256B para ECDSA)
```

## Aparece em
- [[migrar-criptografia-para-resistencia-quantica]] — aplicação completa de PQC + QKD
- [[algoritmos-shor-grover-quebra-rsa-ecdsa]] — por que PQC é necessário
- [[nist-fips-203-204-205]] — standards atuais

---
*Conceito extraído em 2026-04-02*
