---
tags: [design, ia, generativo, ui-ux, prototipagem, stitch]
source: https://x.com/namcios/status/2034354088922558713?s=20
date: 2026-04-02
tipo: aplicacao
---

# Gerar Interfaces e Design Systems Completos com IA (Google Stitch)

## O que é

Google Stitch (potenciado pela Galileo AI) é um agente de design que gera interfaces navegáveis, protótipos e design systems completos a partir de input em linguagem natural ou voz. Elimina design júnior/pleno e comprime o pipeline designer → dev em uma sessão.

## Como implementar

**Prompt no Stitch:**
```
Criar interface de dashboard financeiro com:
- Header com logo e menu
- Cards mostrando saldo, receita, despesa
- Gráfico de tendências últimos 30 dias
- Tema escuro, fonte Poppins
- Paleta: azul (#3B82F6), verde (#10B981)
```

**Output esperado:**
- Componentes React editáveis
- Estilos Tailwind
- Prototipo navegável
- DESIGN.md (design system exportável)

**Voz:**
```
"Design uma tela de login minimalista em tom azul,
com email, senha e botão de login. Fundo gradiente azul-branco"
```

**Export DESIGN.md:**
```yaml
---
name: "Financial Dashboard"
colors:
  primary: "#3B82F6"
  success: "#10B981"
  dark: "#1F2937"
components:
  Card:
    padding: 1rem
    borderRadius: 8px
  Button:
    bgColor: primary
    padding: "8px 16px"
---
```

**Integração com React:**
```jsx
// components/DashboardCard.jsx (gerado por Stitch)
export default function Card({ title, value, icon }) {
  return (
    <div className="p-4 bg-gray-900 rounded-lg border border-gray-800">
      <p className="text-gray-400">{title}</p>
      <p className="text-2xl font-bold text-white">{value}</p>
      {icon && <div className="mt-2">{icon}</div>}
    </div>
  );
}
```

## Stack e requisitos

- **Google Stitch**: web-based (acesso via Google)
- **React/Next.js**: para usar outputs
- **Tailwind**: padrão nos exports
- **Design tokens**: importar DESIGN.md automaticamente

## Armadilhas

1. **Lógica complexa**: Stitch gera UI, não business logic. Conectar funcionalidade manualmente.
2. **Brand guidelines**: Passar paleta/tipografia no prompt inicial.
3. **Revisão humana**: Sempre revisar antes de produção (estética subjective).

## Conexões

- [[conversao-html-para-react-com-vibe-coding]] - Converter designs em código
- [[design-vetorial-com-agentes-ia]] - Ícones/vetores com IA

## Histórico

- 2026-04-02: Nota original
- 2026-04-02: Reescrita com implementação
