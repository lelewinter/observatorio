---
tags: [conceito, computacao-quantica, qml, otimizacao, diferenciacao]
date: 2026-04-02
tipo: conceito
aliases: [Parameter-shift]
---
# Parameter-Shift Rule

## O que é

Parameter-shift rule é método para computar gradiente de circuito quântico em hardware real sem backpropagation quântico (que é impossível). Fórmula: δf/δθ = [f(θ + π/2) - f(θ - π/2)] / 2. Ou seja, para cada parâmetro, executa circuito 4 vezes (2 para +π/2, 2 para -π/2) para estimar gradiente por diferenças finitas. Trade-off: 4× mais execuções por iteração de otimização vs. 1× em backprop clássico, mas funciona em hardware quântico real com superposição e medição.

## Como funciona

**Derivação simplificada**:

Observável quântico O parametrizado por θ:
```
f(θ) = ⟨ψ(θ)|O|ψ(θ)⟩
```

Para porta com ângulo θ (Ex: RY(θ)):
```
Jacobiano de RY(θ) é iσ_Y/2 (matriz de Pauli)
```

Se expandir em série de Taylor (até primeira ordem):
```
f(θ + δ) ≈ f(θ) + δ * df/dθ + O(δ²)
f(θ - δ) ≈ f(θ) - δ * df/dθ + O(δ²)

Subtraindo:
f(θ + δ) - f(θ - δ) ≈ 2δ * df/dθ

Portanto: df/dθ ≈ [f(θ + δ) - f(θ - δ)] / (2δ)
```

Escolher δ = π/2 torna expressão exata (sem termo O(δ²)) para rotações.

**Implementação em PennyLane** (automática):
```python
import pennylane as qml

@qml.qnode(qml.device('qiskit.aer', wires=1))
def circuit(params):
    qml.RY(params[0], wires=0)
    return qml.expval(qml.PauliZ(0))

params = [0.5]

# Gradiente via parameter-shift (automático)
grad = qml.grad(circuit)(params)

# Internamente, PennyLane executou:
# f(0.5 + π/2), f(0.5 - π/2) para cada parâmetro
# Resultado: gradiente preciso sem backprop quântico
```

**Complexidade**:
- N parâmetros: 2N execuções por gradiente (vs. 1 em clássico)
- VQE com 40 parâmetros: 80 execuções por iteração

## Para que serve

Parameter-shift rule é único método conhecido para treinar circuitos quânticos em hardware real com superposição. Alternativas:
- Backprop clássico: não funciona (medição destrói superposição)
- Finite differences: exigem δ pequeno, custo numérico alto
- Analytic gradients: requerem capacidade de computar Jacobiano em tempo real (impossível em hardware atual)

Aplicações: treinar qualquer circuito variacional (VQC em QML, ansatz em VQE, QAOA).

Trade-off: custo em execuções é significativo. Para 10 parâmetros otimizando por 100 iterações com 100 shots por execução = 100.000 shots totais em hardware real (~$30-100 em cloud).

## Exemplo prático

```python
# Demonstrar parameter-shift rule manualmente
import pennylane as qml
import numpy as np

dev = qml.device('default.qubit', wires=1)

@qml.qnode(dev)
def circuit(theta):
    qml.RY(theta, wires=0)
    return qml.expval(qml.PauliZ(0))

theta = 0.5
delta = np.pi / 2

# Calcular gradiente manualmente
f_plus = circuit(theta + delta)
f_minus = circuit(theta - delta)
grad_manual = (f_plus - f_minus) / 2

# Calcular via automático
grad_auto = qml.grad(circuit)(theta)

print(f"Manual gradient: {grad_manual:.6f}")
print(f"Auto gradient: {grad_auto:.6f}")
print(f"Match: {np.isclose(grad_manual, grad_auto)}")

# Verificar: derivada de cos(θ) é -sin(θ)
analytic = -np.sin(theta)
print(f"Analytic: {analytic:.6f}")
print(f"All match: {np.isclose(grad_auto, analytic)}")
```

Comparação de custo (para otimização com SGD, 100 iterações, 10 parâmetros):

| Método | Execuções | Tempo (simulador) | Tempo (hardware real) |
|--------|-----------|-------------------|----------------------|
| Clássico (backprop) | 1 | 1 ms | 1 ms |
| Parameter-shift | 20 | 20 ms | 5-10 minutos |
| Finite diff (δ=0.01) | 20 | 20 ms | 5-10 minutos |

Overhead é dominante em hardware real (overhead de comunicação/fila).

## Aparece em
- [[quantum-machine-learning-circuitos-variaclionais-aplicacoes-hibridas]] - parameter-shift rule é core de VQC training
- [[algoritmos-quanticos-shor-grover-vqe-qaoa-classes-problemas]] - VQE usa parameter-shift para otimizar ansatz
- [[frameworks-programacao-quantica-qiskit-cirq-pennylane-comparacao]] - PennyLane implementa automaticamente

---
*Conceito extraído em 2026-04-02*
