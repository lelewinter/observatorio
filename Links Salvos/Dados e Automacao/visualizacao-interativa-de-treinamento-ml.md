---
tags: [machine-learning, visualizacao, educacao, gradient-flow, debugging]
source: https://x.com/_vmlops/status/2039297059933786500?s=20
date: 2026-04-02
tipo: aplicacao
---
# Visualização Interativa de Dinâmica de Treinamento ML: Gradientes, Pesos, Fronteiras em Tempo Real

## O que é
Técnica de instrumentação de modelos ML durante treinamento para visualizar em tempo real: (1) magnitude e direção de gradientes em cada layer, (2) evolução de pesos (histogramas + scatter), (3) fronteira de decisão em 2D/3D, (4) loss surface (landscape otimizador). Transforma treinamento de "caixa preta" em processo compreensível e debugável.

## Como implementar

**Arquitetura de Visualização:**

```
Model Training Loop
  ↓
[Hook system]
  ├── Forward pass → capture activations
  ├── Backward pass → capture gradients
  ├── Param update → capture weight deltas
  └── Metrics → loss, accuracy, etc.
  ↓
[Real-time Visualization Engine]
  ├── Gradient flow chart (por layer)
  ├── Weight distribution (histograma)
  ├── Decision boundary (2D/3D)
  ├── Loss surface (heatmap)
  └── Metric curves (loss, acc, val_loss)
  ↓
[Web Dashboard]
  └── Plotly/Matplotlib em browser
```

**Passo 1: Instrumentação com PyTorch Hooks**

```python
import torch
import torch.nn as nn
from collections import defaultdict
import numpy as np

class GradientTracker:
    def __init__(self, model: nn.Module):
        self.model = model
        self.gradients = defaultdict(list)
        self.weights = defaultdict(list)
        self.activations = defaultdict(list)
        self.hooks = []

    def register_hooks(self):
        """Registrar hooks em todas as layers"""
        for name, module in self.model.named_modules():
            if isinstance(module, (nn.Linear, nn.Conv2d)):
                # Hook no forward pass (capture activations)
                def make_forward_hook(layer_name):
                    def forward_hook(module, input, output):
                        self.activations[layer_name].append(output.detach().cpu())
                    return forward_hook

                hook_f = module.register_forward_hook(make_forward_hook(name))
                self.hooks.append(hook_f)

                # Hook no backward pass (capture gradients)
                def make_backward_hook(layer_name):
                    def backward_hook(grad):
                        self.gradients[layer_name].append({
                            'magnitude': torch.norm(grad).item(),
                            'mean': torch.mean(grad).item(),
                            'std': torch.std(grad).item(),
                            'percentiles': np.percentile(grad.cpu().detach().numpy(), [25, 50, 75, 95])
                        })
                        return grad
                    return backward_hook

                if module.weight.requires_grad:
                    hook_b = module.weight.register_hook(make_backward_hook(f"{name}.weight"))
                    self.hooks.append(hook_b)

    def capture_weights(self):
        """Capturar estado de pesos pós-update"""
        for name, param in self.model.named_parameters():
            if param.requires_grad:
                self.weights[name].append({
                    'mean': param.data.mean().item(),
                    'std': param.data.std().item(),
                    'min': param.data.min().item(),
                    'max': param.data.max().item(),
                    'norm': torch.norm(param.data).item()
                })

    def cleanup(self):
        """Remove hooks pra economizar memória"""
        for hook in self.hooks:
            hook.remove()

# Uso
model = nn.Sequential(
    nn.Linear(784, 128),
    nn.ReLU(),
    nn.Linear(128, 64),
    nn.ReLU(),
    nn.Linear(64, 10)
)

tracker = GradientTracker(model)
tracker.register_hooks()

# Treinamento
for epoch in range(10):
    for batch_x, batch_y in train_loader:
        logits = model(batch_x)
        loss = criterion(logits, batch_y)
        loss.backward()
        optimizer.step()

        tracker.capture_weights()

tracker.cleanup()
```

**Passo 2: Visualização de Gradients (Gradient Flow)**

```python
import plotly.graph_objects as go

def plot_gradient_flow(tracker: GradientTracker, epoch: int):
    """Visualizar magnitude de gradientes por layer ao longo do tempo"""
    fig = go.Figure()

    for layer_name in tracker.gradients.keys():
        if len(tracker.gradients[layer_name]) > 0:
            magnitudes = [g['magnitude'] for g in tracker.gradients[layer_name]]
            fig.add_trace(go.Scatter(
                y=magnitudes,
                name=layer_name,
                mode='lines',
                line=dict(width=2)
            ))

    fig.update_layout(
        title=f"Gradient Flow - Epoch {epoch}",
        xaxis_title="Training Step",
        yaxis_title="Gradient Magnitude (L2 norm)",
        yaxis_type="log",
        hovermode="x unified"
    )

    return fig

# Output pra notebook ou salvar HTML
fig = plot_gradient_flow(tracker, epoch=1)
fig.show()
```

**Passo 3: Visualização de Pesos (Weight Distribution)**

```python
def plot_weight_evolution(tracker: GradientTracker):
    """Histograma 3D: layer × step × magnitude"""
    import plotly.express as px

    data_rows = []
    for layer_name, weight_history in tracker.weights.items():
        for step, w_stats in enumerate(weight_history):
            data_rows.append({
                'layer': layer_name,
                'step': step,
                'mean': w_stats['mean'],
                'std': w_stats['std'],
                'norm': w_stats['norm']
            })

    df = pd.DataFrame(data_rows)

    fig = px.line(
        df,
        x='step',
        y='norm',
        color='layer',
        title="Weight Norm Evolution",
        labels={'step': 'Training Step', 'norm': 'L2 Norm'},
        hover_data=['mean', 'std']
    )

    return fig
```

**Passo 4: Visualização de Fronteira de Decisão (2D/3D)**

Para modelos treinados em 2D data (problema pedagogical):

```python
import numpy as np
import matplotlib.pyplot as plt

def plot_decision_boundary_2d(model, X, y, epoch: int, device='cpu'):
    """Plotar fronteira de decisão em 2D após cada época"""
    # Criar mesh grid
    x_min, x_max = X[:, 0].min() - 0.5, X[:, 0].max() + 0.5
    y_min, y_max = X[:, 1].min() - 0.5, X[:, 1].max() + 0.5
    xx, yy = np.meshgrid(np.linspace(x_min, x_max, 200),
                         np.linspace(y_min, y_max, 200))

    # Predict on mesh
    mesh_data = np.c_[xx.ravel(), yy.ravel()]
    mesh_tensor = torch.FloatTensor(mesh_data).to(device)

    with torch.no_grad():
        Z = model(mesh_tensor).argmax(dim=1).cpu().numpy()
    Z = Z.reshape(xx.shape)

    # Plot
    fig, ax = plt.subplots(figsize=(10, 8))

    # Decision boundary
    ax.contourf(xx, yy, Z, alpha=0.4, cmap='RdBu')
    ax.contour(xx, yy, Z, colors='black', linewidths=0.5)

    # Data points
    scatter = ax.scatter(X[:, 0], X[:, 1], c=y, s=50, cmap='RdBu', edgecolors='k')
    ax.set_title(f"Decision Boundary - Epoch {epoch}")
    ax.set_xlabel("Feature 1")
    ax.set_ylabel("Feature 2")

    plt.colorbar(scatter)
    return fig

# Usar em callback durante treinamento
class BoundaryCallback:
    def __init__(self, model, X_test, y_test, output_dir='./boundaries'):
        self.model = model
        self.X_test = X_test
        self.y_test = y_test
        self.output_dir = output_dir

    def on_epoch_end(self, epoch):
        fig = plot_decision_boundary_2d(self.model, self.X_test, self.y_test, epoch)
        fig.savefig(f"{self.output_dir}/boundary_epoch_{epoch:03d}.png", dpi=100)
        plt.close()
```

**Passo 5: Dashboard Interativo (Plotly + Streamlit)**

```python
import streamlit as st
import plotly.graph_objects as go

st.set_page_config(layout="wide")
st.title("ML Training Visualization Dashboard")

# Sidebar
st.sidebar.write("### Training Status")
selected_epoch = st.sidebar.slider("Select Epoch", 0, max_epochs, 0)
selected_layers = st.sidebar.multiselect("Layers to Watch", list(tracker.gradients.keys()))

# Main dashboard
col1, col2 = st.columns(2)

with col1:
    st.subheader("Gradient Flow")
    fig_grad = plot_gradient_flow(tracker, selected_epoch)
    st.plotly_chart(fig_grad, use_container_width=True)

    st.subheader("Weight Norms")
    fig_weights = plot_weight_evolution(tracker)
    st.plotly_chart(fig_weights, use_container_width=True)

with col2:
    st.subheader("Loss Curves")
    fig_loss = go.Figure()
    fig_loss.add_trace(go.Scatter(y=train_losses, name="Train Loss"))
    fig_loss.add_trace(go.Scatter(y=val_losses, name="Val Loss"))
    st.plotly_chart(fig_loss, use_container_width=True)

    st.subheader("Decision Boundary")
    boundary_img = Image.open(f"./boundaries/boundary_epoch_{selected_epoch:03d}.png")
    st.image(boundary_img)

st.subheader("Gradient Statistics")
stats_data = []
for layer in selected_layers:
    if tracker.gradients[layer]:
        latest_grad = tracker.gradients[layer][-1]
        stats_data.append({
            'Layer': layer,
            'Magnitude': latest_grad['magnitude'],
            'Mean': latest_grad['mean'],
            'Std': latest_grad['std']
        })
df_stats = pd.DataFrame(stats_data)
st.dataframe(df_stats)
```

**Passo 6: Detecção Automática de Problemas**

```python
class TrainingHealthMonitor:
    @staticmethod
    def detect_vanishing_gradients(tracker: GradientTracker, threshold: float = 1e-5):
        """Identificar vanishing gradients"""
        issues = []
        for layer_name, grads in tracker.gradients.items():
            if len(grads) > 10:
                recent_mags = [g['magnitude'] for g in grads[-10:]]
                avg_mag = np.mean(recent_mags)
                if avg_mag < threshold:
                    issues.append(f"⚠️ {layer_name}: gradients very small ({avg_mag:.2e})")
        return issues

    @staticmethod
    def detect_exploding_gradients(tracker: GradientTracker, threshold: float = 100):
        """Identificar exploding gradients"""
        issues = []
        for layer_name, grads in tracker.gradients.items():
            if len(grads) > 10:
                recent_mags = [g['magnitude'] for g in grads[-10:]]
                max_mag = np.max(recent_mags)
                if max_mag > threshold:
                    issues.append(f"🔥 {layer_name}: gradients exploding ({max_mag:.2e})")
        return issues

    @staticmethod
    def detect_overfitting(train_losses, val_losses, patience: int = 5):
        """Detectar overfitting (val_loss aumentando enquanto train_loss diminui)"""
        if len(train_losses) < patience or len(val_losses) < patience:
            return []

        recent_train = train_losses[-patience:]
        recent_val = val_losses[-patience:]

        train_trend = np.polyfit(range(patience), recent_train, 1)[0]
        val_trend = np.polyfit(range(patience), recent_val, 1)[0]

        if train_trend < -0.01 and val_trend > 0.01:
            return ["⚠️ Overfitting detected: train loss down, val loss up"]

        return []

# Uso
monitor = TrainingHealthMonitor()
health_issues = []
health_issues.extend(monitor.detect_vanishing_gradients(tracker))
health_issues.extend(monitor.detect_exploding_gradients(tracker))
health_issues.extend(monitor.detect_overfitting(train_losses, val_losses))

if health_issues:
    st.warning("Health Issues Detected:")
    for issue in health_issues:
        st.write(issue)
```

## Stack e requisitos

**Bibliotecas:**
- PyTorch ou TensorFlow (model training)
- Plotly (visualização interativa)
- Streamlit (dashboard)
- Matplotlib (static plots)
- NumPy, Pandas (processamento de dados)

**Infraestrutura:**
- Jupyter notebook ou Streamlit app
- GPU recomendada pra treino mais rápido

**Habilidades:**
- Compreensão de backpropagation e gradientes
- Familiaridade com frameworks ML
- Python + data visualization

## Armadilhas e limitações

**Overhead de Memória:** Registrar todos os gradientes/activations explode RAM. **Mitigação:**
- Limitar frequency (a cada N steps em vez de todo step)
- Ou usar "rolling buffer" (últimas 100 steps apenas)
- Ou usar Gradient Checkpointing (recalcular em vez de armazenar)

**Complexidade com Modelos Grandes:** ViT com 300M params → não cabe em vizualizações simples. **Mitigação:**
- Agrupar por "block" em vez de individual layers
- Usar PCA/t-SNE pra reduzir dimensionalidade

**Interpretação Enganosa:** Visualização bonita ≠ modelo bom. **Mitigação:**
- Sempre validar com métricas de teste
- Visualização é compreensão, não verdade

## Conexões

- [[deteccao-mudanca-anomalia]] - detectar anomalias no treinamento
- [[producao-criativa-como-processo-estatistico]] - otimização iterativa de hiperparâmetros
- [[iteração-produto-feedback]] - feedback loop de melhoria

## Histórico
- 2026-04-02: Nota criada
- 2026-04-02: Nota reescrita e enriquecida pelo pipeline de curadoria
