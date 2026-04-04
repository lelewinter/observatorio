---
date: 2026-03-24
tags: [design, ia, claude, generacao, prompts, visual-production]
source: https://x.com/AmirMushich/status/2036169931612467708?s=20
autor: "@AmirMushich"
tipo: aplicacao
---

# Gerar Prompts Otimizados Desconstruindo Referências Visuais com Claude

## O que é

Claude analisa imagem de referência (Pinterest, Savee.it, shotdeck), desconstrói componentes visuais (iluminação, composição, texturas, paleta), produz prompt estruturado para Google Nano Banana 2 ou similares. Entrada: imagem. Saída: prompt que funciona em primeira iteração.

## Como implementar

**1. Preparar imagem de referência**

Arquivo: screenshot, foto, ou link para inspiração visual.

**2. Prompt de desconstrução (em Claude)**

```
Analise esta imagem como art director experiente.

Desconstrua em seções:
1. Tipo de cena
2. Composição (rule of thirds, focal points)
3. Iluminação (tipo, direção, temperatura cor, intensidade)
4. Profundidade de campo (shallow, medium, deep)
5. Paleta de cores (primária, secundária, acentos)
6. Texturas (materiais visíveis)
7. Atmosfera (mood, estilo visual)
8. Perspectiva (ângulo câmera, lente focal)
9. Qualidade visual (detalhe, resolução aparente)
10. Estilo (realista, ilustração, cinematic, etc)

Agora gere prompt estruturado OTIMIZADO PARA
[Google Nano Banana 2 | DALL-E 3 | Midjourney]

Formato:
Main subject: [descrição primária]
Composition: [layout, rule of thirds, focal points]
Lighting: [tipo, direção, temperatura]
Depth: [depth of field description]
Color palette: [hex ou descrição]
Texture: [materiais, superfícies]
Mood: [atmosfera, emoção]
Style: [estilo visual, referências]
Technical: [resolução, qualidade, aspecto]
Forbidden: [coisas a evitar]

Generate immediately actionable prompt:
"[Full prompt ready to copy-paste]"
```

**3. Exemplo concreto: desconstrução**

Referência: foto de cadeira em estúdio

Claude analisa:
```
1. Tipo: Product photography, studio setting
2. Composição: Objeto central, fundo neutro desfocado
3. Iluminação: Three-point (key light esquerda, fill light direita, back light sutil)
4. Profundidade: Rasa (shallow depth of field, bokeh background)
5. Paleta: Tons quentes (sepia/dourado), branco/cinza neutro fundo
6. Texturas: Madeira clara, tecido linho, metal polido
7. Atmosfera: Minimalista, limpo, profissional, elegante
8. Perspectiva: Eye-level, ligeira angulação 45°
9. Qualidade: Fotorrealística, detalhe alto, resolução 4K
10. Estilo: Fotografia comercial, editorial luxury
```

Prompt output:
```
"A minimalist luxury wooden chair with natural linen upholstery,
shot in studio with three-point lighting (warm key light from left,
subtle fill right, delicate back-light). Shallow depth of field with
soft bokeh background in warm grey-beige. Warm sepia-toned color
palette, photorealistic detail, 4K quality, editorial photography,
professional commercial style."
```

**4. Refinamento iterativo**

Primeira geração: se resultado não match:
```
"Image misses [específico detalhe].
Adjust prompt:
- Increase emphasis on [elemento]
- Reduce [elemento secundário]
- Add specific reference: [estilo/artista]"
```

Claude refina e regenera prompt.

**5. Pipeline produção visual**

```
1. Coleta referência (Pinterest, Pinterest boards)
2. Upload para Claude
3. Executa desconstrução (3 min)
4. Copia prompt output
5. Cola em [Google Nano | DALL-E | Midjourney]
6. Primeira geração geralmente "bom"
7. Se precisa tweak: volta step 4 com feedback "aumenta X, diminui Y"
```

**6. Casos de uso estruturados**

| Tipo | Output |
|------|--------|
| Product design | Renders de produto com múltiplos ângulos |
| Environment design | Concept art de cenários |
| Character design | Personagem em múltiplas poses |
| UX/UI mockup | Interface layout polido |
| Marketing creative | Banners, hero images, ads |

## Stack e requisitos

- Claude (Vision model, ex: claude-3-sonnet)
- Imagem referência (PNG, JPG, mín 512x512)
- Gerador imagem (Google Nano, DALL-E, Midjourney, Krea)
- Opcional: Figma ou editor para post-processing

## Armadilhas e limitações

- **Claude às vezes falha**: Se referência muito complexa, desconstrução genérica. Especifique detalhes manualmente
- **Overfitting**: Prompt pode replicar *exatamente* referência, sem criatividade. Peça para "usar referência como inspiração, não cópia"
- **Terminologia**: Diferentes engines usam "prompt syntax" diferente. Especifique qual engine usando
- **Estilo bleeding**: Múltiplas referências podem confundir Claude. Use uma referência por sessão
- **Qualidade varia**: Mesmo com prompt perfeito, gerador pode falhar. Não é garantido

## Conexões

[[geracao-automatizada-de-prompts]]
[[geracao-de-cenas-multi-shot-por-ia]]
[[geração-de-json-a-partir-de-qualquer-fonte]]

## Histórico

- 2026-03-24: Nota criada
- 2026-04-02: Reescrita como guia de implementação
