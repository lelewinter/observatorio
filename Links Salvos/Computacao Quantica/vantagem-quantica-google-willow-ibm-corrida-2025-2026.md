---
tags: [computacao-quantica, supremacia-quantica, vantagem-quantica, google-willow, ibm, milestones, 2025, 2026]
source: https://www.hpcwire.com/2025/10/22/google-claims-quantum-advantage-with-willow-chip/
date: 2026-03-28
tipo: aplicacao
---
# Acompanhar Milestones de Vantagem Quantica e Implicacoes de Seguranca

## O que é

A corrida por vantagem quântica escalou significativamente em 2025. Google Willow e IBM Kookaburra demonstraram marcos históricos em correção de erros e velocidade de processamento. Este guia oferece timeline precisa dos eventos de 2025-2026, o que cada um significa tecnicamente, implicações para criptografia, e probabilidade de cada predição do setor se concretizar. Crítico para entender o estado real da computação quântica vs. hype.

## Como implementar

**Parte 1: Distinção Supremacia Quântica vs. Vantagem Quântica**

- **Supremacia Quântica (2019)**: computador quântico resolve problema que clássico não consegue em tempo razoável. Google Random Circuit Sampling: 5 minutos em Sycamore vs. 10.000 anos em supercomputador. Problema: é artificial (sem aplicação do mundo real).

- **Vantagem Quântica (2025)**: resolve problema com aplicação real mais rápido que clássico. Critério: problema tem interpretação física verificável (não depende de confiança em clássico).

Google Willow cruzou essa linha em dezembro 2024 (anunciado em 2025) com algoritmo correlador temporal fora de ordem — problema em física quântica com verificação clássica.

**Parte 2: Google Willow — O Primeiro Marco Real**

Hardware:
- 105 qubits supercondutores
- Taxa de erro por porta: ~0.1% (recorde anterior: 0.3%)
- Especificação: Google Quantum AI Sycamore-v3

Três marcos simultâneos:

1. **Supressão exponencial de erros abaixo do threshold**:
   - Primeiro sistema hardware a demonstrar isso
   - Distance 7 surface code: taxa de erro lógica **2.4× melhor** que melhor qubit físico individual
   - Implica: escalar código (maior distance) reduz erro exponencialmente, não linearmente

2. **Execução de algoritmo verificável**:
   - Out-of-time correlator (OTO): mede "scrambling" de informação em sistemas quânticos
   - Resultado: 13.000× mais rápido que supercomputador para cálculo equivalente
   - Tempo: 5 minutos vs. 10^25 anos em clássico
   - Verificação: problema em física quântica, resultado é matematicamente verificável

3. **Benchmark não-artificial**:
   - Diferente de Random Circuit Sampling, OTO tem significado físico
   - Aplicável a sistemas de matéria condensada, cosmologia
   - Primeiro passo em direção a "utilidade prática"

Código / Documentação:
```python
# Simular versão simplificada de Willow em Cirq
import cirq

# Grid de qubits do Willow (5x5 grid simplificado)
qubits = [cirq.GridQubit(i, j) for i in range(5) for j in range(5)]

circuit = cirq.Circuit()

# Codificar estado inicial
for q in qubits:
    circuit.append(cirq.H(q))

# Evoluir sob Hamiltoniano
for _ in range(5):
    for q in qubits:
        circuit.append(cirq.rz(0.1)(q))
    for i in range(4):
        for j in range(5):
            if i < 4:
                circuit.append(cirq.CNOT(qubits[i*5+j], qubits[(i+1)*5+j]))

# Evoluir inverso
for _ in range(5):
    for q in qubits:
        circuit.append(cirq.rz(-0.1)(q))

# Medir correlador O(0) correlador O(T)
circuit.append(cirq.measure(*qubits, key='result'))

print(circuit)
```

Implicações imediatas:
- QEC é viável em hardware real (não apenas teoria)
- Caminho para fault tolerance é claro
- Google roadmap: 2028-2030 sistema com centenas de qubits lógicos

**Parte 3: IBM Kookaburra (2025) — Liderança em Escala**

Hardware:
- 1.386 qubits em módulo único (maior supercondutor single-chip em 2025)
- Multi-chip architecture: 4.158 qubits totais via quantum links de comunicação
- Taxa de erro: 0.15-0.25% por gate (comparável a Willow)
- Primeira prova de comunicação quântica entre chips

Estratégia IBM diferente de Google:
- Google: foco em QEC de superfície, escala lenta, profundidade cuidadosa
- IBM: foco em qLDPC, comunicação entre chips, hardware modular

qLDPC vs. Surface Codes:
```
Surface Code (Willow):
- Distance 7: 49 data + 48 syndrome = 97 qubits por lógico
- Escalável mas overhead imenso

qLDPC (IBM):
- Distance 7: ~10-20 qubits por lógico
- Mais compacto, IBM padrão 2025+

IBM roadmap:
2024: Heron (133 qubits)
2025: Kookaburra (1.386 qubits, multi-chip)
2026: 5.000+ qubits multi-chip
2029: Fault tolerance em escala
```

Implementação: acesso via IBM Quantum Cloud
```python
from qiskit_ibm_runtime import QiskitRuntimeService

service = QiskitRuntimeService(token="YOUR_TOKEN")

# Kookaburra quando disponível
backend = service.backend("ibm_kookaburra")

# Propriedades
print(backend.configuration().n_qubits)  # 1386
print(backend.configuration().basis_gates)  # ['id', 'rz', 'sx', 'x', 'cx']
print(backend.properties().t1(qubit=0))  # T1 time em µs

# Executar
result = backend.run(qc, shots=1000).result()
```

**Parte 4: Microsoft e Qubits Topológicos (2025) — Alternativa Disruptiva**

Microsoft anunciou qubits topológicos (anyons de Majorana) em 2025 — abordagem fundamentalmente diferente.

Ideia:
- Qubit protegido topologicamente contra certos tipos de erro
- Menor overhead de QEC intrinsecamente
- Ainda em fase inicial (<10 qubits demonstrados)

Timeline Microsoft:
- 2025: Demonstração de qubits topológicos (prova de conceito)
- 2028-2030: Escala para 100+ qubits
- 2032-2035: Competir com supercondutores em larga escala

Se funcionar, topológicos poderiam saltar sobre QEC tradicional. Se não, é aprendizado custoso.

**Parte 5: Iceberg Quantum Pinnacle (2026) — Afirmação Ousada**

Empresa: Iceberg Quantum (startup Canadian)
Anúncio: Fevereiro 2026

Afirmação:
- Quebrar RSA-2048 requer <100.000 qubits físicos (vs. 1 milhão anterior)
- Via qLDPC + architecture otimizada
- Prototipagem computacional, não hardware real ainda

Veracidade questionável:
- Baseado em simulações, não testes
- Assumências otimistas sobre taxa de erro e decoder performance
- Comunidade quântica ainda avaliando (peer review em progresso)

**Parte 6: Implicações de Segurança Criptográfica**

Timeline realista de ameaça a RSA-2048:

```
2024: RSA teoricamente vulnerável a Shor, mas requer 4M qubits lógicos
2025: Willow demonstrou QEC é viável, timeline reduzido para 2030s
2026: Iceberg afirma <100k qubits possível (ainda não validado)
2028-2029: Primeiros sistemas com 100+ qubits lógicos (Google/IBM roadmap)
2030-2032: RSA-2048 é vulnerável SE:
  - Qubits lógicos atingem 100k-1M
  - Decoder em tempo real funciona a escala
  - Hardware não colapsa sob custo térmico de refrigeração

2032+: Espera-se quebra de RSA-2048, ECDSA, outros baseados em DLP

Realidade: mesmo que quebrável teoricamente em 2032, demandará:
- $1-10 bilhões em hardware
- Acesso a superfícies de refrigeração massivas
- Expertise rara

NIST Post-Quantum Cryptography Standard (2024):
- ML-KEM (baseado em lattices)
- ML-DSA (assinatura lattice)
- SLH-DSA (hash-based)
Adotar agora reduz risco de "harvest now, decrypt later" (adversários guardando encrypted traffic para decrypar quando QC disponível)
```

Implementação: Migração para PQC
```python
# Exemplo: gerar chave ML-KEM (substituir RSA)
from liboqs import KeyEncapsulation

kem = KeyEncapsulation.KeyEncapsulation("ML-KEM-512")
public_key = kem.generate_keypair()

# Encapsulate (cliente)
ciphertext, shared_secret_client = kem.encap_secret(public_key)

# Decapsulate (servidor)
shared_secret_server = kem.decap_secret(ciphertext)

assert shared_secret_client == shared_secret_server
```

**Parte 7: Predições do Setor vs. Realidade**

| Afirmação | Fonte | Probabilidade 2026 | Status |
|-----------|-------|-------------------|--------|
| QEC abaixo de threshold | Google Willow | 95% ✓ | ALCANÇADO |
| Vantagem quântica em problema real | Google/IBM | 85% ✓ | PARCIALMENTE (Willow) |
| Fault tolerance em 2029 | IBM roadmap | 50% | Em progresso |
| >1M qubits lógicos em 2030 | McKinsey | 20% | Improvável |
| RSA-2048 quebrável em 2030 | Gartner | 15% | Muito otimista |
| Simulação molecular prática | Nature | 70% ✓ | VQE + UCCSD funciona |
| QML vantagem comprovada | Xanadu | 25% | Ainda dequantizado |

**Parte 8: Interpretação de Anúncios — Como Descontar Hype**

Checklist para avaliar afirmações de vantagem quantica:

1. **Hardware real ou simulação?** (Real > simulação)
2. **Problema verificável ou só confiança?** (Verificável > confiança)
3. **Comparação contra quê?** (Clássico otimizado > clássico naive)
4. **Ordem de magnitude é verídica?** (13.000× do Willow vs. 10^6× do 2019)
5. **Peer review ou press release?** (Peer > press)
6. **Efeito de tamanho: N qubits vs. N gates usados?** (Último é real)

Aplicando a Willow (dezembro 2024):
1. ✓ Hardware real (105 qubits)
2. ✓ Problema verificável (OTO é física quântica)
3. ✓ Contra supercomputador otimizado
4. ✓ 13.000× é ordem de magnitude real
5. ✓ Publicado em Nature (peer-reviewed)
6. ✓ Usa ~70 qubits efetivos, não todos 105

Aplicando a Iceberg (fevereiro 2026):
1. ✗ Simulação (não hardware)
2. ✓ Problema verificável (RSA)
3. ? Contra QEC perfeito (assumições otimistas)
4. ? 100k vs. 1M é estimativa teórica
5. ? Ainda em revisão
6. ? Baseado em números assumidos, não medidos

Conclusão: Willow é sólido, Iceberg é promissor mas não comprovado.

## Stack e requisitos

- **Linguagem**: Python 3.8+
- **Libs**: Qiskit, Cirq (para compreender anúncios), Numpy
- **Hardware**: Simulador local (entender marcos), acesso opcional a Google/IBM para validação
- **Custo**: Gratuito (educação), $1-5k/mês se seguir roadmaps de pesquisa
- **Tempo**: 4-6 horas entender timeline, 1-2 semanas acompanhar literatura

## Armadilhas e limitações

1. **Hype extremo**: setor mistura teoria com realidade. "Vantagem quântica" significa coisas diferentes para diferentes pessoas.

2. **Shifting goalposts**: quando marco X não é atingido no prazo, indústria redefine marco como "esperado em" X+N anos. Desconfie de prazos.

3. **No progress on classical side**: benchmarks comparam quântico de 2025 vs. clássico de 2015. Clássico melhorou também.

4. **Scaling law desconhecida**: não sabemos se erro cai exponencialmente o suficiente ao escalar. Pode plateaurar.

5. **Decoder é gargalo invisível**: papers focam em hardware, decodificação em tempo real é problema não-resolvido. Pode ser mais difícil que se esperava.

6. **Criptografia não-urgente**: RSA ainda é seguro por 10+ anos. Corrida por vantagem é mais sobre liderança tecnológica do que ameaça imediata.

## Conexões

Cada marco (Willow, Kookaburra) depende de progresso em [[correcao-erros-quanticos-codigos-superficie-caminho-computacao-tolerante-falhas]]. Competição entre tecnologias em [[hardware-quantico-nisq-era-supercondutores-ions-fotonico]]. Milestones viabilizam [[algoritmos-quanticos-shor-grover-vqe-qaoa-classes-problemas]] prático. [[simulacao-quantica-molecular-quimica-farmacos-materiais]] é aplicação que mais se beneficia de progresso recente.

## Histórico
- 2026-03-28: Nota criada a partir de HPC Wire
- 2026-04-02: Reescrita com timeline precisa, checklist de hype-desconto, análise de credibilidade
