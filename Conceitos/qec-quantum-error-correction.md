---
tags: [conceito, computacao-quantica, correcao-de-erros, qec, fault-tolerance]
date: 2026-04-02
tipo: conceito
aliases: [Quantum Error Correction, Correção de Erros Quântica]
---
# QEC (Quantum Error Correction)

## O que é

QEC é técnica para proteger qubits lógicos contra erros de qubits físicos. Qubits físicos erram (decoerência, desalinhamento, crosstalk) com taxa ~0.1-1% por operação. Sem correção, circuito profundo (>100 gates) acumula erro até resultado ser ruído puro. QEC codifica cada qubit lógico em múltiplos qubits físicos com redundância de forma que erros sejam detectáveis e corrigíveis sem destruir superposição. Razão de qubit físico/lógico é O(d²) para surface codes, O(log d) para qLDPC.

## Como funciona

Exemplo simplificado: código de repetição (3 qubits físicos por lógico).

Codificação:
```
Lógico |0⟩_L = |000⟩ (3 cópias idênticas)
Lógico |1⟩_L = |111⟩
```

Medição de síndrome:
```
Paridade A-B: determina se erro ocorreu entre qubits 0 e 1
Paridade B-C: determina se erro ocorreu entre qubits 1 e 2
Padrão de síndrome → tipo de erro
```

Decoder: mapa síndrome → correção aplicada

Limitação: não funciona se taxa de erro acima de threshold. Surface codes requerem p_physical < 10^-3 (1% de erro deve cair para 0.1%). Abaixo de threshold, escalar código (aumentar distance) reduz erro exponencialmente.

Dois paradigmas (2026):

**Surface Code** (Google Willow):
```
Distance d: d² qubits data + (d-1)² syndrome = ~d² qubits total
d=7: 49 data + 48 syndrome = 97 qubits por lógico
Síndromes locais (cada syndrome mede 4 vizinhos)
Topologia 2D regular, fácil fabricar
```

**qLDPC** (IBM):
```
Distance d: ~10-20 qubits total (vs. d² para surface)
Síndromes não-locais mas esparsas
Mais compacto
Decoder mais complexo (MWPM em grafo de síndrome)
```

## Para que serve

QEC é pré-requisito para:
1. **Computação tolerante a falhas**: circuitos arbitrariamente profundos sem degradação exponencial
2. **Algoritmos práticos**: Shor requer ~4M qubits lógicos para RSA-2048, impossible sem QEC
3. **Simulação molecular**: moléculas grandes requerem circuitos profundos (>1000 gates), só viável com QEC

Sem QEC: máximo ~100 gates úteis hoje. Com QEC madura: >1M gates possível (2029+).

Trade-off: QEC requer muitos qubits físicos (1000s-100.000s para 10-100 qubits lógicos úteis). Overhead é imenso até ~2035 quando fabricação madura.

## Exemplo prático

```python
# Simulador simplificado de surface code
class SurfaceCode:
    def __init__(self, distance):
        self.d = distance
        self.physical_qubits = distance * distance
        self.syndrome_qubits = (distance - 1) ** 2

    def threshold_error_rate(self):
        """Threshold é ~0.1% para surface code"""
        return 0.001  # 1 erro per 1000 gates

    def error_per_gate(self, p_phys):
        """Probabilidade de erro lógico após correção"""
        if p_phys > self.threshold_error_rate():
            return p_phys  # Acima de threshold, erro cresce
        else:
            # Abaixo de threshold: erro reduz exponencialmente com d
            return (100 * p_phys) ** ((self.d + 1) / 2)

# Exemplo
code_d5 = SurfaceCode(5)
p_phys = 0.001  # 0.1% erro por gate

p_logical = code_d5.error_per_gate(p_phys)
print(f"Distance {code_d5.d}: {code_d5.physical_qubits} qubits")
print(f"Erro lógico: {p_logical:.2e} (reduzido de {p_phys})")

# Distance 7
code_d7 = SurfaceCode(7)
p_logical_d7 = code_d7.error_per_gate(p_phys)
print(f"Distance {code_d7.d}: {code_d7.physical_qubits} qubits")
print(f"Erro lógico: {p_logical_d7:.2e} (reduzido ainda mais)")
```

Timeline (Google Willow alcançou):
- 2024: Demonstração de supressão abaixo do threshold (Willow, distance 7)
- 2025: Primeiros decoders em tempo real (hardware acoplado)
- 2026: Múltiplos qubits lógicos paralelos
- 2028-2030: Sistemas com 10-100 qubits lógicos úteis

## Aparece em
- [[correcao-erros-quanticos-codigos-superficie-caminho-computacao-tolerante-falhas]] - QEC é tópico central
- [[hardware-quantico-nisq-era-supercondutores-ions-fotonico]] - hardware implementa QEC
- [[vantagem-quantica-google-willow-ibm-corrida-2025-2026]] - QEC é marco central da corrida 2025-2026
- [[algoritmos-quanticos-shor-grover-vqe-qaoa-classes-problemas]] - Shor requer QEC madura

---
*Conceito extraído em 2026-04-02*
