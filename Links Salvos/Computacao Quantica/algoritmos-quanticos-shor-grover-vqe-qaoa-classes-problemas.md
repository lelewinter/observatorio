---
tags: [computacao-quantica, algoritmos, shor, grover, vqe, qaoa, otimizacao, criptografia]
source: https://codnestx.com/quantum-algorithms-in-2025-shors-grovers-and-the-future-of-computing/
date: 2026-03-28
tipo: aplicacao
---
# Implementar Algoritmos Quânticos Shor, Grover, VQE e QAOA em Hardware Real

## O que é

Existem quatro algoritmos quânticos fundamentais com aplicações práticas verificáveis: Shor (quebra RSA via fatoração), Grover (busca em banco não estruturado), VQE (simulação molecular), e QAOA (otimização combinatória). Cada um explora mecanismos diferentes de superposição e interferência, e sua escolha depende do problema e do hardware disponível. Compreender suas limitações e requisitos é crítico antes de investir tempo em implementação.

## Como implementar

**Algoritmo de Shor (Fatoração de Inteiros)**

O algoritmo de Shor usa transformada quântica de Fourier (QFT) e ordem clássica para fatorar um número grande N em tempo polinomial O(log³ N). A implementação em Qiskit começa com a QFT — a operação que amplifica a amplitude da ordem correta através de interferência construtiva. Para quebrar RSA-2048 (617 dígitos), requer ~4.000 qubits lógicos e circuito de profundidade ~100 milhões. Hoje: impossível em qualquer hardware NISQ. Use Qiskit para prototipagem em simulador com números pequenos (números menores que 100). O código carrega: preparação do estado de superposição com Hadamard, fase kickback via controle unitário de potências modulo N, e QFT para extrair frequência. Experimente com números semi-primos pequenos (15 = 3×5) para validação. A limitação prática é que simuladores clássicos conseguem simular até ~25 qubits; além disso, precisaria de hardware real com QEC madura.

Estrutura do circuito: entrada com N bits (número a fatorar), ~20N qubits de trabalho para QFT e aritmética modular, entrega período via medição. A vulnerabilidade de RSA depende da capacidade de descobrir esse período em tempo polinomial. A implementação de Shor em Qiskit está no repositório `qiskit/qiskit-tutorials` com referências a Miller e Venegas-Andraca.

**Algoritmo de Grover (Busca em Banco Não Estruturado)**

Grover acelera busca em lista não ordenada de N itens de O(N) para O(√N) — vantagem quadrática universal. Para buscar 1 item entre 1 milão, em vez de 1 milhão de passos clássicos, Grover precisa de apenas ~1.000 iterações quânticas. Implementação: prepare superposição uniforme com Hadamard em todos os qubits. Em cada iteração: (1) aplique oracle que marca o item correto (inverte fase de |target⟩), (2) inverta sobre média (phase kickback). Repita √N vezes. Medir no final fornece o índice do item com probabilidade >99%.

Na prática: Grover é relevante quando o oracle é rápido de implementar. Busca em banco de dados relacional requer mapeamento de chaves para qubits (log₂(N) qubits para N registros). Aplicação real: quebra de chaves simétricas — Grover reduz segurança do AES-256 para ~128 bits porque precisa testar √2^256 ≈ 2^128 chaves. Por isso NIST recomenda AES-256 como seguro pós-quântico (dobrar tamanho de chave compensa Grover). Implementação prototipagem em PennyLane: 6 linhas de código para buscar em lista de 8 itens.

**VQE (Variational Quantum Eigensolver) para Simulação Molecular**

VQE é o algoritmo híbrido mais prático para NISQ. Objetivo: encontrar energia do estado fundamental de uma molécula. Arquitetura: o circuito quântico (ansatz) prepara um candidato de estado, mede esperança do Hamiltoniano H (energia), o otimizador clássico (COBYLA, SLSQP) ajusta parâmetros do ansatz para minimizar energia. Iteração até convergência.

Implementação em Qiskit + Qiskit Nature: (1) definir molécula (e.g., H₂, água, cafeína) e mapear Hamiltoniano para operador de Pauli (~12-20 termos para moléculas pequenas). (2) escolher ansatz — UCC (Unitary Coupled Cluster, mais preciso) ou UCCSD (mais profundo). UCCSD com single e double excitações requer profundidade ~100-300 em hardware com 4-8 qubits lógicos. (3) executar em simulador com noise ou hardware real. (4) comparar resultado com DFT clássico para validação. Exemplo: H₂ converge em ~50 iterações com 2 qubits, 6 portas parametrizadas. Água (3 átomos, ~10 elétrons) requer 10 qubits lógicos e ~1.000 iterações, viável em IBM Heron ou IonQ hoje.

Limitações: nível de ruído degrada gradientes em hardware real. Mitigação de erros via zero-noise extrapolation ou readout error mitigation reduz overhead. Profundidade de circuito cresce cubicamente com tamanho da molécula — para proteínas (>100 elétrons), requer QEC integrada que não existe em 2026.

**QAOA (Quantum Approximate Optimization Algorithm) para Otimização Combinatória**

QAOA resolve problemas NP-difíceis como Max-Cut, Traveling Salesman Problem (TSP), alocação de portfólio via aproximação. Estrutura: codifique problema como grafo, a hamiltonian C codifica o custo (penalidade negativa para soluções boas). Ansatz com p níveis: (1) evolução sob cost Hamiltonian, (2) evolução sob mixer Hamiltonian (tipicamente X⊗X⊗...). Parâmetros: p (profundidade) e ângulos β, γ. Otimizador clássico ajusta. Medir no final fornece solução aproximada.

Implementação prototipagem: começar com p=1 em MAX-CUT com 4 nós. Qiskit: defina grafo, mapear para QAOA com `QAOA.from_opflow()`, executar em backend real. Profundidade QAOA é O(p) — muito menor que VQE. Com p=5-10, consegue aproximações boas em 10-50 iterações. Aplicações: UPS/DHL otimizam rotas em hardware IBM; Morgan Stanley testa carteiras em IonQ.

Trade-off: QAOA não garante ótimo global, apenas aproximação — tipicamente 85-95% do ótimo em problemas clássicos verificáveis. Vantagem sobre clássico ainda não comprovada em escala industrial, mas resiliência ao ruído (profundidade baixa) faz de QAOA o algoritmo de otimização favorito para era NISQ.

## Stack e requisitos

- **Linguagem**: Python 3.8+
- **Libs principais**: Qiskit 1.0+, PennyLane 0.42+, Cirq (se Google hardware)
- **Hardware**: simulador local (até 25 qubits, 2-4 horas por circuito) ou acesso a IBM Quantum Cloud (via token), IonQ (via Amazon Braket), Google Quantum AI
- **APIs**: Anthropic (pré-processamento), IBM/Google/IonQ tokens
- **Custo**: IBM Quantum grátis com filas longas, Amazon Braket ~$0,30 por task, Google Quantum livre para pesquisa
- **Tempo de desenvolvimento**: Shor prototipagem ~1 dia (simulador), produção impossível até 2029. Grover ~1 dia. VQE ~3-5 dias (validação contra DFT). QAOA ~2-3 dias.

## Armadilhas e limitações

1. **Shor é inatingível em NISQ**: não execute "sério" — use para educar. O requisito de 4.000 qubits lógicos não existe em 2026. Simuladores clássicos fazem Shor em números pequenos mais rápido que quânticos.

2. **Grover tem overhead linear em implementação real**: o oracle precisa ser codificado em portas, o que pode custar O(N) gates — anulando a vantagem. Relevante só quando oracle é inerentemente rápido (e.g., acessar memória quântica).

3. **VQE sofre com "barren plateaus"**: gradientes desaparecem em circuitos profundos com muitos parâmetros aleatórios. Mitigação: usar warm-start (inicializar com DFT), parameter sharing, ou ansatze estruturados. Sem mitigation, otimizador fica preso.

4. **QAOA aproximation ratio degrada com problema**: MAX-CUT tem razão ~0.878 clássica; QAOA com p=1 típico consegue ~0.65-0.70. Aumentar p ajuda, mas custo quadrático em profundidade.

5. **Ruído real**: hardware atual com depolarização ~0.1-1% por gate faz profundidade >20 impraticável sem mitigation. VQE com >100 gates vê degradação significativa de acurácia.

6. **Ansatz crítico**: choice de ansatz em VQE/QAOA define tudo. Hardware-efficient ansatze reduzem profundidade mas perdem expressividade. UCC é expressivo mas profundo. Não há regra universal — requer experimentação.

## Conexões

Esses algoritmos são a base de todas as aplicações quânticas práticas. Shor determina urgência de criptografia pós-quântica ([[post-quantum-criptografia]]). VQE alimenta [[simulacao-quantica-molecular-quimica-farmacos-materiais]]. QAOA e VQE são ancestrais de [[quantum-machine-learning-circuitos-variaclionais-aplicacoes-hibridas]]. Implementação exige escolha de [[frameworks-programacao-quantica-qiskit-cirq-pennylane-comparacao]]. Limitações práticas vêm de [[hardware-quantico-nisq-era-supercondutores-ions-fotonico]] e exigem [[correcao-erros-quanticos-codigos-superficie-caminho-computacao-tolerante-falhas]].

## Histórico
- 2026-03-28: Nota criada a partir de artigo CodNest
- 2026-04-02: Nota reescrita como guia prático de implementação com stack técnico
