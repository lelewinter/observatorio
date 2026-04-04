---
tags: [ia, multimodal, coding-agents, visao-computacional, llm]
source: https://x.com/zaidmukaddam/status/2039372037538685018?s=20
date: 2026-04-02
tipo: aplicacao
---

# Gerar Código a partir de Screenshots com Modelos Vision-Coding Nativos

## O que e

GLM-5V-Turbo e similares integram visão e codificação em arquitetura unificada (não pipeline). Convertem screenshots/wireframes direto em HTML/React sem passo intermediário textual. GUI Agents nativos podem navegar interfaces interpretando elementos visuais.

## Como implementar

**Diferença arquitetural**:
- **Pipeline traditional**: Image → Vision Encoder → caption "blue button on left side" → Language Model → "create button with blue color" → código
- **Native multimodal**: Image → Unified Encoder → Direct Code Generation (fusão acontece em camadas profundas, não em interface textual)

**Setup para geração de código visual** (exemplo com GLM-5V-Turbo):
```python
from glm_vision_code import GLMVisionCodeModel

model = GLMVisionCodeModel.from_pretrained("glm-5v-turbo")

# Input: screenshot
screenshot = load_image("app-screenshot.png")

# Direct code generation
code = model.generate_code(
    image=screenshot,
    target_language="react",
    framework="tailwind",
    include_responsive=True
)

print(code)
# Output:
# export default function App() {
#   return (
#     <div className="flex items-center justify-center h-screen bg-blue-50">
#       <button className="px-6 py-3 bg-blue-600 text-white rounded">
#         Click me
#       </button>
#     </div>
#   )
# }
```

**GUI Agent para automação** (navegar e interagir com interfaces):
```python
from glm_vision_code import GUIAgent

agent = GUIAgent(model=model)

# Objective: "log into Twitter and like the top tweet"
goal = "log into Twitter and like the top tweet"

# Agent loop
while not agent.is_goal_complete():
    screenshot = agent.take_screenshot()

    # Modelo prediz: qual é próxima ação?
    action = agent.predict_action(
        image=screenshot,
        goal=goal
    )
    # Possíveis actions: click(x, y), type(text), scroll(direction)

    agent.execute_action(action)

print("Goal completed!")
```

**Workflow de design → code**:
```python
# Wireframe (low fidelity design)
wireframe = load_image("wireframe.png")

# Gerar versão inline (CSS included)
inline_code = model.generate_code(
    image=wireframe,
    target_language="html",
    css_framework="bootstrap"
)

# Gerar versão component (React)
component_code = model.generate_code(
    image=wireframe,
    target_language="jsx",
    framework="nextjs"
)

# Ambos a partir da mesma imagem!
```

**Prompt engineering para visão-código**:
```python
# Contexto adicional ajuda qualidade
code = model.generate_code(
    image=screenshot,
    target_language="react",
    context={
        "design_system": "Material UI",
        "theme": "dark mode",
        "accessibility": "WCAG AA",
        "responsive_breakpoints": ["mobile", "tablet", "desktop"]
    }
)
```

**Integração com Claude Code** (agente híbrido):
```python
# Usar GLM-5V-Turbo para interpretar screenshots
# Usar Claude Code para refactoring/testing/deployment
screenshot = agent.take_screenshot()

# Step 1: GLM-5V gera scaffold
scaffold = glm_model.generate_code(screenshot)

# Step 2: Claude Code refina e testa
claude_response = claude.request(f"""
Here's the generated scaffold:
{scaffold}

Please:
1. Add proper error handling
2. Include unit tests with jest
3. Follow this design system: {design_tokens}
""")
```

## Stack e requisitos

- **Model**: GLM-5V-Turbo (ou OpenAI GPT-4V com plugins de codificação)
- **Latência**: 2-5 segundos por inferência (GPU recomendada)
- **VRAM**: 16GB+ (modelo ~13B parâmetros)
- **Suporte visual**: PNG, JPEG, GIF, SVG (exceto vídeo por enquanto)
- **Linguagens alvo**: Python, JavaScript/TypeScript, Java, C#, Go
- **Frameworks**: React, Vue, Angular, Flutter, SwiftUI

## Armadilhas e limitacoes

- **Qualidade código**: Gera boilerplate rápido mas refactoring manual é necessário (não é production-ready direto).
- **Specificity visual**: Se wireframe é ambíguo, modelo pode interpretar diferente do intencionado; ser explícito em design.
- **Gaps visuais**: Elementos muito pequenos, textos em alta resolução podem ser perdidos; screenshot deve ser clara.
- **Gui Agents lento**: Loop de screenshot→predict→execute é serial e lento (2-5s por ação). Para 10 ações: 20-50s total.
- **State tracking**: Agent não "aprende" ao longo da navegação; cada screenshot é processado independentemente.
- **Dynamic content**: Interfaces com conteúdo renderizado dinamicamente (carregamento via JS) podem confundir modelo.

## Conexoes

[[Modelos Omnimodais Nativos Multimodal]] [[Modelo Foundation para Atividade Neural]] [[Claude Code Melhores Praticas]]

## Historico

- 2026-04-02: Nota criada
- 2026-04-02: Reescrita para template aplicacao