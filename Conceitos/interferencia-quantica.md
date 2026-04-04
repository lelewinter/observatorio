---
tags: [conceito, computacao-quantica, fisica-quantica, interferencia]
date: 2026-04-02
tipo: conceito
aliases: [Quantum interference]
---
# Interferência Quântica

## O que é

Interferência quântica é o mecanismo onde amplitudes de caminhos diferentes se somam ou cancelam. Se duas trajetórias levam ao mesmo resultado final, suas amplitudes se adicionam (interferência construtiva se fases alinham, amplitude aumenta). Se fases diferem por π, amplitudes cancelam (interferência destrutiva). Formalmente: amplitudes são números complexos, e suas relações de fase determinam interferência.

## Como funciona

Superposição de dois caminhos para mesmo resultado:
```
ψ = α₁ e^(iφ₁) + α₂ e^(iφ₂)
```

Probabilidade: |ψ|² = |α₁|² + |α₂|² + 2|α₁||α₂|cos(φ₂ - φ₁)

Se φ₂ - φ₁ = 0 (fases alinhadas): cos(0) = 1, termo cruzado é +2|α₁||α₂| (construtiva)
Se φ₂ - φ₁ = π (fases opostas): cos(π) = -1, termo cruzado é -2|α₁||α₂| (destrutiva, anula se |α₁| = |α₂|)

**Algoritmos quânticos usam operações unitárias para controlar fases e criar interferência**. Exemplo: Grover amplifica amplitude da solução correta (interferência construtiva) e cancela as erradas (destrutiva).

Dois Hadamards com phase gate no meio:
```
H → superposição uniforme
P(θ) → adiciona fase a um caminho
H → interfere os caminhos
```

Resultado: distribuição não-uniforme, concentrada em estados com fase "correta".

## Para que serve

Interferência é o mecanismo que evita que superposição seja puramente aleatória. Sem interferência, medir resultado de circuito em superposição 2^N retorna resultado aleatório (útil em nada). Com interferência bem desenhada:
- Algoritmo de Shor: amplia amplitude de fatoração correta
- Algoritmo de Grover: amplia amplitude de item marcado
- VQE: amplifica amplitude de estado de mínima energia

Trade-off: interferência é delicada. Uma porta fora do lugar muda fases, destrói padrão. Algoritmos quânticos são "orquestrados" para explorar interferência construtiva em resposta certa.

## Exemplo prático

```python
# Demonstrar interferência destrutiva
from qiskit import QuantumCircuit
from qiskit_aer import AerSimulator
import numpy as np

qc = QuantumCircuit(1)

# Primeira Hadamard: cria superposição (|0⟩ + |1⟩)/√2
qc.h(0)

# Phase gate: adiciona fase π (180°) para |1⟩
# Sem o phase gate, segunda Hadamard retorna ao |0⟩
# Com phase gate, amplitudes interferen destrutivamente em |1⟩
qc.p(np.pi, 0)  # Pauli Z phase, equivalente a adicionar -1 em |1⟩

# Segunda Hadamard: interfere os caminhos
qc.h(0)

qc.measure_all()

# Simular
simulator = AerSimulator()
result = simulator.run(qc, shots=1000).result()
counts = result.get_counts(qc)

# Resultado: quase 100% em |0⟩, quase 0% em |1⟩
# Sem phase gate: 50-50 entre |0⟩ e |1⟩
# Com phase gate: interferência destrutiva cancela |1⟩
print(counts)
# {'0': 982, '1': 18} (maioria em 0 devido interferência)
```

Implementação de Grover (2-qubit):
```python
# Buscar por estado |11⟩
qc = QuantumCircuit(2)

# Inicializar em superposição
qc.h(0)
qc.h(1)

# Oracle: marcar |11⟩ com phase flip (multiplicar amplitude por -1)
qc.cz(0, 1)  # Controlled-Z: fase -1 se ambos qubits são 1

# Amplificação (invert-about-average)
qc.h(0)
qc.h(1)
qc.z(0)
qc.z(1)
qc.cz(0, 1)
qc.h(0)
qc.h(1)

qc.measure_all()

# Resultado: maioria em |11⟩ (item marcado amplificado por interferência)
```

## Aparece em
- [[computacao-quantica-processa-informacao-usando-superposicao-emaranhamento-interferencia]] - interferência como um dos 3 pilares
- [[algoritmos-quanticos-shor-grover-vqe-qaoa-classes-problemas]] - todos usam interferência para amplificar respostas
- [[quantum-machine-learning-circuitos-variaclionais-aplicacoes-hibridas]] - VQC treinam para explorar interferência
- [[frameworks-programacao-quantica-qiskit-cirq-pennylane-comparacao]] - operações de fase são primitivas em todos os SDKs

---
*Conceito extraído em 2026-04-02*
