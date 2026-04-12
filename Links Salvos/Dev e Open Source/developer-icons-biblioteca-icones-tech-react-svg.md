---
tags: [react, svg, icones, ui, open-source, developer-tools]
source: https://x.com/heygurisingh/status/2041073938114191492
date: 2026-04-06
tipo: aplicacao
---
# Developer Icons: Biblioteca Tipada de Ícones Tech para React

## O que é
Developer Icons é uma biblioteca React de componentes totalmente tipados (TypeScript) com SVGs customizáveis para frameworks, linguagens, ferramentas e tecnologias populares. Cada ícone é exportado como componente React nomeado (HtmlIcon, JavascriptIcon, PythonIcon, ReactIcon, etc), mantém suporte a variantes light/dark/wordmark, é otimizado com SVGO, e permite customização de tamanho, cor e stroke-width via props padrão de SVG. Instalação via npm, MIT licensed, funciona em React, Next.js, Astro e qualquer stack JavaScript/TypeScript moderno.

## Como implementar

### Instalação
```bash
npm install developer-icons
# ou
yarn add developer-icons
# ou
pnpm add developer-icons
```

Nenhuma configuração é necessária. A biblioteca é zero-config e funciona imediatamente.

### Uso básico em React
```jsx
import { ReactIcon, JavascriptIcon, PythonIcon } from 'developer-icons';

export function TechStack() {
  return (
    <div className="flex gap-4">
      <ReactIcon size={48} />
      <JavascriptIcon size={48} />
      <PythonIcon size={48} />
    </div>
  );
}
```

### Props e customização
Cada componente aceita props padrão de SVG:

```jsx
import { TypescriptIcon, NodeIcon, PostgresIcon } from 'developer-icons';

export function CustomIcons() {
  return (
    <>
      {/* Tamanho customizado */}
      <TypescriptIcon width={64} height={64} />
      
      {/* Cor customizada */}
      <NodeIcon fill="#339933" />
      
      {/* Stroke width para ícones line-based */}
      <PostgresIcon strokeWidth={1.5} />
      
      {/* Combinações */}
      <PostgresIcon 
        size={48} 
        fill="#336791" 
        className="hover:opacity-75 transition"
      />
    </>
  );
}
```

### Variantes (light, dark, wordmark)
Nem todo ícone tem variantes, mas tecnologias populares têm múltiplas:

```jsx
import { 
  ReactIcon,
  ReactIconLight,
  ReactIconDark,
  ReactIconWordmark
} from 'developer-icons';

export function IconVariants() {
  return (
    <div className="grid grid-cols-4 gap-4 p-4 bg-gray-100">
      <div className="p-4 bg-white">
        <ReactIconLight size={48} />
        <p className="text-sm mt-2">Light</p>
      </div>
      
      <div className="p-4 bg-gray-800">
        <ReactIconDark size={48} />
        <p className="text-sm mt-2 text-white">Dark</p>
      </div>
      
      <div className="p-4 bg-white col-span-2">
        <ReactIconWordmark width={120} />
        <p className="text-sm mt-2">Wordmark</p>
      </div>
    </div>
  );
}
```

### Listagem completa de ícones disponíveis
A biblioteca suporta 200+ tecnologias. Aqui está uma amostra (veja documentação para lista completa):

**Frontend:**
```jsx
import {
  ReactIcon, VueIcon, AngularIcon, SvelteIcon,
  NextIcon, NuxtIcon, AstroIcon, RemixIcon
} from 'developer-icons';
```

**Backend & Servidores:**
```jsx
import {
  NodeIcon, DjangoIcon, FastapiIcon, SpringIcon,
  GoIcon, RustIcon, ErlangIcon, LuaIcon
} from 'developer-icons';
```

**Linguagens:**
```jsx
import {
  JavascriptIcon, TypescriptIcon, PythonIcon,
  JavaIcon, CppIcon, RustIcon, GoIcon, RubyIcon
} from 'developer-icons';
```

**Bancos de dados:**
```jsx
import {
  PostgresIcon, MysqlIcon, MongodbIcon,
  RedisIcon, NedbIcon, MariadbIcon, SqliteIcon
} from 'developer-icons';
```

**Ferramentas DevOps:**
```jsx
import {
  DockerIcon, KubernetesIcon, TerraformIcon,
  AnsibleIcon, JenkinsIcon, CircleciIcon, GitIcon
} from 'developer-icons';
```

### Caso de uso real: Dashboard de portfolio
```jsx
import React from 'react';
import {
  ReactIcon, TypescriptIcon, NodeIcon,
  PostgresIcon, DockerIcon, GitIcon,
  TailwindIcon, VitestIcon, AstroIcon
} from 'developer-icons';

export function PortfolioTechStack() {
  const technologies = [
    { name: 'React', icon: ReactIcon, category: 'Frontend' },
    { name: 'TypeScript', icon: TypescriptIcon, category: 'Language' },
    { name: 'Node.js', icon: NodeIcon, category: 'Runtime' },
    { name: 'PostgreSQL', icon: PostgresIcon, category: 'Database' },
    { name: 'Docker', icon: DockerIcon, category: 'DevOps' },
    { name: 'Git', icon: GitIcon, category: 'VCS' },
    { name: 'Tailwind CSS', icon: TailwindIcon, category: 'Styling' },
    { name: 'Vitest', icon: VitestIcon, category: 'Testing' },
    { name: 'Astro', icon: AstroIcon, category: 'Tooling' },
  ];

  return (
    <section className="py-12 px-6">
      <h2 className="text-3xl font-bold mb-8">Tech Stack</h2>
      
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        {technologies.map((tech) => {
          const Icon = tech.icon;
          return (
            <div
              key={tech.name}
              className="flex items-center gap-4 p-4 rounded-lg bg-gradient-to-br from-blue-50 to-indigo-50 border border-blue-200 hover:shadow-lg transition-shadow"
            >
              <Icon size={40} className="flex-shrink-0" />
              <div>
                <h3 className="font-semibold text-gray-900">{tech.name}</h3>
                <p className="text-sm text-gray-600">{tech.category}</p>
              </div>
            </div>
          );
        })}
      </div>
    </section>
  );
}
```

### Integração com componentes headless (Radix, Shadcn)
```jsx
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@radix-ui/react-select';
import { ReactIcon, VueIcon, AngularIcon } from 'developer-icons';

export function FrameworkSelector() {
  const frameworks = [
    { value: 'react', label: 'React', icon: ReactIcon },
    { value: 'vue', label: 'Vue', icon: VueIcon },
    { value: 'angular', label: 'Angular', icon: AngularIcon },
  ];

  return (
    <Select>
      <SelectTrigger className="w-48">
        <SelectValue placeholder="Escolha um framework" />
      </SelectTrigger>
      <SelectContent>
        {frameworks.map((fw) => {
          const Icon = fw.icon;
          return (
            <SelectItem key={fw.value} value={fw.value}>
              <div className="flex items-center gap-2">
                <Icon size={16} />
                {fw.label}
              </div>
            </SelectItem>
          );
        })}
      </SelectContent>
    </Select>
  );
}
```

### TypeScript: Aproveitar tipagem completa
```tsx
import { 
  ReactIcon,
  NodeIcon,
  PostgresIcon,
  type IconProps // Importar tipos
} from 'developer-icons';

// Componente tipado que aceita qualquer ícone
interface TechListProps {
  technologies: Array<{
    name: string;
    Icon: React.ComponentType<IconProps>;
  }>;
}

export function TechList({ technologies }: TechListProps) {
  return (
    <ul className="space-y-2">
      {technologies.map((tech) => (
        <li key={tech.name} className="flex items-center gap-2">
          <tech.Icon size={24} />
          <span>{tech.name}</span>
        </li>
      ))}
    </ul>
  );
}

// Uso
const myTechs: TechListProps['technologies'] = [
  { name: 'React', Icon: ReactIcon },
  { name: 'Node.js', Icon: NodeIcon },
  { name: 'PostgreSQL', Icon: PostgresIcon },
];

export default () => <TechList technologies={myTechs} />;
```

### Tratamento de temas light/dark com Tailwind
```jsx
import { ReactIcon } from 'developer-icons';

export function IconWithTheme() {
  return (
    <div className="dark:bg-gray-900 bg-white">
      {/* Toma cor do texto context (inheritance) */}
      <ReactIcon 
        size={48}
        className="text-blue-600 dark:text-blue-400"
      />
      
      {/* Ou fill explícito */}
      <ReactIcon 
        size={48}
        fill="currentColor"
        className="text-red-600 dark:text-red-400"
      />
    </div>
  );
}
```

## Stack e requisitos

### Dependências
- **React**: 16.8+ (hooks)
- **TypeScript**: 4.4+ (tipos completos disponíveis)
- **Node.js**: 14+ (build/install)

### Compatibilidade de frameworks
- **React**: Funciona 100%, suporte completo
- **Next.js**: App Router e Pages Router, SSR/SSG funciona
- **Astro**: Funciona via integração React ou como componente puro
- **Remix**: Funciona normalmente
- **SvelteKit**: Pode usar via wrapper ou converter para Svelte

### Build tools compatíveis
- **Webpack**: Funciona
- **Vite**: Recomendado, mais rápido
- **Turbopack**: Funciona
- **esbuild**: Funciona

### Tamanho e performance
- **Tamanho base**: ~30KB gzipped (todos os 200+ ícones)
- **Tree-shaking**: Suportado, importações não-usadas são removidas
- **Modo produçao**: ~10-15KB gzipped se importar apenas ícones usados
- **Sem dependências**: Zero dependências externas (puro React + SVGs)

### Suporte a browser
- Moderno (Chrome 90+, Firefox 88+, Safari 14+)
- Sem suporte a IE11 (não é objetivo da biblioteca)

## Armadilhas e limitações

### 1. Limitação de ícones disponíveis
Developer Icons cobre as 200+ tecnologias mais populares, mas se você precisa de um ícone para ferramenta obscura, pode não existir. Tecnologias muito novas (lançadas em 2026) podem estar ausentes. Mitigação: verifique lista completa de ícones antes de comprometer com a biblioteca, use ícones genéricos (gear, cube) como fallback, considere adicionar SVG custom para ícones faltantes, ou contribua para o projeto (GitHub está aberto a PRs).

### 2. Sem suporte animado
Todos os ícones são SVGs estáticos. Se você quer ícones que rotacionam, piscam ou têm animações interativas, precisa adicionar CSS/framer-motion manualmente. Mitigação: use CSS animations (rotate, pulse, etc via Tailwind), ou considere bibliotecas como `react-icons` que têm mais suporte animado, integre framer-motion para efeitos complexos.

### 3. Customização limitada de design
Os ícones têm design fixo. Você pode mudar cor e tamanho, mas não pode alterar proporções, stroke, ou design. Se quiser ícones com estilo "flat" em vez de "outline", precisa encontrar alternativa. Mitigação: use a biblioteca para ícones mais padronizados e crie SVGs custom para ícones que precisam design único, combina Developer Icons com library adicional (como `heroicons` para UI genérica).

### 4. Sem suporte para variantes de tamanho otimizado
Todos os ícones são um único SVG que escala. Não há versões otimizadas para 16px vs 48px (que poderiam ter diferentes níveis de detalhe). Em tamanhos muito pequenos, alguns ícones perdem legibilidade. Mitigação: teste ícones em tamanhos reais do seu design, use sizes mínimos de 20px para ícones pequenos, considere usar símbolos mais simples para UI muito densa.

### 5. Overhead de bundle se não usar tree-shaking
Se seu bundler não faz tree-shaking bem (Webpack muito velho), importar a biblioteca inteira traz todos os 200+ ícones. Mitigação: use Vite ou webpack 5+, valide bundle size com `npm run build`, considere importar seletivamente usando path imports (`from 'developer-icons/react'` se biblioteca suportar).

## Conexões
- [[Dev/Frontend/React Component Libraries|React Component Libraries]]
- [[Dev/Frontend/SVG e Otimizacao de Icones|SVG e Otimização de Ícones]]
- [[Dev/Frontend/Tailwind CSS e Styling|Tailwind CSS e Styling]]
- [[Dev/TypeScript/Type-Safe Components|Type-Safe Components]]
- [[Dev/Tools/Build Tools - Vite webpack|Build Tools - Vite, webpack]]

## Histórico
- 2026-04-06: Nota criada com base em anúncio Developer Icons do X/Twitter
