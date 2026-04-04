---
tags: [claude-code, computer-use, gui-automation, agentes, testing]
source: https://x.com/claudeai/status/2038663014098899416?s=20
date: 2026-04-02
tipo: aplicacao
---

# Usar Computer Use em Claude Code para Testar Interfaces Automaticamente

## O que é

Claude Code pode controlar GUI: screenshots, cliques, digitação, scroll. Agente testa código que criou abrindo app, interagindo. Fecha loop dev: write → test → fix autonomamente.

## Como implementar

**1. Ativar computer use (se disponível)**

Claude Pro/Max, research preview:

```python
from anthropic_computer_use import ComputerUseAgent

agent = ComputerUseAgent(
    model="claude-opus-4-1",
    tools=["screenshot", "mouse", "keyboard"],
    require_human_confirmation=True  # Safety: pede OK antes de ações
)
```

**2. Caso de uso 1: Teste de UI automatizado**

```python
# Workflow: Build React component → Open browser → Test

task = """
1. I just built a React button component
2. Open browser, go to http://localhost:3000
3. Take screenshot of rendered page
4. Click the button
5. Verify button responds (color change, text change, whatever was coded)
6. Report result
"""

agent.execute(task)

# Resultado: "Button renders correctly and changes color to blue on click ✓"
```

**3. Caso de uso 2: Teste de formulário**

```python
# Test form submission end-to-end

task = """
1. Open CRM desktop app
2. Click "New Contact" button
3. Fill form:
   - Name: John Doe
   - Email: john@example.com
   - Phone: 555-1234
4. Submit form
5. Verify contact appears in list
6. Report success or error
"""

result = agent.execute(task)
# Resultado: "Contact 'John Doe' created successfully. Visible in list."
```

**4. Caso de uso 3: Debugging visual**

```python
# Iterative debugging: code → screenshot → fix → repeat

task = """
1. Build CSS layout (flexbox centered button)
2. Open in browser
3. Take screenshot
4. If button is NOT centered, adjust CSS and try again
5. Repeat until button is perfectly centered
6. Report final screenshot
"""

agent.execute_iteratively(task, max_iterations=3)
# Claude tries, sees it's off-center, adjusts, tries again...
```

**5. Prompt estruturado para computer use**

```
You are an automated tester using computer vision and mouse control.

Task: [descrição do teste]

Rules:
1. Take screenshots frequently to understand state
2. Only click on visible elements
3. Double-check result before reporting
4. If action fails, take screenshot and analyze
5. Report pass/fail with evidence (screenshot)

Action sequence:
[step 1]
[step 2]
[step 3]
...
[Verify result]
```

**6. Segurança: human confirmation**

```python
agent = ComputerUseAgent(
    require_human_confirmation=True,
    dangerous_actions=[
        "delete_file",
        "delete_directory",
        "format_drive",
        "sudo_command"
    ]
)

# Antes de rodar ação arriscada:
# Claude: "I want to delete /tmp/cache. OK to proceed?"
# Humano: Confirma ou bloqueia
```

**7. Integração com CI/CD**

```bash
#!/bin/bash
# test_with_computer_use.sh

# 1. Build app
npm run build

# 2. Start server
npm start &
SERVER_PID=$!

# 3. Run Claude computer use tests
python test_automation.py

# 4. Stop server
kill $SERVER_PID

# 5. Report results
cat test_results.txt
```

## Stack e requisitos

- Claude Pro/Max (research preview)
- GUI desktop (Windows/Mac/Linux)
- X11/Wayland (Linux) ou native (Win/Mac)
- Screenshots capability
- App to test (web/desktop)

## Armadilhas e limitações

- **Research preview**: Unstable, may fail
- **Latency**: Screenshots + reasoning = 1-2 min per action
- **Vision limitations**: Can't read tiny text, blurry screenshots
- **Flakiness**: Network latency, popup dialogs break automation
- **Security risk**: Agent can click wrong thing. Always review before production
- **Cost**: screenshot + reasoning = ~$0.5 per test. Budget accordingly

## Conexões

[[claude-code-embarcado-em-editor-de-notas]]
[[code-review-checklist-3-fases-claude-code]]

## Histórico

- 2026-04-02: Nota criada
- 2026-04-02: Reescrita como guia de implementação
