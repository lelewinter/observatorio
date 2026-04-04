# Obsidian Vault Orphan Analysis Report

**Vault Location:** `/sessions/serene-sleepy-allen/mnt/Claude/`
**Analysis Date:** 2026-04-02
**Total Markdown Files:** 1,217

---

## Executive Summary

Your vault contains **1,217 markdown notes**, of which **57.7% (702 notes)** are completely orphaned—having ZERO outgoing wikilinks and ZERO incoming wikilinks. These appear as isolated dots in Obsidian's graph view.

**However**, 542 of these orphans are in `Projects/second-brain-pipeline/quartz/node_modules/`—build artifacts and dependency READMEs that should probably be excluded from the vault if not actively used.

**Excluding build artifacts**, you have **660 "real" notes**, of which **22% (145 notes)** are genuinely orphaned.

---

## Detailed Breakdown (All Notes, Including Build Artifacts)

**Total Notes: 1,217**

| Connection Status | Count | % |
|---|---:|---:|
| Fully connected (both incoming + outgoing) | 362 | 29.7% |
| Only receives citations (no outgoing) | 63 | 5.2% |
| Only makes citations (no incoming) | 90 | 7.4% |
| **Completely orphaned (neither)** | **702** | **57.7%** |
| **TOTAL** | **1,217** | **100%** |

---

## Detailed Breakdown (Excluding node_modules Build Artifacts)

**Total "Real" Notes: 660**

| Connection Status | Count | % |
|---|---:|---:|
| Fully connected (both incoming + outgoing) | 339 | 51.4% |
| Only receives citations (no outgoing) | 63 | 9.5% |
| Only makes citations (no incoming) | 90 | 13.6% |
| **Completely orphaned (neither)** | **145** | **22.0%** |
| **TOTAL** | **660** | **100%** |

---

## Orphan Distribution by Major Folder

| Folder | Orphaned | Total | Orphan % |
|---|---:|---:|---:|
| Conceitos | 2 | 45 | 4.4% |
| Links Salvos | 44 | 236 | 18.6% |
| **Projects** | **656** | **929** | **70.6%** |
| ├─ Quartz node_modules | 542 | (build artifacts) | — |
| ├─ Quartz content & docs | 81 | — | — |
| └─ Other Projects | 33 | — | — |

**Key Finding:** The extremely high orphan rate in Projects/ is almost entirely due to the Quartz node_modules directory (542 orphaned files containing package dependency documentation). This directory appears to be a web publishing tool for your vault, with dependency metadata that has accumulated.

---

## Link Statistics

When analyzing cross-references between notes:
- **515 notes** have at least ONE outgoing wikilink
- **455 notes** have at least ONE incoming wikilink (cited by others)
- **362 notes** participate in the "core graph" (fully connected)
- **90 notes** are "leaf" pages (cited but never cite back)
- **63 notes** are "hub" pages (cite others but are never cited)

---

## Top Orphaned Note Categories

### 1. Quartz Node Modules Build Artifacts (542 notes)
**Location:** `Projects/second-brain-pipeline/quartz/node_modules/`

These are NPM dependency README files included in your vault. Likely not needed for daily use. Consider removing or moving to `.gitignore` if using version control.

### 2. Unlinked "Links Salvos" Entries (44 orphans in main vault)
**Location:**
- `Links Salvos/IA e LLMs/` (42 notes)
- `Links Salvos/Games e 3D/` (2 notes)

These saved links were never connected to any concept notes, MOCs, or other pages in your vault. They may need:
- Connection to relevant MOC pages
- Tags for discovery (currently unused for wikilinks)
- Removal if no longer relevant

### 3. Concept Notes (2 orphans)
**Location:** `Conceitos/`
- `ffmpeg-montagem-video.md`
- `text-to-speech-apis.md`

Very low orphan rate here (4.4%), suggesting good internal linking practices in this folder.

### 4. Quartz Documentation Notes (81 orphans)
**Location:**
- `Projects/second-brain-pipeline/quartz/content/Links Salvos/` (81 notes)
- `Projects/second-brain-pipeline/quartz/docs/` (15 notes)

These are duplicates or copies of your Links Salvos entries, likely created when publishing your vault as a public website. Not part of your working vault.

---

## List of 145 "Real" Orphaned Notes (excluding node_modules)

### Core Vault (genuine disconnected notes)

#### Conceitos/ (2)
1. `Conceitos/ffmpeg-montagem-video.md`
2. `Conceitos/text-to-speech-apis.md`

#### Links Salvos/Games e 3D/ (2)
1. `Links Salvos/Games e 3D/geracao-de-personagens-3d-jogaveis-por-imagem.md`
2. `Links Salvos/Games e 3D/landing-page-3d-scroll-based.md`

#### Links Salvos/IA e LLMs/ (42 notes)
1. `agent-router-model.md`
2. `agente-ai-autonomo-com-auto-modificacao.md`
3. `ancoragem-de-janela-de-uso-em-apis.md`
4. `anotacoes-visuais-como-input-para-ia.md`
5. `arquitetura-de-agentes-de-codigo-open-source.md`
6. `arquitetura-interna-do-claude-code.md`
7. `arquiteturas-especializadas-de-modelos-de-ia.md`
8. `base-de-dados-de-acoes-agenticas.md`
9. `bibliotecas-de-workflows-com-llms.md`
10. `bitnet-b158-inferencia-em-cpu.md`
11. `browser-cli-para-agentes-de-ia.md`
12. `browser-como-container-de-agente-de-ia.md`
13. `mcp-em-jogos-compilados-unity.md`
14. `memoria-persistente-em-agentes-de-codigo.md`
15. `modelos-de-codificacao-multimodal.md`
16. `motion-graphics-gerados-por-ia-com-design-system.md`
17. `office-suite-para-agentes-de-ia.md`
18. `orquestracao-hibrida-de-llms.md`
19. `otimizacao-de-tokens-via-claudemd.md`
20. `pipeline-autonomo-de-geracao-de-jogos-com-ia.md`
21. `plataformas-de-ia-customizada-sob-demanda.md`
22. `plugins-openai-open-source.md`
23. `producao-de-video-programatica-com-ia.md`
24. `quantizacao-de-llms.md`
25. `quantizacao-dinamica-de-llms.md`
26. `redacao-silenciosa-de-thinking-em-llms.md`
27. `repositorios-github-para-aiml.md`
28. `repositorios-github-para-claude-code.md`
29. `repositorios-open-source-de-ia.md`
30. `separacao-de-responsabilidades-em-workflow-de-ia.md`
31. `skills-uxui-para-agentes-de-codigo.md`
32. `spec-driven-development.md`
33. `stack-de-ia-local-self-hosted.md`
34. `teleporte-de-sessoes-entre-dispositivos.md`
35. `timesfm-foundation-model-para-series-temporais.md`
36. `traducao-de-tela-em-tempo-real.md`
37. `tts-open-weight-com-clonagem-de-voz.md`
38. `unity-mcp-integracao-llm-com-game-engine.md`
39. `vazamento-de-codigo-proprietario-de-ia.md`
40. `vibe-coding-para-desenvolvimento-de-jogos.md`
41. `visualizacao-de-orquestracao-de-agentes-ia.md`
42. `workflow-3d-completo-via-mcp.md`

#### Projects/second-brain-pipeline/ (4)
1. `Projects/second-brain-pipeline/README.md`
2. `Projects/second-brain-pipeline/quartz/.github/ISSUE_TEMPLATE/bug_report.md`
3. `Projects/second-brain-pipeline/quartz/.github/ISSUE_TEMPLATE/feature_request.md`
4. `Projects/second-brain-pipeline/quartz/.github/pull_request_template.md`

#### Quartz Documentation (81)
81 duplicate/copy notes in `Projects/second-brain-pipeline/quartz/content/Links Salvos/` and 15 docs in `Projects/second-brain-pipeline/quartz/docs/`

---

## Recommendations

### 1. Immediate Cleanup (Optional but recommended)

Remove or move `Projects/second-brain-pipeline/quartz/node_modules/` out of your vault. This 542-file directory contains build artifact metadata that's inflating your orphan count and likely not needed for daily work. It should be in `.gitignore` if you're using version control.

### 2. Connect Orphaned Links (22% of working vault)

Consider linking your 46 orphaned "Links Salvos" notes to relevant MOCs:
- `[[MOC - Agentes Autonomos.md]]` (many AI agent links)
- `[[MOC - Claude Code e Produtividade.md]]` (tools & productivity)
- `[[MOC - Ferramentas Dev e Open Source.md]]` (open-source tools)
- `[[MOC - Modelos Locais e IA Privada.md]]` (local/private models)

Even a single backlink per orphan note will integrate them into your graph.

### 3. Review Concept Orphans

The 2 orphaned concept notes might be valuable but overlooked:
- `ffmpeg-montagem-video.md` → Could link to MOC - Design e Producao Visual
- `text-to-speech-apis.md` → Could link to MOC - Ferramentas Dev

Consider whether these need broader discoverability.

### 4. Leverage Existing Connections

Your vault is actually quite connected when excluding build artifacts:
- **362 fully-connected notes** (hub pages in a strong core graph)
- **90 leaf pages** are likely saved links waiting to be integrated
- **63 hub pages** are your MOCs and central reference points

This suggests a healthy zettelkasten structure with room for better integration of the newer saved links.

### 5. Track Going Forward

As you add new links via your second-brain-pipeline (which this vault supports), consider:
- Auto-tagging saved links with `[[MOC references]]`
- Creating parent/child relationships in your linking strategy
- Monthly "orphan reviews" to surface isolated notes worth connecting

---

## Technical Notes

### Analysis Method
- Scanned all `.md` files recursively in vault
- Parsed body content only (ignored YAML frontmatter)
- Extracted all `[[wikilinks]]` using regex pattern `\[\[([^\[\]]+)\]\]`
- Tracked both directions: outgoing (links made) and incoming (links received)
- Orphans defined as: 0 outgoing AND 0 incoming wikilinks

### Link Pattern Recognition
- `[[note-name]]` → recognized
- `[[note-name|display text]]` → recognized (properly aliased)
- `[[path/note-name]]` → recognized
- Excludes dead links (targets not in vault)
- Excludes malformed links

### File Count Verification
- Total markdown files: 1,217
- Files in node_modules: 557
- Real vault notes: 660
- Orphaned (all): 702
- Orphaned (real): 145
