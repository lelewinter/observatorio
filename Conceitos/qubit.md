---
tags: [conceito, computacao-quantica, hardware, fisica-quantica]
date: 2026-04-02
tipo: conceito
aliases: [Quantum bit, q-bit]
---
# Qubit

## O que é

Qubit (quantum bit) é a unidade fundamental de informação quântica. Diferentemente de um bit clássico que é 0 ou 1, um qubit pode existir em superposição de ambos os estados simultaneamente: α|0⟩ + β|1⟩, onde |α|² + |β|² = 1. Ao medir, o qubit colapsa para 0 ou 1 com probabilidades |α|² e |β|² respectivamente. Um qubit é a entidade que qualquer hardware quântico manipula.

## Como funciona

Fisicamente, qubits podem ser implementados de várias formas:
- **Supercondutores**: circuito de Josephson com dois níveis de energia (ground e excited)
- **Íons aprisionados**: níveis hiperfinos de um átomo suspenso
- **Fotônica**: polarização ou número de fótons em modo óptico
- **Átomos neutros**: níveis ópticos de um átomo em armadilha

Matematicamente, o estado é representado como vetor no espaço de Hilbert 2D:
```
|ψ⟩ = α|0⟩ + β|1⟩
```

Operações (portas quânticas) são matrizes unitárias 2×2:
- **Hadamard (H)**: cria superposição igual: H|0⟩ = (|0⟩ + |1⟩)/√2
- **Pauli X/Y/Z**: rotações de 180° em diferentes eixos
- **RX/RY/RZ**: rotações parametrizadas de ângulo arbitrário

Múltiplos qubits: N qubits formam espaço de Hilbert 2^N dimensional. Dois qubits independentes: |ψ₁⟩⊗|ψ₂⟩. Emaranhados: não podem ser fatorados (Ex: Bell state: (|00⟩ + |11⟩)/√2).

## Para que serve

Qubits exploram superposição para paralelismo massivo: N qubits representam 2^N estados simultaneamente. Isso permite que algoritmos quânticos como Shor, Grover, e VQE processem vastamente mais informação por operação do que clássicos com bits.

Trade-off: medir um qubit destrói superposição, fornecendo apenas um resultado. Então interferência (amplificar soluções certas, cancelar erradas) é crítica em design de algoritmos quânticos.

Quando usar: sempre que objetivo é computação quântica. A capacidade de fazer superposição + interferência é vantagem que diferencia quântico de clássico.

Quando não: bits clássicos são preferíveis se interfere com simplicidade (Ex: circuitos digitais não-quânticos).

## Exemplo prático

```python
# Criar qubit em superposição com Qiskit
from qiskit import QuantumCircuit

qc = QuantumCircuit(1)
qc.h(0)  # Hadamard: |0⟩ → (|0⟩ + |1⟩)/√2

qc.measure(0, 0)
# Medição: 50% chance de medir 0, 50% de medir 1

# Em hardware: qubit é entidade física (circuito Josephson, íon, fóton)
# que evolui de acordo com Hamiltoniano, depois é medido
```

## Aparece em
- [[algoritmos-quanticos-shor-grover-vqe-qaoa-classes-problemas]] - qubits são entidade que algoritmos manipulam
- [[computacao-quantica-processa-informacao-usando-superposicao-emaranhamento-interferencia]] - qubit é portador de superposição e emaranhamento
- [[hardware-quantico-nisq-era-supercondutores-ions-fotonico]] - diferentes implementações físicas de qubits
- [[frameworks-programacao-quantica-qiskit-cirq-pennylane-comparacao]] - qubits são abstração fundamental em qualquer SDK

---
*Conceito extraído em 2026-04-02*
