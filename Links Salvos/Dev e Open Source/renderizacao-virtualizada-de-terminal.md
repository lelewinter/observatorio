---
tags: [terminal, rendering, performance, ui, virtualizacao]
date: 2026-04-02
tipo: aplicacao
---
# Renderizar UI no Terminal com Virtualização

## O que é
Desenhar apenas as linhas visíveis no terminal. Permite aplicações com 10mil+ itens sem lag.

## Como implementar
```python
class VirtualizedTerminalUI:
    def __init__(self, height):
        self.height = height
        self.scroll_offset = 0
        self.items = list(range(10000))
    
    def render(self):
        visible_items = self.items[self.scroll_offset:self.scroll_offset + self.height]
        for i, item in enumerate(visible_items):
            print(f"{i:3d}: {item}")
    
    def scroll_down(self):
        self.scroll_offset += 1
        self.render()
```

## Stack e requisitos
- Curses (Python) ou Blessed
- Buffer de tela (stdout)

## Histórico
- 2026-04-02: Reescrita
