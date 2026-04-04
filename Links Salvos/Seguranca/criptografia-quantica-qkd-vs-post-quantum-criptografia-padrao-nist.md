---
tags: [computacao-quantica, criptografia, qkd, post-quantum, nist, seguranca, rsa, aes]
source: https://www.nist.gov/pqc
date: 2026-03-28
tipo: aplicacao
---
# Migrar Infraestrutura de Criptografia para Resistência Quântica: PQC e QKD

## O que e

Computadores quânticos suficientemente avançados quebram RSA, ECC e praticamente toda criptografia de chave pública moderna em horas via algoritmo de Shor. A defesa exige duas estratégias complementares: substituir RSA/ECC por **Post-Quantum Cryptography (PQC)** — algoritmos resistentes a ataques quânticos que rodam em hardware clássico — e implementar **Quantum Key Distribution (QKD)** para distribuição de chaves fisicamente incondicionalmente segura.

A urgência é real: adversários já coletam dados criptografados hoje para decriptação futura ("harvest now, decrypt later"), e agências governamentais exigem conformidade com padrões NIST antes de 2027.

## Como implementar

**Diagnóstico: O que está em risco**

Qualquer dado transportado via HTTPS, VPN, certificados SSL/TLS com RSA/ECC está vulnerável. AES-256 é parcialmente afetado (Grover reduz segurança efetiva para ~128 bits) mas ainda considerado seguro por décadas. Foco imediato: (1) chave pública em certificados digitais, (2) key exchange (Diffie-Hellman), (3) assinaturas digitais em documentos/código.

Mapeie seu inventário:
```bash
# Find OpenSSL certificates in use
openssl s_client -connect api.acme.com:443 -showcerts 2>/dev/null | grep -A5 "Public-Key:"

# Check TLS versions and cipher suites
nmap --script ssl-enum-ciphers -p 443 api.acme.com

# Audit code signatures
gpg --list-keys  # Check key sizes
find . -name "*.crt" -o -name "*.pem" | xargs openssl x509 -in {} -noout -pubkey -text
```

Resultado esperado: inventário de todos os certificados RSA/ECC e seus key sizes, datas de expiração, sistemas dependentes.

**Post-Quantum Cryptography: Implementação em 3 Fases**

**Fase 1: Standards Adoption (2026–2027)**

NIST finalizou 3 padrões em agosto de 2024 (FIPS 203, 204, 205) + HQC em março 2025:

1. **FIPS 203 (ML-KEM)**: encapsulamento de chave para key exchange, substitui ECDH
   - Baseado em Module-LWE (lattice-based)
   - Tamanho de chave: 768 bytes (privada) + 1184 bytes (pública)
   - Overhead de largura de banda: ~1.5x vs ECDH
   - Implementação: liboqs, wolfSSL, boringssl

2. **FIPS 204 (ML-DSA)**: assinaturas digitais, substitui ECDSA
   - Baseado em Module-LWE/SIS
   - Tamanho de assinatura: 2420 bytes vs 256 bytes (ECDSA)
   - Performance: 30–50x mais lento em geração, 2–3x em verificação
   - Mitigação: assine offline quando possível, cache resultados

3. **FIPS 205 (SLH-DSA)**: assinaturas baseadas em hash, alternativa se lattices forem quebradas
   - Sem dependência em problemas matemáticos (apenas segurança de hash)
   - Mais robusto, mais lento

4. **HQC (Hamming Quasi-Cyclic)**: alternativa para encapsulamento baseada em código
   - Menor latência que lattices
   - Mais recente, menos auditado

**Configuração de TLS 1.3 com PQC**

Cloudflare e Google já testam em produção. Configure seu servidor:

```bash
# Instale liboqs (Open Quantum Safe)
git clone https://github.com/open-quantum-safe/liboqs.git
cd liboqs && mkdir build && cd build
cmake -DCMAKE_BUILD_TYPE=Release ..
make -j$(nproc)
sudo make install

# Compile OpenSSL 3.x com suporte PQC
git clone https://github.com/open-quantum-safe/openssl.git
cd openssl
./config --prefix=/opt/oqs-openssl
make -j$(nproc)
make install

# Configure nginx/apache para usar PQC
# Exemplo nginx (nginx.conf):
server {
  listen 443 ssl;
  ssl_certificate /path/to/ml-kem-cert.pem;
  ssl_certificate_key /path/to/ml-kem-key.pem;

  # Hybrid approach: PQC + classical para compatibilidade
  ssl_protocols TLSv1.3;
  ssl_ciphers "TLS_ML_KEM_768_RSA_PSS_RSAE_SHA256:TLS_ECDHE_RSA_WITH_AES_256_GCM_SHA384";
  ssl_ecdh_curve 'ML-KEM-768:secp384r1';
}
```

Híbrido é crítico: não saia 100% de RSA/ECC agora porque (1) clientes antigos não suportam PQC, (2) se PQC cair no futuro, ainda tem clássico como fallback.

**Fase 2: Migração de PKI (2027–2029)**

Substitua CAs:

```bash
# Gere CA com ML-DSA
oqs-openssl req -new -x509 -newkey mlDSA87 \
  -keyout ca-key.pem -out ca-cert.pem \
  -days 3650 -subj "/CN=Quantum-Safe-CA"

# Assine certificados de servidor com ML-DSA
oqs-openssl req -new -newkey mlDSA87 \
  -keyout server-key.pem -out server.csr \
  -subj "/CN=api.acme.com"

oqs-openssl x509 -req -in server.csr \
  -CA ca-cert.pem -CAkey ca-key.pem \
  -out server-cert.pem -days 365 -CAcreateserial
```

Implemente em camadas:
1. Novos certificados: já com ML-DSA
2. Renovação existentes: migra durante renew (não antes)
3. Assinaturas de código: Sign tools, binários, updates com ML-DSA

**Fase 3: QKD para Dados de Ultra-Longa Duração (Opcional, 2028+)**

QKD usa propriedades da mecânica quântica (no-cloning theorem) para garantir que qualquer espionagem na troca de chaves seja detectável. Não é vulnerável a Shor porque não usa matemática clássica.

Limitações práticas:
- Requer fibra óptica quântica dedicada (não reutiliza fibra normal)
- Distância máxima: 100–300 km sem repetidores (ainda em P&D)
- Custo: ~$1M por link de 10 km
- Taxa de dados: 1–100 kbps (lento comparado a clássico)

Caso de uso real: governos e bancos com dados de vida útil 50+ anos:

```
Arquitetura: [Sede A] --QKD--> [Repetidor B] --QKD--> [Sede C]
             |                  |                     |
             | ML-KEM TLS       | ML-KEM TLS          | ML-KEM TLS
             v                  v                     v
           [Banco]            [Servidor]            [Backup]

Fluxo:
1. QKD distribui chaves simétrias via enlace quântico
2. ML-KEM key exchange é feito localmente em cada ponta
3. Dados confidenciais são criptografados com chaves simétricas (AES-256)
```

Se sua organização tem dados classificados com horizon de 50+ anos e orçamento, avalie partners como Quantum Xchange, ID Quantique. Caso contrário, PQC sozinho é suficiente.

**Monitoramento de Transição**

Mantenha dashboard de conformidade:
```sql
-- Audit certificates
SELECT
  domain,
  algorithm,
  key_size,
  expires_at,
  CASE
    WHEN algorithm IN ('RSA', 'ECDSA') THEN 'vulnerable'
    WHEN algorithm IN ('ML-DSA', 'ML-KEM') THEN 'post-quantum'
  END as status
FROM certificates
ORDER BY expires_at ASC;
```

**Plano de Transição Recomendado**

- **Q1 2026**: Audit completo (inventário de certificados, listar dependências)
- **Q2 2026**: Prepare ambiente: instale liboqs, configure hybrid TLS
- **Q3 2026**: Rodar 10% de tráfego via TLS-PQC em staging
- **Q4 2026**: Migrar novos certificados
- **2027**: Conformidade com mandatos governamentais (jan 2027 NSS, abril 2026 Canadá)
- **2028–2030**: Renovação de certificados existentes conforme vencem

## Stack e requisitos

**Bibliotecas e Tools:**
- liboqs-openssl (última versão, compilar do source)
- Pydantic/cryptography Python (3.10+) para validação
- NIST FIPS 203/204/205 libraries (liboqs inclui)
- OpenSSL 3.x mínimo

**Hardware:**
- Processador: qualquer CPU moderna (overhead de PQC é ~30% vs ECC em verificação)
- RAM: sem aumento significativo (~100MB extra por servidor)
- Armazenamento: certificados PQC são maiores (1.2KB vs 0.4KB para ECC)

**Custo de Implementação:**
- Desenvolvimento: ~60–120 horas (audit + teste + deployment)
- Infraestrutura: $0 (software open-source)
- QKD (se adicionar): $50K–$500K por enlace (infraestrutura física)

**Compliance:**
- EUA: NSS quantum-safe até janeiro 2027
- Canadá: federal até abril 2026, crítico até 2031
- UE: padrões em desenvolvimento (espera NIST)
- Indústria: (bancário, healthcare) começam pilotos 2026

## Armadilhas e limitacoes

**Performance Degrada em Assinaturas PQC**

ML-DSA é 30–50x mais lento em geração (mas only ~2–3x em verificação). Se você assina certificados online (ACME, CAs), pode virar gargalo. Solução: assine offline, cache resultados por 1+ ano.

**Compatibilidade com Clientes Antigos**

Clientes que não entendem ML-DSA falham. Solução: sempre use **hybrid** (PQC + RSA/ECC), negocie algoritmo durante handshake TLS.

**Dependência em NIST Standards é Risco Centralizado**

Se NIST standards caírem (improvável, mas possível após descoberta teórica), você migra para HQC ou outrosstandards. Mantenha flexibilidade na arquitetura.

**QKD Não Substitui PQC**

QKD protege geração de chaves, mas não assinaturas digitais. Precisa dos dois para defesa completa. Além disso, QKD tem latência e custo — use para dados críticos apenas.

**Harvest Now, Decrypt Later é Ameaça Silenciosa**

Seus dados de hoje estão sendo copiados por adversários. Priorize migração de dados sensíveis com long-term value: segredos de estado, IP industrial, dados médicos. Não é urgente para logs de transação ou sessões de usuário (vida curta).

## Conexoes

- [[algoritmos-shor-grover-quebra-rsa-ecdsa]] — por que RSA/ECC são vulneráveis
- [[mecanica-quantica-no-cloning-colapso-medição]] — fundamentos físicos de QKD
- [[lattice-based-cryptography-lwe-sis]] — matemática por trás de ML-KEM/ML-DSA
- [[certificados-pki-x509-cadeia-confianca]] — como integrar PQC em PKI existente
- [[compliance-regulatorio-nist-eua-canada]] — deadlines mandatórios
- [[openssl-tls-handshake]] — onde PQC é negociado em TLS 1.3

## Historico
- 2026-03-28: Nota criada a partir de NIST.gov
- 2026-04-02: Nota reescrita e enriquecida pelo pipeline de curadoria
