---
tags: [conceito, criptografia, segurança, ameaça-quântica, ataque, estratégia]
date: 2026-04-02
tipo: conceito
aliases: [HNDL, Coleta e Decriptação Futura, Colheita Agora]
---
# Harvest Now, Decrypt Later (HNDL)

## O que e

Estratégia de ataque onde adversário coleta dados criptografados (tráfego HTTPS, comunicações, documentos) hoje, sabendo que será capaz de decriptá-los quando possuir computador quântico (5–15 anos no futuro).

Não é ataque teórico: agências de inteligência já implementam. NSA está arquivando tráfego TLS em larga escala.

## Como funciona

**Fase 1: Coleta (hoje, 2026)**

```
Adversário monitora tráfego:
  [Cliente] --HTTPS (RSA)--> [Servidor]
           <-- dados confidenciais ---

Captura:
  1. Certificado do servidor (chave pública RSA-2048)
  2. Dados criptografados com AES-256 (usando chave derivada de key exchange RSA)
  3. Salva tudo: armazena em disco, criptografa com chave local

Custo: zero (só monitoramento de rede passivo)
Risco: nenhum (simétrico: não deixa rastro)
```

**Fase 2: Decriptação (2032–2035, quando computador quântico existe)**

```
Adversário tem 2000+ qubits lógicos:

1. Executa Shor contra RSA-2048 do certificado → fatora em horas
   - Obtém chave privada do servidor
2. Usa chave privada para derivar chave de sessão AES original
3. Decripta dados salvos há anos: mensagens, transações, segredos
```

**Matemática Concreta**

```
Cenário: Banco (2026) ✓ encriptado com AES-256(derived from RSA-2048 via ECDH)
         Adversário copiou tráfego TLS

Timeline:
  2026: Coleta (custo: $0)
  2030: IBM/Google tem 2000 qubits lógicos (estimado)
  2031: Adversário dedica 1 servidor com 2000 qubits por 8h
  2032: Executa Shor contra RSA-2048 → fatora (tempo: 8h, custo: $10K eletricidade)
  2033: Decripta dados de 2026 → tem transações bancárias de 7 anos atrás
```

## Pra que serve (entendimento e mitigação)

**Urgência de PQC**: Não esperar qubit lógicos existirem. Migrar para Post-Quantum Cryptography agora garante que dados coletados hoje não são decriptáveis futuramente. É "forward secrecy" contra quântico.

**Priorizar Dados de Longa Vida**: Nem todos os dados precisam ser protegidos contra HNDL:
- ✗ Logs de acesso (relevância: dias/semanas)
- ✗ Sessões de usuário (relevância: horas)
- ✗ Notificações (relevância: minutos)
- ✓ Segredos de estado (relevância: 50+ anos)
- ✓ Identidades criptografadas (relevância: 20+ anos)
- ✓ IP industrial (relevância: 10+ anos)
- ✓ Dados médicos (relevância: lifetime do paciente)

**Estratégia de Defesa em Camadas**:
1. **Criptografia com PQC agora**: Novos dados com ML-KEM/ML-DSA imunes a Shor
2. **Re-encriptação de dados históricos**: Dados sensíveis antigos (2020–2025) com PQC
3. **QKD para críticos**: Links financeiros/governamentais usam QKD (segurança de física, não matemática)
4. **Monitoramento de ameaça quântica**: Rastrear progresso em qubits lógicos, ajustar cronograma

## Exemplo pratico

**Auditoria: Dados em Risco via HNDL**

```python
import subprocess
from datetime import datetime, timedelta

class DataHarvestRiskAssessment:
    def __init__(self):
        self.crypto_weak = []  # RSA/ECC data
        self.crypto_strong = []  # PQC data

    def scan_certificates(self, domains):
        """Scan quais domínios usam RSA vs PQC"""
        for domain in domains:
            cmd = f"openssl s_client -connect {domain}:443 -showcerts 2>/dev/null | grep 'Public-Key:'"
            result = subprocess.run(cmd, shell=True, capture_output=True, text=True)

            if "4096" in result.stdout or "2048" in result.stdout:
                self.crypto_weak.append(domain)
            elif "mlkem" in result.stdout.lower():
                self.crypto_strong.append(domain)

    def estimate_harvest_risk(self, data_age_years, sensitivity="high"):
        """
        Estimar risco de HNDL para dados específicos

        Sensibilidade:
          "low": logs, sessões (não vale a pena colher)
          "medium": dados de uso (vale se qubit 3-5 anos)
          "high": segredos, IPs (vale sempre)
        """
        qubit_timeline = 2031  # Estimado para 2000 qubits lógicos
        data_collection_year = datetime.now().year - data_age_years

        if sensitivity == "high":
            # Sempre vale colher
            return {
                "risk": "CRÍTICO",
                "reason": "Dados sensíveis com ciclo de vida longo",
                "action": "Migrar para PQC IMEDIATAMENTE"
            }

        if qubit_timeline - data_collection_year > 10:
            # Mais de 10 anos antes de poder decriptar
            return {
                "risk": "BAIXO",
                "reason": "Tempo suficiente para ciclo de vida de dado expirar",
                "action": "Migrar quando renovar certs (plano normal)"
            }
        else:
            # Menos de 10 anos: dado ainda é sensível quando qubit chega
            return {
                "risk": "ALTO",
                "reason": f"Dado coletado em {data_collection_year}, qubit chega {qubit_timeline}, diferença: {qubit_timeline - data_collection_year} anos",
                "action": "Re-encriptar com PQC agora"
            }

    def generate_report(self):
        """Gerar plano de migração"""
        print("=== HARVEST NOW DECRYPT LATER RISK ASSESSMENT ===\n")

        print(f"Domínios com RSA/ECC (vulneráveis): {len(self.crypto_weak)}")
        for domain in self.crypto_weak[:5]:
            print(f"  - {domain}")
            risk = self.estimate_harvest_risk(data_age_years=3, sensitivity="high")
            print(f"    {risk}")

        print(f"\nDomínios com PQC (protegidos): {len(self.crypto_strong)}")

        print("\n=== PLANO DE AÇÃO ===")
        print("1. Re-encriptar dados históricos sensíveis (2020–2025) com PQC")
        print("2. Migrar novos certificados para ML-DSA/ML-KEM")
        print("3. Configurar TLS 1.3 hybrid (PQC + RSA para compatibilidade)")
        print("4. Monitorar qubit progress, ajustar cronograma conforme progresso")

# Uso
assessment = DataHarvestRiskAssessment()
assessment.scan_certificates([
    "api.banco.com",
    "seguro.telesaude.com",
    "secret.gov.br"
])
assessment.generate_report()
```

**Output esperado**:
```
=== HARVEST NOW DECRYPT LATER RISK ASSESSMENT ===

Domínios com RSA/ECC (vulneráveis): 3
  - api.banco.com
    {'risk': 'CRÍTICO', 'reason': 'Dados sensíveis com ciclo de vida longo', 'action': 'Migrar para PQC IMEDIATAMENTE'}
  - seguro.telesaude.com
    {'risk': 'CRÍTICO', ...}

=== PLANO DE AÇÃO ===
1. Re-encriptar dados históricos sensíveis (2020–2025) com PQC
2. Migrar novos certificados para ML-DSA/ML-KEM
3. ...
```

## Aparece em
- [[post-quantum-cryptography-pqc]] — solução criptográfica
- [[quantum-key-distribution-qkd]] — solução de física
- [[algoritmos-shor-grover]] — por que Shor torna isso possível
- [[migrar-criptografia-para-resistencia-quantica]] — plano de ação

---
*Conceito extraído em 2026-04-02*
