---
date: 2026-03-24
tags: [ia, google-stitch, claude, web-design, prompts, landing-pages, saas]
source: https://x.com/viktoroddy/status/2036138516070146225?s=20
autor: "@viktoroddy"
tipo: aplicacao
---

# Gerar Landing Pages Animadas com Prompts Multi-Modelo

## O que é

Prompts estruturados para gerar landing pages premium funcionam em múltiplos modelos (Google Stitch, Claude, MotionSites). Entrada: descrição + brief de design. Saída: página HTML/CSS com animações "liquid glass", dark theme, SaaS elements (CTA, métricas).

## Como implementar

**1. Estruturar prompt de landing page**

Template base:
```
Crie uma landing page dark e premium para:
- Empresa: [nome]
- Serviço: [descrição]
- Design: [estilo, ex: "liquid glass"]
- Elementos obrigatórios: hero, features (3-5), benefits, CTA, testimonials
- Animações: suaves, não barulhentas
- Paleta: dark mode com acentos [cor principal]
```

Exemplo concreto:
```
Crie landing page dark premium para APEX (plataforma de aceleração de receita).
Design liquid glass: glassmorphism cards, smooth transitions, dark navy background.
Inclua: hero com CTA, 4 features com ícones, metrics section, 3 testimonials, footer.
Paleta: dark navy, purple accent, white text.
Animações on scroll suaves.
```

**2. Testar em múltiplos modelos**

| Modelo | Comando |
|--------|---------|
| Claude | Cole prompt em chat, peça "Generate HTML+CSS" |
| Google Stitch | https://stitch.google.com → paste prompt |
| MotionSites | http://motionsites.ai → select template |

**3. Refinar outputs**

Comparar iterativamente:
- Visual polish (Claude: melhor tipografia; Stitch: melhor animações)
- Tempo geração (Stitch: mais rápido)
- Custo (Claude: mais caro por uso extenso)

**4. Biblioteca de prompts reutilizáveis**

Armazenar em arquivo `.prompts/landing-pages.md`:

```markdown
## SaaS Dark Premium
[seu prompt estruturado]
Model: Claude, Stitch (ambos)
Output: HTML + inlined CSS
Refinements: add gradient overlay, increase animation duration

## E-commerce Minimalist
[outro prompt]
...
```

**5. Automação: batch generation**

```python
import anthropic

prompts = [
    "Create landing page for StartupA...",
    "Create landing page for StartupB...",
]

client = anthropic.Anthropic()
for prompt in prompts:
    msg = client.messages.create(
        model="claude-opus-4-1",
        max_tokens=4096,
        messages=[{"role": "user", "content": prompt}]
    )
    # Save HTML to file
    with open(f"landing_{idx}.html", "w") as f:
        f.write(msg.content[0].text)
```

## Stack e requisitos

- Claude API (ou Google Stitch/MotionSites)
- HTML5, CSS3 (output nativo)
- Browser para preview
- Opcional: Python para automação batch

## Armadilhas e limitações

- **Prompt quality critical**: Impreciso = design medíocre. Invest 30min em prompt, poupa horas em iteração
- **Modelos divergem**: Alguns preferem Tailwind, outros inline CSS. Especifique no prompt
- **Animações Heavy**: GPU-bound. Teste performance em devices mobile antes de deploy
- **Falta brand consistency**: Cada geração é isolada. Use sistema de design (colors, fonts) nos prompts
- **SEO não automático**: Modelos geram HTML limpo mas sem otimização SEO. Add manualmente

## Conexões

[[geracao-automatizada-de-prompts]]
[[geracao-de-json-a-partir-de-qualquer-fonte]]
[[framework-winston-para-apresentacoes]]

## Histórico

- 2026-03-24: Nota criada
- 2026-04-02: Reescrita como guia de implementação
