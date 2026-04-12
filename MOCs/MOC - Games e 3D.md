---
tags: [moc, games, 3d, gamedev, three-js, comfyui, computer-vision, webgpu, neural-rendering]
date: 2026-04-02
tipo: moc
---
# Games e 3D

Panorama completo de game development moderno, geração 3D por IA, renderização em tempo real via browser, e computer vision integrada em jogos. O vault contém 34 notas mapeando ferramentas, técnicas e arquiteturas para criar experiências 3D interativas desde o protótipo até produção, com foco em soluções open-source, local-first e browser-native que eliminam barreiras de acesso para devs solo.

## Geração 3D Acelerada por IA

A captura e síntese 3D atravessou transição crítica em 2024-2025. [[geracao-3d-a-partir-de-imagem|TRELLIS-2 (Microsoft, 4B parâmetros) converte foto 2D em malha 3D texturizada com PBR em <100ms via representação O-Voxel]]. O fluxo prático: carregar imagem, rodar inferência em GPU (RTX 3060+ requer 50-100ms), exportar GLB pronto para Unreal/Unity. Limitações conhecidas incluem ambiguidade de profundidade (sem múltiplas vistas, o modelo "adivinha") e reflexos/transparência (vidro e metal geram geometria estranha). Workaround: usar prompts negativos fortes e remeshing via Instant Meshes se detalhes finos forem críticos.

[[nvidia-kimodo-geracao-de-animacao-3d-com-ia|NVIDIA Kimodo]] — gerador de animações 3D nativas via IA, acelerando produção de cinemáticas e cinematics em engines. [[tripo-p10-topologia-quad-limpa-para-engines|Tripo P1.0]] — síntese 3D rápida com topologia quad limpa, otimizada para game engines.

Paralelo a síntese de malha está [[3d-gaussian-splatting|Gaussian Splatting para reconstrução fotométrica de cenas reais]]. OpenSplat (C++ open-source) transforma 100-200 fotografias de uma cena em representação volumétrica renderizável em tempo real (60-120 FPS). Pipeline: Structure-from-Motion via COLMAP, otimização iterativa de gaussianas (5-10 min em RTX 3080 para cena média), export como `.splat` comprimido (~20-50MB). Integração em game engines via NVIDIA Kaolin Wisp (Unreal 5) ou Three.js loaders para web. Trade-offs: cenas maiores que 100m² exigem RAM excessiva (~32GB), dinâmica é limitada (gaussianas estáticas), edição pós-reconstrução é manual.

Tecnologias emergentes como [[geracao-procedural-de-personagens-e-mapas-isometricos|geração procedural de sprites isométricos]] e [[geracao-de-sites-3d-com-ia|síntese de sites 3D via IA]] expandem para domínios específicos. O denominador comum: todos exploram representações compactas (voxels, splats, sprites procedurais) que podem ser renderizadas eficientemente em hardware consumer.

## Renderização Tempo Real em Browser e WebAssembly

Three.js permanece padrão de facto para visualização 3D em navegador, com Two.js cobrindo 2D. [[mvp-3d-no-browser-com-threejs-e-cesiumjs|Protótipos MVP usando Three.js + CesiumJS]] demonstram que aplicações geoespaciais completas rodamem browser sem servidor custom. WebGPU (sucessor a WebGL) oferece acesso direto a GPU com overhead reduzido. [[renderizacao-de-grama-3d-com-webgpu|Renderização de grama procedural com WebGPU]] mostra que efeitos visuais complexos são viáveis: compute shaders paralelos para instancing massivo, resultando em paisagens com bilhões de fios de grama a 60 FPS.

[[webassembly-supera-performance-nativa|WebAssembly supera performance nativa em certos cenários]] quando otimizado para SIMD e memory layout. Implicação prática: portar C++/Rust para WASM (via Emscripten/wasm-pack) resulta em executáveis 5-10x mais rápidos que JavaScript puro para processamento intensivo (path tracing, cálculos de física). Limitações: debugging é mais complicado, tamanho de binário inicial é 2-5MB, e nem todos browsers suportam SIMD uniformemente (fallback necessário).

## Computer Vision Integrada em Tempo Real

MediaPipe (Google) é ferramenta mais prática para integrar computer vision localmente. [[MediaPipe Face Recognition Local Edge|Face detection/landmarks roda inteiramente no browser via WebGL ou WebAssembly sem cloud]]. 16 landmarks faciais com latência <100ms em dispositivo mobile. [[Micro-Handpose WebGPU Hand Tracking Browser|Hand tracking otimizado (Micro-Handpose) usa WebGPU compute shaders para rastreamento de 21 pontos (mão inteira) em tempo real]].

Caso de uso prático: [[tony-stark-jarvis-visualizacao-3d-mediapipe|Tony Stark & Jarvis — UI 3D holográfica onde gestos de mão controlam visualização de dados]]. Fluxo: capturar mão via webcam → MediaPipe extrai 21 landmarks → mapear para controles 3D (pan/zoom/rotate) → renderizar via Three.js. Funciona em browser padrão, requer <2GB RAM, zero cloud.

Repository [[github-fun-with-cv-tutorials-collidingscopes|fun-with-cv-tutorials]] agrega 40+ tutoriais com código pronto: detecção de objeto, pose estimation, segmentação semântica. Cada tutorial é <200 linhas, autocontido.

## Game Design e Prototipagem Sem Código

Antes de engine real (Unity/Unreal), prototipagem rápida economiza semanas. [[ferramentas-prototipagem-game-designers-sem-codigo|Matriz decisória: qual ferramenta para qual pergunta]]. GameMaker para mecânicas 2D (~8-16h validação), Twine para narrativa (~4-8h), Figma para UX (~2-4h), Bitsy para atmosfera visual (~2-3h). Fluxo recomendado: Dia 1 Twine (outline), Dia 2 Figma (mockup), Dia 3 GameMaker (loop gameplay), Dia 4 user testing. Decisão: se <2h feedback = volta para no-code; se >4h testing = prosseguir para engine.

[[12-principios-animacao-disney-funcionam-diferente-em-games|Princípios Disney em games requerem inversão lógica]]. Em filme, animação serve diretor. Em game, serve jogador em tempo real. Squash & Stretch em filme é 50% deformação/50ms; em game é 10-15% deformação/<50ms (player sente responsividade). Anticipation em filme presságia movimento (250-300ms); em game máximo 30-50ms (input lag frustra). Solução técnica: usar `Time.deltaTime` (frame-rate independent), easing curves para feedback (ease-out rápido em hit reaction = "juicy" feel).

## Assets de Jogo via IA: Avaliação Crítica

Mercado de ferramentas IA para geração de game assets explodiu em 2024-2025. [[saturacao-de-ferramentas-ia-para-game-assets-exige-criterio-para-distinguir-solu|Critério para avaliar: obra real do criador vs. vibecoding superficial]]. Red flags: demo com assets genéricos/feios, prompts não exportáveis, sem casos reais documentados. Green flags: criadores com portfólio games, exemplos antes/depois do seu tool, integração com pipelines reais (Blender, engine). [[vibe-coding-para-desenvolvimento-de-jogos|Vibe Coding]] demonstra que LLMs podem gerar integralmente código, assets e design de fases em ciclos iterativos, transformando desenvolvedor solo em diretor criativo. [[rl-agent-hollow-knight-reinforcement-learning|RL Agent Hollow Knight]] — agente treinado via reinforcement learning para jogar Hollow Knight, demonstrando aplicabilidade prática de RL em game design e QA.

[[geracao-de-assets-3d-com-ia|Geração 3D com IA]] (TRELLIS, Meshy, Kaedim) funciona bem para objetos simples (cadeiras, mesas, armas). Falha em: (1) humanoides (rostos deformados, proporções erradas), (2) topologia otimizada (mesh tem triângulos desnecessários), (3) PBR fino (texturas são baked, não procedurais). Mitigação: usar para rough blockout, depois artista faz retopo/textura em Blender.

[[geracao-de-sprites-isometricos-com-ia|Sprites isométricos]] e [[geracao-de-modelos-3d-por-comando|modelos via prompt texto]] são mais determinísticos e práticos que meshes complexos. Exemplo real: jogo indie com 500 NPCs — usar IA para gerar variações de corpo/roupa economiza 6 meses vs. manual.

## Curadoria de Recursos e Educação

[[10-youtube-gems-solo-game-devs|10 canais YouTube para devs solo]] cobertas: sistemas de monetização (Brackeys), game feel ("juicy" mechanics), otimização de performance. Mais útil que cursos pagos porque são criados por devs que realmente shipparam jogos.

[[repositorios-open-source-curados-centralizam-recursos-de-desenvolvimento-de-jogo|Repositórios curados (GameDev-Resources no GitHub)]] centralizam engines, assets, áudio, tutoriais. Elimina "paralysis of choice" — todos os links já foram validados por comunidade.

[[jogos-indie-podem-se-tornar-ferramentas-acidentais-de-treinamento-profissional-a|Indie games como ferramentas de treinamento]]  — caso real onde jogo vendido por $20 tornou-se ferramenta profissional para treinar operadores de máquinas pesadas. Game design acidental: mecânicas coincidiam com skills reais, melhor pedagogia que software de treinamento caro.

## Workflows Proprietários vs. Open-Source

[[ComfyUI Posicionamento Agent Wave|ComfyUI é única ferramenta node-based open-source agnóstica de modelo]] que pode ser manipulada por agentes de IA. Workflows em JSON, extensível via custom nodes, API completa. Comparado a Midjourney/Runway (fechadas): zero lock-in, qualquer modelo (SD, SDXL, custom), versionável em Git. Setup: 2-3h para primeiros modelos, depois iteração rápida. [[Editor 3D Open Source para Construcao Arquitetonica|Pascal Editor]] — editor 3D browser-native open-source para cenas arquitetônicas, sem download.

Trade-off: open-source requer mais setup inicial vs. proprietário. Mas longo prazo: controle, custo zero, integração em pipelines custom.

## Estado Atual e Tendências

2026 marca transição de "IA gera assets" para "IA otimiza pipeline completo". ComfyUI + agentes de IA = workflow onde prompt gera conceito → malha 3D → animação → integração em engine. [[workflow-3d-completo-via-mcp|Workflows 3D via MCP]] estendem essa orquestração: agentes encadeiam geração, rigging, retexturização e animação automaticamente. [[unity-mcp-integracao-llm-com-game-engine|Unity-MCP]] permite que agentes não apenas gerem assets, mas executem ações direto no editor e runtime, viabilizando loops autônomos de desenvolvimento. MediaPipe + WebGPU = interactive 3D experiências no browser sem download. Gaussian Splatting demonstra que fotografias reais podem virar assets prontos para engine (relevante para fotogrametria de estúdio).

Gargalo atual: custo computacional em hardware consumer (GPU 8GB+ requerida para TRELLIS, simulação de grama em WebGPU) e falta de integração automática entre ferramentas (cada ferramenta é ponta isolada, glue manual necessário). Expectativa 2026-2027: frameworks que orquestram (IA gera → otimiza → exporta → integra) emergem.

## Ferramentas e Stack Prático

**Geração 3D**: TRELLIS-2 (local, 100ms), Gaussian Splatting via OpenSplat (local, 5-15 min), Meshy/Kaedim (cloud, $10-100/modelo).

**Renderização**: Three.js (browser 3D), WebGPU (performance avançada), Unity/Unreal (produção), Godot (open-source engine).

**Game Design**: Twine (narrativa), Figma (UX), GameMaker (2D), Bitsy (exploração pixel art).

**Computer Vision**: MediaPipe (face/hand local), OpenCV (processamento clássico), YOLO (detecção objeto).

**Prototipagem**: Construct 3 (drag-drop), Flickgame (5 min), Godot (free, node-based).

**Asset Creation**: Blender (open-source 3D art), Krita (digital painting), Aseprite (pixel art, $20).

**Curadorias**: GameDev-Resources (GitHub), 10-youtube-gems (curado por devs).

## Atualizacoes Abril 2026

- **Gaussian Splatting standardized**: KHR_gaussian_splatting glTF extension (Khronos, backed by Google/NVIDIA/Apple) torna 3GS compatível com qualquer game engine via standard aberto
- **FastGS**: Treina 3DGS em 100 segundos (CVPR 2026), reduzindo barreira de entrada para fotogrametria em tempo real
- **WebGPU now in 95% of browsers**: Safari 26 completou rollout global, viabilizando shader-intensive 3D apps sem fallback WebGL
- **Three.js WebGPU integration seamless since r171+**: integração nativa simplifica porting de código WebGL existente
- **Unity 6.4 released with AI Beta tools**: ferramentas de geração de assets e code generation integradas ao editor
- **GTA 6 launch Nov 19 2026**, Project ROME modding engine com official mod marketplace — padrão novo para monetização de user-generated content
- **Tripo P1.0**: Fast 3D com topologia quad limpa, pronto para game engines (vs. Meshy/Kaedim com geometria suja)
- **ComfyUI Cloud exited beta**, Qwen diffusion model support — acesso fácil a custom diffusion models sem setup local

## Conexões com Outros Temas

Geração 3D conecta com [[MOC - IA e LLMs]] via orquestração de agentes (ComfyUI + Claude para pipelines automatizados). Realtime rendering em WebGPU cruza [[MOC - Dev e Open Source]] (WASM, bibliotecas optimization). Computer vision é ponte para [[MOC - Dados e Automacao]] (MediaPipe integrado em bots/agents). Game feel e animação dependem de compreensão de [[MOC - Negocios e Startups]] (indie games como validação de mercado rápida, protótipos reduzem burn rate).
