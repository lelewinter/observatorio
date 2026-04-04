---
tags: [conceito, computacao-quantica, hardware, timeline, erros]
date: 2026-04-02
tipo: conceito
aliases: [Noisy Intermediate-Scale Quantum]
---
# NISQ Era (Noisy Intermediate-Scale Quantum)

## O que é

Era NISQ é período histórico onde computadores quânticos têm 50-1000 qubits físicos, mas taxas de erro altas (0.1-1% por gate) que impedem cálculos longos. Sistemas desta era (Google Sycamore, IBM Heron, IonQ) resolvem problemas pequenos com profundidade ~100-300 gates. Além disso, erro acumula inviabilizando resultado. Era NISQ começou ~2016, espera-se terminar quando QEC madura (2028-2030). Todos os computadores quânticos disponíveis em 2026 estão em era NISQ.

## Como funciona

Dinâmica de erro em NISQ:

```
Circuito com d gates (depth)
Erro por gate: p (típico 0.1-1%)
Erro total acumulado: P_total ≈ 1 - (1-p)^d

Se d=10, p=0.1%: P_total ≈ 1%
Se d=100, p=0.1%: P_total ≈ 9.5%
Se d=1000, p=0.1%: P_total ≈ 63%

Profundidade útil (antes de resultado ser ruído): ~100-300 gates dependendo de p
```

**NISQ algorithms** são projetados para profundidade rasa:
- VQE: profundidade moderada, recuperável com error mitigation
- QAOA: profundidade baixa (p=1-5 níveis)
- Hybrid: quebra problema em múltiplos subcircuitos rasos

**Sem QEC**: não há forma de estender além de ~300 gates de forma confiável.

## Para que serve

Pesquisa NISQ busca demostrar vantagem quântica em problemas reais apesar das limitações:
1. **VQE + error mitigation**: simulação molecular com validação contra DFT clássico
2. **QAOA**: otimização combinatória em escala pequena-média
3. **QML**: classificação/clustering com circuitos variacionais

Timeline:
- **2016-2019**: Era NISQ nasce (IBM 5-20 qubits, Google Sycamore 53 qubits)
- **2019**: Google supremacia quântica (artificial benchmark)
- **2022-2024**: Refinamento de algoritmos NISQ, error mitigation
- **2024-2025**: Demos de vantagem real (Willow), QEC abaixo threshold
- **2025-2028**: Transição para QEC, fim de era NISQ
- **2028-2030+**: Fault-tolerant quantum computing

## Exemplo prático

```python
# Demonstrar limite de profundidade em NISQ
from qiskit import QuantumCircuit
from qiskit_aer import AerSimulator
from qiskit_aer.noise import NoiseModel, depolarizing_error

# Simular com ruído realista (Willow-like)
noise_model = NoiseModel()
error_1q = depolarizing_error(0.001, 1)  # 0.1% per single-qubit gate
error_2q = depolarizing_error(0.005, 2)  # 0.5% per two-qubit gate

noise_model.add_all_qubit_quantum_errors(error_1q, ['h', 'ry', 'rz'])
noise_model.add_all_qubit_quantum_errors(error_2q, ['cx'])

# Testar circuito de profundidade crescente
for depth in [10, 50, 100, 200]:
    qc = QuantumCircuit(2)

    for _ in range(depth):
        qc.h(0)
        qc.cx(0, 1)

    qc.measure_all()

    # Sem ruído (ideal)
    simulator_ideal = AerSimulator()
    result_ideal = simulator_ideal.run(qc, shots=1000).result()
    counts_ideal = result_ideal.get_counts(qc)

    # Com ruído
    simulator_noisy = AerSimulator(noise_model=noise_model)
    result_noisy = simulator_noisy.run(qc, shots=1000).result()
    counts_noisy = result_noisy.get_counts(qc)

    # Fidelidade: sobreposição entre distribuições ideal e com ruído
    fidelity = sum(min(counts_ideal.get(outcome, 0), counts_noisy.get(outcome, 0))
                   for outcome in set(counts_ideal) | set(counts_noisy)) / 1000

    print(f"Depth {depth}: Fidelity {fidelity:.2%}")

# Resultado esperado:
# Depth 10: Fidelity ~98%
# Depth 50: Fidelity ~90%
# Depth 100: Fidelity ~60%
# Depth 200: Fidelity ~10-30%
```

Comparação NISQ vs. Futuro:

| Aspecto | NISQ (2026) | Fault-Tolerant (2030+) |
|---------|------------|------------------------|
| Qubits físicos | 100-1000 | 100.000-1.000.000 |
| Taxa erro/gate | 0.1-1% | <0.00001% |
| Profundidade útil | 100-300 | 1.000.000+ |
| Algoritmos | VQE, QAOA, QML | Shor, Grover, simulação real |
| QEC | Não integrada | Integrada |
| Overhead térmico | Gerenciável | Significativo (MW) |
| Custo | $1-100M | $1-10B |

## Aparece em
- [[hardware-quantico-nisq-era-supercondutores-ions-fotonico]] - definição de NISQ e características de hardware
- [[algoritmos-quanticos-shor-grover-vqe-qaoa-classes-problemas]] - VQE/QAOA são algoritmos NISQ-friendly
- [[quantum-machine-learning-circuitos-variaclionais-aplicacoes-hibridas]] - QML é pesquisa primária em era NISQ
- [[correcao-erros-quanticos-codigos-superficie-caminho-computacao-tolerante-falhas]] - QEC marca fim de era NISQ
- [[vantagem-quantica-google-willow-ibm-corrida-2025-2026]] - marcos de vantagem acontecem na era NISQ

---
*Conceito extraído em 2026-04-02*
