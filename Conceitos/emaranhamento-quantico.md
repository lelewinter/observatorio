---
tags: [conceito, computacao-quantica, fisica-quantica, entanglement]
date: 2026-04-02
tipo: conceito
aliases: [Entanglement, Correlação não-local]
---
# Emaranhamento Quântico

## O que é

Emaranhamento é correlação não-separável entre dois ou mais qubits de forma que medir um instantaneamente define o estado do outro. Formalmente, um estado é emaranhado se não pode ser fatorado como produto tensor de estados individuais. Exemplo clássico: Bell state (|00⟩ + |11⟩)/√2 — medir qubit A determina qubit B mesmo a distâncias arbitrárias, violando localidade local (mas sem transmitir informação).

## Como funciona

Emaranhamento é criado por portas que acoplam qubits (Ex: CNOT, CZ). CNOT opera assim:
```
Controle |0⟩, Alvo |0⟩ → |0⟩, |0⟩ (sem mudança)
Controle |0⟩, Alvo |1⟩ → |0⟩, |1⟩ (sem mudança)
Controle |1⟩, Alvo |0⟩ → |1⟩, |1⟩ (inverte alvo)
Controle |1⟩, Alvo |1⟩ → |1⟩, |0⟩ (inverte alvo)
```

Quando aplicado a superposição:
```
CNOT[(|0⟩ + |1⟩)/√2 ⊗ |0⟩] = CNOT[(|0⟩⊗|0⟩ + |1⟩⊗|0⟩)/√2]
                               = (|0⟩⊗|0⟩ + |1⟩⊗|1⟩)/√2
```

Resultado: Bell state maximalmente emaranhado. Os qubits não têm estado individual bem-definido — seu estado só faz sentido como par.

**Propriedade crítica**: medir qubit A como 0 força qubit B a ser 0 (com correlação perfeita). Medir como 1 força B a ser 1. Não há comunicação clássica — é correlação preexistente no estado quântico.

## Para que serve

Emaranhamento é recurso para algoritmos quânticos:
1. **Algoritmo de Grover**: usa emaranhamento para distribuir amplitude entre candidatos
2. **VQE/QAOA**: ansatz profundo enmaranham qubits para representar estados complexos
3. **QEC**: códigos de superfície/qLDPC usam emaranhamento para redundância
4. **Redes quânticas**: emaranhamento entre nós de comunicação quantica

Trade-off: emaranhamento degrada com ruído (decoerência). Taxa de erro por gate em hardware real reduz correlação exponencialmente com profundidade.

## Exemplo prático

```python
# Criar Bell state em Qiskit
from qiskit import QuantumCircuit
from qiskit_aer import AerSimulator

qc = QuantumCircuit(2)

# Hadamard no primeiro qubit
qc.h(0)

# CNOT para emaranhar
qc.cx(0, 1)

qc.measure_all()

# Simular
simulator = AerSimulator()
result = simulator.run(qc, shots=1000).result()
counts = result.get_counts(qc)

# Resultado: APENAS |00⟩ e |11⟩
# |01⟩ e |10⟩ nunca aparecem
print(counts)
# {'00': 497, '11': 503} (não há 01 ou 10)

# Interpretação: medições em A e B são 100% correlacionadas
# Se A = 0, B = 0. Se A = 1, B = 1.
```

Prova experimental que não é predeterminado (não é "hidden variable"):
```python
# Medir qubits em bases diferentes
qc = QuantumCircuit(2, 2)
qc.h(0)
qc.cx(0, 1)

# Preparar para medir A em base X (aplicar H antes de medir)
qc.h(0)
qc.measure(0, 0)
qc.measure(1, 1)

# Resultado: medições ainda correlacionadas, provando emaranhamento é real
# (não apenas coincidência de medições predeterminadas)
```

## Aparece em
- [[computacao-quantica-processa-informacao-usando-superposicao-emaranhamento-interferencia]] - emaranhamento como um dos 3 pilares
- [[correcao-erros-quanticos-codigos-superficie-caminho-computacao-tolerante-falhas]] - surface codes usam emaranhamento para redundância
- [[algoritmos-quanticos-shor-grover-vqe-qaoa-classes-problemas]] - Grover e VQE exploram emaranhamento
- [[quantum-machine-learning-circuitos-variaclionais-aplicacoes-hibridas]] - ansatz profundos enmaranham qubits para expressividade

---
*Conceito extraído em 2026-04-02*
