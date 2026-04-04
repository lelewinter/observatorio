---
tags: [conceito, game-design, mecanicas]
date: 2026-04-02
tipo: conceito
aliases: [Core Loop, Loop Central]
---

# Core Loop de Game Design

## O que é
A ação repetida e fundamental que o jogador executa a cada segundo do jogo. É o "batida do coração" do game — sem um core loop satisfatório, não há retenção.

## Como funciona
Todo jogo tem ciclo: jogador vê estado → toma decisão → executa ação → recebe feedback → avança estado. Repetição. Uma vez a cada 2-5 segundos. Se esse ciclo é vazio ou sem consequência, o jogador sai. Se é satisfatório, ele quer repetir infinitamente.

Exemplos de core loops:
- **Roguelike**: ver inimigo → calcular rota → atacar → receber dano/loot → avançar → repeat (2 seg)
- **Puzzle**: ver grade → arrastar peça → validar movimento → animar satisfação → repeat (5 seg)
- **Multiplayer**: rotar câmera → almejar → disparar → feedback visual/audio → repeat (1 seg)

O core loop é *anterior* a progression, monetização ou narrativa. É o alicerce. Se o loop não prende, o resto do jogo não importa.

## Pra que serve
[[Montar Fundação de Design com YouTube Curado]] — entender core loop é o primeiro passo de design.

Criadores indie usam core loop como ferramenta de triagem: se consegue fazer um core loop satisfatório em 2 semanas, o conceito provavelmente vale a pena explorar.

## Exemplo prático
Prototipo em pseudocódigo (Godot/GDScript):

```gdscript
# Core loop de action roguelike
func _process(delta):
    # Ver estado
    var player_pos = global_position
    var enemies = get_visible_enemies()

    # Decisão + execução
    var input_dir = Input.get_vector("ui_left", "ui_right", "ui_up", "ui_down")
    global_position += input_dir * speed * delta

    # Feedback sensorial (criticamente importante)
    if input_dir != Vector2.ZERO:
        play_footstep_sound()
        show_dust_particles()
        update_animation_state(input_dir)

    # Consequência
    for enemy in enemies:
        if distance_to(enemy) < attack_range:
            deal_damage(enemy)
            screen_shake(0.1)
            play_hit_sound()
            gain_blood_splatter_visual()

    # Repeat via _process frame-by-frame
```

## Aparece em
- [[Montar Fundação de Design com YouTube Curado]] - conceito base de game design
- [[12-principios-animacao-disney-funcionam-diferente-em-games]] - feedback sensorial no loop

---
*Conceito extraído em 2026-04-02*
