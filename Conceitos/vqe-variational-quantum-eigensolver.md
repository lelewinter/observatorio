---
tags: [conceito, computacao-quantica, algoritmos, otimizacao, vqe, hibrido]
date: 2026-04-02
tipo: conceito
aliases: [Variational Quantum Eigensolver]
---
# VQE (Variational Quantum Eigensolver)

## O que é

VQE é algoritmo híbrido quântico-clássico que encontra estado de mínima energia de uma molécula. O circuito quântico (ansatz) prepara candidato de estado com ângulos parametrizados θ. O otimizador clássico (COBYLA, SLSQP) ajusta θ para minimizar energia esperada. Iteração até convergência. VQE é aplicação mais promissora de hardware NISQ atualmente (2026) porque requer profundidade moderada (~200 gates) e demonstra vantagem verificável sobre métodos clássicos em moléculas com >30 elétrons.

## Como funciona

1. **Mapeamento da molécula**:
   - Geometria atômica (Ex: H₂ com ligação 0.74 Å)
   - Calcular integrais eletrônicas (kinética + Coulomb)
   - Segunda quantização: converter para operadores fermiônicos
   - Jordan-Wigner mapping: converter para operadores Pauli (portas quânticas)

2. **Ansatz (circuito parametrizado)**:
   - UCCSD (Unitary Coupled Cluster Single & Double) é padrão
   - Cada excitação eletrônica é um parâmetro e uma porta
   - Profundidade: O(N²) com N = número de elétrons

3. **Medição de energia**:
   - Medir expectativa ⟨ψ(θ)|H|ψ(θ)⟩ onde H é Hamiltoniano
   - Separar em termos de Pauli (Ex: 0.5⟨Z₀Z₁⟩ - 0.3⟨X₀Y₁⟩)
   - Medir cada termo separadamente (ou otimizar gruppings)

4. **Otimização clássica**:
   ```
   repeat:
     E(θ) ← medir energia média
     ∇E(θ) ← computar gradiente (parameter-shift rule: 4 execuções por parâmetro)
     θ ← θ - learning_rate * ∇E
   until E converge
   ```

## Para que serve

VQE resolve problema exponencialmente difícil para clássicos: encontrar energia exata de molécula com elétrons correlacionados. Métodos clássicos (DFT, CCSD(T)) fazem aproximações ou têm custo factorial. VQE:
- Sem aproximações de exchange-correlation (vs. DFT)
- Sem limite de tamanho de molécula (vs. CCSD(T) em clássicos)
- Funciona em hardware NISQ com ruído moderado

Aplicações: descoberta de fármacos, design de materiais, catalisadores, baterias.

Trade-off: requer circuito profundo (300-2000 gates para moléculas realistas), sujeito a ruído. Mitigation necessária: zero-noise extrapolation, readout error correction, warm-start em DFT clássico.

## Exemplo prático

```python
# VQE para H2 em Qiskit
from qiskit_nature.second_q.drivers import PySCFDriver
from qiskit_nature.second_q.mappers import JordanWignerMapper
from qiskit_nature.second_q.algorithms import GroundStateEigensolver, VQEUCCFactory
from qiskit_algorithms.optimizers import COBYLA
from qiskit_aer.primitives import Estimator

# 1. Definir molécula
driver = PySCFDriver(
    atom="H 0 0 0; H 0 0 0.74",
    basis="sto3g",
    charge=0,
    spin=0
)

problem = driver.run()

# 2. Mapear para Hamiltonian
mapper = JordanWignerMapper()
hamiltonian = mapper.map(problem.second_q_ops()[0])

# 3. Definir ansatz
ansatz_factory = VQEUCCFactory(
    qubit_converter=mapper,
    excitations='sd'  # single + double
)

# 4. Otimizador
optimizer = COBYLA(maxiter=500)

# 5. Estimador
estimator = Estimator()

# 6. Resolver
solver = VQEUCCFactory(ansatz_factory, optimizer, estimator)
result = solver.solve(problem)

print(f"Ground state energy: {result.eigenvalues[0]:.6f} Ha")
print(f"Iterations: {result.metadata[0]['eval_count']}")

# H2 típico: converge em 50-100 iterações, ~5 minutos em IBM Heron
```

Comparação com DFT:
```python
# DFT clássico
from pyscf import gto, dft

mol = gto.M(atom='H 0 0 0; H 0 0 0.74', basis='sto-3g')
mf = dft.RKS(mol)
mf.xc = 'lda,vwn'
dft_energy = mf.kernel()

# VQE vs DFT
print(f"VQE: {vqe_energy:.6f}")
print(f"DFT: {dft_energy:.6f}")
print(f"Diferença: {abs(vqe_energy - dft_energy):.6f}")
```

## Aparece em
- [[algoritmos-quanticos-shor-grover-vqe-qaoa-classes-problemas]] - VQE é um dos 4 algoritmos fundamentais
- [[simulacao-quantica-molecular-quimica-farmacos-materiais]] - VQE é core de simulação molecular
- [[quantum-machine-learning-circuitos-variaclionais-aplicacoes-hibridas]] - VQE é prototipo de ansatz variacional parametrizado
- [[frameworks-programacao-quantica-qiskit-cirq-pennylane-comparacao]] - Qiskit Nature é ferramenta padrão para VQE
- [[hardware-quantico-nisq-era-supercondutores-ions-fotonico]] - VQE é aplicação favorita para NISQ

---
*Conceito extraído em 2026-04-02*
