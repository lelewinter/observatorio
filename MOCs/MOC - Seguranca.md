---
tags: [moc, seguranca, ciberseguranca, criptografia, quantum, pqc, qkd, nist]
date: 2026-04-02
tipo: moc
---
# Segurança

Defesa de infraestrutura de criptografia contra ameaças quânticas, migrações para padrões pós-quânticos (PQC), e distribuição incondicionalmente segura de chaves via QKD. O vault condensa ameaça real (timeline para quebra de RSA/ECC), padrões NIST (ML-KEM, ML-DSA, SLH-DSA), planos de migração pragmáticos, e trade-offs de implementação.

## Ameaça Quântica à Criptografia: Timeline e Realidade

[[criptografia-quantica-qkd-vs-post-quantum-criptografia-padrao-nist|Defesa Dupla: Post-Quantum Cryptography (PQC) + Quantum Key Distribution (QKD)]] — computadores quânticos com ~4 milhões de qubits lógicos quebram RSA-2048 via algoritmo de Shor em tempo polinomial. Timeline realista de ameaça: 2024-2026 demonstrações de QEC (quantum error correction) viável, 2028-2030 primeiros sistemas com 100+ qubits lógicos, 2030-2032 RSA-2048 teoricamente quebrável (requer $1-10 bilhões em hardware + expertise rara, não acesso casual).

Urgência real (2026): "harvest now, decrypt later" — adversários coletam dados criptografados hoje sabendo que serão decriptáveis em 5-10 anos. Dados sensíveis com long-term value (segredos de estado, IP industrial, saúde, negociações diplomáticas) devem migrar NOW. Dados com vida curta (logs de transação <1 ano, sessões de usuário) são low-priority.

Google Willow (2025) demonstrou QEC abaixo do threshold teoricamente (primeiro hardware prova que escalar reduz erro exponencialmente). IBM Kookaburra (2025) escalou para 1.386 qubits em chip único. Ambos ainda 10.000x+ longe de quebrar RSA, mas viabilidade é comprovada.

## Padrões Post-Quantum do NIST

NIST finalizou 3 padrões primários (2024) + HQC (2025):

**FIPS 203 (ML-KEM)**: encapsulamento de chave para key exchange (substitui ECDH, Diffie-Hellman)
- Baseado em Module-LWE (lattice-based cryptography)
- Tamanho chave: 768 bytes (privada) + 1184 bytes (pública) — overhead ~1.5x vs ECDH
- Latência: comparável a ECDH
- Robustez: baseado em problema matemático (Module-LWE) que resiste a ataques quânticos conhecidos

**FIPS 204 (ML-DSA)**: assinaturas digitais (substitui ECDSA, RSA)
- Baseado em Module-LWE/SIS
- Tamanho assinatura: 2420 bytes vs 256 bytes (ECDSA) — overhead 10x
- Performance: 30-50x mais lento em geração, 2-3x em verificação
- Prático quando: signatures offline (não crítico em latência), cache resultados por 1+ ano

**FIPS 205 (SLH-DSA)**: assinaturas hash-based (alternativa ultra-conservadora)
- Sem dependência em problemas matemáticos (apenas segurança de hash)
- Mais confiável se lattices forem quebradas, mais lento
- Use como fallback se ML-DSA tiver descoberta teórica

**HQC (Hamming Quasi-Cyclic)**: alternativa para encapsulamento
- Baseado em teoria de códigos (não lattices)
- Menor latência que lattices, overhead também menor
- Mais recente (menos auditado), mas promissor

## Plano de Migração PQC (Pragmático)

**Q1 2026 — Audit completo**: inventário de todos certificados RSA/ECC (domínios, datas expiração, dependências). Comando: `openssl s_client -connect api.example.com:443 -showcerts 2>/dev/null | grep -A5 "Public-Key:"`. Mapa de sistemas dependentes (qual servidor/serviço usa qual certificado). Classificar por criticidade (dados long-term = alta prioridade).

**Q2 2026 — Setup híbrido**: instala liboqs (Open Quantum Safe) e OpenSSL 3.x compilado com suporte PQC. Configura TLS 1.3 com **hybrid approach** (PQC + RSA/ECC simultaneamente). Exemplo nginx.conf: `ssl_ciphers "TLS_ML_KEM_768_RSA_PSS_RSAE_SHA256:TLS_ECDHE_RSA_WITH_AES_256_GCM_SHA384"`. Híbrido é crítico porque: (1) clientes antigos não entendem ML-KEM, (2) se PQC cai no futuro, RSA é fallback.

**Q3 2026 — Migração de CA**: gera novo CA com ML-DSA (não RSA). Comando: `oqs-openssl req -new -x509 -newkey mlDSA87 -keyout ca-key.pem -out ca-cert.pem`. Emite novos certificados de servidor com ML-DSA. Renova certificados existentes conforme expiram (não força renovação antes).

**Q4 2026 — Assinaturas de código**: sign tools, binários, updates com ML-DSA. Requer infra de deployment modificada (verificadores precisam suportar ML-DSA).

**2027-2030 — Renovação completa**: conforme certificados RSA/ECC expiram naturalmente, substituem por PQC. Sem deadline urgente, rotineiro.

## Quantum Key Distribution (QKD): Quando Considerar

QKD usa propriedades quânticas (no-cloning theorem) para garantir que espionagem é detectável. Não é vulnerável a Shor porque não usa matemática clássica. Mas limitações práticas são severas:

- Requer fibra óptica **quântica dedicada** (não reutiliza fibra normal)
- Distância máxima: 100-300 km sem repetidores (ainda em P&D em 2026)
- Custo: ~$1M por link de 10 km
- Taxa de dados: 1-100 kbps (muito lento, vs. clássico Gbps)

**Caso de uso real**: governos/bancos com dados de vida útil 50+ anos e budget. Arquitetura: [Sede A] --QKD--> [Repetidor B] --QKD--> [Sede C]. QKD distribui chaves simétricas (ultra-seguro), ML-KEM TLS é camada adicional. Aplicação: dados classificados, negociações diplomáticas.

**Conclusão**: QKD é insurance policy para ultra-long-term data, não requer para maioria de cenários. PQC sozinho (ML-KEM + ML-DSA) é suficiente para 99% das cases. Se sua org tem dados 50+ anos e orçamento: avalie partners como Quantum Xchange, ID Quantique.

## Monitoramento de Transição

Dashboard de conformidade (SQL query):
```sql
SELECT domain, algorithm, key_size, expires_at,
  CASE
    WHEN algorithm IN ('RSA', 'ECDSA') THEN 'vulnerable'
    WHEN algorithm IN ('ML-DSA', 'ML-KEM') THEN 'post-quantum'
  END as status
FROM certificates ORDER BY expires_at ASC;
```

Alertas: certificados vencendo em <90 dias, algoritmos antigos acima de 50% do portfolio.

## Conformidade Regulatória

- **EUA**: NSS (National Security Memorandum) exige PQC até janeiro 2027 para agências federais
- **Canadá**: federal até abril 2026, crítico até 2031
- **UE**: padrões em desenvolvimento (segue NIST), sem deadline firme 2026
- **Indústria**: setor bancário, healthcare começam pilotos 2026, mandatos esperados 2027-2028

## Armadilhas e Trade-Offs

**Performance degrada em assinaturas PQC**: ML-DSA é 30-50x mais lento em geração (mas ~2-3x em verificação). Se você assina certificados online frequente, pode virar gargalo. Mitigação: assine offline, cache resultados por 1+ ano.

**Compatibilidade com clientes antigos**: clientes que não entendem ML-KEM/ML-DSA falham. Solução: always use hybrid (PQC + RSA), negocie algoritmo durante handshake TLS 1.3. Browsers e LibreSSL/OpenSSL já suportam hybrid em 2026.

**Dependência centralizada em NIST standards**: se NIST standards caem (teoricamente improvável após peer review massivo), você migra para HQC ou outro standard. Mantenha flexibilidade em PKI.

**QKD não substitui PQC**: QKD protege geração de chaves, mas não assinaturas digitais. Ambos são necessários para defesa completa.

## Stack Prático

**Bibliotecas**: liboqs-openssl (compilar do source), OpenSSL 3.x+, Python cryptography library 3.10+.

**Hardware**: qualquer CPU moderna (overhead PQC é ~30% vs ECC em verificação), RAM negligenciável (100MB extra), armazenamento (certs PQC 1.2KB vs 0.4KB ECC).

**Custo implementação**: 60-120 horas desenvolvimento (audit + teste + deployment), $0 software (open-source), QKD opcional ($50k-500k per link se adicionar).

## Estado Atual e Tendências

2026 é ano crítico de "vontade vs. realidade". NIST standards existem, ferramentas existem (liboqs, OpenSSL 3.x), mas maioria de organizações ainda não migrou. Razões: inércia, "ainda temos tempo" (falso), compatibilidade preocupante (híbrido resolve isso), fear of unknown (lattices ainda são "novas", confiança é baixa).

Expectativa 2026-2027: compliance driven migration (governo exige, então private sector segue). Large banks/tech começam, mid-market espera até 2028-2029. Small startups usam PQC by default (new codebases sem legacy).

## Conexões com Outros Temas

Criptografia pós-quântica é defesa contra ameaça explorada por [[MOC - Computacao Quantica]] (algoritmos de Shor, vantagem quântica). PQC é fundação de [[MOC - Dev e Open Source]] (ferramentas, bibliotecas, arquitetura). Conformidade regulatory conecta [[MOC - Negocios e Startups]] (deadline compliance, custo de transição).
