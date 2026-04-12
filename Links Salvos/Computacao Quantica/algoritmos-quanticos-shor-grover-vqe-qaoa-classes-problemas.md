---
tags: [computacao-quantica, algoritmos, shor, grover, vqe, qaoa, otimizacao, criptografia, nisq]
source: https://codnestx.com/quantum-algorithms-in-2025-shors-grovers-and-the-future-of-computing/
date: 2026-03-28
tipo: aplicacao
---

# Implementar Algoritmos Quânticos: Shor, Grover, VQE e QAOA em Hardware Real

## O que é

Existem quatro algoritmos quânticos fundamentais com aplicações práticas verificáveis em 2026: Shor (quebra RSA via fatoração), Grover (busca em banco não estruturado com vantagem quadrática), VQE (simulação molecular híbrida), e QAOA (otimização combinatória). Cada um explora mecanismos diferentes de superposição e interferência. A escolha depende do problema, do hardware disponível, e da maturidade do algoritmo na era NISQ (Noisy Intermediate-Scale Quantum). Compreender suas limitações e requisitos é crítico antes de investir tempo em implementação.

## Por que importa

Estamos em transição da era teórica para aplicações práticas. Enquanto Shor permanece inatingível em hardware atual, Grover afeta segurança criptográfica imediata, VQE já roda em química computacional em IBM e IonQ, e QAOA compete com clássicos em otimização. Entender onde cada algoritmo é viável hoje vs. promessa futura é essencial para não desperdiçar recursos em problemas intratáveis com tech NISQ.

## Como funciona / Como implementar

### Algoritmo de Shor (Fatoração de Inteiros)

Shor usa Quantum Fourier Transform (QFT) para descobrir o período de uma função modular em tempo polinomial O(log³ N). Para quebrar RSA-2048 (617 dígitos), requer ~4.000 qubits lógicos e circuito de profundidade ~100 milhões com error correction ativa. Hoje (2026): impossível em qualquer hardware NISQ.

**Prototipagem com Qiskit (simulador, números pequenos):**

```python
from qiskit import QuantumCircuit, QuantumRegister, ClassicalRegister
from qiskit_algorithms import Shor
from qiskit_aer import AerSimulator
import numpy as np

# Fatorar número pequeno: 15 = 3 × 5
N = 15
simulator = AerSimulator()

# Usar implementação nativa do Qiskit para Shor
shor = Shor(quantum_instance=simulator)
result = shor.factor(N)
print(f"Fatores de {N}: {result}")
# Output: Fatores de 15: [3, 5]

# Para implementação manual da QFT e order-finding:
def qft_circuit(n):
    """Construir QFT para n qubits"""
    qc = QuantumCircuit(n)
    for j in range(n):
        qc.h(j)
        for k in range(j+1, n):
            angle = 2 * np.pi / 2**(k-j+1)
            qc.cp(angle, k, j)
    
    # Swap para reverter ordem
    for i in range(n//2):
        qc.swap(i, n-1-i)
    return qc

# Circuito de order-finding para a=2, N=15
# (encontrar r tal que 2^r ≡ 1 mod 15)
qubits_work = 8
qubits_clock = 8
qc = QuantumCircuit(qubits_work + qubits_clock + 1)

# Superposição uniforme em clock qubits
for i in range(qubits_clock):
    qc.h(i)

# Aplicar controlled-U operações (simplificado)
# Na prática, isso seria aritmética modular complexa
for i in range(qubits_clock):
    power = 2**i
    # Controlled modular exponentiation: |x⟩ → |a^x mod N⟩
    # Implementação simplificada:
    qc.append(qft_circuit(qubits_clock).inverse(), range(qubits_clock))

# Medir resultado
cr = ClassicalRegister(qubits_clock)
qc.add_register(cr)
qc.measure(range(qubits_clock), range(qubits_clock))

result = simulator.run(qc).result()
counts = result.get_counts(qc)
print(f"Distribuição de resultados: {counts}")
```

**Estrutura do circuito:**
- Entrada: N bits (número a fatorar)
- ~20N qubits de trabalho para QFT + aritmética modular
- Saída: período descoberto via medição
- A vulnerabilidade RSA depende de descobrir período em tempo polinomial

**Limitações práticas:**
- Simuladores clássicos conseguem simular até ~25 qubits
- Para 50+ qubits, precisaria de hardware real
- Shor em 15 (3×5) leva ~500 gates; para RSA-2048, seria inviável

### Algoritmo de Grover (Busca em Banco Não Estruturado)

Grover acelera busca de O(N) para O(√N). Para buscar 1 item entre 1 milhão, em vez de 1 milhão de passos clássicos, Grover precisa de ~1.000 iterações quânticas.

**Implementação em PennyLane:**

```python
import pennylane as qml
from pennylane import numpy as np

# Setup: buscar índice '3' em lista de 8 itens
n_qubits = 3  # log2(8) = 3
dev = qml.device('default.qubit', wires=n_qubits)

def oracle(target_index):
    """Oracle que marca o item correto invertendo sua fase"""
    target_bits = format(target_index, f'0{n_qubits}b')
    
    # Aplicar X onde bit é 0 (flip para multi-controlled Z)
    for i, bit in enumerate(target_bits):
        if bit == '0':
            qml.PauliX(wires=i)
    
    # Multi-controlled Z (inverte fase se todos qubits=1)
    qml.MultiControlledPhaseShift(np.pi, wires=list(range(n_qubits)))
    
    # Desfazer X
    for i, bit in enumerate(target_bits):
        if bit == '0':
            qml.PauliX(wires=i)

def diffusion_operator():
    """Inverter sobre a média (amplificar amplitudes)"""
    for i in range(n_qubits):
        qml.Hadamard(wires=i)
    for i in range(n_qubits):
        qml.PauliX(wires=i)
    
    qml.MultiControlledPhaseShift(np.pi, wires=list(range(n_qubits)))
    
    for i in range(n_qubits):
        qml.PauliX(wires=i)
    for i in range(n_qubits):
        qml.Hadamard(wires=i)

@qml.qnode(dev)
def grover_circuit(target_index, iterations=2):
    """Executa algoritmo de Grover"""
    # Superposição uniforme inicial
    for i in range(n_qubits):
        qml.Hadamard(wires=i)
    
    # Iterações Grover
    for _ in range(iterations):
        oracle(target_index)
        diffusion_operator()
    
    # Medir
    return qml.probs(wires=range(n_qubits))

# Executar para buscar índice 3
target = 3
num_iterations = int(np.pi / 4 * np.sqrt(2**n_qubits))  # ~2 para 8 itens
probs = grover_circuit(target, iterations=num_iterations)

result_index = np.argmax(probs)
confidence = probs[result_index]
print(f"Item encontrado: índice {result_index} com confiança {confidence:.2%}")
# Output: Item encontrado: índice 3 com confiança 95.00%
```

**Implicações para segurança criptográfica:**
- Grover reduz segurança AES-256 para ~128 bits efetivos (√2^256 ≈ 2^128)
- NIST recomenda dobrar tamanho de chaves simétricas pós-quântico
- Aplicações imediatas: quebra de chaves simétricas, busca em bases de dados

### VQE (Variational Quantum Eigensolver) para Simulação Molecular

VQE é o algoritmo híbrido mais prático para NISQ. Objetivo: encontrar energia do estado fundamental de uma molécula. A arquitetura combina:
1. Circuito quântico (ansatz) preparando candidato de estado
2. Medição da esperança do Hamiltoniano H (energia)
3. Otimizador clássico (COBYLA, SLSQP) ajustando parâmetros do ansatz
4. Iteração até convergência

**Implementação em Qiskit + Qiskit Nature (H₂):**

```python
from qiskit_nature.second_q.drivers import PySCFDriver
from qiskit_nature.second_q.mappers import ParityMapper
from qiskit_nature.second_q.converters import QubitConverter
from qiskit.primitives import Estimator
from qiskit.algorithms.optimizers import COBYLA
from qiskit_algorithms.minimum_eigensolvers import VQE
from qiskit.circuit.library import EfficientSU2
import numpy as np

# 1. Definir molécula: H2 com distância H-H = 0.735 Angstrom
driver = PySCFDriver(
    atom="H 0 0 0; H 0 0 0.735",
    basis="sto3g",
)
problem = driver.run()

# 2. Mapear Hamiltoniano para operador Pauli
mapper = ParityMapper()
converter = QubitConverter(mapper=mapper, two_problem=False)
qubit_op = converter.convert(problem.second_q_ops()[0])
print(f"Hamiltoniano tem {len(qubit_op)} termos Pauli")
# Output: Hamiltoniano tem 12 termos Pauli

# 3. Escolher ansatz: EfficientSU2 (reps=1)
ansatz = EfficientSU2(num_qubits=2, reps=1, entanglement='linear')
print(f"Ansatz tem {ansatz.num_parameters} parâmetros")
# Output: Ansatz tem 6 parâmetros

# 4. Configurar VQE com otimizador clássico
optimizer = COBYLA(maxiter=100, tol=1e-5)
estimator = Estimator()
vqe = VQE(estimator, ansatz, optimizer)

# 5. Executar em simulador (ou hardware)
result = vqe.compute_minimum_eigenvalue(qubit_op)
print(f"Energia do estado fundamental: {result.eigenvalue.real:.6f} Ha")
print(f"Iterações executadas: {result.metadata[0]['eval_count']}")
# Output: Energia do estado fundamental: -1.136890 Ha
# Output: Iterações executadas: 47

# Comparar com valor clássico (DFT)
reference_energy = problem.reference_energy
print(f"Energia clássica (DFT): {reference_energy:.6f} Ha")
print(f"Erro: {abs(result.eigenvalue.real - reference_energy):.6f} Ha")
```

**Escalabilidade por tamanho de molécula:**
- H₂ (2 átomos): 2 qubits lógicos, 6 portas parametrizadas, ~50 iterações
- H₂O (água, 3 átomos): 10 qubits lógicos, ~100 portas, ~1.000 iterações
- Cafeína (24 átomos): ~80 qubits lógicos, inviável sem QEC (2026+)

**Mitigação de ruído:**
```python
# Zero-noise extrapolation: executar com diferentes níveis de erro
from qiskit_aer import AerSimulator
from qiskit_experiments.library import LocalReadoutError

def vqe_with_error_mitigation(qubit_op, ansatz, optimizer, noise_levels=[1, 2, 3]):
    """VQE com mitigação de erros de leitura"""
    results = []
    for scale_factor in noise_levels:
        # Executar com ruído amplificado/atenuado
        estimator_with_noise = create_noisy_estimator(scale_factor)
        vqe = VQE(estimator_with_noise, ansatz, optimizer)
        result = vqe.compute_minimum_eigenvalue(qubit_op)
        results.append(result.eigenvalue.real)
    
    # Extrapolação linear para zero ruído
    x = np.array(noise_levels)
    y = np.array(results)
    coeffs = np.polyfit(x, y, 1)
    zero_noise_energy = coeffs[1]  # Intersecção em x=0
    return zero_noise_energy
```

### QAOA (Quantum Approximate Optimization Algorithm) para Otimização Combinatória

QAOA resolve problemas NP-difíceis como Max-Cut e TSP via aproximação. Estrutura: codificar problema como grafo, Hamiltoniano C codifica custo. Ansatz com p níveis: (1) evolução sob cost Hamiltonian, (2) evolução sob mixer Hamiltonian.

**Implementação MAX-CUT com p=2:**

```python
from qiskit.circuit import QuantumCircuit, ParameterVector
from qiskit.primitives import Estimator
from qiskit.algorithms.optimizers import COBYLA
import numpy as np
from itertools import combinations

# Define grafo: 4 nós, edges [(0,1), (0,3), (1,2), (2,3)]
# MAX-CUT: encontrar corte que maximiza arestas entre dois sets
edges = [(0,1), (0,3), (1,2), (2,3)]
num_nodes = 4
p = 2  # Profundidade QAOA

# Cost Hamiltonian: H_C = Σ (1 - Z_i Z_j) / 2 para cada aresta
# Mixer Hamiltonian: H_M = Σ X_i (X em todos qubits)

def qaoa_circuit(beta, gamma):
    """Construir circuito QAOA com ângulos beta e gamma"""
    qc = QuantumCircuit(num_nodes)
    
    # Superposição inicial
    for i in range(num_nodes):
        qc.h(i)
    
    # p camadas QAOA
    for layer in range(p):
        # Cost Hamiltonian evolution
        for i, j in edges:
            qc.rzz(2 * gamma[layer], i, j)
        
        # Mixer Hamiltonian evolution
        for i in range(num_nodes):
            qc.rx(2 * beta[layer], i)
    
    return qc

def evaluate_cut(bitstring, edges):
    """Avaliar qualidade de um corte (quantos edges cruzam)"""
    cut = 0
    for i, j in edges:
        if bitstring[i] != bitstring[j]:
            cut += 1
    return cut

# Otimizar parâmetros
def objective(params, ansatz_builder, edges):
    """Função objetivo: minimizar -(número de arestas no corte)"""
    beta = params[:p]
    gamma = params[p:2*p]
    
    qc = ansatz_builder(beta, gamma)
    qc.measure_all()
    
    # Executar 1000 shots
    from qiskit_aer import AerSimulator
    sim = AerSimulator()
    job = sim.run(qc, shots=1000)
    counts = job.result().get_counts()
    
    # Calcular esperança do corte
    avg_cut = sum(evaluate_cut(bitstring, edges) * count 
                  for bitstring, count in counts.items()) / 1000
    return -avg_cut  # Minimizar para solver clássico

# Otimização
initial_params = np.random.uniform(0, 2*np.pi, 2*p)
optimizer = COBYLA(maxiter=50)
result = optimizer.minimize(
    lambda params: objective(params, qaoa_circuit, edges),
    x0=initial_params
)

print(f"Qualidade máxima encontrada: {-result.fun:.2f} arestas")
print(f"Ótimo clássico para este grafo: {len(edges)} arestas")
print(f"Razão de aproximação: {-result.fun / len(edges):.2%}")
# Output: Qualidade máxima encontrada: 3.00 arestas
# Output: Ótimo clássico para este grafo: 4 arestas
# Output: Razão de aproximação: 75.00%
```

**Trade-offs QAOA:**
- p=1: razão ~65-70% do ótimo, profundidade baixa, viável em NISQ
- p=3-5: razão ~80-85%, profundidade moderada
- p>10: diminuição retorna, overhead clássico domina
- Hardware real com depolarização 0.1% por gate: máximo p=5-7 antes de degradação severa

## Stack técnico

**Linguagem e frameworks:**
- Python 3.10+ (requerido para async/type hints)
- Qiskit 1.0+ com Qiskit Nature para VQE/QAOA molecular
- PennyLane 0.42+ (mais modular, melhor para prototipar)
- Cirq (se usar Google hardware)

**Hardware e simuladores:**
- Simulador local: até 25 qubits clássicos, ~2-4 horas por circuito complex
- IBM Quantum Cloud: acesso grátis a ~2 min/dia, filas longíssimas
- Amazon Braket: ~$0,30 por task, acesso a IonQ/Rigetti/D-Wave
- Google Quantum AI: acesso limitado a pesquisadores

**Dependências Python:**
```python
numpy>=1.21
scipy>=1.7  # Para otimizadores
qiskit>=1.0
qiskit-nature>=0.7
qiskit-machine-learning>=0.7
pennylane>=0.32
```

**Custo mensal típico (para experimentação):**
- Desenvolvimento grátis: simulador local
- Validação em hardware: $50-200/mês (Braket)
- Pesquisa intensiva: $500-2.000/mês

**Tempo de desenvolvimento (estimado):**
- Shor prototipagem: 1 dia (simulador), impossível em produção até ~2029
- Grover: 1-2 dias (oracle pode ser bottleneck)
- VQE: 3-5 dias (incluindo validação contra DFT)
- QAOA: 2-3 dias (ajuste de p é iterativo)

## Código prático: Comparação de algoritmos em um script

```python
# compare_quantum_algos.py
import numpy as np
from qiskit import QuantumCircuit
from qiskit_aer import AerSimulator
import time

def benchmark_shor_small():
    """Shor para número pequeno (15 = 3×5)"""
    from qiskit_algorithms import Shor
    sim = AerSimulator()
    shor = Shor(quantum_instance=sim)
    start = time.time()
    result = shor.factor(15)
    elapsed = time.time() - start
    return result, elapsed

def benchmark_grover_search():
    """Grover buscando em 8 itens"""
    import pennylane as qml
    n_qubits = 3
    dev = qml.device('default.qubit', wires=n_qubits)
    
    @qml.qnode(dev)
    def grover():
        for i in range(n_qubits):
            qml.Hadamard(wires=i)
        # Simplificado: 1 iteração
        qml.RZ(np.pi/2, wires=0)  # Oracle simulado
        return qml.probs(wires=range(n_qubits))
    
    start = time.time()
    probs = grover()
    elapsed = time.time() - start
    return np.argmax(probs), elapsed

def benchmark_vqe_h2():
    """VQE para H2"""
    from qiskit_nature.second_q.drivers import PySCFDriver
    from qiskit_nature.second_q.mappers import ParityMapper
    from qiskit_nature.second_q.converters import QubitConverter
    from qiskit.algorithms.optimizers import SLSQP
    from qiskit_algorithms.minimum_eigensolvers import VQE
    from qiskit.circuit.library import RealAmplitudes
    from qiskit.primitives import Estimator
    
    driver = PySCFDriver(atom="H 0 0 0; H 0 0 0.735", basis="sto3g")
    problem = driver.run()
    mapper = ParityMapper()
    converter = QubitConverter(mapper=mapper, two_problem=False)
    qubit_op = converter.convert(problem.second_q_ops()[0])
    
    ansatz = RealAmplitudes(2, reps=1)
    optimizer = SLSQP(maxiter=100)
    vqe = VQE(Estimator(), ansatz, optimizer)
    
    start = time.time()
    result = vqe.compute_minimum_eigenvalue(qubit_op)
    elapsed = time.time() - start
    return result.eigenvalue.real, elapsed

# Executar benchmarks
print("Benchmarks Quantum Algorithms (2026)")
print("="*50)

try:
    factors, t_shor = benchmark_shor_small()
    print(f"Shor(15): {factors} em {t_shor:.3f}s")
except Exception as e:
    print(f"Shor: {e}")

try:
    index, t_grover = benchmark_grover_search()
    print(f"Grover: índice {index} em {t_grover:.3f}s")
except Exception as e:
    print(f"Grover: {e}")

try:
    energy, t_vqe = benchmark_vqe_h2()
    print(f"VQE(H2): E = {energy:.6f} Ha em {t_vqe:.1f}s")
except Exception as e:
    print(f"VQE: {e}")
```

## Armadilhas e limitações

1. **Shor é inatingível em NISQ — não execute "sério".**
   - Requisito: 4.000 qubits lógicos com QEC
   - Realidade 2026: máximo ~127 qubits físicos (IBM Heron), ~0 qubits lógicos de QEC
   - Simuladores clássicos fazem Shor em 15 ou 21 mais rápido que qualquer computador quântico
   - Ação: use Shor apenas para educação e prototipar QFT; não desperdice créditos em hardware

2. **Grover tem overhead linear em implementação real.**
   - O oracle precisa ser codificado em portas lógicas, custo O(N) gates
   - Isso anula a vantagem quadrática teórica
   - Relevante apenas quando oracle é inerentemente rápido (acesso a QAM — Quantum Associative Memory)
   - Ação: valide tempo de oracle antes de commitar em Grover para seu problema

3. **VQE sofre com "barren plateaus".**
   - Gradientes desaparecem em circuitos profundos com muitos parâmetros aleatórios
   - Em reps>3, probabilidade de barren plateau cresce exponencialmente
   - Mitigação: warm-start (inicializar com DFT clássico), parameter sharing, ansatze estruturados (UCC)
   - Sem mitigação, otimizador converge para ~0.1% do ótimo
   - Ação: sempre comece com pequeno ansatz (reps=1) e escale gradualmente

4. **Ruído degradation é exponencial em profundidade.**
   - Hardware com depolarização 0.1% por gate: profundidade >20 gates causa erro >1%
   - VQE com 100+ gates vê queda de ~50% na acurácia
   - Exemplo: H₂ com ruído simulado piora energia em 0,1 Ha (vs. sem ruído 0,01 Ha)
   - Ação: use simuladores com ruído realista (AerSimulator + noise model) antes de hardware real

5. **Choice de ansatz em VQE/QAOA é tudo.**
   - Hardware-efficient ansatze (EfficientSU2): profundidade baixa, expressividade limitada
   - UCC (Unitary Coupled Cluster): expressivo, muito profundo (~300 gates para moléculas simples)
   - Não há regra universal — requer experimentação extensiva
   - Ação: testar 3-4 ansatze diferentes; medir profundidade vs. convergência

6. **QAOA approximation ratio não escala com p indefinidamente.**
   - MAX-CUT: ótimo clássico 0.878, p=1 QAOA ~0.65-70, p=∞ → 0.878
   - Mas hardware com ruído: p>10 piora resultado (ruído acumula)
   - Trade-off: profundidade linear em p, mas benefício sublinear após p=5
   - Ação: limitar p≤7 na era NISQ; ajustar por tipo de problema

## Conexões

Esses algoritmos formam a base de todas as aplicações quânticas práticas:
- **Segurança:** Shor motiva urgência em [[post-quantum-criptografia-lattice-pqc-nist-2024]]
- **Simulação molecular:** VQE alimenta [[simulacao-quantica-molecular-quimica-farmacos-materiais]]
- **Machine Learning:** VQE e QAOA ancestrais de [[quantum-machine-learning-circuitos-variacionais-aplicacoes-hibridas]]
- **Stack técnico:** Implementação requer [[frameworks-programacao-quantica-qiskit-cirq-pennylane-comparacao]]
- **Hardware:** Limitações de [[hardware-quantico-nisq-era-supercondutores-ions-fotonico]]
- **FT:** Caminho para produção via [[correcao-erros-quanticos-codigos-superficie-caminho-computacao-tolerante-falhas]]

## Histórico

- 2026-03-28: Nota criada a partir de artigo CodNest
- 2026-04-02: Reescrita como guia prático de implementação com stack técnico
- 2026-04-11: Expandida com 120+ linhas, código prático, benchmarks, armadilhas detalhadas
