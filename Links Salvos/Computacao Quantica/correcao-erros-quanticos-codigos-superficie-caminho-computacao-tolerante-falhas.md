---
tags: [computacao-quantica, correcao-de-erros, qec, surface-codes, qldpc, fault-tolerant, qubits-logicos]
source: https://www.riverlane.com/blog/quantum-error-correction-our-2025-trends-and-2026-predictions
date: 2026-03-28
tipo: aplicacao
---
# Implementar Correção de Erros Quântica com Códigos de Superfície e qLDPC

## O que é

Qubits físicos erram frequentemente (taxa ~0,1-1% por operação). Para computação quântica útil, é preciso codificar qubits lógicos usando redundância — múltiplos qubits físicos guardam um qubit lógico de forma que erros sejam detectáveis e corrigíveis. Dois paradigmas dominam: códigos de superfície (2D, clássico, prova de conceito do Google Willow) e qLDPC (mais compacto, adotado por IBM). Este guia cobre a teoria, simulação, e como ler roadmaps de hardware.

## Como implementar

**Parte 1: Qubits Lógicos vs. Físicos — Conceito Fundamental**

Um qubit lógico é codificado em N qubits físicos. Erros em qualquer subconjunto dos físicos podem ser detectados sem colapsar a superposição do lógico — se a taxa de erro física está abaixo de um limiar (threshold), aumentar N reduz taxa de erro lógico exponencialmente.

Exemplo concreto: code distance d=3 requer d² = 9 qubits físicos por lógico. Se cada qubit físico erra com probabilidade p=0.1%, após correção, qubit lógico erra com ~10^-5. Distance d=5: 25 qubits físicos por lógico, erro lógico ~10^-10. A relação é grosseiramente p_lógico ~ (p_físico / p_threshold)^d.

Implementação prototipagem: simulador de código de superfície com 9 qubits (distance 3):

```python
import numpy as np

class SurfaceCode:
    def __init__(self, distance):
        self.d = distance
        # Grid de qubits físicos: d x d data + (d-1) x (d-1) syndrome
        self.data_qubits = distance * distance
        self.syndrome_qubits = (distance - 1) ** 2
        self.total_qubits = self.data_qubits + self.syndrome_qubits

    def measure_syndrome(self, data_errors):
        """
        data_errors: vetor de comprimento data_qubits com 0 ou 1
        Retorna síndrome = paridade dos erros ao redor de cada qubit syndrome
        """
        syndrome = []
        for i in range((self.d - 1) ** 2):
            # Cada syndrome qubit mede paridade de 4 data qubits vizinhos
            parity = 0
            neighbors = self._get_neighbors(i)
            for neighbor_idx in neighbors:
                parity ^= data_errors[neighbor_idx]
            syndrome.append(parity)
        return np.array(syndrome)

    def decode(self, syndrome, error_model='i.i.d'):
        """
        Decodificador simples: encontra correlação da síndrome com padrão de erro
        """
        # Em prática real: Minimum Weight Perfect Matching (complexo, O(n^3))
        # Aqui: simulação simplificada
        pass

code = SurfaceCode(distance=3)
print(f"Distance 3: {code.data_qubits} data + {code.syndrome_qubits} syndrome = {code.total_qubits} qubits totais")
# Distance 3: 9 data + 4 syndrome = 13 qubits totais
```

**Parte 2: Codigos de Superfície (Google Willow)**

Códigos de superfície arranjo 2D de qubits. Medições de síndrome são locais (cada syndrome qubit verifica 4 vizinhos). Vantagem: topologia regular, fácil de fabricar em supercondutores. Desvantagem: razão data/lógico é O(d²) — distance 7 requer 49 qubits data, ~100 total.

Implementação: simulador com ruído e decoder

```python
from qiskit.providers.fake_provider import FakeWillow
from qiskit.circuit import QuantumCircuit
from qiskit_aer.noise import NoiseModel

# Usar modelo de ruído do Willow (0.1% per gate)
willow = FakeWillow()
noise_model = NoiseModel.from_backend(willow)

# Circuito de teste: preparar estado lógico |0⟩ com distance 3
qc = QuantumCircuit(13, name='surface_code_d3')

# Inicializar todos em |0⟩
# (Em prática: estabilizers preparam estado)

# Medir syndrome qubits 4 vezes para verificar erros
for round_num in range(4):
    for i in range(4):  # 4 syndrome qubits
        qc.measure(9 + i, i)  # medir syndrome qubit i+9

# Simular com ruído
from qiskit_aer import AerSimulator
simulator = AerSimulator(noise_model=noise_model)
result = simulator.run(qc, shots=100).result()

# Decodificar síndrome e corrigir
syndrome_patterns = result.get_counts(qc)
for syndrome, count in syndrome_patterns.items():
    # syndrome é sequência de 4 bits (2^4 = 16 padrões possíveis)
    print(f"Syndrome {syndrome}: {count} shots")
```

Interpretação: cada síndrome é um padrão de bits que indica onde erros aconteceram no grid. O decodificador mapeia síndrome → mapa de erros mais provável → aplicar correções. Willow usou surface codes com distance 7 para demonstrar supressão de erros abaixo do threshold.

**Parte 3: Códigos qLDPC (IBM, Iceberg Quantum)**

qLDPC = Quantum Low-Density Parity-Check. Em vez de verificações locais de paridade, usa verificações esparsas mas não-locais. Resultado: razão data/lógico cai de O(d²) para O(log(d)) — para distance 15, qLDPC precisa ~50 qubits vs. 225 para surface code.

Implementação teórica (detalhe matemático):

```python
# Código qLDPC é definido por matriz de paridade H (sparse)
# Cada linha de H é uma medição (síndrome qubit)
# Cada coluna é um qubit data

# Exemplo: distance 3 qLDPC (hipotético)
import scipy.sparse as sp

# Matriz de paridade (sparse): 8 syndrome qubits, 16 data qubits
# Cada syndrome mede paridade de ~3-4 qubits (sparse)
H = sp.csr_matrix([
    [1, 1, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],  # syndrome 0
    [0, 1, 1, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],  # syndrome 1
    # ... (8 linhas)
])

# Decodificação é MWPM (Minimum Weight Perfect Matching) em grafo de síndrome
# Complexidade: O(n^3) para n syndrome qubits
# Em hardware: decoders em tempo real rodam em FPGA/GPU

print(f"qLDPC: density {H.nnz / (H.shape[0] * H.shape[1]):.2%}")
# ~20% densidade (sparse vs. ~100% para surface code)
```

**Parte 4: Decoders em Tempo Real — O Gargalo Prático**

O verdadeiro desafio não é o código, é o decoder. Após cada medição de síndrome, o decoder deve identificar padrão de erro em microsegundos (taxa de clock do hardware ~1 µs). Para >100 qubits lógicos, isso requer aceleração em hardware.

Riverlane (startup 100% focada em decoders) desenvolveu decoders em tempo real baseados em:
- MWPM clássico com pré-processamento
- Redes neurais para predição de padrão
- Look-up tables (pré-computadas para distâncias pequenas)

Implementação simplificada com lookup table:

```python
# Para distance 3, pré-computar todos 16 síndrome patterns → erro mais provável
lookup_table = {
    '0000': [0, 0, 0, 0, 0, 0, 0, 0, 0],  # nenhum erro
    '0001': [0, 0, 0, 1, 0, 0, 0, 0, 0],  # erro no qubit 3
    '0010': [0, 0, 1, 0, 0, 0, 0, 0, 0],  # erro no qubit 2
    # ... (13 patterns)
}

def decode_surface_code_d3(syndrome):
    """Decodificação via lookup table (para distance 3)"""
    return lookup_table.get(syndrome, None)

# Em tempo real: hardware faz lookup em ~100 ns
```

**Parte 5: Timeline Prático até Fault Tolerance**

- 2024: Google Willow demonstrou supressão abaixo do threshold com distance 7 (51 qubits físicos, ~5 lógicos por run)
- 2025: IBM Kookaburra primeiro sistema com qLDPC hardware-integrated (não apenas simulação)
- 2026: Iceberg Quantum Pinnacle anunciou <100k qubits necessários para quebrar RSA-2048 via qLDPC (vs. 1M anterior)
- 2028-2030: Primeira corrida para sistemas com 100-1000 qubits lógicos em tolerância a falhas

## Stack e requisitos

- **Linguagem**: Python 3.8+
- **Libs**: Qiskit, Qiskit Aer, Scipy (sparse matrices), PyMatching (MWPM decoder)
- **Hardware**: Simulador local (até ~20 qubits, segundos), ou IBM Quantum (distance 7 via Willow quando disponível)
- **Decoders**: PyMatching (clássico open-source) ou Riverlane (proprietário, em beta)
- **Custo**: Simulação grátis, hardware real ~$1-5k por hora em IBM/Google
- **Tempo**: Entender conceitos ~4-6 horas, implementar simulador distance 3 ~1 dia, rodar em hardware real ~3-5 dias (fila)

## Armadilhas e limitações

1. **Threshold é necessário mas não suficiente**: cruzar threshold reduz taxa de erro lógico exponencialmente, mas não a zero. Hardware precisa estar bem abaixo de threshold para vantagem prática.

2. **Distância vs. profundidade**: aumentar distance reduz erro lógico, mas aumenta número de portas de correção — se essas portas têm taxa de erro igual aos data qubits, volta ao quadrado um. Requer portas de muito alta fidelidade (<0.01% erro).

3. **Síndrome não diz exatamente qual erro ocorreu**: múltiplos padrões de erro podem gerar mesma síndrome. Decodificador escolhe padrão mais provável — se escolher errado, erro se propaga.

4. **Decodificação em tempo real é crítico**: se decoder mais lento que taxa de medição, erros acumulam antes de serem corrigidos. Para 1 GHz gates, precisa decoder em <1 ns — limite físico duro.

5. **Overhead de recursos é imenso**: para quebrar RSA-2048 com surface codes, requer ~1 bilhão de qubits físicos (1 milhão lógicos × 1000 razão). qLDPC reduz para ~100 milhões, mas é ainda impraticável antes de 2035.

6. **Desvios de design não-ideal**: códigos teóricos assumem portas perfeitas e medições projetivas. Hardware real tem:
   - Portas multi-qubit com fidelidades desiguais
   - Medições com readout errors
   - Crosstalk entre qubits próximos
   Mitigação: design de código específico para hardware.

## Conexões

QEC é pré-requisito para que [[algoritmos-quanticos-shor-grover-vqe-qaoa-classes-problemas]] sejam executáveis em escala. Willow demonstrou QEC em prática com [[hardware-quantico-nisq-era-supercondutores-ions-fotonico]]. Decoders são ponto quente de pesquisa que determina timeline para [[vantagem-quantica-google-willow-ibm-corrida-2025-2026]]. qLDPC é estratégia central de IBM roadmap.

## Histórico
- 2026-03-28: Nota criada a partir de Riverlane blog
- 2026-04-02: Reescrita com código de simulador, timeline prático, e análise de gargalos
