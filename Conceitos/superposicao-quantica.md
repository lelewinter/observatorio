---
tags: [conceito, computacao-quantica, fisica-quantica, superposicao]
date: 2026-04-02
tipo: conceito
aliases: [Quantum superposition]
---
# Superposição Quântica

## O que é

Superposição é a capacidade de um sistema quântico existir em múltiplos estados simultaneamente até ser medido. Formalmente, um qubit em superposição é: |ψ⟩ = α|0⟩ + β|1⟩, onde α e β são amplitudes complexas com |α|² + |β|² = 1. Com N qubits em superposição, o sistema representa 2^N estados com amplitudes definidas — paralelismo exponencial.

## Como funciona

Superposição emerge da linearidade da equação de Schrödinger. Se |0⟩ e |1⟩ são soluções, qualquer combinação linear é solução válida.

A porta Hadamard cria superposição uniforme:
```
H|0⟩ = (|0⟩ + |1⟩)/√2
H|1⟩ = (|0⟩ - |1⟩)/√2
```

Com N qubits todos em superposição via Hadamard:
```
⊗ᴺ H|0⟩ = 1/√(2^N) × (|00...0⟩ + |00...1⟩ + ... + |11...1⟩)
```

O sistema "explora" todos 2^N estados simultaneamente em paralelo quântico. Nenhuma realidade alternativa — é representação matemática de probabilidades correlacionadas.

Evolução temporal: superposição é preservada sob operações unitárias até medição. Interferência (adicionar ou cancelar amplitudes) permite explorar essa propriedade.

## Para que serve

Superposição é a base de aceleração quântica. Algoritmo de Grover usa superposição para testar 2^N candidatos em O(√2^N) = O(2^(N/2)) passos. Algoritmo de Shor usa superposição para explorar ordem de grupos exponencialmente grandes em tempo polinomial.

Sem superposição: circuito quântico é equivalente a circuito clássico (determinístico ou probabilístico). Com superposição + interferência: vantagem quântica.

Trade-off: medição reduz superposição a um único estado. Algoritmos quânticos são projetados para interferência construtiva no estado correto.

## Exemplo prático

```python
# Criar superposição em Qiskit
from qiskit import QuantumCircuit
from qiskit_aer import AerSimulator
import numpy as np

qc = QuantumCircuit(3)

# Hadamard em todos os 3 qubits
for i in range(3):
    qc.h(i)

qc.measure_all()

# Simular
simulator = AerSimulator()
result = simulator.run(qc, shots=1000).result()
counts = result.get_counts(qc)

# Resultado: distribuição uniforme sobre 8 estados (000, 001, ..., 111)
# Cada aparece ~125 vezes (1000/8)
# Antes de medição: superposição de 8 estados com amplitudes iguais
# Após medição: colapsa para um dos 8

print(counts)
# {'000': 125, '001': 127, '010': 118, '011': 130, '100': 122, '101': 129, '110': 124, '111': 125}
```

## Aparece em
- [[computacao-quantica-processa-informacao-usando-superposicao-emaranhamento-interferencia]] - superposição como um dos 3 pilares
- [[algoritmos-quanticos-shor-grover-vqe-qaoa-classes-problemas]] - Shor e Grover exploram superposição
- [[quantum-machine-learning-circuitos-variaclionais-aplicacoes-hibridas]] - feature maps criam superposição para codificar dados
- [[hardware-quantico-nisq-era-supercondutores-ions-fotonico]] - todos os hardwares implementam superposição

---
*Conceito extraído em 2026-04-02*
