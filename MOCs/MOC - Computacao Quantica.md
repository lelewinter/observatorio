---
tags: [moc, computacao-quantica, qubits, algoritmos, hardware, qml, vqe, qaoa, erro-quantum, frameworks]
date: 2026-04-02
tipo: moc
---
# Computação Quântica

Fundamentals de computação quântica (superposição, emaranhamento, interferência), arquitetura de hardware NISQ (supercondutores, ions, fotônico), implementação de algoritmos quânticos (Shor, Grover, VQE, QAOA), correção de erros quânticos, machine learning quântico, e simulação molecular. O vault contém 8 notas densas cobrindo landscape técnico 2025-2026, timeline de milestones, e interpretação crítica de hype vs. realidade.

## Fundamentos: Computação via Superposição, Emaranhamento, Interferência

[[computacao-quantica-processa-informacao-usando-superposicao-emaranhamento-interferencia|Processamento de Informação em Superposição]] — computação quântica é paradigma fundamentalmente diferente de clássico. Bit (0 ou 1) → qubit (superposição de 0 e 1 simultâneos até medição). N qubits = 2^N estados possíveis em superposição (exponencial). Exemplo: 3 qubits podem representar todos 8 valores (000, 001, ..., 111) simultaneamente.

Mecanismos: **Superposição** permite explorar múltiplos caminhos em paralelo (espacio exponencial). **Emaranhamento** correlaciona qubits (medir um afeta outro instantaneamente, não causa transmissão FTL). **Interferência** amplifica amplitudes de respostas corretas (construtiva) e cancela incorretas (destrutiva) — a chave para vantagem quântica.

Exemplo algorítmico: busca em banco não-estruturado de N itens. Clássico: O(N) consultas. Grover (quantum): O(√N) — quadrático speedup universal. Shor (fatoração): O(log³N) vs clássico O(N^(1/3)) — exponential speedup, mas específico a fatoração.

Limitação fundamental: nenhum algoritmo quântico é universalmente mais rápido que clássico. Vantagem existe apenas em classes específicas de problemas (Shor, Grover, simulação molecular, otimização). Hype vs. realidade: nem todo problema fica 1000x mais rápido.

## Hardware Quântico: NISQ Era (2024-2027)

[[hardware-quantico-nisq-era-supercondutores-ions-fotonico|Quatro Modalidades de Hardware com Trade-offs Distintos]] — NISQ = Noisy Intermediate-Scale Quantum (dezenas a milhares de qubits, taxa de erro 0.1-1% por gate).

**Supercondutores** (Google, IBM): qubits são circuitos LC em estado fundamental (|0⟩) vs. estado excitado (|1⟩). Taxa de erro: 0.1-0.3% por gate (melhor atual), tempo de coerência: 1-100 microsegundos (exigir operações rápidas). Escalabilidade: acoplamento entre vizinhos em 2D grid. Temperatura: 15 millikelvin (refrigeração custosa). Maior ecossistema, mais maturidade. Google Willow (105 qubits), IBM Heron (133 qubits), IBM roadmap Kookaburra (1.386 qubits).

**Ions Capturados** (IonQ, Honeywell, Alpine): qubits são íons presos em armadilha eletromagnética, transições são diferenças de nível de energia. Taxa de erro: 0.1-0.5%, tempo de coerência: segundos (excelente). Gate fidelity: 99.9%+. Desvantagem: conectividade all-to-all mas operações gate é lento (~microsegundos vs nanosegundos). Escalabilidade: 50-100 qubits em 2026. Menor ecossistema.

**Fotônico** (Xanadu, PsiQuantum): qubits são fótons (partículas de luz), gates via interferometers/beamsplitters. Taxa de erro: 1-5% (pior). Vantagem: operar em temperatura ambiente. Escalabilidade: em P&D ainda. Promise: 1M qubits no futuro, mas não em 2026.

**Topológicos** (Microsoft): qubits baseados em anyons (defects topológicos). Taxa de erro: potencialmente <0.01% (proteção topológica), mas ainda demonstração. Escalabilidade: <10 qubits em 2025, promessa é 100+ em 2028-2030.

Conclusão prática: 2026 = supercondutores dominam, ions competem, fotônico/topológico são research. Escolha de hardware depende de aplicação (Shor precisa muito qubits lógicos, VQE funciona em qualquer com 4-10 qubits).

## Algorithms Quânticos: Shor, Grover, VQE, QAOA

[[algoritmos-quanticos-shor-grover-vqe-qaoa-classes-problemas|Quatro Algoritmos Fundamentais com Aplicações e Limitações Práticas]]

**Shor (Fatoração de Inteiros)**: quebra RSA via transformada quântica de Fourier (QFT). Requisitos: ~4.000 qubits lógicos (para RSA-2048), profundidade de circuito ~100 milhões. Implementação simulador: prototipe em números pequenos (15 = 3×5) em Qiskit. Realidade 2026: impossível em qualquer hardware NISQ. Usar para educação, não produção. Relevância: determina urgência de [[MOC - Seguranca]] (criptografia pós-quântica).

**Grover (Busca em Banco)**: acelera busca não-estruturada de O(N) → O(√N). Implementação prototipagem: 6 linhas de código em PennyLane, ~1.000 iterações para buscar 1 item entre 1 milhão. Armadilha: oracle (função que marca resposta correta) precisa ser implementado em portas — pode custar O(N) gates, anulando vantagem. Aplicação real: ataque em AES-256 reduz segurança efetiva para ~128 bits (por isso NIST recomenda AES-256 como seguro pós-quântico mesmo com Grover).

**VQE (Variational Quantum Eigensolver)**: encontra energia do estado fundamental de molécula. Arquitetura: circuito quântico (ansatz) prepara candidato de estado, mede esperança do Hamiltoniano (energia), otimizador clássico (COBYLA) ajusta parâmetros. Iteração até convergência. Implementação: H₂ em 2 qubits converge em ~50 iterações. Água (H₂O) em 10 qubits ~1.000 iterações. Limitação: profundidade cresce cubicamente com tamanho da molécula — proteínas (>100 elétrons) requer QEC madura (não existe em 2026). Armadilha: "barren plateaus" (gradientes desaparecem em redes profundas), mitigation via warm-start (inicializar com DFT clássica) ou ansatze estruturados (UCC, UCCSD).

**QAOA (Quantum Approximate Optimization)**: resolve problemas NP-difíceis (MAX-CUT, TSP, portfolio allocation) via aproximação. Ansatz com p níveis: evolução sob cost Hamiltonian, evolução sob mixer. Profundidade O(p) — muito menor que VQE. Aproximation ratio típico: 85-95% do ótimo (não garante ótimo global). Implementação: começar com p=1 em MAX-CUT com 4 nós. Morgan Stanley testa em IonQ, UPS/DHL otimizam rotas em IBM. Realidade: vantagem comprovada vs. clássico ainda não em escala industrial (2026).

## Correção de Erros Quânticos: O Caminho para Fault Tolerance

[[correcao-erros-quanticos-codigos-superficie-caminho-computacao-tolerante-falhas|QEC é Bottleneck Principal para Escalabilidade]] — qubits físicos erram (~0.1-1% por gate). Para computação útil e longa, codificar qubits lógicos usando muitos físicos. Surface codes (Willow): distance 7 requer 49 dados + 48 syndrome = 97 qubits físicos por 1 lógico. Overhead imenso (100x). IBM qLDPC: ~10-20 qubits físicos por lógico (mais compacto).

Google Willow demonstrou QEC abaixo do threshold (primeiro hardware prova escalabilidade): distance 7 surface code = taxa de erro lógica 2.4× melhor que melhor qubit físico individual. Implica: escalar código (maior distance) reduz erro exponencialmente, não linearmente — path para fault tolerance é viável.

Milestone: IBM roadmap = fault tolerance (código funcional 24/7 sem degeneração) em 2029-2030. Crítico: decodificação em tempo real é problema não-resolvido (pode ser gargalo invisível).

## Vantagem Quântica: Timeline e Interpretação Crítica

[[vantagem-quantica-google-willow-ibm-corrida-2025-2026|Milestones 2025-2026 e Desconto de Hype]] — Distinção: Supremacia Quântica (2019, Google Random Circuit Sampling: 5 min vs 10.000 anos) = artificial, sem aplicação real. Vantagem Quântica (2025, Willow) = problema com interpretação física verificável, benchmark não-artificial.

Willow checklist (todas passam): ✓ Hardware real (105 qubits), ✓ Problema verificável (out-of-time correlator em física), ✓ Contra supercomputador otimizado (não naive), ✓ Ordem de magnitude real (13.000×), ✓ Peer-reviewed (Nature), ✓ Efetivos qubits ~70 (não todos 105).

Iceberg Quantum (fevereiro 2026) afirma quebrar RSA-2048 requer <100k qubits (vs. 1M anterior). Checklist (algumas falham): ✗ Simulação (não hardware real), ✓ Problema verificável (RSA), ✗ Assumições otimistas (decoder perfeito, taxa de erro 0%), ? Baseado em números assumidos, não medidos. Conclusão: promissor mas não comprovado.

## Machine Learning Quântico

[[quantum-machine-learning-circuitos-variaclionais-aplicacoes-hibridas|QML usa Circuitos Variacionais como Camadas de Rede]] — QML combina hardware quântico com otimização clássica para aprender padrões. Exemplo: quantum neural network onde camadas quânticas (VQE-style) alternadas com clássicas (PyTorch). Feature map prepara dados clássicos como estados quânticos, circuito parametrizável processa, medição extrai resultado.

Vantagem teórica: kernel quântico pode ter dimensionalidade exponencial (2^N para N qubits). Realidade: ainda não há aplicação onde quantum outperforms clássico de forma robusta (2026). "Dequantization" — algoritmos clássicos que emulam quantum de forma eficiente — reduziram vantagem teórica.

Aplicações em estudo: classificação de imagens, detecção de anomalias, otimização de portfólio. Nenhuma em produção real.

## Simulação Molecular: Aplicação com Maior Vantagem Comprovável

[[simulacao-quantica-molecular-quimica-farmacos-materiais|Simulação Molecular é Aplicação Mais Madura]] — simular moléculas com precisão quântica é exponencialmente difícil clássicamente (espaço de Hilbert cresce exponencialmente). Hamiltoniano de moléculas maps naturalmente para qubits. Aplicações: descoberta de drogas (estimar energia de ligação), design de materiais (propriedades eletrônicas), catalisadores.

VQE + UCCSD ansatz converge para H₂O (trivial) mas águas maiores, proteínas ainda fora de reach NISQ (profundidade demanda QEC). Expectativa 2028-2030: moléculas de ~50 átomos simuladas com vantagem sobre clássico (ainda não batidos em 2026).

## Frameworks de Programação Quântica

[[frameworks-programacao-quantica-qiskit-cirq-pennylane-comparacao|Três Frameworks Dominantes: Qiskit (IBM), Cirq (Google), PennyLane (Xanadu)]]

**Qiskit 1.0+** (IBM): mais usado, comunidade grande, aceita qualquer backend (IBM, IonQ, simuladores). Python-first. Curva de aprendizado: média. Documentação: excelente.

**Cirq** (Google): baixo-level (controle fino), otimizado para supercondutores. Python. Curva: mais íngreme. Comunidade: média.

**PennyLane** (Xanadu): diferenciável (integra com PyTorch/TensorFlow), ideal para QML. Python. Curva: média. Documentação: ótima.

Escolha: comece com Qiskit (maior ecossistema), mude pra PennyLane se QML é foco.

## Estado Atual e Tendências (2026)

NISQ era continua (30-100 qubits lógicos ainda 5-7 anos de distância). Willow provou QEC viável, mas escalabilidade tem incógnitas (decoder performance? overhead TBD?). Momentum agora em: (1) correção de erros (Google/IBM focam), (2) aplicações NISQ-friendly (VQE, QAOA), (3) compatibilidade com IA (Shor é preocupação futura, PQC é defesa agora).

Expectativa 2027-2030: primeiras aplicações práticas (simulação molecular, otimização de rota), adotção em indústria (pharma, airlines), regulação (padrões de quantum safety, compliance).

Curto prazo (2026): usar quantum via cloud (IBM Quantum, IonQ via AWS Braket, Google), educação/pesquisa, nenhuma produção crítica. Médio prazo (2027-2029): casos de uso específicos começam, mas beta. Longo prazo (2030+): quem dominou quantum agora (pesquisadores, early adopters) obtém vantagem competitiva.

## Ferramentas e Stack Prático

**Linguagem**: Python 3.8+.

**Simuladores**: Qiskit Aer (até ~25 qubits), PennyLane (até 20), Cirq (até 25). Além disso, precisa clusters de HPC.

**Hardware Cloud**: IBM Quantum (grátis, filas longas), IonQ (via Amazon Braket, $0.30/task), Google Quantum (pesquisa).

**Libs**: Qiskit 1.0+, Cirq, PennyLane 0.42+, Numpy, Scipy.

**Custo**: educação=grátis, pesquisa=grátis, produção=$1-5k/mês (cloud access).

**Tempo aprendizado**: Qiskit basics 1-2 semanas, proficiency 2-3 meses, especialidade (QML, QEC) 6-12 meses.

## Conexões com Outros Temas

Computação quântica é ameaça explorada por [[MOC - Seguranca]] (Shor quebra RSA), solução é criptografia pós-quântica. QML conecta com [[MOC - IA e LLMs]] (machine learning). Simulação molecular alimenta química e discovery (aplicação prática). Frameworks/algoritmos conectam com [[MOC - Dev e Open Source]] (Qiskit é open-source, repositórios curados).
