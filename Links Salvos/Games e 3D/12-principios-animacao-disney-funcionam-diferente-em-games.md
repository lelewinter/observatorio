---
tags: [game-design, animacao, principios-disney, game-feel, interacao]
source: https://www.linkedin.com/feed/update/urn:li:activity:7441800955865759745/
date: 2026-03-28
tipo: aplicacao
---

# Aplicar Princípios Disney em Game Animation

## O que é
Os 12 princípios de animação Disney funcionam em games, mas com lógica invertida: em filmes, animação serve o diretor; em games, serve o jogador e sua resposta em tempo real.

## Como implementar
**Mapeamento dos 12 princípios para game context**:

1. **Squash & Stretch**
   - Filme: caricatura exagerada (corpo deforma 50%)
   - Game: feedback de impacto rápido (deforma 10-15%, 50ms max)
   - Exemplo: personagem salta e comprime no pouso, depois se expande
   - Unreal Blueprint: `World Offset` via sine wave, amortecido

2. **Anticipation**
   - Filme: pré-aviso do movimento (50-100ms)
   - Game: "coyote time" — tolera pulo até 100ms após sair plataforma
   - Problema: anticipation longa bloqueia input do jogador
   - Solução: máximo 30-50ms em action games, 200ms+ em puzzle

3. **Staging**
   - Filme: dirigir olhar da câmera
   - Game: usar luz, som e partículas simultaneamente
   - Exemplo: inimigo brilha antes de atacar + som de alerta

4. **Timing**
   - Filme: fixo (24/30 fps constante)
   - Game: adaptativo (15-120 fps, variável)
   - Solução: usar `Time.deltaTime` (Godot, Unity) para frame-rate independence

```gdscript
# Godot exemplo: aplicar squash ao pouso
var fall_velocity = 0.0

func _process(delta):
    fall_velocity += gravity * delta
    global_position.y += fall_velocity * delta

    # Squash on ground
    if is_on_floor():
        squash_scale = lerp(1.0, 0.85, 0.15)  # Compress 15%
        scale.y = squash_scale
        fall_velocity = 0

    # Stretch on jump
    if Input.is_action_pressed("jump") and is_on_floor():
        squash_scale = 1.15
        fall_velocity = -jump_force
```

5. **Follow Through**
   - Filme: cabo segue o movimento do corpo
   - Game: "ragdoll follow" interrompível sem travamento
   - Exemplo: capa de personagem continua balançando 200ms após movimento parar

6. **Arcs**
   - Filme: trajetória suave (spline Bezier)
   - Game: arco interrompível por input
   - Solução: animar via `AnimationPlayer` com curvas personalizadas

7. **Secondary Action**
   - Filme: braços batem enquanto corre
   - Game: gerenciar via **animation layers** (base movement + adicional)
   - Unreal: use blend spaces para combinar movimento + secondary

8. **Overlapping Action**
   - Filme: partes do corpo terminam em tempos diferentes
   - Game: essencial para feedback — pernas param, torso continua

9. **Slow In/Out**
   - Filme: easing curves suave
   - Game: crítico para "juiciness" — hit feedback usa ease-out rápido

```gdscript
# Ease-out para hit reaction (210ms)
var elapsed = 0.0
func apply_hit_reaction():
    elapsed = 0.0
    while elapsed < 0.21:
        var t = elapsed / 0.21  # 0-1
        var eased = 1.0 - pow(1.0 - t, 3)  # Ease-out cubic
        scale = Vector3.ONE.lerp(Vector3(1.1, 0.9, 1.0), eased)
        await get_tree().process_frame
        elapsed += get_process_delta_time()
```

10. **Exaggeration**
    - Filme: expressão extrema
    - Game: apenas em feedback crítico (damage taken, level complete)

11. **Solid Drawing**
    - Filme: anatomia correta
    - Game: menos crítico se gameplay é claro

12. **Appeal**
    - Filme: personagem carismático
    - Game: mesmo princípio, mas através do game feel (responsividade + feedback)

## Stack e requisitos
- **Engine**: Unreal 5 (Anim Blueprints + Blend Spaces), Godot 4 (AnimationPlayer + custom tweens), Unity (Animator + Cinemachine)
- **Ferramentas**: Blender (preview animation), Spline (animatic tests)
- **Framework conceitual**: [[core-loop-game-design]] precisa validar que "feel" está bom
- **Tempo aprendizado**: 2-4 semanas praticar, 2-3 meses dominar

## Armadilhas e limitações
- **Timing fixo falha em variável framerates**: sempre usar `deltaTime`
- **Anticipation longa frustra**: players esperam responsividade <50ms
- **Follow-through exagerada quebra pacing**: manter a <300ms
- **Layer complexity explode**: > 3 animation layers = confuso, hard to debug
- **Budget de animação**: AAA film tem 1 animator/personagem; indie tem 1 para 10
- **Rerigging é custoso**: mudar proporção afeta todas as animações existentes

## Conexões
- [[core-loop-game-design]]
- [[game-feel-juiciness]]
- [[animation-blending-layer-system]]
- [[movimento-responsivo-input]]

## Histórico
- 2026-03-28: Nota criada (Sergei Vasiuk)
- 2026-04-02: Reescrita para implementação técnica em engines
