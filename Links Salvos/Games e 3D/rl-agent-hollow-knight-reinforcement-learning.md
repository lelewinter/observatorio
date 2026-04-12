---
tags: [reinforcement-learning, games, hollow-knight, agente-autonomo, pytorch, gymnasium, stable-baselines3]
source: https://github.com/seermer/HollowKnight_RL
date: 2026-04-11
tipo: aplicacao
---
# RL Agent para Hollow Knight: Treinando Agentes Autônomos em Ambientes Visuais Complexos

## O que é

Treinar agentes de reinforcement learning (RL) para jogar Hollow Knight é um projeto de ponta que combina visão computacional, engenharia de reward shaping e deep learning. Diferentemente de jogos com estados simples (como Atari clássico), Hollow Knight é um metroidvania 2D com dinâmicas complexas: o agente precisa aprender não apenas a se mover, mas também a reconhecer inimigos, gerenciar recursos (vida, soul, charms) e derrotar bosses com padrões de ataque sofisticados.

Um agente RL bem treinado em Hollow Knight consegue aprender políticas de comportamento que emergem da interação com o ambiente, sem programação explícita de estratégias. Isso envolve capturar frames do jogo em tempo real, extrair features relevantes usando object detection (YOLO), calcular rewards estruturados que guiam o aprendizado, e iterar treinos usando algoritmos como PPO, A3C ou DQN.

A relevância prática é enorme: esse tipo de agente serve como prototipo para automação em ambientes visuais mais complexos (robótica, simulação industrial, jogos comerciais), e o Hollow Knight é um benchmark excelente porque combina dificuldade real com determinismo (diferentemente de ambientes estocásticos puros).

## Como implementar

### Passo 1: Configurar o Ambiente e Dependências

```bash
# Criar ambiente virtual Python
python -m venv hollow_rl_env
source hollow_rl_env/bin/activate  # Linux/Mac: source, Windows: hollow_rl_env\Scripts\activate

# Instalar dependências principais
pip install gymnasium stable-baselines3 torch torchvision opencv-python numpy pandas matplotlib tensorboard

# Para versões específicas (estáveis em 2026)
pip install gymnasium==0.29.0
pip install stable-baselines3==2.3.0
pip install torch==2.1.0 torchvision==0.16.0
pip install opencv-python==4.8.0
pip install pyyaml requests
```

### Passo 2: Criar um Wrapper Gymnasium para Hollow Knight

```python
import gymnasium as gym
from gymnasium import spaces
import numpy as np
import cv2
from mss import mss
import time

class HollowKnightEnv(gym.Env):
    """
    Ambiente Gymnasium customizado para Hollow Knight.
    Captura frames da tela, processa e retorna estados para o agente.
    """
    
    def __init__(self, game_window_region=None, frame_skip=4):
        super().__init__()
        
        # Se region não for especificada, usar área padrão do game
        self.game_window_region = game_window_region or {
            'top': 100, 'left': 100, 'width': 1280, 'height': 720
        }
        self.frame_skip = frame_skip
        self.sct = mss()
        
        # Action space: 7 ações discretas
        # 0: nada, 1: esq, 2: dir, 3: pulo, 4: esq+pulo, 5: dir+pulo, 6: ataque
        self.action_space = spaces.Discrete(7)
        
        # Observation space: frames redimensionados 84x84 (como Atari)
        self.observation_space = spaces.Box(
            low=0, high=255, 
            shape=(84, 84, 1),  # Escala de cinza
            dtype=np.uint8
        )
        
        self.episode_rewards = 0
        self.steps = 0
        self.max_steps = 10000
        
    def _capture_frame(self):
        """Captura frame da tela e redimensiona para 84x84."""
        screenshot = self.sct.grab(self.game_window_region)
        frame = np.array(screenshot)
        # Converter BGR para escala de cinza
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        # Redimensionar para 84x84
        resized = cv2.resize(gray, (84, 84))
        return np.expand_dims(resized, axis=2)
    
    def _get_reward(self, game_state):
        """
        Calcular reward baseado em observações de game state.
        Isso requer integração com detecção de objeto/OCR para ler game info.
        """
        reward = 0
        
        # Exemplo de reward shaping (requer mod/API do jogo):
        # - Health aumentado: +1
        # - Inimigo derrotado: +10
        # - Boss health reduzido: +5 * (dano / boss_max_health)
        # - Dano tomado: -2
        # - Caiu em pico: -5
        
        return reward
    
    def _send_action(self, action):
        """Enviar input para o jogo usando pyautogui ou hook de input."""
        import pyautogui
        
        key_map = {
            0: None,           # nada
            1: 'a',            # esquerda
            2: 'd',            # direita
            3: 'w',            # pulo
            4: ['a', 'w'],     # esq + pulo
            5: ['d', 'w'],     # dir + pulo
            6: 'z'             # ataque
        }
        
        keys = key_map[action]
        if keys:
            if isinstance(keys, list):
                for key in keys:
                    pyautogui.press(key)
            else:
                pyautogui.press(keys)
    
    def step(self, action):
        """Executar um passo da simulação."""
        # Repetir ação frame_skip vezes
        total_reward = 0
        for _ in range(self.frame_skip):
            self._send_action(action)
            time.sleep(0.016)  # ~60 FPS
        
        # Capturar novo frame
        observation = self._capture_frame()
        
        # Calcular reward (integração com game state)
        reward = self._get_reward(None)  # Implementar extração real de state
        total_reward += reward
        
        self.episode_rewards += total_reward
        self.steps += 1
        
        # Verificar terminação
        done = self.steps >= self.max_steps
        truncated = False
        
        return observation, total_reward, done, truncated, {}
    
    def reset(self, seed=None):
        """Reset do ambiente."""
        super().reset(seed=seed)
        
        self.episode_rewards = 0
        self.steps = 0
        
        # Enviar input para restart (menu do jogo)
        import pyautogui
        pyautogui.press('r')
        time.sleep(2)
        
        observation = self._capture_frame()
        return observation, {}
    
    def close(self):
        """Cleanup."""
        pass
```

### Passo 3: Treinar o Agente com Stable Baselines3

```python
from stable_baselines3 import PPO, DQN
from stable_baselines3.common.vec_env import DummyVecEnv
from stable_baselines3.common.callbacks import CheckpointCallback
import os

# Criar ambiente
env = HollowKnightEnv()
env = DummyVecEnv([lambda: env])

# Callbacks para salvar checkpoints
checkpoint_callback = CheckpointCallback(
    save_freq=50000,
    save_path="./models/",
    name_prefix="hollow_knight_ppo"
)

# Treinar agente PPO (Policy Gradient, recomendado para visão)
model = PPO(
    "CnnPolicy",  # CNN para processar imagens
    env,
    learning_rate=2.5e-4,
    n_steps=2048,
    batch_size=64,
    n_epochs=10,
    gamma=0.99,
    gae_lambda=0.95,
    clip_range=0.2,
    verbose=1,
    tensorboard_log="./logs/"
)

# Treinar por 1 milhão de timesteps
model.learn(
    total_timesteps=1_000_000,
    callback=checkpoint_callback,
    tb_log_name="ppo_hollow_knight"
)

# Salvar modelo final
model.save("hollow_knight_ppo_final")
```

### Passo 4: Avaliação e Visualização

```python
from stable_baselines3.common.evaluation import evaluate_policy
import matplotlib.pyplot as plt

# Carregar modelo treinado
model = PPO.load("hollow_knight_ppo_final")

# Avaliar performance
mean_reward, std_reward = evaluate_policy(
    model, 
    env, 
    n_eval_episodes=10,
    deterministic=True
)

print(f"Mean Reward: {mean_reward:.2f} +/- {std_reward:.2f}")

# Visualizar episódio
obs, _ = env.reset()
total_reward = 0
for _ in range(500):
    action, _states = model.predict(obs, deterministic=True)
    obs, reward, done, truncated, info = env.step(action)
    total_reward += reward
    
    if done or truncated:
        print(f"Episode finished with total reward: {total_reward}")
        break
```

### Passo 5: Implementar Reward Shaping Avançada

```python
class HollowKnightRewardShaper:
    """
    Shaper de rewards baseado em detecção de estado do jogo.
    Integra-se com YOLO ou OCR para ler informações vitais.
    """
    
    def __init__(self):
        self.prev_health = 9  # Health máximo
        self.prev_enemies_alive = 0
        self.prev_boss_health = 1.0
    
    def shape_reward(self, detection_results):
        """
        Detection_results: dict com {
            'player_health': int,
            'enemy_count': int,
            'boss_health_ratio': float,
            'items_collected': bool,
            'damage_taken': int
        }
        """
        reward = 0.0
        
        # Bonus por derrotar inimigos
        enemy_diff = self.prev_enemies_alive - detection_results['enemy_count']
        if enemy_diff > 0:
            reward += 10.0 * enemy_diff
        
        # Penalty por dano tomado
        health_loss = self.prev_health - detection_results['player_health']
        if health_loss > 0:
            reward -= 2.0 * health_loss
        
        # Bonus por progredir contra boss
        boss_damage = self.prev_boss_health - detection_results['boss_health_ratio']
        if boss_damage > 0:
            reward += 5.0 * boss_damage
        
        # Bonus por itens
        if detection_results['items_collected']:
            reward += 1.0
        
        # Update estado anterior
        self.prev_health = detection_results['player_health']
        self.prev_enemies_alive = detection_results['enemy_count']
        self.prev_boss_health = detection_results['boss_health_ratio']
        
        return reward
```

### Passo 6: Configurar Game Mods (Recomendado)

Para leitura mais confiável de game state, instalar mods do Hollow Knight:

```
- EnemyHPBar mod: mostra vida de inimigos em tela
- Satchel: permite ler status de items via OCR
- Debug console: acessar dados de jogo via API
```

## Stack e requisitos

### Dependências Críticas

| Componente | Versão | Custo |
|-----------|--------|------|
| Python | 3.10+ | Grátis |
| Gymnasium | 0.29.0+ | Grátis (OpenAI) |
| Stable Baselines3 | 2.3.0+ | Grátis (DLR-RM) |
| PyTorch | 2.1.0+ | Grátis (Meta/Linux Fundation) |
| OpenCV | 4.8.0+ | Grátis |
| Hollow Knight | Qualquer versão | ~15 EUR (Steam) |

### Hardware Recomendado

- **GPU**: NVIDIA RTX 3060+ (mínimo) ou RTX 4090 (ideal para treino de 1M+ timesteps)
- **CPU**: Ryzen 5 5600X ou Intel i7-12700K
- **RAM**: 16GB mínimo, 32GB recomendado
- **Storage**: 500GB para checkpoints + logs + modelos

### Tempo de Treino

- Baseline (100k timesteps): 2-4 horas em GPU
- Produção (1M timesteps): 20-40 horas em GPU RTX 3060
- Treino de boss específico: 5-10 horas

### Custo Mensal (se usar cloud)

- Google Colab Pro: ~13 EUR/mês (GPU T4 compartilhada)
- Paperspace Gradient: ~15-30 EUR/mês (A100 40GB)
- AWS EC2 p3.2xlarge: ~24.48 EUR/hora (V100 GPU)

## Armadilhas e limitações

### 1. Sparse Rewards e Exploration

**Problema**: Sem reward shaping cuidadosa, o agente recebe rewards muito espaçados (só ao derrotar boss ou coletar item), dificultando aprendizado.

**Solução**: Implementar reward shaping intermediária:
- +0.1 por movimento em direção ao objetivo
- +1.0 por ataque bem-sucedido
- -0.01 por step (incentiva terminar rápido)
- +10 por derrotar inimigo

**Implementação**:
```python
# Usar classe RewardShaper acima, integrada ao step()
reward = self.reward_shaper.shape_reward(current_state)
```

### 2. Processamento de Frames e Latência

**Problema**: Capturar frames via screenshot (~16ms), processar CNN (~50ms), executar ação (~32ms) = 100ms de latência. O jogo roda a 60 FPS (16.6ms por frame). Isso cria lag perceptível.

**Solução**: 
- Use frame skipping agressivo (4-8 frames)
- Offload capture para thread separada
- Cache frames processados

```python
import threading
import queue

class FrameCapture:
    def __init__(self):
        self.queue = queue.Queue(maxsize=2)
        self.thread = threading.Thread(target=self._capture_loop, daemon=True)
        self.thread.start()
    
    def _capture_loop(self):
        while True:
            frame = self._capture_frame()
            try:
                self.queue.put_nowait(frame)
            except queue.Full:
                pass
    
    def get_latest_frame(self):
        try:
            return self.queue.get_nowait()
        except queue.Empty:
            return None
```

### 3. Generalização entre Bosses

**Problema**: Um agente treinado em King's Brand pode falhar em Hornet Sentinela porque padrões de ataque são totalmente diferentes. Overfitting em um boss é comum.

**Solução**: 
- Treinar em múltiplos bosses simultaneamente (curriculum learning)
- Usar transfer learning: fine-tune modelo genérico em boss específico
- Data augmentation: variar seed aleatório, configs de charm

```python
# Curriculum learning: começar com boss fácil, subir dificuldade
bosses = ['Gruz Mother', 'Hive Knight', 'Absolute Radiance']
for boss in bosses:
    env.set_boss(boss)
    model.learn(200_000)
    model.save(f"model_{boss}")
```

### 4. Determinismo vs Estocasticidade do Jogo

**Problema**: Hollow Knight tem RNG mínimo, mas Hollow Knight: Silksong pode ter. Determinismo absoluto facilita overfitting a seeds específicas.

**Solução**: Adicionar stochasticity artificial:
```python
def add_noise_to_state(state, noise_level=0.01):
    noise = np.random.normal(0, noise_level, state.shape)
    return np.clip(state + noise, 0, 255)
```

### 5. Segmentação de Inimigos e Bosses

**Problema**: Detectar inimigos via YOLO é complexo em Hollow Knight porque:
- Muitos inimigos pequenos na tela ao mesmo tempo
- Animações rápidas (blur motion)
- Backgrounds que confundem detector

**Solução**: Usar Roboflow dataset pré-treinado em Hollow Knight:
```python
# Download dataset do Roboflow
from roboflow import Roboflow
rf = Roboflow(api_key="seu_api_key")
project = rf.workspace("hollow-knight-dataset").project("hollow-knight")
dataset = project.download("yolov8", location="./hk_dataset")

# Fine-tune YOLOv8 em seu subset de bosses
from ultralytics import YOLO
model = YOLO('yolov8n.pt')
results = model.train(data='./hk_dataset/data.yaml', epochs=50, imgsz=416)
```

## Conexoes

[[Reinforcement Learning - Conceitos Fundamentais|Deep Q-Networks e Policy Gradients (PPO, A3C)]]
[[Gymnasium Environment API|Framework para criar ambientes RL customizados]]
[[Vision-Based RL|Usar CNNs para processar observações visuais]]
[[Hollow Knight Speedrun Strategies|Contexto: movimentos ótimos que um agente poderia aprender]]
[[Object Detection com YOLO|Extrair estado do jogo em tempo real]]
[[Reward Shaping Engineering|Técnica crítica para RL em ambientes complexos]]

## Historico

- 2026-04-11: Nota criada com stack completo Gymnasium + Stable Baselines3 + PyTorch
- Baseado em projeto ativo: https://github.com/seermer/HollowKnight_RL
- Referências de reward shaping: https://theses.liacs.nl/2727 (Universidade de Leiden, 2022-2023)
