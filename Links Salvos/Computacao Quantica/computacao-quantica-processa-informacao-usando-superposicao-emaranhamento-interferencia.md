---
tags: [computacao-quantica, qubits, superposicao, emaranhamento, interferencia, fisica-quantica, hardware]
source: https://www.linkedin.com/posts/erinaldofonseca_computa%C3%A7%C3%A3o-qu%C3%A2ntica-ugcPost-7442262752494100480-ESEg
date: 2026-03-28
tipo: aplicacao
---
# Explorar Superposição, Emaranhamento e Interferência em Circuitos Quânticos Básicos

## O que é

Computação quântica processa informação de forma fundamentalmente diferente da clássica, baseando-se em três mecanismos: superposição (qubits em múltiplos estados simultaneamente), emaranhamento (correlação não-local entre qubits), e interferência (amplificação de soluções corretas). Dominar esses três conceitos é pré-requisito para entender qualquer algoritmo quântico. Este guia oferece hands-on experiência construindo circuitos que demonstram cada mecanismo isoladamente, depois combinados.

## Como implementar

**Conceito 1: Superposição com Porta Hadamard**

A porta Hadamard é a operação fundamental que cria superposição. Aplicada a um qubit em |0⟩, transforma para (|0⟩ + |1⟩)/√2 — uma combinação igual de 0 e 1. Aplicar Hadamard a N qubits cria superposição de 2^N estados com amplitudes iguais — parallelismo massivo.

Implementação Qiskit:
```python
from qiskit import QuantumCircuit, QuantumRegister, ClassicalRegister
from qiskit_aer import AerSimulator

# 3 qubits, 3 bits clássicos para medição
qc = QuantumCircuit(3, 3)

# Aplicar Hadamard em cada qubit
for i in range(3):
    qc.h(i)

# Medir todos os qubits
qc.measure(range(3), range(3))

# Simular 1000 shots
simulator = AerSimulator()
result = simulator.run(qc, shots=1000).result()
counts = result.get_counts(qc)

# Resultado: distribuição uniforme sobre 000, 001, 010, 011, 100, 101, 110, 111
# Cada estado aparece ~125 vezes (1000/8)
print(counts)
```

Interpretação: 3 Hadamards criam superposição de 8 estados com peso igual. Sem medição, o circuito "experimenta" todas as 8 possibilidades em paralelo. Este é o fundamento do paralelismo quântico.

**Conceito 2: Emaranhamento via CNOT**

O portão CNOT (Controlled-NOT) emaranha dois qubits: se controle é |1⟩, inverte alvo. Quando aplicado a um par em superposição, cria correlação que não pode ser descrita por qubits individuais.

Implementação:
```python
qc = QuantumCircuit(2, 2)

# Superposição no primeiro qubit
qc.h(0)

# CNOT: 0 é controle, 1 é alvo
qc.cx(0, 1)

qc.measure(range(2), range(2))

simulator = AerSimulator()
result = simulator.run(qc, shots=1000).result()
counts = result.get_counts(qc)

# Resultado: APENAS |00⟩ e |11⟩ aparecem (~500 cada)
# NÃO apareça |01⟩ ou |10⟩ — esses estados são impossíveis
print(counts)
```

Interpretação: os dois qubits estão correlacionados. Medir o primeiro como 0 força o segundo a ser 0. Medir como 1 força o segundo a ser 1. Esta é a "magic" do emaranhamento — medir um informa sobre o outro instantaneamente.

**Conceito 3: Interferência via Padrão de Amplitude**

Interferência é o mecanismo que amplifica soluções corretas. Usamos portas para criar amplitudes positivas para respostas certas e negativas (ou canceladas) para erradas.

Implementação de interferência construtiva:
```python
qc = QuantumCircuit(1)

# Criar superposição
qc.h(0)

# "Marcar" um estado com fase relativa
# Phase gate: rotaciona fase sem afetar probabilidade
qc.p(1.57, 0)  # adicionar π/2 de fase

# Segunda Hadamard para interferir
qc.h(0)

qc.measure(0, 0)

simulator = AerSimulator()
result = simulator.run(qc, shots=1000).result()
counts = result.get_counts(qc)

# Resultado: maioria em |0⟩ (interferência construtiva)
print(counts)
```

Concatenar dois Hadamards com uma phase gate no meio cria padrão de interferência. Amplitudes reforçam ou cancelam dependendo da fase relativa.

**Integração: Bell State (máximo emaranhamento + superposição)**

Combinar Hadamard + CNOT cria um estado de Bell — maximamente emaranhado e em superposição simultânea:

```python
qc = QuantumCircuit(2, 2)

# Hadamard no primeiro qubit
qc.h(0)

# CNOT para emaranhar
qc.cx(0, 1)

# Visualizar o estado antes de medir
qc.draw(output='mpl')

qc.measure(range(2), range(2))

simulator = AerSimulator()
result = simulator.run(qc, shots=1000).result()
counts = result.get_counts(qc)

# Resultado: 50% |00⟩, 50% |11⟩
print(counts)
```

Este é o estado de Bell mais básico — superposição de dois estados emaranhados. Qualquer algoritmo quântico real usa técnicas similares para coordenar qubits.

**Exercício Completo: Simulador de Grover 2-qubit**

Implementar versão simplificada de Grover (buscar por um item marcado entre 4):

```python
def grover_2qubit():
    qc = QuantumCircuit(2, 2)

    # Inicializar em superposição
    qc.h(0)
    qc.h(1)

    # Oracle: marcar |11⟩ com phase flip
    # (Controle: ambos qubits 1, então flip fase)
    qc.cz(0, 1)  # fase -1 se ambos 1

    # Amplificação (invert over average)
    qc.h(0)
    qc.h(1)
    qc.z(0)
    qc.z(1)
    qc.cz(0, 1)  # interferência
    qc.h(0)
    qc.h(1)

    qc.measure(range(2), range(2))

    simulator = AerSimulator()
    result = simulator.run(qc, shots=1000).result()
    return result.get_counts(qc)

counts = grover_2qubit()
# Resultado: maioria em |11⟩ (item marcado)
print(counts)
```

## Stack e requisitos

- **Linguagem**: Python 3.8+
- **Libs**: Qiskit 1.0+, Qiskit Aer, Matplotlib (visualização)
- **Hardware**: Simulador local suficiente (até 25 qubits, segundos), ou IBM Quantum Cloud
- **Custo**: Grátis (simulador local + IBM free tier)
- **Tempo**: 2-3 horas hands-on para entender os 3 conceitos + Grover básico

## Armadilhas e limitações

1. **Superposição não é "múltiplas realidades paralelas"**: é uma representação matemática de probabilidades. Só há uma resposta após medição.

2. **Emaranhamento não transmite informação**: medir qubit A não envia sinal para qubit B — A e B já compartilham correlação. Usar para comunicação violaría relatividade.

3. **Interferência requer design preciso**: fases erradas anulam a vantagem. Algoritmos quânticos são delicados — uma porta fora do lugar quebra tudo.

4. **Simulador clássico é limitado**: simuladores Aer conseguem até ~25-30 qubits em segundos, ~40 qubits em minutos/horas. Para mais, precisa hardware real.

5. **Ruído real degrada superposição**: hardware atual com 0,1% de erro por gate faz superposição com >100 gates impraticável sem mitigation.

## Conexões

Estes três mecanismos são os fundamentos de todos os [[algoritmos-quanticos-shor-grover-vqe-qaoa-classes-problemas]]. Superposição e interferência são o coração de [[quantum-machine-learning-circuitos-variaclionais-aplicacoes-hibridas]]. Emaranhamento é explorado em [[correcao-erros-quanticos-codigos-superficie-caminho-computacao-tolerante-falhas]] para redundância. Implementação prática depende da escolha de [[frameworks-programacao-quantica-qiskit-cirq-pennylane-comparacao]] e [[hardware-quantico-nisq-era-supercondutores-ions-fotonico]].

## Histórico
- 2026-03-28: Nota criada a partir de post LinkedIn
- 2026-04-02: Reescrita com código executável e exercícios hands-on
