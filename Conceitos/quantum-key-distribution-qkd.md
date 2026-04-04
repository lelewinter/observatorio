---
tags: [conceito, computação-quantica, criptografia, física-quântica, segurança, qkd]
date: 2026-04-02
tipo: conceito
aliases: [QKD, Quantum Key Distribution, Distribuição Quântica de Chaves]
---
# Quantum Key Distribution (QKD)

## O que e

Protocolo criptográfico que usa propriedades da mecânica quântica (no-cloning theorem, colapso por medição) para distribuir chaves simétricas entre duas partes de forma fisicamente incondicionalmente segura: qualquer tentativa de espionagem é detectável.

Diferencia-se de criptografia clássica (RSA, ECDH) porque não repousa em dificuldade matemática — repousa em física. Imune a computadores quânticos porque não usa matemática.

Limitação: requer infraestrutura física (fibra óptica quântica ou links de satélite), distância limitada (~300 km), taxa de dados lenta (~1–100 kbps).

## Como funciona

**Protocolo BB84 (exemplo clássico)**

1. Alice quer enviar chave pra Bob via canal público
2. Alice gera sequência de bits aleatórios + base de medição aleatória para cada bit
   ```
   Bit:    1 0 1 0 1 1 0 1 0 1 ...
   Base:   + × + × × + × + + × ...  (+ = horizontal, × = diagonal)
   ```
3. Alice envia photons polarizados conforme (bit, base)
4. Bob gera bases aleatórias, mede cada photon
   ```
   Bob escolhe: × + × × + + × + + + ...
   ```
5. Após transmissão, Alice e Bob comparam publicamente quais bases matcham
   ```
   Casou:    S S   S     S   (S = sift)
   Bit:      1     0   1
   ```
6. Bits onde bases casam = chave segura

**Detecção de Espionagem (Eve)**

Se Eve tenta medir photons:
- Ela não sabe a base, escolhe aleatória
- Se erra a base, muda o estado do photon (colapso quântico)
- Bob detecta: taxa de erro (QBER) sobe de ~0% (sem Eve) pra ~25% (com Eve)

```
Sem Eve:           QBER ~ 0%     → Seguro
Com Eve:           QBER ~ 25%    → Detecta espionagem
```

**Protocolo Moderno: QKD com Decoy States**

BB84 puro é lento. Versões práticas (como implementada em Micius):

1. Sender envia photons em diferentes intensidades (real + decoys)
2. Receiver detecta, distingue sinais reais de decoys
3. Reduz vulnerabilidade a ataques de side-channel
4. Taxa: 1–100 kbps conforme distância

## Pra que serve

**Dados com Ciclo de Vida Muito Longo**: Governo, militares, bancos. Dados que precisam ser confidenciais por 50+ anos. QKD garante que mesmo se adversário tem recurso quântico em 2050, não decripta chaves distribuídas em 2026 via QKD.

**Links Críticos**: Comunicação entre sedes de banco, entre agências governamentais. Um enlace QKD (10 km) custa ~$1M mas é investimento em segurança de longo prazo.

**Quando NÃO usar**:
- Dados com ciclo curto (logs, sessões): PQC é suficiente
- Infraestrutura distribuída (Cloud, múltiplas regiões): QKD requer fibra dedicada, impraticável
- Performance crítica: 1 kbps é muito lento pra tráfego normal
- Orçamento limitado: $1M+ por link é caro

**Complementa PQC**: QKD distribui chaves simétricas seguramente. PQC protege key exchange e assinaturas. Defesa em profundidade.

## Exemplo pratico

Setup de QKD para infraestrutura de banco (simulado):

```
[Banco HQ]  --fibra QKD (10 km)--  [Banco Filial]
    |                                   |
    |-- Hardware QKD (Toshiba/ID Qnt)  |-- Hardware QKD
    |
    v
  [Key Server com chaves simétricas]
    |
    | (AES-256 com chaves QKD)
    v
  [PostgreSQL Criptografado]

Fluxo:
1. QKD distribui chave simétrica K_1 entre HQ e Filial a cada 1 hora
2. Dados financeiros criptografados com AES-256-K_1
3. Se espionagem detectada em QKD, ambas sides descartam K_1
4. Dados com K_1 são considerados comprometidos, descartam backups antigos
```

**Monitoramento**:

```python
import qkd_library  # Hypothetical QKD SDK

class QKDManager:
    def __init__(self, qkd_device):
        self.device = qkd_device

    def check_link_health(self):
        """Monitor QBER, taxa de erro"""
        qber = self.device.get_qber()
        key_rate = self.device.get_key_rate()

        if qber > 0.11:  # Threshold para detecção de espionagem
            raise SecurityAlert(f"Possível espionagem, QBER={qber}")

        if key_rate < 100:  # bps
            log.warning(f"QKD slow: {key_rate} bps")

        return {"qber": qber, "key_rate": key_rate}

    def distribute_symmetric_key(self, recipients):
        """Use QKD-generated key para AES"""
        raw_key = self.device.get_siftedkey()  # QKD output

        # Distill chave: privacy amplification
        final_key = self.privacy_amplify(raw_key)

        # Use com AES
        cipher = AES.new(final_key, AES.MODE_GCM)
        return cipher

# Monitoramento contínuo
qkd = QKDManager(device)
while True:
    health = qkd.check_link_health()
    print(f"QKD Health: {health}")
    time.sleep(300)  # Check every 5min
```

## Aparece em
- [[migrar-criptografia-para-resistencia-quantica]] — combinação PQC + QKD
- [[mecanica-quantica-no-cloning-colapso-medição]] — fundamentos físicos
- [[harvest-now-decrypt-later]] — problema que QKD mitiga

---
*Conceito extraído em 2026-04-02*
