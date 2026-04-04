---
tags: [game-dev, recursos-curados, engines, ferramentas, github, awesome-list]
source: https://x.com/tom_doerr/status/2038215533431066669?s=20
date: 2026-04-02
tipo: aplicacao
---

# Usar listas curadas GitHub como roadmap de ferramentas game dev

## O que é
Repositórios "awesome-list" consolidam ferramentas validadas pela comunidade em estrutura categórica: engines, assets, áudio, shaders, publicação. GameDev-Resources (github.com/Kavex) é referência com 4.5K stars + 91 contribuidores. Funciona como mapa do ecossistema: o que existe, qual é state-of-the-art, onde procurar.

## Como implementar

**Usar lista como checklist de pipeline:**

```markdown
# Game Dev Pipeline Checklist (baseado em awesome-list)

## 1. Engine
- [ ] Escolhida: _______________
- [ ] Versão instalada: _______________
- [ ] Tutorial inicial completado: _______________

Opções verificadas (awesome-list):
- Godot 4.x (2D+3D, open-source)
- Unity 2023+ (massive ecosystem)
- Unreal 5.x (AAA-grade)
- Raylib (minimalist, C)
- Bevy (Rust, experimental)

## 2. Pixel Art / Sprite
- [ ] Editor escolhido: _______________
- [ ] Assets pack baixado: _______________

Opções da awesome-list:
- Aseprite ($20, pay-what-you-want)
- PiskelApp (free, web)
- PyxelEdit ($10)
- OpenGameArt.org (assets free)
- Kenney.nl (assets high quality)

## 3. Tile Maps & Level Design
- [ ] Ferramenta: _______________
- [ ] Primeiros 3 levels criados: _______________

Recomendadas:
- Tiled (free, standard)
- OGMO Editor (free)
- Crocotile 3D (voxel-based)

## 4. 3D Modeling (se 3D)
- [ ] Ferramenta: _______________
- [ ] Primeiro asset criado: _______________

Free (awesome-list):
- Blender (industry standard, learning curve steep)
- Godot (editor integrado básico)

Pago:
- Maya (student $0)
- 3DS Max (student $0)

## 5. Audio
- [ ] Efeitos sonoros: _______________
- [ ] Música: _______________
- [ ] Voice lines: _______________

Ferramentas:
- Audacity (recording, editing)
- LMMS (music composition)
- FamiTracker (chiptune)
- Freesound.org (samples)
- OpenGameArt (royalty-free)

## 6. Shader / VFX
- [ ] Shader editor: _______________
- [ ] Shaders customizados: _______________

Repositórios (awesome-list):
- Shader Toy (web-based)
- Geeks3D Shader Resources
- LibGDX Shader examples

## 7. Physics & Collision
- [ ] Engine nativa (Godot, Unity)
- OU
- [ ] Biblioteca externa:

Opções:
- Box2D (2D, C++)
- Chipmunk (2D)
- Rapier (Rust)

## 8. Publicação
- [ ] Platform escolhida: _______________
- [ ] Build testado: _______________

Opções recomendadas:
- Steam (maior audience, mas competitive)
- itch.io (indie-friendly, royalties)
- Game Jolt
- Kongregate
- Epic Games Store
- App Store / Google Play (mobile)

## 9. Version Control
- [ ] Git setup: _______________
- [ ] GitHub/GitLab criado: _______________

Setup:
```bash
git config --global user.name "Your Name"
git init meu_jogo
cd meu_jogo
git remote add origin https://github.com/user/meu_jogo.git
```

## 10. Build & Deploy
- [ ] Build process documentado: _______________
- [ ] CI/CD pipeline (opcional): _______________

Ferramentas:
- GitHub Actions (free)
- Itch.io Butler (deployment automático)
```

**Script para clonar e navegar awesome-list localmente:**

```python
#!/usr/bin/env python3
# awesome_game_dev_browser.py

import os
import subprocess
import json
from pathlib import Path
from urllib.parse import urljoin

class AwesomeGameDevBrowser:
    def __init__(self, repo_url="https://github.com/Kavex/GameDev-Resources.git"):
        self.repo_url = repo_url
        self.repo_dir = Path("./GameDev-Resources")
        self.readme = None

    def clone_or_update(self):
        """Clonar ou atualizar repositório local"""
        if self.repo_dir.exists():
            print(f"Atualizando {self.repo_dir}...")
            subprocess.run(
                ["git", "-C", str(self.repo_dir), "pull"],
                check=True
            )
        else:
            print(f"Clonando {self.repo_url}...")
            subprocess.run(
                ["git", "clone", "--depth", "1", self.repo_url],
                check=True
            )

    def parse_readme(self):
        """Parsear README.md e extrair categorias"""
        readme_path = self.repo_dir / "README.md"

        with open(readme_path, "r", encoding="utf-8") as f:
            content = f.read()

        # Parsear estrutura markdown
        categories = {}
        current_category = None
        current_section = None

        for line in content.split("\n"):
            if line.startswith("## "):
                current_category = line[3:].strip()
                categories[current_category] = {}
            elif line.startswith("### "):
                current_section = line[4:].strip()
                if current_category:
                    categories[current_category][current_section] = []
            elif line.startswith("- ["):
                # Link format: - [Name](url)
                import re
                match = re.match(r"- \[(.*?)\]\((.*?)\)", line)
                if match and current_section:
                    name, url = match.groups()
                    categories[current_category][current_section].append(
                        {"name": name, "url": url}
                    )

        self.categories = categories
        return categories

    def list_categories(self):
        """Listar todas as categorias"""
        for idx, cat in enumerate(self.categories.keys(), 1):
            print(f"{idx:2d}. {cat}")

    def list_section(self, category, section):
        """Listar itens de uma seção"""
        try:
            items = self.categories[category][section]
            print(f"\n{category} > {section}:\n")
            for idx, item in enumerate(items, 1):
                print(f"  {idx:2d}. {item['name']}")
                print(f"      → {item['url']}\n")
        except KeyError:
            print(f"Seção não encontrada")

    def interactive_mode(self):
        """Navegação interativa"""
        while True:
            print(f"\n{'='*60}")
            print("AWESOME GAMEDEV RESOURCES")
            print(f"{'='*60}\n")

            self.list_categories()

            choice = input("\nEscolha categoria (ou 'q' para sair): ").strip()

            if choice.lower() == "q":
                break

            try:
                category_idx = int(choice) - 1
                category = list(self.categories.keys())[category_idx]

                print(f"\n{category}:")
                sections = list(self.categories[category].keys())
                for idx, section in enumerate(sections, 1):
                    print(f"  {idx}. {section}")

                section_choice = input("\nEscolha seção: ").strip()
                section_idx = int(section_choice) - 1
                section = sections[section_idx]

                self.list_section(category, section)

            except (ValueError, IndexError):
                print("Escolha inválida")

    def export_filtered_list(self, category_filter, output_file="meu_roadmap.json"):
        """Exportar subconjunto de recursos para projeto específico"""
        filtered = {
            cat: sections
            for cat, sections in self.categories.items()
            if any(keyword in cat.lower() for keyword in category_filter)
        }

        with open(output_file, "w") as f:
            json.dump(filtered, f, indent=2)

        print(f"✓ Exportado em {output_file}")

# Uso
if __name__ == "__main__":
    browser = AwesomeGameDevBrowser()

    # Setup
    browser.clone_or_update()
    browser.parse_readme()

    # Modo interativo
    browser.interactive_mode()

    # OU export para projeto específico 2D indie
    # browser.export_filtered_list(["pixel art", "2d", "free"])
```

**Criar seu próprio subset da awesome-list:**

```markdown
# Meu Roadmap de Game Dev - 2D Pixel Art Indie

Baseado em: https://github.com/Kavex/GameDev-Resources

## Engine
- **Godot 4.1** (eleito porque é 2D-first, open-source, export pra web)
  Instalado em: `C:\Users\me\AppData\Roaming\Godot`

## Pixel Art
- **Aseprite** ($20 one-time) - Principal editor
- **OpenGameArt.org** - Buscar assets free quando não quer fazer do zero
- **Kenney.nl** - Tilesets e sprites high-quality free
- **PiskelApp** - Backup online

## Level Design
- **Tiled** (free) - Map editor padrão para Godot
- **Tutorial completado**: https://thornydev.medium.com/creating-a-pixel-art-game-in-godot-part-1-ac28055ad588

## Audio
- **Audacity** - Gravar vozes / efeitos
- **LMMS** - Compor música simples
- **OpenGameArt** - Buscar SFX royalty-free

## Publicação
- **itch.io** - Primary (indie-friendly)
- **GitHub** - Para fazer open-source e receber feedback

## Próximos passos
1. [x] Instalar Godot 4.1
2. [ ] Completar tutorial Godot "Your First Game"
3. [ ] Criar primeira cena de teste (2-3h)
4. [ ] Integrar sprites do Kenney (1h)
5. [ ] Criar build pra web (test)
```

## Stack e requisitos

**Repositórios awesome-list recomendados:**
- GitHub/Kavex/GameDev-Resources (4.5K stars, 91 contributors)
- GitHub/games-on-rails/awesome-game-dev (alternativa: Rust/Elixir focused)
- GameJams.com (comunidade, not a list)

**Categorias essenciais (sempre presentes em good awesome-list):**
1. Game Engines (Godot, Unity, Unreal)
2. Graphics (2D, 3D, VFX)
3. Audio (SFX, music composition)
4. Physics
5. Level Design tools
6. Pixel art / sprite tools
7. 3D Modeling
8. Publishing platforms
9. Communities / Learning
10. Code (game frameworks, libraries)

**Frequência de atualização:**
- Awesome-list ativa: pull requests aceitos 1-2x/mês
- Confiabilidade: quanto mais stars, mais validada pela comunidade

## Armadilhas e limitações

**Quando NOT usar awesome-list:**
- Como substituto para documentação oficial (lista é superficial)
- Para aprender profundo (usar tutoriais + docs originais)
- Para encontrar ferramentas ultra-especializadas (não está lá)
- Como marketing channel (links quebrados existem)

**Problemas comuns:**
- Links desatualizados (ferramenta descontinuada)
- Duplicação (mesma ferramenta listada 3x com nomes diferentes)
- Viés de popularidade (Godot vs Unreal overrepresentado)
- Falta de comparações (lista diz "o que existe" não "qual é melhor")

**Melhor uso (realmente funciona):**
- Para **discovery** (saber que ferramenta X existe)
- Para **validação** (se está em awesome-list, é respeitado)
- Para **contexto** (quantas alternativas existem?)
- **NÃO** para decisão final (sempre testar 3+ opções)

## Conexões
- [[repositorio-curado-de-recursos-gamedev]]
- [[repositorios-open-source-curados-centralizam-recursos-de-desenvolvimento-de-jogo]]
- [[saturacao-de-ferramentas-ia-para-game-assets-exige-criterio-para-distinguir-solu]]

## Histórico
- 2026-04-02: Nota criada
- 2026-04-02: Reescrita como guia de implementação prática