---
tags: [game-dev, youtube, recursos, aprendizado, solo-dev, design]
source: https://www.linkedin.com/feed/update/urn:li:activity:7392516229577592832/
date: 2026-03-28
tipo: aplicacao
---

# Montar Fundação de Design com YouTube Curado para Solo Devs

## O que é

Uma curadoria estratégica de 10 canais do YouTube focados em game design conceitual, retenção de jogadores e arquitetura de sistemas. Subststitui cursos genéricos que ensinam ferramentas (tooling) pela base teórica que sustenta todos os grandes jogos: o **core loop**. Leticia vai de consumidor passivo de vídeos para implementador ativo de conceitos de design.

## Por que importa agora

O gargalo de solo devs não é conhecimento técnico — é falta de fundação em design. Qualquer um consegue seguir um tutorial de Godot, mas poucos conseguem estruturar um jogo que mantém o jogador voltando. YouTube tem curadores especializados que decompõem hits de mercado (Hollow Knight, Celeste, Fortnite, Genshin) e explicam **por que funcionam**, não apenas como foram feitos. Essa curadoria economiza meses de tentativa-e-erro.

## Como implementar

### Fase Zero: Core Loop (2-3 semanas)

Antes de prototipar qualquer coisa, comece com a **espinha dorsal** de todo jogo: o loop de ação que repete a cada 3-10 segundos.

**Defina:** Qual é a ação principal repetida?
- Atirar (Hades)
- Pular e lançar gancho (Hollow Knight)
- Construir estrutura (Fortnite)

**Estruture no papel:**
```
Input → Ação → Feedback → Recompensa → Loop (10s)
```

Assista sequencialmente a playlists sobre "The Real Core Loop", "10 Second Loop" ou similar. Alguns canais excelentes:
- **Game Maker's Toolkit** — Lucas Pope, decompõe mecânicas fundamentais
- **Brackeys** (ainda acessível em archive) — core loops estruturados
- **Extra Credits** — design patterns em grandes clássicos

**Exercício prático:** Escolha um jogo que você ama. Mapeie seu core loop em 1 minuto de gameplay no papel (desenho). Qual é o loop? Quanto tempo leva? Como o jogo o torna "viciante"?

### Fase Um: Progression Systems (3-4 semanas)

Após core loop robusto, construa a **pirâmide de progressão** que transforma vitórias pequenas em objetivos maiores.

**Estrutura típica:**
```
Sessão (1 vitória = 2 minutos)
    ↓ 5 sessões
Desafio Diário (Meta curta, 15 min)
    ↓ 7 dias
Checkpoint Semanal (Boss, recompensa, 1 hora)
    ↓ 4 semanas
Temporada / Ato (narrativo ou cosmético)
```

**Vídeos chave:** GDC talks sobre "progression design", "battle passes que não exploram", "cosmetics como storytelling".

**Exemplo código Godot 4** (GDScript):
```gdscript
# daily_challenge.gd
extends Node

var current_streak: int = 0
var daily_reward_multiplier: float = 1.0

func complete_core_loop() -> void:
    current_streak += 1
    daily_reward_multiplier = 1.0 + (current_streak * 0.1)  # +10% per day
    
    var xp_earned = 100 * daily_reward_multiplier
    emit_signal("progression_updated", {
        "streak": current_streak,
        "next_milestone": ceil(current_streak / 7) * 7,
        "xp": xp_earned
    })
    
    # Reset daily challenge at midnight UTC
    var time_until_reset = _seconds_until_midnight()
    get_tree().create_timer(time_until_reset).timeout.connect(reset_daily)

func _seconds_until_midnight() -> float:
    var now = Time.get_ticks_msec() / 1000.0
    var seconds_today = int(now) % 86400
    return float(86400 - seconds_today)
```

### Fase Dois: Juiciness e Game Feel (3-4 semanas)

A diferença entre um clique sem resposta e um clique que faz o jogador se sentir **poderoso**. Juiciness = feedback sensorial (animação + som + partículas).

**Leitura visual:**
- Screenshake no impacto (1-2 frames, 2-3 pixels)
- Animação de sprite (mesmo que apenas 2 frames, faz diferença)
- Partículas no alvo (explosão, brilho, dust)

**Código de screenshake (Godot):**
```gdscript
# camera_shake.gd
extends Camera2D

func add_trauma(intensity: float) -> void:
    var trauma = clamp(trauma + intensity, 0.0, 1.0)
    
    _update_shake()

func _update_shake() -> void:
    var shake_x = randf_range(-trauma * 5, trauma * 5)
    var shake_y = randf_range(-trauma * 3, trauma * 3)
    
    offset = Vector2(shake_x, shake_y)
    trauma = max(trauma - 0.02, 0.0)  # Decay
    
    if trauma > 0.0:
        get_tree().root.call_deferred("_update_shake")
```

**Vídeos:** Procure "juiciness game design", "game feel", "polish in game dev". Ver antes/depois de um jogo com e sem feedback é revolucionário.

### Fase Três: Monetization Fundamentals (2-3 semanas)

Entenda monetização **do ponto de vista do player**, não de extração. Os melhores indies monetizam por **confiança**, não predação.

**Modelos estudados:**
- **Cosmetics (skins, emotes):** Zerar incentivos competitivos (nunca pay-to-win)
- **Battle Pass:** Recompensa grinders, mas limite FOMO (nunca "desaparece" o conteúdo)
- **Early Access:** Transparência sobre roadmap, envolva comunidade
- **No ads / No P2W:** Cultura de jogo respeitoso (Hollow Knight, Celeste)

**Verificação:** Você pagaria por cosmetic do seu próprio jogo? Se não, redesenhe.

### Fase Quatro: Marketing Solo Dev (2-3 semanas)

**Você é produto + criador.** Sua jornada dev é mais valiosa que o jogo terminado.

**Tática:**
- Thread semanal no Twitter: progresso visual (GIF), aprendizado (1 lição de design), comunidade
- Comunidade: itch.io, IndieDB, Discord dev communities
- Feedback loop: você publica progress, comunidade critica, você itera

**Exemplo thread:**
```
🧵 Dev log #47: Como core loop muda tudo

Semana passada: jogo "perfeito" mas 3 playtesters sairam em 2 min.
Problema: loop de 30s + muito downtime.

Refiz para 8s:
  - Ação principal (atirar): 2s
  - Recarregar + animar: 3s
  - Resultado visual: 3s

Resultado: 10x mais retentivo.

Lição: não é sobre "mais features". É sobre refinar
a coisa que você já tem até ficar viciante.

Qual é o core loop do seu jogo?
```

## Stack e requisitos

- **YouTube Premium:** Não (gratuito, mas sem ads ajuda)
- **Engine:** Godot 4 (free), Unreal Engine 5 (free tier), Unity (free tier)
- **Papel + caneta:** Diagramas e mapeamentos são muito mais rápidos que textos
- **Comunidade:** Discord (dev communities), Twitter/X (indie ecosystem), itch.io (feedback)
- **Ferramentas auxiliares:**
  - Aseprite ou Krita (pixel art / design)
  - FMOD ou Wwise (design de som, opcional)
  - Figma (UI/UX antes de code)

## Código prático: Estrutura básica de retenção

```gdscript
# retention_tracker.gd
extends Node

class RewardSchedule:
    var minutes_between: int
    var xp_amount: int
    var name: String
    
    func _init(mins: int, xp: int, label: String) -> void:
        minutes_between = mins
        xp_amount = xp
        name = label

var reward_schedule = [
    RewardSchedule.new(1, 10, "First Tick"),
    RewardSchedule.new(5, 50, "5 Min Milestone"),
    RewardSchedule.new(10, 100, "10 Min Milestone"),
    RewardSchedule.new(30, 300, "Half Hour"),
]

var session_timer: float = 0.0
var current_schedule_idx: int = 0

func _process(delta: float) -> void:
    session_timer += delta
    
    if current_schedule_idx < reward_schedule.size():
        var next_reward = reward_schedule[current_schedule_idx]
        var seconds_needed = next_reward.minutes_between * 60
        
        if session_timer >= seconds_needed:
            _grant_reward(next_reward)
            current_schedule_idx += 1

func _grant_reward(reward: RewardSchedule) -> void:
    emit_signal("reward_granted", reward.name, reward.xp_amount)
    # Play celebration animation, sound, particle effect
```

## Armadilhas e limitações

**1. Consumir vídeo sem implementar = ilusão de conhecimento.** Você assiste 10 vídeos sobre core loops e sente que "entendeu", mas nunca testou um. Regra: a cada 2-3 vídeos, pause e implemente 1 protótipo testável — mesmo que trivial (clique → recompensa visual). A implementação quebra a ilusão.

**2. Canais raramente cobrem finanças e publicação.** YouTube ensina design, não negócio. Ninguém fala sobre:
- Contatos comerciais (estúdios, publishers indie)
- Impostos em diferentes países (royalties Steam, App Store)
- Suporte pós-lançamento (bug fixes, DLC roadmap)
- Mediação de comunidade tóxica

**3. Solo dev ainda precisa de Arte, Código, Projeto.** Esses vídeos cobrem design conceitual mas você continua precisando saber:
- Animação (não é automático)
- Programação (não está no vídeo)
- Arte visual consistente (design não é pixelart)
- Audio design (efeitos + música diferem)

Se você não consegue fazer nenhuma dessas 4 coisas sozinho, vai travar. Comece com escopo micro (ex: jogo 2D, sem art 3D, sem música original).

**4. Hype ciclos de tecnologia podem desviar seu foco.** YouTube em 2026 está cheio de "melhor engine 2026" e "IA vai gerar seu jogo". Resista. Escolha uma engine e aprenda design com ela até dominá-la. Trocar de ferramenta no meio do projeto é armadilha garantida de solo devs.

**5. Métrica enganosa: quantidade de horas.** Você assiste 50 horas de vídeo e sente que fez 50 horas de trabalho. Não fez. Metáfora: assistir 50 horas de vídeo sobre natação não te torna nadador. Regra: a cada hora de vídeo, dedique 2 horas de implementação.

## Conexões

- [[core-loop-game-design]] — Aprofundar em loops e feedback
- [[ferramentas-prototipagem-game-designers-sem-codigo]] — Se código não é sua força
- [[12-principios-animacao-disney-funcionam-diferente-em-games]] — Juiciness em prática
- [[retention-mechanics-players]] — Economia de recompensas
- [[monetizacao-indie-games]] — Modelos sustentáveis

## Histórico

- 2026-03-28: Nota criada (Sergei Vasiuk LinkedIn)
- 2026-04-02: Reescrita para aplicação prática
- 2026-04-11: Expandida com código Godot 4, estrutura de fases, armadilhas específicas
