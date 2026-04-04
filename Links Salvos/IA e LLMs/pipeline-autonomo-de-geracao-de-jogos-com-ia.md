---
tags: []
source: https://x.com/sukh_saroy/status/2036557095273898403?s=20
date: 2026-04-02
tipo: aplicacao
---

# Pipeline Multi-Agente com QA Visual para Projetos Godot 4

## O que é

Sistema autônomo que transforma uma descrição textual em projeto Godot 4 funcional com código, assets 2D/3D e validação visual. Encadeia Claude Code (orquestração), Gemini Vision (geração de arte), Tripo3D (conversão 2D→3D) e feedback visual contínuo.

## Como implementar

**Etapa 1: Orquestração com Claude Code.** Estruture um prompt que instrua Claude a: receber descrição de mecânica, decompor em arquivos GDScript e estrutura de cenas Godot, gerar código de física e comportamento de NPCs, criar árvore de scenes com nomes padronizados. Claude Code escreve diretamente para o filesystem do projeto — `.gd` scripts, `scene.tscn` files, estrutura de pastas conforme padrão Godot.

**Etapa 2: Geração de assets via Gemini.** Após o código, instrua Gemini Vision a: gerar imagens 2D baseadas no tema descrito (character sprites, tilesets, UI backgrounds), criar mapa de cores consistente. Salve outputs em `assets/2d/`. Defina resolução (ex: 128x128 pixels para sprites) e formato (PNG com alpha).

**Etapa 3: Conversão 3D com Tripo3D.** Passe as imagens geradas para Tripo3D com prompt estruturado: converter sprite 2D em modelo 3D, otimizar topology, exportar em `.gltf` (compatível com Godot). Salve em `assets/3d/`. Se jogo é 2D, pule esta etapa; se é 3D ou 2.5D, use Tripo3D.

**Etapa 4: Loop de QA Visual.** Compile o projeto no Godot editor via CLI (`godot --headless project.godot`). Capture screenshot do jogo em execução. Passe screenshot para Gemini Flash com checklist: "Identifique (1) z-fighting ou overlaps visuais, (2) texturas faltantes ou ausentes, (3) física quebrada (objetos flutuando/caindo infinito), (4) HUD ilegível. Para cada problema, liste linha de código responsável."

**Etapa 5: Correção autônoma.** Claude Code recebe relatório de QA, identifica linhas problemáticas, executa edições diretas nos scripts `.gd`, recompila, e re-passa para QA. Loop até zero problemas visuais.

**Integração prática.** Configure como GitHub Actions (se repositório público) ou scheduled script em Windows Task Scheduler (se local). Trigger: nova descrição em comentário de issue ou webhook em webhook.json.

## Stack e requisitos

- Godot 4.x (instalado e em PATH)
- Claude Code com acesso a filesystem
- Gemini 2.0 Flash Vision API + Tripo3D API (credenciais)
- VRAM: 6GB+ (Gemini local) ou cloud APIs
- Tempo end-to-end: 5-15 minutos por projeto pequeno
- Custo: ~$0.20-0.50 por ciclo QA (Gemini Vision + Tripo3D)

## Armadilhas e limitações

QA visual não detecta bugs lógicos (ex: colisão não funiona mas visualmente parece OK). Gemini pode gerar assets visualmente coerentes mas com paleta de cores repetitiva. Tripo3D é fraco em detalhe fino — bom para protótipos, não production-ready. Screenshots em baixa resolução prejudicam detecção de problemas pequenos. Timeout em compilação Godot sem headless display requer setup X11/Xvfb em Linux.

## Conexões

[[Vibe Coding para Desenvolvimento de Jogos]], [[Sistemas Multi-Agente para Engenharia de Software]], [[Unity-MCP Integração LLM com Game Engine]]

## Histórico

- 2026-04-02: Nota criada
- 2026-04-02: Reescrita como guia de implementação