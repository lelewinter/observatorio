---
tags: []
source: https://x.com/tom_doerr/status/2039142162311369056?s=20
date: 2026-04-02
tipo: aplicacao
---
# Treinar Robô com Imitation Learning via Demonstrações Humanas

## O que é

Framework de aprendizado onde robôs adquirem políticas de controle motor imitando demonstrações humanas (teleoperation ou kinesthetic teaching) sem necessidade de função de recompensa explícita. Suportado por baselines de referência (RoboManipBaselines) para benchmarking e reproducibilidade.

## Como implementar

### Fase 1: Setup de Ambiente

Instale dependências:

```bash
# Clone RoboManipBaselines
git clone https://github.com/isri-aist/RoboManipBaselines
cd RoboManipBaselines
pip install -e .

# Dependências adicionais
pip install torch torchvision torchaudio
pip install dm-control  # ou MuJoCo para simulação
pip install tensorboard wandb
```

### Fase 2: Coletar Demonstrações Humanas

**Método 1: Teleoperation (Controle Remoto)**

```python
# collect_demos_teleop.py
from robomanip_baselines import TeleopCollector
import numpy as np

collector = TeleopCollector(
    robot="ur5",  # UR5, ou outro robot
    task="pick_and_place",
    save_dir="./demonstrations"
)

# Usuário controla robot via joystick/interface
# Sistema registra: observations (camera, joint pos), actions (joint commands), rewards (opcional)
num_demos = 50  # Coleta 50 demonstrações diferentes

for i in range(num_demos):
    print(f"Demo {i+1}/{num_demos} - Pressione Enter para começar...")
    input()

    collector.record_episode(duration_seconds=30)  # Grava 30 segundos

print("Demonstrações salvas em ./demonstrations/")
```

**Método 2: Kinesthetic Teaching (Guiamento Manual)**

```python
# collect_demos_kinesthetic.py
from robomanip_baselines import KinestheticCollector

collector = KinestheticCollector(
    robot="robot_arm",
    task="folding_cloth",
    save_dir="./demonstrations"
)

# Você guia os joints do robô fisicamente
# O sistema aprende a trajetória
for i in range(20):
    print(f"Demo {i+1}/20 - Guie o robô manualmente...")
    collector.record_episode(duration_seconds=20)

print("Trajetórias kinésticas capturadas.")
```

### Fase 3: Escolher Algoritmo de Imitation Learning

**Behavioral Cloning (Mais Simples)**

```python
from robomanip_baselines.algorithms import BehavioralCloning

bc = BehavioralCloning(
    policy_model="transformer",  # ou "cnn", "mlp"
    observation_space=obs_space,
    action_space=act_space,
    learning_rate=1e-4
)

# Treinar em demonstrações coletadas
bc.train(
    demonstrations_dir="./demonstrations",
    epochs=100,
    batch_size=32,
    validation_split=0.2,
    checkpoint_dir="./models/bc"
)

print("Modelo treinado. Testando...")
bc.evaluate(num_episodes=10)
```

**DAgger (Com Feedback de Especialista)**

```python
from robomanip_baselines.algorithms import DAgger

dagger = DAgger(
    base_policy=bc,  # inicia com BC
    expert_policy=expert_teleop,
    observation_space=obs_space,
    action_space=act_space
)

# DAgger itera: política falha, especialista corrige, treina novamente
dagger.train(
    initial_demonstrations="./demonstrations",
    num_dagger_iterations=5,
    episodes_per_iteration=10,
    checkpoint_dir="./models/dagger"
)
```

**Diffusion Policy (Mais Robusto)**

```python
from robomanip_baselines.algorithms import DiffusionPolicy

diffusion = DiffusionPolicy(
    observation_space=obs_space,
    action_space=act_space,
    num_diffusion_steps=50,
    learning_rate=1e-4
)

# Treina política como modelo de difusão (captura multimodalidade de movimentos)
diffusion.train(
    demonstrations_dir="./demonstrations",
    epochs=200,
    batch_size=64,
    checkpoint_dir="./models/diffusion"
)

# Gera ações por iteração de difusão (mais lento, mais robusto)
action = diffusion.predict(observation, num_steps=50)
```

### Fase 4: Deployment no Robô Real

```python
from robomanip_baselines.deployment import RobotDeployer

# Carregue modelo treinado
deployed = RobotDeployer(
    model_path="./models/diffusion/checkpoint_best.pt",
    robot_interface="ur5_driver",  # adaptador específico do robot
    frequency_hz=10  # 10 comandos por segundo
)

# Execute tarefa
success_count = 0
for trial in range(10):
    observation = robot.get_observation()
    success = deployed.execute_task(observation, max_steps=200)
    if success:
        success_count += 1
    print(f"Trial {trial+1}: {'SUCCESS' if success else 'FAILED'}")

print(f"Taxa de sucesso: {success_count}/10")
```

### Fase 5: Avaliação e Benchmarking

```python
from robomanip_baselines import evaluate_policy

results = evaluate_policy(
    policy_path="./models/diffusion/checkpoint_best.pt",
    task="pick_and_place",
    num_episodes=20,
    render=True,
    metrics=["success_rate", "completion_time", "trajectory_smoothness"]
)

print(f"Taxa de sucesso: {results['success_rate']:.1%}")
print(f"Tempo médio: {results['completion_time']:.1f}s")
print(f"Suavidade: {results['trajectory_smoothness']:.2f}")
```

## Stack e requisitos

- **Simulação**: MuJoCo ou Gazebo + ROS
- **Robô**: UR5, Fetch, Panda (qualquer com drivers compatíveis)
- **Coleta**: Camera RGB-D + sistema de teleoperation (joystick ou VR)
- **Treinamento**: GPU com 8GB VRAM (NVIDIA recomendado)
- **Frameworks**: PyTorch, RoboManipBaselines, dm-control
- **Dados**: 20-100 demonstrações por tarefa
- **Tempo**: 2-8 horas treinamento em GPU, tarefas simples; semanas para complexas

## Armadilhas e limitações

1. **Distribuição de Demonstrações**: Se demos são pouco variadas, modelo não generaliza. Coleta 50-100 com variações de ângulo, velocidade, posição inicial.

2. **Distribution Shift**: Modelo aprende da demonstração, mas robô real tem fricção/delays diferentes. DAgger mitiga, mas não elimina.

3. **Behavioral Cloning é Mode-Averaging**: BC tende a "embaralhar" entre múltiplas demonstrações. Diffusion Policy resolve melhor.

4. **Tarefas com Objetos Deformáveis**: IL é excelente, mas objetos como roupas têm infinitas variações. Combine com curriculum learning.

5. **Custo Humano**: Coleta de 50-100 demos leva horas. Explore crowdsourcing ou sim-to-real transfer.

## Conexões

- [[modelo-foundation-para-atividade-neural]] — redes neurais para controle
- [[otimizacao-de-agentes-por-reinforcement-learning]] — RL como alternativa a IL
- [[inferencia-local-de-llms-gigantes]] — executar modelos grandes em edge

## Histórico

- 2026-04-02: Nota criada
- 2026-04-02: Guia prático de implementação

## Exemplos
1. **Behavioral Cloning em linha de montagem**: treinar um robô para encaixar conectores usando ~50 demonstrações humanas via teleoperation, sem programar explicitamente a trajetória.
2. **Diffusion Policy para tarefas domésticas**: dobrar roupas ou manipular objetos deformáveis onde a política multimodal de difusão lida melhor com a variabilidade do movimento humano.
3. **Benchmark comparativo**: usar o RoboManipBaselines para comparar BC vs. ACT vs. Diffusion Policy na mesma tarefa simulada, medindo taxa de sucesso e sensibilidade ao número de demonstrações.

## Relacionado
*(Nenhuma nota existente no vault para linkar neste momento.)*

## Perguntas de Revisão
1. Qual a diferença fundamental entre Behavioral Cloning e DAgger, e por que DAgger mitiga o problema de distribution shift?
2. Por que benchmarks padronizados como o RoboManipBaselines são importantes para a progressão científica em robótica de manipulação?

## Histórico de Atualizações
- 2026-04-02: Nota criada a partir de Telegram