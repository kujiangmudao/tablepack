# -*- coding: utf-8 -*-
"""Command-line interface for pdf-excel."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from . import __version__
from .config import load_settings
from .pipeline import run_batch


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(
        prog="pdf-excel",
        description="MinerU-based PDF table → multi-sheet Excel packaging pipeline "
        "with 原始表格 screenshots and QC notes.",
    )
    p.add_argument("-V", "--version", action="version", version=f"pdf-excel {__version__}")
    p.add_argument(
        "-c",
        "--config",
        type=Path,
        default=None,
        help="Path to config.yaml (default: ./config.yaml)",
    )
    p.add_argument("--root", type=Path, default=None, help="Project root (default: cwd)")
    p.add_argument("--pdf-dir", type=Path, default=None, help="Directory of source PDFs")
    p.add_argument("--output-dir", type=Path, default=None, help="Output packages directory")
    p.add_argument("--work-dir", type=Path, default=None, help="MinerU raw cache directory")
    p.add_argument("--mineru", type=Path, default=None, help="Path to mineru executable")
    p.add_argument("-b", "--backend", default=None, help="MinerU backend (default: pipeline)")
    p.add_argument("-l", "--lang", default=None, help="MinerU language (default: ch)")
    p.add_argument(
        "--force",
        action="store_true",
        help="Re-run MinerU even if cache exists",
    )
    p.add_argument(
        "--keep-empty-tables",
        action="store_true",
        help="Keep empty table_body nodes as failed sheets (default: drop them)",
    )
    p.add_argument(
        "--skip-existing",
        action="store_true",
        help="Skip PDFs that already have output/<stem>/<stem>.xlsx",
    )
    p.add_argument(
        "--dry-config",
        action="store_true",
        help="Print resolved config and exit",
    )
    p.add_argument(
        "filters",
        nargs="*",
        help="Optional substrings to filter PDF filenames",
    )
    return p


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    overrides = {}
    if args.root:
        overrides["root"] = args.root
    if args.pdf_dir:
        overrides["pdf_dir"] = args.pdf_dir
    if args.output_dir:
        overrides["output_dir"] = args.output_dir
    if args.work_dir:
        overrides["work_dir"] = args.work_dir
    if args.mineru:
        overrides["mineru_bin"] = args.mineru
    if args.backend:
        overrides["backend"] = args.backend
    if args.lang:
        overrides["language"] = args.lang
    if args.keep_empty_tables:
        overrides["drop_empty_tables"] = False
    if args.skip_existing:
        overrides["skip_existing_excel"] = True

    root = args.root or Path.cwd()
    settings = load_settings(root=root, config_path=args.config, overrides=overrides)

    if args.dry_config:
        print(json.dumps(settings.as_dict(), ensure_ascii=False, indent=2))
        return 0

    summary = run_batch(
        settings,
        force_mineru=args.force,
        name_filters=args.filters or None,
    )
    ok = sum(1 for r in summary if r.get("ok"))
    print(f"Done: {ok}/{len(summary)} packages OK", flush=True)
    return 0 if summary and ok == len(summary) else (0 if summary else 1)


if __name__ == "__main__":
    raise SystemExit(main())
