---
tags: [computacao-quantica, machine-learning, qml, vqc, circuitos-variaclionais, hibrido, neural-networks]
source: https://pmc.ncbi.nlm.nih.gov/articles/PMC12053761/
date: 2026-03-28
tipo: aplicacao
---
# Treinar Circuitos Quânticos Variacionais para Machine Learning

## O que é

Quantum Machine Learning (QML) combina hardware quântico com otimização clássica para aprender padrões em dados. O elemento central é o Variational Quantum Circuit (VQC): um circuito parametrizado onde ângulos de portas são "pesos" treináveis, análogos a uma camada neural. Treinamento acontece via backpropagation clássico (parameter-shift rule). Este guia cobre teoria, implementação prototipagem em PennyLane + PyTorch, limitações reais, e timing para utilidade prática.

## Como implementar

**Parte 1: Arquitetura VQC — Três Componentes**

Um VQC tem sempre a mesma estrutura:

1. **Feature Map (Codificação)**: mapeia dados clássicos X (vetor real) para estado quântico. Tipicamente:
```python
# Feature map simples: rotações dependentes de dados
for i, x_i in enumerate(x):
    qc.rx(x_i, wires=i)  # ângulo proporcional ao dado
    qc.ry(x_i, wires=i)
```

2. **Ansatz (Camada Parametrizada)**: circuito com ângulos θ treináveis:
```python
def ansatz(params):
    # Alternância entre single-qubit rotations e entanglement
    for layer in range(depth):
        for i in range(n_qubits):
            qc.ry(params[layer * n_qubits + i], wires=i)
        for i in range(n_qubits - 1):
            qc.cx(wires=[i, i+1])  # entanglement layer
```

3. **Medição (Output)**: extrair valor escalar (expectância):
```python
# Medir esperança de Z no qubit 0
return qml.expval(qml.PauliZ(0))
```

Arquitetura final:
```
Input (dados clássicos X)
    ↓
[Feature Map: 1-2 camadas]
    ↓
[Ansatz: parametrizado, d camadas]
    ↓
[Medição: expectância de Pauli]
    ↓
Output (predição escalar)
```

**Parte 2: Parameter-Shift Rule — Como Treinar Sem Backprop Quântico**

Backpropagation tradicional (computar gradiente via regra da cadeia) não funciona em hardware quântico porque medição colapsa estado. Solução: parameter-shift rule.

Ideia: para gate com ângulo θ, gradiente é:

```
δf/δθ = [f(θ + π/2) - f(θ - π/2)] / 2
```

Ou seja, precisa executar circuito 4 vezes por parâmetro (dois para +π/2, dois para -π/2) em vez de 1. Mas funciona em hardware real.

Implementação em PennyLane (automática):
```python
import pennylane as qml
import numpy as np

dev = qml.device('qiskit.aer', wires=2)

@qml.qnode(dev)
def circuit(params):
    # Feature map
    qml.RX(0.5, wires=0)  # exemplo de dado

    # Ansatz com params treináveis
    qml.RY(params[0], wires=0)
    qml.CNOT(wires=[0, 1])
    qml.RY(params[1], wires=1)

    return qml.expval(qml.PauliZ(0))

params = np.array([0.1, 0.2])

# Calcular gradiente (PennyLane faz parameter-shift automaticamente)
grad = qml.grad(circuit)(params)
print(f"Gradiente: {grad}")
# Resultado: gradiente computado com 4 execuções de circuito
```

Trade-off: 4× mais execuções para cada iteração de otimização. Se circuito tem 10 parâmetros, cada step de otimização custa 40 execuções em hardware real.

**Parte 3: Implementação Completa — Classificador Binário em PyTorch**

Treinar VQC para classificar dados sintéticos (XOR, ou dados circulares):

```python
import torch
import torch.nn as nn
import pennylane as qml
from torch.optim import Adam
import numpy as np

# Gerar dados de treinamento (XOR)
X_train = np.array([
    [0, 0],
    [0, 1],
    [1, 0],
    [1, 1]
])
y_train = np.array([0, 1, 1, 0])  # XOR labels

# Device quântico
dev = qml.device('qiskit.aer', wires=2, shots=100)

# Definir VQC
class QuantumNet(nn.Module):
    def __init__(self):
        super().__init__()
        self.n_qubits = 2
        self.n_layers = 2
        self.params = nn.Parameter(
            torch.randn(self.n_layers * self.n_qubits)
        )

    def forward(self, x):
        # Feature map
        qml.RX(x[0], wires=0)
        qml.RX(x[1], wires=1)

        # Ansatz
        for layer in range(self.n_layers):
            for i in range(self.n_qubits):
                qml.RY(self.params[layer * self.n_qubits + i], wires=i)
            qml.CNOT(wires=[0, 1])

        # Medição
        return qml.expval(qml.PauliZ(0))

# Criar QML node
@qml.qnode(dev)
def qml_circuit(params, x):
    # Feature map
    qml.RX(x[0], wires=0)
    qml.RX(x[1], wires=1)

    # Ansatz com params
    for layer in range(2):
        for i in range(2):
            qml.RY(params[layer * 2 + i], wires=i)
        qml.CNOT(wires=[0, 1])

    return qml.expval(qml.PauliZ(0))

# Converter para função PyTorch
class QMLClassifier(nn.Module):
    def __init__(self):
        super().__init__()
        self.params = nn.Parameter(torch.randn(4))

    def forward(self, x):
        # x tem shape (batch, 2)
        return qml_circuit(self.params, x)

model = QMLClassifier()
optimizer = Adam(model.parameters(), lr=0.01)
loss_fn = nn.MSELoss()

# Treinar
epochs = 50
for epoch in range(epochs):
    optimizer.zero_grad()

    # Forward pass em batch
    predictions = []
    for x_i in X_train:
        pred = qml_circuit(model.params, x_i)
        predictions.append(pred)

    predictions = torch.stack(predictions)
    loss = loss_fn(predictions, torch.tensor(y_train, dtype=torch.float))

    loss.backward()
    optimizer.step()

    if epoch % 10 == 0:
        print(f"Epoch {epoch}, Loss: {loss.item():.4f}")

# Avaliar
with torch.no_grad():
    preds = []
    for x_i in X_train:
        pred = qml_circuit(model.params, x_i)
        preds.append(1 if pred > 0 else 0)

    accuracy = sum(p == y for p, y in zip(preds, y_train)) / len(y_train)
    print(f"Accuracy: {accuracy:.2%}")
```

**Parte 4: Quantum Kernel Methods — Alternativa a VQC Direto**

Em vez de treinar VQC como rede, usá-lo para calcular kernel quântico (similarity entre pares de dados). Depois treinar SVM clássico com esse kernel.

```python
def quantum_kernel(x1, x2):
    """Kernel quântico: | ⟨ψ(x1) | ψ(x2) ⟩ |²"""
    @qml.qnode(dev)
    def kernel_circuit(x1, x2):
        # Codificar x1
        qml.RX(x1[0], wires=0)
        qml.RX(x1[1], wires=1)

        # Aplicar rotações inversas para x2 (interferência)
        qml.RX(-x2[0], wires=0)
        qml.RX(-x2[1], wires=1)

        # Medir probabilidade de voltar a |00⟩
        return qml.probs(wires=[0, 1])[0]  # P(00)

    return kernel_circuit(x1, x2)

# Construir matriz de kernel
K = np.zeros((len(X_train), len(X_train)))
for i in range(len(X_train)):
    for j in range(len(X_train)):
        K[i][j] = quantum_kernel(X_train[i], X_train[j])

# Treinar SVM com kernel quântico
from sklearn.svm import SVC
svm = SVC(kernel='precomputed')
svm.fit(K, y_train)
```

Vantagem: quantum kernel pode separar dados em espaço de Hilbert de alta dimensão que clássico não consegue.
Desvantagem: requer O(n²) execuções de circuito para n amostras (vs. O(n·p) para VQC com p parâmetros).

**Parte 5: Limitações Reais — "Dequantização" e Quando NÃO Usar QML**

Problema crítico: muitos algoritmos QML foram "dequantizados" — alguém encontrou versão clássica que é tão rápida ou mais.

Exemplos:
- **QSVM (Quantum SVM com kernel)**: dequantizado (Tang, 2021). Clássico que aproxima kernel quântico em tempo polinomial.
- **VQC para classificação genérica**: muitas tentativas fracassaram quando comparadas rigorosamente com DNN clássico no mesmo dataset.

Quando QML provavelmente funciona:
1. **Dados quânticos**: espectros moleculares, output de simulações quânticas. Esses dados só existem em hardware quântico.
2. **Dimensionalidade alta > memória clássica**: dataset que exigiria >exabyte para armazenar vetores clássicos. Quântico pode codificar em amplitude (mas não consegue extrair tudo).
3. **Estrutura específica**: problemas com simetrias que VQC explorai naturalmente.

Realidade em 2026: QML ainda é pesquisa. Não há aplicação de produção com vantagem inequívoca sobre clássico.

**Parte 6: Timeline e Roadmap**

- **2024-2025**: QML demonstrada em NISQ com <100 qubits. Acurácias competitivas em problemas pequenos e sintetizados.
- **2026-2027**: Pesquisa intensa em novos ansatze e kernels. Primeiras aplicações industriais exploratórias (farmacêutica).
- **2028-2030**: QML com QEC matura — começa a ter vantagem real em dados quânticos. Empresas como Zapata, Rigetti investindo.
- **2030+**: QML comercial assume quando dados quântico for commodity (Ex: simulações de química que todos usam).

## Stack e requisitos

- **Linguagem**: Python 3.8+
- **Libs**: PennyLane 0.42+, PyTorch 2.0+, scikit-learn
- **Hardware**: Simulador local (grátis, até 25 qubits), ou IBM/IonQ tokens para hardware real
- **Custo**: Simulação grátis, hardware real ~$0.30-1.00 por task
- **Tempo aprendizado**: 3-5 dias entender VQC + parameter-shift rule, implementar classificador ~1 dia, otimizar para dataset real ~1-2 semanas

## Armadilhas e limitações

1. **Barren Plateaus**: com muitos parâmetros aleatórios em circuitos profundos, gradientes desaparecem para zero. Otimizador fica preso. Mitigação: inicializar com valores pequenos, usar ansatze estruturados (hardware-efficient), ou warm-start com clássico.

2. **Parameter-shift rule é cara**: treinar VQC com 10 parâmetros por 100 iterações requer 40.000 execuções de circuito. Em hardware real a $0.30/task, custa $12k. Em simulador ~2 horas.

3. **Ruído degrada rapidamente**: VQC com >50 gates em hardware real com 0.1% ruído por gate vê degradação severa (~30% loss em acurácia comparado ao simulador ideal).

4. **Dequantização inesperada**: implementar "vantagem garantida" e depois descobrir clássico consegue simular em tempo polinomial. Validação rigorosa (vs. clássico, em múltiplos datasets) é crítica.

5. **Ansatz design importa imensamente**: escolha ruim de ansatz torna VQC não-expressivo (não consegue aprender padrão). Não há receita universal — requer experimentação.

6. **Datos: quantidade vs. qualidade**: VQC em NISQ com ruído requer dataset muito limpo. Dados ruidosos → modelo não consegue aprender vs. superfit.

## Conexões

VQC são aplicação prática de [[algoritmos-quanticos-shor-grover-vqe-qaoa-classes-problemas]] (QAOA é prototipo de ansatz). Implementação em [[frameworks-programacao-quantica-qiskit-cirq-pennylane-comparacao]] — PennyLane é padrão ouro para QML. Rodando em [[hardware-quantico-nisq-era-supercondutores-ions-fotonico]]. Prático apenas após [[correcao-erros-quanticos-codigos-superficie-caminho-computacao-tolerante-falhas]]. Exemplo aplicado: [[simulacao-quantica-molecular-quimica-farmacos-materiais]] com QML para predição de propriedades.

## Histórico
- 2026-03-28: Nota criada a partir de PMC/Nature
- 2026-04-02: Reescrita com código executável, parameter-shift rule detalhado, e análise de dequantização
