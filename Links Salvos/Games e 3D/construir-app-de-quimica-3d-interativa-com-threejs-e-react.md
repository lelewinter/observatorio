---
tags: []
source: https://x.com/i/status/2040034179812139393
date: 2026-04-03
tipo: aplicacao
---
# Construir App de Química 3D Interativa com Three.js e React

## O que e

Um estudante do ensino médio construiu uma aplicação web de química em 3D totalmente interativa, com visualização de moléculas, orbitais e estruturas atômicas renderizadas em tempo real no navegador. O projeto demonstra que é possível criar ferramentas educacionais científicas visualmente impressionantes usando apenas tecnologias web modernas, sem backend complexo ou engine proprietária. Isso importa porque o mesmo stack pode ser replicado para qualquer domínio de visualização científica ou educacional.

## Como implementar

**Arquitetura geral do projeto**

O stack central combina React como framework de UI com Three.js para renderização 3D via WebGL. A lógica de química (ligações, valências, geometria molecular) fica separada em módulos JavaScript puros, enquanto o Three.js cuida exclusivamente da camada visual. Essa separação é crítica: misturar lógica química com código de renderização cria um monolito impossível de manter.

```
src/
  chemistry/        # lógica pura: moléculas, ligações, VSEPR
  components/       # componentes React
  scene/            # setup Three.js, câmera, iluminação
  data/             # banco de elementos, geometrias pré-calculadas
```

**Setup inicial com React + Three.js**

Inicie o projeto com Vite (muito mais rápido que CRA para projetos com assets 3D pesados):

```bash
npm create vite@latest chemistry-app -- --template react
cd chemistry-app
npm install three @react-three/fiber @react-three/drei
npm install zustand  # gerenciamento de estado global
```

A biblioteca `@react-three/fiber` (R3F) é o wrapper React para Three.js — ela abstrai o loop de animação e o gerenciamento de cena em JSX, eliminando boilerplate massivo. `@react-three/drei` fornece helpers prontos: `OrbitControls`, `Environment`, `Text3D`, `Sphere`, `Cylinder`.

**Modelagem de moléculas: dados e geometria**

Cada molécula é representada como um grafo: nós são átomos, arestas são ligações. Armazene os dados em JSON:

```json
{
  "H2O": {
    "atoms": [
      { "symbol": "O", "position": [0, 0, 0], "radius": 0.73, "color": "#ff4444" },
      { "symbol": "H", "position": [0.96, -0.93, 0], "radius": 0.31, "color": "#ffffff" },
      { "symbol": "H", "position": [-0.96, -0.93, 0], "radius": 0.31, "color": "#ffffff" }
    ],
    "bonds": [[0,1,1],[0,2,1]]
  }
}
```

As posições 3D devem ser baseadas em coordenadas cristalográficas reais (Ångströms convertidos para unidades de cena). O banco de dados público **PubChem** fornece coordenadas 3D via API REST gratuita:

```
https://pubchem.ncbi.nlm.nih.gov/rest/pug/compound/name/water/JSON
```

Para geometria VSEPR (predição de forma molecular), implemente o algoritmo de minimização de repulsão entre pares de elétrons: cada domínio eletrônico se posiciona para maximizar distância angular dos demais. Isso gera automaticamente geometrias tetraédricas, lineares, trigonais, etc.

**Renderização 3D dos átomos e ligações**

Com R3F, cada átomo vira um componente React:

```jsx
function Atom({ position, color, radius, symbol }) {
  const [hovered, setHovered] = useState(false);

  return (
    <mesh
      position={position}
      onPointerOver={() => setHovered(true)}
      onPointerOut={() => setHovered(false)}
    >
      <sphereGeometry args={[radius, 32, 32]} />
      <meshStandardMaterial
        color={color}
        roughness={0.3}
        metalness={0.1}
        emissive={hovered ? color : '#000000'}
        emissiveIntensity={hovered ? 0.3 : 0}
      />
    </mesh>
  );
}
```

Ligações são cilindros posicionados entre dois átomos. Calcule o ponto médio, rotação e comprimento dinamicamente:

```js
function getBondTransform(posA, posB) {
  const start = new THREE.Vector3(...posA);
  const end = new THREE.Vector3(...posB);
  const direction = end.clone().sub(start);
  const length = direction.length();
  const midpoint = start.clone().add(end).multiplyScalar(0.5);
  const quaternion = new THREE.Quaternion();
  quaternion.setFromUnitVectors(
    new THREE.Vector3(0, 1, 0),
    direction.normalize()
  );
  return { position: midpoint, quaternion, length };
}
```

Ligações duplas e triplas são representadas como dois ou três cilindros finos deslocados lateralmente em relação ao eixo da ligação.

**Iluminação e visual polido**

O diferencial visual de apps como esse está na iluminação. Use uma combinação:

```jsx
<ambientLight intensity={0.4} />
<directionalLight position={[10, 10, 5]} intensity={1.2} castShadow />
<pointLight position={[-5, 5, -5]} intensity={0.6} color="#4488ff" />
<Environment preset="studio" />  // drei: IBL (image-based lighting)
```

Adicione `bloom` para o efeito de brilho nos átomos usando `@react-three/postprocessing`:

```bash
npm install @react-three/postprocessing
```

```jsx
import { EffectComposer, Bloom } from '@react-three/postprocessing';

<EffectComposer>
  <Bloom luminanceThreshold={0.6} intensity={0.8} mipmapBlur />
</EffectComposer>
```

**Interatividade: seleção, rotação e painel de informações**

`OrbitControls` do Drei já fornece rotação/zoom com mouse e touch. Para seleção de átomo ao clicar, use raycasting nativo do Three.js integrado ao sistema de eventos do R3F (os handlers `onClick`, `onPointerOver` nos meshes). Ao selecionar um átomo, dispare um evento no Zustand para abrir o painel lateral com propriedades do elemento (número atômico, eletronegatividade, configuração eletrônica).

**Tabela periódica e busca**

Integre um JSON completo da tabela periódica (disponível em `github.com/Bowserinator/Periodic-Table-JSON`) como fonte de dados. Construa uma UI de tabela periódica 2D em CSS Grid que, ao clicar num elemento, carrega e exibe sua geometria 3D mais estável na cena.

## Stack e requisitos

- **Linguagem:** JavaScript/TypeScript (TypeScript fortemente recomendado para tipagem das estruturas moleculares)
- **Framework:** React 18+ com Vite 5+
- **3D:** Three.js r160+, @react-three/fiber 8+, @react-three/drei 9+
- **Pós-processamento:** @react-three/postprocessing 2+
- **Estado:** Zustand 4+
- **Dados:** PubChem REST API (gratuita, sem chave), Periodic-Table-JSON (open source)
- **Hardware cliente:** GPU integrada suficiente para moléculas simples; GPU dedicada para cenas com >50 átomos e bloom ativo
- **Sem backend:** 100% client-side, pode ser hospedado em GitHub Pages, Vercel ou Netlify gratuitamente
- **Custo:** R$ 0 (zero) para stack completo
- **Tempo de build:** <30s com Vite
- **Bundle size:** ~800KB gzipped com Three.js completo; use tree-shaking para reduzir

## Armadilhas e limitacoes

**Performance com moléculas grandes:** Proteínas com milhares de átomos travam o WebGL em mobile e GPUs fracas. O limite prático sem otimização é ~200 átomos. Para ir além, use `InstancedMesh` (renderiza milhares de esferas iguais em um único draw call) — isso exige refatorar toda a lógica de renderização de átomos.

**Coordenadas 3D nem sempre disponíveis:** A PubChem API retorna coordenadas 3D apenas para compostos com estrutura 3D depositada. Para moléculas raras ou hipotéticas, você precisará calcular geometria via VSEPR ou integrar um solver externo (como o RDKit compilado para WebAssembly).

**Rotação de cilindros é matematicamente traiçoeira:** O cálculo de quaternion para alinhar cilindros com ligações tem casos degenerados quando a ligação é paralela ao eixo Y (vetor padrão do cilindro). Adicione tratamento explícito para esse caso.

**Three.js e React: conflito de lifecycle:** Sem R3F, gerenciar Three.js dentro de `useEffect` manualmente causa memory leaks clássicos (geometrias e materiais não descartados). Sempre use o sistema de dispose do R3F ou chame `geometry.dispose()` e `material