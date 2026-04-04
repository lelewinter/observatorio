---
tags: [computacao-quantica, hardware, qubits, supercondutores, ions-aprisionados, fotonico, nisq]
source: https://thequantuminsider.com/2026/02/23/understanding-the-quantum-computing-hardware-landscape/
date: 2026-03-28
tipo: aplicacao
---
# Avaliar Hardware Quântico: Supercondutores vs. Íons vs. Fotônica vs. Átomos Neutros

## O que é

Hardware quântico existe em quatro modalidades principais com trade-offs radicalmente diferentes: supercondutores (rápidos, ruído), íons aprisionados (lento, alta fidelidade), fotônica (temperatura ambiente, perda) e átomos neutros (escala, ainda experimental). Cada tecnologia tem roadmap distinto para 2030. Escolher qual usar depende de seu algoritmo, orçamento, e tolerância a ruído. Este guia oferece critério de comparação prático.

## Como implementar

**Parte 1: Os Quatro Paradigmas — Quadro Comparativo**

```
                    SUPERCONDUTORES      IONS               FOTONICO         ATOMOS NEUTROS
Temperatura         10-20 mK             Ambiente (ou < 1K) Ambiente         ~100 µK
Tempo coerência     100 µs               min-seg            µs               seg-min
Fidelidade porta    98-99.5%             >99.9%             85-95%           97-98%
Velocidade porta    10-100 ns            1-10 µs            100 ns           100 ns-1 µs
Qubits atuais       27-1386              10-50              20-50            200+
Escalabilidade      2D grid              1D cadeia          2D fotônica      2D/3D óptica
Maior desafio       Ruído t1/t2          Velocidade         Perda fótons     Escalabilidade
Timeline QEC        2026-2028            2028-2030          2030+            2028-2030
Empresa líder       IBM, Google, Rigetti IonQ, Quantinuum   Xanadu, PsiQ     QuEra, Pasqal
```

**Parte 2: Supercondutores (IBM, Google, Rigetti, IQM) — Líderes em Escala**

Qubits supercondutores são circuitos de Josephson operando em refrigerador de diluição a ~10-20 mK. Quando resfriados abaixo de temperatura crítica, resistência cai a zero. Qubits armazenam energia de excitação (fótons) em cavidades supercondutoras.

Características técnicas:
- **Operação**: dois estados |0⟩ (ground) e |1⟩ (excited) codificados como níveis de energia do oscilador
- **Gates**: microondas ressoam frequência de qubit, induzem rotação Rabi. CNOT via interação capacitiva entre qubits vizinhos
- **Coerência**: T1 (relaxamento) ~50-200 µs, T2 (defase) ~50-100 µs. Gates rápidos aproveitam essa janela
- **Taxa de erro**: 0.1-1% por gate (melhor qubit supercondutores ~0.08%, pior ~1%)

Implementação prototipagem: acessar IBM Quantum Cloud
```python
from qiskit_ibm_runtime import QiskitRuntimeService

service = QiskitRuntimeService(channel="ibm_quantum", token="YOUR_TOKEN")
backends = service.backends(filters=lambda x: x.configuration().n_qubits >= 100)

# Listar backends disponíveis
for backend in backends:
    config = backend.configuration()
    print(f"{backend.name}: {config.n_qubits} qubits, T1~{config.t1}µs")

# Executar em IBM Heron (133 qubits, 2025)
backend = service.backend("ibm_heron")
result = backend.run(qc, shots=1000).result()
```

Mapa topológico (IBM Heron 133-qubit):
- Grade 2D de qubits com links entre vizinhos
- Cada qubit tem ~4-6 vizinhos
- CNOT entre não-vizinhos requer swap chains (adiciona profundidade)

Limitações supercondutores:
1. **Refrigeração**: dilution fridge custa $500k-2M, consome 5-10 kW, requer manutenção frequente
2. **T1/T2 curtos**: limita profundidade de circuito a ~100-200 gates antes de decoerência
3. **Crosstalk**: gates em qubits vizinhos interferem, requer software de mitigação
4. **Fabricação**: supercondutores requerem limpeza ultrassônica, ambiente controlado

**Vantagem de supercondutores**: são os únicos com >1000 qubits hoje. Roadmaps de IBM/Google/Rigetti levam para 2028-2030 com QEC integrada.

**Parte 3: Íons Aprisionados (IonQ, Quantinuum) — Melhor Fidelidade**

Íons aprisionados são átomos carregados suspensos por campos eletromagnéticos. Diferente de supercondutores, não precisa refrigeração extrema (pode rodar perto de temperatura ambiente com cooling a lasers).

Características técnicas:
- **Operação**: qubits codificados em dois níveis hiperfinos do átomo (Ex: ytterbium-171, bário-137)
- **Gates**: lasers ressoam transição, induzem rotação. Interação com todos os outros íons (all-to-all connectivity)
- **Coerência**: T1 ~ segundos, T2 ~ minutos (40-60 vezes melhor que supercondutores)
- **Taxa de erro**: >99.9% fidelidade por gate (5-10× melhor que supercondutores)
- **Velocidade**: gates lentíssimos (1-10 µs vs. 10-100 ns em supercondutores)

Implementação acesso via Amazon Braket:
```python
import boto3
from braket.aws import AwsDevice

# Conectar a IonQ via AWS
device = AwsDevice("arn:aws:braket:::device/qpu/ionq/Harmony")

# Submeter circuito
task = device.run(qc, s3_destination_folder=("my-bucket", "tasks"), shots=1000)
result = task.result()
```

All-to-all connectivity é vantagem única:
- Não precisa swap chains para CNOT entre qubits não-vizinhos
- Circuitos com muitos CZ globais são mais curtos
- Útil para algoritmos que requerem conectividade densa (QML, some otimizações)

Limitações:
1. **Escalabilidade**: ions em cadeia 1D. Aumentar número requer nova topologia de armadilha. Hoje max ~20-50 qubits.
2. **Crosstalk**: gates em um íon afetam vizinhos via campo fraco — requer correção ativa
3. **Custo operacional**: lasers contínuos para cooling + lock, requer expertise
4. **Profundidade limitada**: apesar alta coerência, gates lentos significam profundidade útil ~500-1000 (vs. ~100 em supercondutores)

**Vantagem de ions**: melhor para aplicações que precisam altíssima fidelidade com circuitos moderadamente profundos (VQE de moléculas pequenas, química).

**Parte 4: Fotônica (Xanadu, PsiQuantum) — Escalabilidade Teórica**

Qubits fotônicos são fótons. Codificação: número de fótons em modo óptico (Fock states), ou dois modos ortogonais (dual-rail).

Características:
- **Operação**: portas ópticas (beamsplitters, phase shifters) combinam/interferem fótons
- **Temperatura**: ambiente (enorme vantagem!)
- **Conectividade**: fotônica integrada com silício pode ter topologia 2D
- **Coerência**: fótons não decaem (T1 ~ infinito), mas perdem-se no circuito (~1-5% per gate)
- **Taxa de erro**: 5-15% por gate (pior que outras modalidades)

Abordagem computation by measurement (MBQC):
```python
# Em vez de gates tradicionais, usar medições e feedforward
# Cluster state é preparado uma vez, operações via medições projetivas

# Pseudocódigo:
# 1. Preparar cluster state emaranhado em 2D
# 2. Medir qubits sequencialmente com ângulos que codificam algoritmo
# 3. Feedforward clássico compensa erros de medição

# Vantagem: resiliente a perda — se fóton se perde durante medição, apenas falha esse qubit
```

Implementação: Xanadu Photonics engine (Strawberry Fields)
```python
import strawberryfields as sf
from strawberryfields import ops

# Criar programa fotônico
prog = sf.Program(2)

with prog.context as q:
    ops.Squeezed(0.5) | q[0]
    ops.Squeezed(0.5) | q[1]
    ops.Beamsplitter(np.pi/4) | (q[0], q[1])
    ops.MeasureFock() | q

# Executar
engine = sf.LocalEngine(backend="fock", cutoff_dim=10)
result = engine.run(prog)
```

Limitações fotônicas:
1. **Perda de fótons**: principal problema. Fótons perdidos = qubits perdidos
2. **Detecção**: detectores de fótons únicos têm eficiência <90%, adiciona mais perda
3. **Integração**: fotônica integrada com silício é imatura (2025 primeiras demonstrações)
4. **Não há CNOT direto**: gates exigem quatro fótons (squeezing + postselection), muito overhead

**Vantagem de fotônica**: temperatura ambiente, integração com infraestrutura óptica, potencial de redes quânticas. PsiQuantum aposta em fotônica para >1 milhão de qubits até 2040.

**Parte 5: Átomos Neutros (QuEra, Pasqal) — Escalabilidade Rápida**

Átomos neutros em armadilhas ópticas. Recente, mas crescimento mais rápido que outras modalidades em 2024-2025.

Características:
- **Operação**: átomos presos por lasers em configuração 2D/3D. Qubits em dois níveis ópticos
- **Gates**: lasers induzem transições Rabi, rotações
- **Conectividade**: 2D ou 3D com vizinhos (não all-to-all)
- **Coerência**: T1 ~ segundos, T2 ~ 100+ ms
- **Taxa de erro**: 97-98% fidelidade por gate
- **Qubits**: QuEra demonstrou 200+ em 2024, roadmap para 1000+ até 2027

Benchmark QuEra:
```python
# QuEra oferece acesso via Amazon Braket (2025)
# Código similar a IonQ

from braket.aws import AwsDevice

device = AwsDevice("arn:aws:braket:::device/qpu/neutral-atom/quera")
result = device.run(qc, shots=1000).result()
```

Vantagem singular: rearrangement — durante execução, átomos podem ser movidos via lasers. Permite reconfigurar conectividade entre operações.

**Vantagem de átomos neutros**: escalabilidade mais rápida que ions, coerência melhor que supercondutores, custo operacional menor que supercondutores.

**Parte 6: Comparação Prática — Qual Escolher em 2026**

```
Se objetivo é:
├─ Aprender / educar
│  └─ Simulador local (grátis, Qiskit Aer)
│
├─ VQE molécula pequena (H2, LiH)
│  ├─ Fidelidade crítica? → IonQ
│  ├─ Custo importante? → IBM Heron + error mitigation
│  └─ Não importa muito → Xanadu (1 fóton quantum)
│
├─ Otimização (MAX-CUT, TSP)
│  ├─ Problema grande (>100 vars)? → IBM (mais qubits)
│  ├─ Conectividade densa? → IonQ (all-to-all)
│  └─ Média/pequeno? → Qualquer um, IBM mais barato
│
├─ QML / classificação
│  ├─ Dados clássicos? → PennyLane em IBM/IonQ
│  ├─ Muitos parâmetros? → Qualquer (mas IonQ melhor coerência)
│  └─ Produção? → Esperar QEC matura (2028+)
│
└─ Pesquisa de hardware / QEC
   └─ Google Willow (se tiver acesso)
```

## Stack e requisitos

- **Hardware**: simulador local (grátis, até 25 qubits), ou cloud tokens
  - IBM Quantum: grátis (filas longas)
  - Google Quantum: pesquisa apenas
  - IonQ via Amazon Braket: $0.30/task
  - Xanadu via cloud: $5-10/task
  - QuEra via Amazon Braket: $1-2/task

- **Custo mensal para pesquisa**: $50-500 dependendo volume
- **Custo para "produção"**: $10k+/mês para 1000s tasks/dia

## Armadilhas e limitações

1. **Simuladores mentirosos**: simulador sem ruído super-otimista. Adicionar ruído realista requer calibração do backend específico.

2. **Filas longas**: IBM Quantum grátis tem esperas de horas/dias. Pago (~$5k/mês) tem prioridade.

3. **Hardware muda frequentemente**: IBM retirou backends de 5-20 qubits em 2025, mantém apenas 100+. Código que funcionou em 2024 pode não rodar em 2026.

4. **Fidelidades publicadas vs. reais**: fabricantes publicam fidelidade ideal em condições perfeitas. Fidelidade real com ruído de 1/f é 5-10% pior.

5. **Topologia não-ideal**: nem todos backends têm topologia que algoritmo precisa. Compilador adiciona SWAPs, aumenta profundidade e erro.

6. **Custo de qubit lógico é imenso**: para fault tolerance, requer ~1000 qubits físicos por lógico. Hardware de $1M pode valer apenas $1k em qubits lógicos.

## Conexões

Hardware limita o que algoritmos são práticos. [[algoritmos-quanticos-shor-grover-vqe-qaoa-classes-problemas]] têm requisitos diferentes por hardware. [[frameworks-programacao-quantica-qiskit-cirq-pennylane-comparacao]] usam backends diferentes. [[correcao-erros-quanticos-codigos-superficie-caminho-computacao-tolerante-falhas]] é roadmap central de cada hardware. [[vantagem-quantica-google-willow-ibm-corrida-2025-2026]] registra milestones por hardware.

## Histórico
- 2026-03-28: Nota criada a partir de The Quantum Insider
- 2026-04-02: Reescrita com quadro comparativo, código de acesso, e árvore de decisão
