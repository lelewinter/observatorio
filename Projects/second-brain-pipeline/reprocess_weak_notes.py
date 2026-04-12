#!/usr/bin/env python3
"""
Reprocessador de notas fracas — Second Brain Pipeline
Escaneia notas em Links Salvos, identifica as que estao abaixo do threshold
de qualidade (baseado em linhas de conteudo), e reprocessa usando o prompt
melhorado com mais profundidade.

Uso:
  python reprocess_weak_notes.py --scan              # lista notas fracas
  python reprocess_weak_notes.py --reprocess          # reprocessa todas as fracas
  python reprocess_weak_notes.py --reprocess --limit 5  # reprocessa ate 5
  python reprocess_weak_notes.py --test FILENAME      # reprocessa 1 nota especifica (teste)
  python reprocess_weak_notes.py --dry-run            # mostra o que faria sem salvar
"""

import json
import re
import sys
import shutil
import argparse
import logging
from pathlib import Path
from datetime import datetime

# Reutiliza funcoes do pipeline principal
sys.path.insert(0, str(Path(__file__).parent))
from pipeline import (
    load_config, generate_note, extract_content, extract_filename,
    get_existing_notes, build_vault_context, pre_extract,
    api_call_with_retry, NOTE_PROMPT, extract_text_from_response,
)
from anthropic import Anthropic

log = logging.getLogger("reprocess")
log.setLevel(logging.INFO)
_console = logging.StreamHandler()
_console.setFormatter(logging.Formatter("%(asctime)s [%(levelname)s] %(message)s", datefmt="%H:%M:%S"))
log.addHandler(_console)

# ── Threshold de qualidade ──────────────────────────────────────────────────
MIN_LINES = 60          # notas com menos de 60 linhas sao consideradas fracas
MIN_SECTIONS = 4        # precisa ter pelo menos 4 secoes (## headers)
MIN_CODE_BLOCKS = 1     # precisa ter pelo menos 1 bloco de codigo


def analyze_note(filepath: Path) -> dict:
    """Analisa qualidade de uma nota e retorna metricas."""
    text = filepath.read_text(encoding="utf-8")
    lines = text.splitlines()
    total_lines = len(lines)

    # Contar secoes (## headers)
    sections = [l for l in lines if l.startswith("## ")]

    # Contar blocos de codigo
    code_blocks = text.count("```")  // 2  # cada bloco tem abertura e fechamento

    # Extrair source URL do frontmatter
    source_url = ""
    for line in lines:
        if line.startswith("source:"):
            source_url = line.replace("source:", "").strip()
            break

    # Extrair tags
    tags = []
    for line in lines:
        if line.strip().startswith("tags:"):
            tags = re.findall(r'[\w-]+', line)
            tags = [t for t in tags if t != "tags"]
            break

    # Extrair titulo
    title = ""
    for line in lines:
        if line.startswith("# ") and not line.startswith("##"):
            title = line[2:].strip()
            break

    # Score de qualidade (0-100)
    score = 0
    score += min(total_lines, 150) / 150 * 40    # ate 40 pontos por tamanho
    score += min(len(sections), 6) / 6 * 25       # ate 25 pontos por secoes
    score += min(code_blocks, 3) / 3 * 20          # ate 20 pontos por codigo
    score += (15 if source_url else 0)              # 15 pontos por ter source

    is_weak = (
        total_lines < MIN_LINES
        or len(sections) < MIN_SECTIONS
        or code_blocks < MIN_CODE_BLOCKS
    )

    return {
        "filepath": filepath,
        "filename": filepath.name,
        "title": title,
        "lines": total_lines,
        "sections": len(sections),
        "code_blocks": code_blocks,
        "source_url": source_url,
        "tags": tags,
        "score": round(score, 1),
        "is_weak": is_weak,
    }


def scan_vault(vault_path: str) -> list[dict]:
    """Escaneia todas as notas e retorna analise de qualidade."""
    salvos = Path(vault_path) / "Links Salvos"
    results = []

    for f in sorted(salvos.rglob("*.md")):
        if f.stem.startswith("digest-") or f.stem.startswith("_"):
            continue
        try:
            analysis = analyze_note(f)
            results.append(analysis)
        except Exception as e:
            log.warning(f"Erro ao analisar {f.name}: {e}")

    return results


def reprocess_note(cfg: dict, client: Anthropic, note_info: dict,
                   existing_notes: list[dict], dry_run: bool = False) -> bool:
    """Reprocessa uma nota fraca gerando versao melhorada."""
    filepath = note_info["filepath"]
    source_url = note_info["source_url"]
    title = note_info["title"]
    tags = note_info["tags"]

    log.info(f"\n{'='*60}")
    log.info(f"Reprocessando: {note_info['filename']}")
    log.info(f"  Score atual: {note_info['score']}/100 ({note_info['lines']} linhas)")

    if not source_url or source_url.startswith("Telegram"):
        log.warning(f"  Sem URL de fonte, pulando")
        return False

    # 1. Re-extrair conteudo da URL original
    log.info(f"  Re-extraindo: {source_url[:70]}...")
    try:
        from pipeline import extract_content as ec
        extracted = ec(source_url)
        content = extracted.get("content", "")
        if extracted.get("title") and extracted["title"] != "Sem titulo":
            title = extracted["title"]
    except Exception as e:
        log.warning(f"  Falha na extracao: {e}")
        content = ""

    # Se extracao falhou, usar conteudo existente da nota como base
    if not content:
        log.info("  Usando conteudo da nota existente como base")
        content = filepath.read_text(encoding="utf-8")

    # 2. Build vault context
    vault_path = cfg.get("vault_path", "")
    context = build_vault_context(
        existing_notes, tags, vault_path,
        exclude_filename=filepath.name,
        title=title, content=content[:500]
    )

    if dry_run:
        log.info(f"  [dry-run] Geraria nota nova para: {title[:60]}")
        return True

    # 3. Gerar nota melhorada
    log.info(f"  Gerando nota melhorada com Sonnet...")
    source_label = "Twitter (X)" if "x.com" in source_url or "twitter.com" in source_url else source_url.split("/")[2] if "/" in source_url else "Web"

    note = generate_note(client, title, source_url, content, context, tags, source_label)

    if not note or len(note.splitlines()) < 40:
        log.warning(f"  Nota gerada muito curta ({len(note.splitlines())} linhas), mantendo original")
        return False

    # 4. Backup da nota original
    backup_dir = Path(vault_path) / "Links Salvos" / "_backups"
    backup_dir.mkdir(parents=True, exist_ok=True)
    backup_path = backup_dir / f"{filepath.stem}_backup_{datetime.now().strftime('%Y%m%d')}.md"
    shutil.copy2(filepath, backup_path)
    log.info(f"  Backup: {backup_path.name}")

    # 5. Adicionar registro de reprocessamento ao historico
    date_str = datetime.now().strftime("%Y-%m-%d")
    if "## Historico" in note:
        note = note.rstrip() + f"\n- {date_str}: Reprocessada (qualidade insuficiente, score {note_info['score']}/100)"
    else:
        note = note.rstrip() + f"\n\n## Historico\n- {date_str}: Reprocessada (qualidade insuficiente)"

    # 6. Salvar nota melhorada
    filepath.write_text(note, encoding="utf-8")
    new_lines = len(note.splitlines())
    log.info(f"  Salva: {note_info['lines']} -> {new_lines} linhas")

    return True


def main():
    parser = argparse.ArgumentParser(description="Reprocessador de notas fracas")
    parser.add_argument("--scan", action="store_true", help="Listar notas fracas")
    parser.add_argument("--reprocess", action="store_true", help="Reprocessar notas fracas")
    parser.add_argument("--test", type=str, help="Reprocessar uma nota especifica (filename)")
    parser.add_argument("--limit", type=int, default=999, help="Maximo de notas a reprocessar")
    parser.add_argument("--dry-run", action="store_true", help="Simular sem salvar")
    parser.add_argument("--threshold", type=int, default=MIN_LINES, help=f"Linhas minimas (default: {MIN_LINES})")
    args = parser.parse_args()

    cfg = load_config()
    vault_path = cfg.get("vault_path", "")

    if not vault_path:
        log.error("vault_path nao configurado")
        return

    # Scan
    log.info(f"Escaneando vault: {vault_path}")
    all_notes = scan_vault(vault_path)
    weak = [n for n in all_notes if n["is_weak"]]
    strong = [n for n in all_notes if not n["is_weak"]]

    log.info(f"\nResultado:")
    log.info(f"  Total: {len(all_notes)} notas")
    log.info(f"  Fortes (>={args.threshold} linhas, >=4 secoes, >=1 codigo): {len(strong)}")
    log.info(f"  Fracas: {len(weak)}")

    if args.scan or (not args.reprocess and not args.test):
        # Mostrar ranking de qualidade
        log.info(f"\n{'─'*70}")
        log.info("NOTAS FRACAS (ordenadas por score):")
        log.info(f"{'─'*70}")
        for n in sorted(weak, key=lambda x: x["score"]):
            has_url = "✓" if n["source_url"] and not n["source_url"].startswith("Telegram") else "✗"
            log.info(f"  [{n['score']:5.1f}] {n['lines']:3d}L {n['sections']}S {n['code_blocks']}C url:{has_url}  {n['filename'][:55]}")

        reprocessable = [n for n in weak if n["source_url"] and not n["source_url"].startswith("Telegram")]
        log.info(f"\n{len(reprocessable)} de {len(weak)} notas fracas tem URL e podem ser reprocessadas")

        # Estimar custo
        cost_per_note = 0.045  # ~3K input tokens + 4K output tokens com Sonnet
        log.info(f"Custo estimado para reprocessar todas: ~${len(reprocessable) * cost_per_note:.2f}")
        return

    # Reprocessar
    if args.test or args.reprocess:
        client = Anthropic()
        existing_notes = get_existing_notes(vault_path)

        if args.test:
            # Reprocessar nota especifica
            target = [n for n in all_notes if args.test in n["filename"]]
            if not target:
                log.error(f"Nota nao encontrada: {args.test}")
                return
            to_process = target[:1]
        else:
            # Reprocessar fracas com URL
            to_process = [
                n for n in sorted(weak, key=lambda x: x["score"])
                if n["source_url"] and not n["source_url"].startswith("Telegram")
            ][:args.limit]

        log.info(f"\nReprocessando {len(to_process)} notas...")
        success = 0
        for i, note_info in enumerate(to_process, 1):
            log.info(f"\n[{i}/{len(to_process)}]")
            try:
                ok = reprocess_note(cfg, client, note_info, existing_notes, dry_run=args.dry_run)
                if ok:
                    success += 1
            except Exception as e:
                log.error(f"  Erro: {e}")

            # Rate limiting
            if i < len(to_process):
                import time
                time.sleep(1)

        log.info(f"\n{'='*60}")
        log.info(f"Concluido: {success}/{len(to_process)} reprocessadas com sucesso")


if __name__ == "__main__":
    main()
