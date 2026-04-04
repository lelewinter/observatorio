---
tags: [computacao-quantica, simulacao-molecular, quimica-quantica, farmacos, materiais, vqe, drug-discovery]
source: https://www.nature.com/articles/s44386-025-00033-2
date: 2026-03-28
tipo: aplicacao
---
# Simular Moléculas com Hardware Quântico para Descoberta de Fármacos

## O que é

Simular moléculas com precisão quântica é exponencialmente difícil para computadores clássicos — o espaço de Hilbert cresce como 2^N com número de elétrons. Computadores quânticos codificam esse espaço naturalmente. Simulação quântica é o caso de uso com vantagem mais tangível e verificável entre todos: McKinsey estima $200-500 bilhões em valor até 2035. Pipelines híbridos já demonstram 20× aceleração em reações específicas. Este guia cobre química quântica prática, implementação em hardware, e timeline de utilidade.

## Como implementar

**Parte 1: Por Que Química é Difícil para Clássicos**

Molécula com N elétrons → espaço de Hilbert com 2^N dimensões. Para 50 elétrons, 2^50 ≈ 10^15 amplitudes. RAM clássica não consegue representar. Métodos aproximados (DFT, CCSD(T)) introduzem erros sistemáticos.

Exemplo: água (H₂O) tem 10 elétrons. Simulação clássica exata requer vetor de 2^10 = 1024 amplitudes complexas. Para cafeína (C₈H₁₀N₄O₂) com ~50 elétrons, matriz de estado tem ~10^15 elementos — impossível.

Computador quântico com 50 qubits lógicos representa naturalmente esse espaço como superposição.

**Parte 2: Mapeamento de Molécula para Hamiltoniano Quântico**

Processo de 4 passos:

1. **Geometria molecular**: definir posições de átomos (Ex: água em ângulo 104.5°)
2. **Integrais eletrônicas**: calcular energia cinética de elétrons + repulsão Coulomb entre núcleo-elétron e elétron-elétron. Método: Hartree-Fock ou post-HF.
3. **Segunda quantização**: converter operadores clássicos em operadores quânticos (criação/aniquilação de elétrons)
4. **Mapeamento Jordan-Wigner ou Bravyi-Kitaev**: converter operadores fermiônicos em operadores de Pauli (portas quânticas)

Implementação em Qiskit:

```python
from qiskit_nature.second_q.drivers import PySCFDriver
from qiskit_nature.second_q.mappers import JordanWignerMapper
from qiskit_nature.second_q.problems import ElectronicStructureProblem

# Define molécula (Ex: H2 com distância de ligação 0.74 Å)
driver = PySCFDriver(
    atom="H 0 0 0; H 0 0 0.74",
    basis="sto3g",  # base mínima
    charge=0,
    spin=0
)

# Calcular integrais eletrônicas
problem = ElectronicStructureProblem(driver)

# Mapear para operadores de Pauli
mapper = JordanWignerMapper()
hamiltonian = mapper.map(problem.second_q_ops()[0])

# Resultado: Hamiltoniano expressado como soma de termos Pauli (e.g., 0.5*Z0*Z1 - 0.3*X0*Y1)
print(f"Número de termos Pauli: {len(hamiltonian)}")
# H2: ~12 termos
# Água: ~100-200 termos
# Cafeína: ~10.000+ termos
```

Cada termo é um expectância de produto de Paulis: ⟨Z₀Z₁⟩, ⟨X₀Y₁Z₂⟩, etc. O circuito quântico mede cada termo separadamente ou com sequências de medição otimizadas.

**Parte 3: VQE para Energia do Estado Fundamental**

VQE iterativamente encontra estado de mínima energia:

```python
from qiskit_nature.second_q.algorithms import GroundStateEigensolver, VQEUCCFactory
from qiskit_algorithms.optimizers import SLSQP, COBYLA
from qiskit_aer.primitives import Estimator

# Definir ansatz (Unitary Coupled Cluster)
ansatz_factory = VQEUCCFactory(
    qubit_converter=mapper,
    num_spatial_orbitals=problem.num_spatial_orbitals,
    num_particles=problem.num_particles,
    excitations='sd'  # single + double excitations
)

# Otimizador clássico
optimizer = COBYLA(maxiter=1000, rhobeg=1.0)

# Estimador quântico
estimator = Estimator(
    skip_qargs_validation=False,
    approximation=False,
    abelian_grouping=True  # agrupar medições por comutatividade
)

# Resolver
solver = VQEUCCFactory(ansatz_factory, optimizer, estimator)
result = solver.solve(problem)

print(f"Ground state energy: {result.eigenvalues[0]:.6f}")
print(f"Iterations needed: {result.metadata[0]['eval_count']}")
```

UCCSD (Unitary Coupled Cluster Single & Double):
- Cada excitação de elétron de orbital ocupado para virtual é um parâmetro
- Para molécula pequena (H₂, He₂): ~4-8 parâmetros
- Água (10 elétrons): ~20-40 parâmetros
- Cafeína: >200 parâmetros

Profundidade de circuito:
- UCCSD com 8 parâmetros: ~100 gates, tempo ~5 minutos em IBM Heron
- UCCSD com 40 parâmetros: ~500 gates, tempo ~2-4 horas (fila)
- Cafeína: ~2000 gates, impossível em NISQ, requer QEC matura

**Parte 4: Comparação com Métodos Clássicos**

| Método | Molécula | Tempo | Acurácia |
|--------|----------|-------|----------|
| DFT (GGA) | Cafeína | <1s | ±0.5 eV (aproximação) |
| CCSD(T) | Água | ~10min | ±0.01 eV |
| VQE + UCCSD | H₂ | 5min | <0.001 eV |
| VQE + UCCSD | Água | 1-2h | ~0.01 eV (com error mitigation) |

VQE vantagem: sem approximações de exchange-correlation. Desvantagem: requere circuito profundo, ruído.

**Parte 5: Implementação Prática — Pipeline Híbrido (Exemplo IonQ + AWS)**

Real case study: Suzuki-Miyaura reaction simulation (2025)

```python
import boto3
from braket.aws import AwsDevice
from braket.circuits import Circuit

# Usar IonQ via Amazon Braket
device = AwsDevice("arn:aws:braket:::device/qpu/ionq/Harmony")

# Definir circuito para uma molécula (intermediário de reação)
circuit = Circuit()

# Feature map: codificar propriedades geométricas
circuit.rx(0, 0.5)
circuit.ry(1, 0.3)

# UCCSD ansatz (simplificado)
for layer in range(2):
    circuit.ry(0, 0.1 * layer)
    circuit.cx(0, 1)
    circuit.ry(1, 0.2 * layer)

# Medir expectância de energia
circuit.result_type.expectation([0.5, 0.3], [0, 1])  # ⟨0.5*Z₀ + 0.3*Z₁⟩

# Executar
task = device.run(circuit, shots=1000)
result = task.result()
energy = result.measurment_counts  # contar outcomes

# Comparar com DFT clássico
dft_energy = calculate_dft_energy()  # usando Psi4/Gaussian

print(f"VQE energy: {vqe_energy:.4f}")
print(f"DFT energy: {dft_energy:.4f}")
print(f"Diferença: {abs(vqe_energy - dft_energy):.4f} eV")

# Se diferença < 0.05 eV, VQE validou a geometria
```

Resultado real (IonQ 2025): 20× aceleração em Suzuki-Miyaura vs. CCSD(T) clássico porque:
- IonQ tem alta fidelidade (~99.9%), permitindo profundidade >200 gates
- Reação específica tem simetrias que UCCSD explora bem
- Pipeline híbrido (clássico + quântico) otimiza custo computacional

**Parte 6: Aplicações Práticas em Descoberta de Fármacos**

1. **Binding affinity prediction**: calcular energia de ligação entre fármaco e proteína-alvo. VQE para ligante + clássico para proteína (grande demais).

2. **Reactivity prediction**: qual isômero é mais reativo? VQE calcula energias HOMO-LUMO de candidatos.

3. **Lead optimization**: variantes de molécula (diferentes grupos R). VQE ordena por reatividade esperada — reduz número de sínteses.

4. **Orphan proteins**: alvos sem fármaco conhecido. Modelar interação quântica com solvente é crucial. VQE + solvente implicit (AQCC) pode descobrir ligantes.

**Parte 7: Limitações Atuais e Timeline**

Limitações em 2026:
- Profundidade UCCSD é O(N²) com N = número de elétrons. Cafeína (~50 elétrons) requer ~2000 gates — impossível com ruído.
- Ruído de hardware degrade exponencialmente. Error mitigation ajuda, mas overhead é 10-100×.
- QEC não madura. Sem QEC, máximo ~200 gates úteis.

Timeline para utilidade:
- **2026-2027**: VQE em moléculas pequenas (<30 elétrons) com validação contra clássico. Produção ainda impossível.
- **2028-2029**: Primeiros sistemas com QEC integrada. Capazes de simular moléculas médias (50+ elétrons) com acurácia competitiva.
- **2030-2035**: Simulação de proteínas e reações complexas. Descoberta de novos fármacos acelerada (6-12 meses vs. 4-6 anos hoje).

Investimentos recentes:
- IBM Project Starling (2025): 10.000 qubits fault-tolerant para 2029, focado em química
- Algorithmiq + Microsoft (2025): métodos avançados de medição para reduzir overhead de VQE
- Merck, Moderna, AstraZeneca: partnerships com IonQ/Quantinuum para explorar simulação

## Stack e requisitos

- **Linguagem**: Python 3.8+
- **Libs**: Qiskit Nature, Qiskit Algorithms, PySCF (cálculo de integrais), Amazon Braket SDK
- **Hardware**: Simulador local (grátis, até 2-3 moléculas pequenas), ou IonQ via Amazon ($0.30-1.00/task)
- **Custo**: Prototipagem em simulador grátis (2-4h wall time), molecule small em IonQ ~$10-50, água ~$100-500
- **Tempo**: Entender VQE + mapeamento ~4-6 horas, rodar H₂ completo ~2 horas (simulação), água ~1 dia com validação

## Armadilhas e limitações

1. **Ansatz importa**: UCCSD é gold standard, mas profundo. Hardware-efficient ansatz é mais raso, mas pode não representar estado. Balanço crítico.

2. **Integrais eletrônicas assumem geometria fixa**: VQE otimiza ângulos de ansatz, não posições atômicas. Para otimização de geometria, precisa loop externo clássico de gradiente descente em geometria. Isso adiciona muitas iterações de VQE.

3. **Erros de medição**: contar outcomes de milhares de shots é estocástico. Variância reduz com mais shots, mas custo é linear em shots.

4. **Orbitais vs. números de ocupação**: mapeamento Jordan-Wigner vs. Bravyi-Kitaev vs. Parity têm propriedades diferentes. Escolha afeta profundidade do circuito. Experimente.

5. **Convergência lenta em platôs**: em pontos onde gradiente é zero, otimizador fica. Warm-start ou otimizador mais sofisticado (SPSA, iCANS) ajuda, mas não garante.

6. **Validação contra clássico é essencial**: VQE pode convergir para energias falsas se ansatz é ruim ou ruído é alto. Sempre comparar com DFT/CCSD(T) confiável.

## Conexões

VQE é aplicação de [[algoritmos-quanticos-shor-grover-vqe-qaoa-classes-problemas]]. Implementação em frameworks [[frameworks-programacao-quantica-qiskit-cirq-pennylane-comparacao]] (Qiskit Nature como padrão). Rodando em [[hardware-quantico-nisq-era-supercondutores-ions-fotonico]] (IonQ preferido para alta fidelidade). Futuro depende de [[correcao-erros-quanticos-codigos-superficie-caminho-computacao-tolerante-falhas]]. Dados quânticos (espectros) alimentam [[quantum-machine-learning-circuitos-variaclionais-aplicacoes-hibridas]].

## Histórico
- 2026-03-28: Nota criada a partir de Nature article
- 2026-04-02: Reescrita com código prático, pipeline real (IonQ), timeline precisa
