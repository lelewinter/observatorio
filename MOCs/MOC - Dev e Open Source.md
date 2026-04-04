---
tags: [moc, dev, open-source, github, ferramentas, programacao, data-engineering, ml, arquitetura-software]
date: 2026-04-02
tipo: moc
---
# Dev e Open Source

Estratégias e recursos para dominar engenharia de software via curadoria de código aberto. O vault contém 27 notas cobrindo: (1) aprendizado acelado via repositórios GitHub e arquivos de referência; (2) padrões arquiteturais (holons, event-driven); (3) ferramentas locais que substituem SaaS caro; (4) processamento de dados, IA e infraestrutura; (5) síntese de voz, manipulação de mídia, web scraping para agentes autônomos.

## Aprendizado Acelerado via Repositórios GitHub

[[10-repositorios-github-data-engineering-essenciais|Data Engineering prática em 10 repositórios curados]] — seleção compilada por Durgesh Singh (líder GenAI na TCS) que cobre desde ETL com Airflow até streaming com Kafka e Data Warehousing. Mais eficaz que cursos online porque cada repo é projeto real que shipou em produção. Tempo típico: 20-40 horas para dominar, vs. 200h em curso tradicional. Caveats: assume comfort com CLI, SQL, Docker.

[[16_github_repos_melhor_curso_ml|16 Repositórios para ML melhores que qualquer curso de $1.000]] — cobertura de fundamentals (álgebra linear, stats) até aplicações (LLMs, diffusion models, reinforcement learning). Estrutura: cada repo tem README detalhado, papers originais, código anotado. Aprendizado ao vivo: executar código → entender resultados → modificar hiperparâmetros. Vantagem psicológica: progresso visível (outputs gráficos, métricas melhorando) vs. videos passivos.

[[mit-700-paginas-livro-algorithms-thinking|MIT: 700 páginas sobre como máquinas pensam via algoritmos]] — consolidação de algoritmos clássicos (sorting, graphs, dynamic programming, string matching) estruturados por **padrão de pensamento** não por linguagem. Relevante para entrevistas, design de sistemas, otimização de código. Trade-off: densidade alta (exige leitura ativa com implementação paralela), mas 100% não-repetitivo.

[[leetcode-e-50-porcento-entrevistas-engenharia-recursos-faltantes|LeetCode é necessário mas insuficiente]] — 200-300 problemas cobrem estructura e algorithms. Faltam 50%: system design (trade-offs de arquitetura, scaling, CAP theorem) e behavioral (communication, conflict resolution). Solução: LeetCode → System Design Interviews (Alex Xu) → behavioral prep (STAR method). Timeline: 3-4 meses, 15h/semana.

## Padrões Arquiteturais e Orquestração

[[arquitetura-holonomica-de-software|Holos (Holons) em Microsserviços]] — cada serviço é "holon": autônomo internamente (banco de dados próprio, lógica encapsulada) + parte de sistema maior (eventos assíncronos, contratos bem-definidos). Princípios: (1) autonomia (serviço não chama outro serviço síncronamente), (2) integração via eventos (Kafka, RabbitMQ), (3) desacoplamento em níveis (holarchy). Implementação: definir change-philosophy.md (modo de pensar sobre mudanças), problem-space.md (o quê está quebrado), solution-space.md (arquitetura). Armadilhas: confundir "evento" com RPC disfarçado (esperando resposta síncrona), eventual consistency exigindo retry/reconciliação.

## Alternativas Open-Source a Soluções Caras

[[alternativas-open-source-ao-bloomberg-terminal-podem-ser-executadas-localmente-s|OpenBB Terminal substitui Bloomberg ($24k/ano) por open-source]] — roda 100% local, integra Yahoo Finance, FRED, Alpha Vantage. Casos: screening de ações (P/L < 15, crescimento > 10%), análise técnica com SMA/RSI, alertas automatizados. Stack: Python + Plotly + Pandas. Limitações: latência 15-20min (vs. Bloomberg real-time), APIs públicas têm rate limits, cobertura geográfica limitada (EUA/China principalmente).

[[clonagem-de-voz-local-open-source|LuxTTS clona qualquer voz de 3 segundos de áudio localmente]] — TTS open-source executa em 1GB VRAM, 150x real-time speed. Casos: audiobooks personalizados (extrair voz do autor, gerar capítulos), NPCs em jogos (diferentes vozes de personagens), assistente pessoal. Requisitos: GPU NVIDIA (CPU 0.5x real-time, inviável) ou acesso a Hugging Face demo (free). Limitações: 3 seg é mínimo (10-30 seg melhor), idiomas menores têm qualidade baixa, pitch/emoção não são replicadas.

## Processamento de Mídia e Dados

[[conversao-de-documentos-para-audiobooks-com-tts|PDF/ebook → audiobook via TTS]] — pipeline prático: extrai texto (PyPDF2), divide em chunks (5 min máximo), clona voz de referência, renderiza chunks paralelos, concatena. Resultado: livro de 300 páginas → ~10h de áudio em <1h de compute. Economia: $1.000-5.000 em narrator profissional.

[[conversao-de-pdf-para-markdown-via-cpu|PDF → Markdown sem GPU]] — OCR via CPU com PaddleOCR ou Tesseract (5-15 min por página, vs. 30s com GPU). Útil para documentos sem OCR embutido. Output preserva estrutura (títulos, listas, tabelas).

[[transcricao-de-audio-local-com-gpu|Transcrição de áudio local com Whisper (OpenAI)]] — transcreve em 30 minutos de áudio em ~1 minuto de GPU (RTX 3080), multilíngue, timestamp preciso. Vs. APIs cloud: latência reduzida (não envia pela rede), privacidade (tudo local), custo zero recorrente.

## Web Scraping e Agentes Autônomos

[[web-scraping-sem-api-para-agentes-ia|Web scraping para agentes sem API]] — técnicas quando site não expõe dados via API: headless Chrome (Playwright/Puppeteer), análise de HTML (BeautifulSoup), extrações via LLM (Claude lendo página + prompt estruturado). Caso: dados financeiros de site sem API → scrape HTML → Claude extrai tabelas → export CSV. Vantagem: mais rápido e mais barato que construir against-API (sem rate limits, sem autenticação), mas frágil (HTML muda).

[[design-generativo-por-ia|Design generativo com IA]] — pipeline onde agentes geram variações de design (layouts, cores, tipografia) baseado em constraints (brand, accessibility). Output: CSS/SVG/React pronto. Aplicação: A/B testing acelerado, geração de landing pages.

[[conversao-html-para-react-com-vibe-coding|HTML → React via "vibe coding"]] — Claude lê componente HTML, entende estrutura/intenção (vibe), reescreve como React component reutilizável com props. Vantagem: automação de refatoração, reduz boilerplate.

## Arquitetura Holística e Filosofia de Design

[[braco-robotico-open-source|Robotic arm open-source]] — arquivos CAD completos (fabricação CNC/3D print), BOM (bill of materials), códigos de controle (Python/ROS). Demonstra filosofia: hardware + software juntos, open design reduz custo de replicação de 50k para ~500.

[[framework-opinado-para-jogos-threejs|Three.js framework opinado para games]] — abstração sobre Three.js que oferece convenções (scene structure, event handling, asset loading), reduzindo boilerplate de 3.000 linhas para 300.

## Recursos e Educação

[[apis-publicas-gratuitas|Compilação de 100+ APIs públicas gratuitas]] — dados de câmalas, clima, cotações, geolocalização, sem autenticação ou com free tier. Útil para protótipos rápidos, demos.

[[leitor-de-ebooks-com-busca-semantica|E-book reader com busca semântica]] — integra embeddings (SentenceTransformers) com ebook reader, busca por conceito (não just keywords). Exemplo: "como criar hábitos?" retorna capítulos relevantes mesmo se não mencionam "hábito" explicitamente.

[[browser-chromium-no-terminal|Chromium no terminal]] — renderizar e capturar screenshots de páginas web via CLI (útil para testes automatizados, scraping visual, debugging).

[[world-model-interativo-em-tempo-real|World model interativo]] — simulação 2D física em tempo real no browser (webgl), treina modelos de predição visual.

[[spec-driven-ai-coding|Spec-driven AI coding]] — workflow onde Claude gera código a partir de especificação formal (OpenAPI, JSON Schema), resultando em acurácia 90%+ (vs. prompt genérico 60%).

## Síntese de Voz e Media

[[tts-open-source-local|TTS open-source local]] — alternativas a LuxTTS: Glow-TTS (rápido), Tacotron 2 (qualidade), VoiceConversion (mudar idade/gênero). Trade-offs: velocidade vs. qualidade.

## Renderização e Layout

[[renderizacao-virtualizada-de-terminal|Terminal virtualizado de alta performance]] — rendering de terminal (potencialmente milhões de cells) sem lag. Relevante para TUI (terminal UI) de alta performance.

[[medicao-de-texto-sem-dom|Medir texto sem DOM]] — JavaScript que calcula width/height de texto sem renderizar (via metricas de font). Útil para layout dinâmico pré-computado.

[[layout-de-texto-sem-dom|Pretext: layout de texto sem CSS]] — biblioteca TypeScript de Cheng Lou (criador React, ex-Messenger, ex-Midjourney) que faz layout de texto via algoritmo puro (sem DOM). Relevante para renderização de texto em canvas/WebGL/PDF.

## Estado Atual e Tendências

2026 marca consolidação de "aprendizado via código" sobre "aprendizado via vídeo". GitHub é principal fonte de verdade, repositórios curados (top 10, top 16) resolvem "paradox of choice". Open-source substitui SaaS em (1) tools financeiras (OpenBB), (2) processamento de mídia (Whisper, LuxTTS), (3) simulation/rendering (Three.js, Chromium headless). Gargalo atual: integração entre ferramentas (cada tool é ponta isolada). Expectativa: orquestração via agentes (agente lê spec → escolhe tool → chama com parâmetros → integra resultado).

## Ferramentas e Stack Prático

**Data Engineering**: Airflow (orchestration), Kafka (streaming), DuckDB (OLAP local), PostgreSQL (transational).

**ML/AI**: PyTorch/TensorFlow (training), Hugging Face (models), Scikit-learn (classics), PennyLane (quantum ML).

**Architecture**: Docker (containers), Kubernetes (orchestration), Terraform (IaC), Event Bus (Kafka/RabbitMQ).

**Media**: FFmpeg (audio/video), Whisper (transcription), LuxTTS (voice clone), Pillow (images).

**Web/Frontend**: Three.js (3D), React (UI), Playwright (automation), BeautifulSoup (scraping).

**Tools**: OpenBB (finance terminal), Celonis (process mining), GDPR-compliant alternatives.

**Languages**: Python (scripting, ML), TypeScript/JavaScript (web), Rust (performance), Go (infrastructure).

## Conexões com Outros Temas

Padrões arquiteturais conectam com [[MOC - IA e LLMs]] via orquestração de agentes e feedback loops. Processamento de mídia (Whisper, LuxTTS) alimenta [[MOC - Games e 3D]] (voice acting para NPCs) e [[MOC - Dados e Automacao]] (podcasts, análise). Ferramentas locais são filosofia de [[MOC - Seguranca]] (dados nunca deixam máquina). Open-source é base de [[MOC - Negocios e Startups]] (MVP com custo ~$0 em ferramentas).
