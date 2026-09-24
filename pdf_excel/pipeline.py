# -*- coding: utf-8 -*-
"""End-to-end package: MinerU → Excel → table crops/figures → notes."""

from __future__ import annotations

import json
import shutil
import subprocess
import traceback
from pathlib import Path
from typing import Any

from .clean import safe_filename
from .config import Settings
from .excel_writer import write_excel
from .models import TableItem
from .names import get_texts
from .parse_mineru import find_content_list, parse_content_list, reindex_tables


def find_auto_dir(settings: Settings, pdf_stem: str) -> Path | None:
    candidate = settings.work_dir / pdf_stem / "auto"
    if candidate.is_dir():
        return candidate
    if not settings.work_dir.exists():
        return None
    for d in settings.work_dir.iterdir():
        if d.is_dir() and d.name == pdf_stem:
            auto = d / "auto"
            if auto.is_dir():
                return auto
    return None


def run_mineru(settings: Settings, pdf_path: Path) -> int:
    if not settings.mineru_bin or not Path(settings.mineru_bin).exists():
        raise FileNotFoundError(
            "MinerU CLI not found. Install MinerU and set mineru_bin in config.yaml "
            "or MINERU_BIN / PDF_EXCEL_MINERU env var. See README.md."
        )
    settings.work_dir.mkdir(parents=True, exist_ok=True)
    cmd = [
        str(settings.mineru_bin),
        "-p",
        str(pdf_path),
        "-o",
        str(settings.work_dir),
        "-b",
        settings.backend,
        "-m",
        settings.method,
        "-l",
        settings.language,
        "-t",
        "true" if settings.enable_table else "false",
        "-f",
        "true" if settings.enable_formula else "false",
    ]
    print(f"[mineru] running: {pdf_path.name}", flush=True)
    print(f"[mineru] cmd: {' '.join(cmd)}", flush=True)
    proc = subprocess.run(cmd, cwd=str(settings.root), capture_output=False)
    print(f"[mineru] exit={proc.returncode} for {pdf_path.name}", flush=True)
    return proc.returncode


def _resolve_img(auto_dir: Path, rel: str | None) -> Path | None:
    if not rel:
        return None
    # MinerU usually emits forward slashes; normalize for Windows.
    rel_norm = str(rel).replace("\\", "/").lstrip("./")
    src = auto_dir / Path(rel_norm)
    if src.exists():
        return src
    alt = auto_dir / "images" / Path(rel_norm).name
    if alt.exists():
        return alt
    # Last resort: basename search under auto/images
    images_dir = auto_dir / "images"
    name = Path(rel_norm).name
    if images_dir.is_dir() and name:
        hit = images_dir / name
        if hit.exists():
            return hit
    return None


def write_notes(
    out_dir: Path,
    stem: str,
    pdf_name: str,
    tables: list[TableItem],
    image_count: int,
    issues: list[str],
    dropped_empty: int = 0,
    language: str = "zh",
) -> Path:
    texts = get_texts(language)
    tables_dir = texts["tables_dir"]
    md_lines = [
        texts["notes_title"].format(stem=stem),
        "",
        texts["notes_source_pdf"].format(v=pdf_name),
        texts["notes_tables_count"].format(v=len(tables)),
        texts["notes_dropped_count"].format(v=dropped_empty) if dropped_empty else None,
        texts["notes_images_count"].format(v=image_count),
        texts["notes_xlsx"].format(v=f"{stem}.xlsx"),
        texts["notes_tables_dir"].format(v=tables_dir),
        texts["notes_images_dir"].format(v=texts["images_dir"]),
        "",
        texts["notes_table_list_header"],
        "",
    ]
    md_lines = [x for x in md_lines if x is not None]

    if tables:
        for t in tables:
            md_lines.append(
                texts["notes_table_h3"].format(index=t.index, caption=t.caption or texts["no_caption"])
            )
            md_lines.append(texts["notes_page_line"].format(v=t.page_idx + 1))
            md_lines.append(texts["notes_source_img"].format(v=t.img_path or texts["none"]))
            if t.issues:
                md_lines.append(texts["notes_issues_line"].format(v="; ".join(t.issues)))
            else:
                md_lines.append(texts["notes_ok_line"])
            md_lines.append("")
    else:
        md_lines.append(texts["notes_no_tables"])
        md_lines.append("")

    md_lines.append(texts["notes_qc_header"])
    md_lines.append("")
    md_lines.append(texts["notes_qc_body"].format(tables_dir=tables_dir))
    md_lines.append("")

    if issues or not tables:
        md_lines.append(texts["notes_limits_header"])
        md_lines.append("")
        for iss in issues:
            md_lines.append(f"- {iss}")
        if not issues and not tables:
            md_lines.append(texts["notes_mineru_empty"])
        md_lines.append("")
        md_lines.append(texts["notes_limits_body"].format(tables_dir=tables_dir))
        path = out_dir / texts["issues_file"]
    else:
        md_lines.append(texts["notes_limits_header"])
        md_lines.append("")
        md_lines.append(texts["notes_all_ok"].format(tables_dir=tables_dir))
        path = out_dir / texts["notes_file"]

    path.write_text("\n".join(md_lines), encoding="utf-8")
    return path


def package_output(settings: Settings, pdf_path: Path, force_mineru: bool = False) -> dict[str, Any]:
    pdf_path = Path(pdf_path)
    stem = pdf_path.stem
    texts = get_texts(settings.output_language)
    result: dict[str, Any] = {
        "pdf": pdf_path.name,
        "stem": stem,
        "ok": False,
        "tables": 0,
        "images": 0,
        "dropped_empty": 0,
        "issues": [],
    }

    if not pdf_path.is_file():
        result["issues"].append(texts["issue_pdf_missing"].format(v=pdf_path))
        return result

    out_dir = settings.output_dir / stem
    xlsx_path = out_dir / f"{stem}.xlsx"
    if settings.skip_existing_excel and xlsx_path.is_file() and not force_mineru:
        result["ok"] = True
        result["skipped"] = True
        result["out_dir"] = str(out_dir)
        result["issues"].append("skipped existing package (skip_existing_excel=true)")
        return result

    auto_dir = find_auto_dir(settings, stem)
    if force_mineru or auto_dir is None:
        try:
            code = run_mineru(settings, pdf_path)
        except FileNotFoundError as e:
            result["issues"].append(str(e))
            out_dir.mkdir(parents=True, exist_ok=True)
            (out_dir / texts["issues_file"]).write_text(
                f"# {stem}\n\n{texts['fail_header']}\n\n{e}\n",
                encoding="utf-8",
            )
            return result
        auto_dir = find_auto_dir(settings, stem)
        if auto_dir is None:
            result["issues"].append(texts["issue_no_auto_dir"].format(v=code))
            out_dir.mkdir(parents=True, exist_ok=True)
            (out_dir / texts["issues_file"]).write_text(
                f"# {stem}\n\n{texts['fail_header']}\n\n{texts['fail_no_auto']}\n\n"
                f"{texts['fail_source_file'].format(v=pdf_path)}\n"
                f"{texts['fail_exit_code'].format(v=code)}\n",
                encoding="utf-8",
            )
            return result

    cl_path = find_content_list(auto_dir)
    if cl_path is None:
        result["issues"].append(texts["issue_no_content_list"])
        out_dir.mkdir(parents=True, exist_ok=True)
        (out_dir / texts["issues_file"]).write_text(
            f"# {stem}\n\n{texts['fail_header']}\n\n{texts['fail_no_content_list']}\n",
            encoding="utf-8",
        )
        return result

    tables, images = parse_content_list(cl_path)
    dropped = 0
    if settings.drop_empty_tables:
        kept: list[TableItem] = []
        for t in tables:
            if t.is_empty:
                dropped += 1
                result["issues"].append(
                    texts["issue_empty_dropped"].format(
                        i=t.index,
                        caption=t.caption or texts["no_caption"],
                        page=t.page_idx + 1,
                    )
                )
            else:
                kept.append(t)
        tables = reindex_tables(kept)

    result["tables"] = len(tables)
    result["images"] = len(images)
    result["dropped_empty"] = dropped

    if out_dir.exists() and settings.wipe_output_package:
        shutil.rmtree(out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    raw_table_dir = out_dir / texts["tables_dir"]
    raw_table_dir.mkdir(parents=True, exist_ok=True)
    fig_dir = out_dir / texts["images_dir"]
    fig_dir.mkdir(parents=True, exist_ok=True)

    for t in tables:
        if not t.img_path:
            t.issues.append(texts["issue_missing_img_path"])
            result["issues"].append(
                texts["issue_table_tag"].format(i=t.index, msg=texts["issue_missing_img_path"])
            )
            continue
        src = _resolve_img(auto_dir, t.img_path)
        if src is None:
            t.issues.append(texts["issue_table_img_missing"].format(v=t.img_path))
            result["issues"].append(
                texts["issue_table_tag"].format(
                    i=t.index, msg=texts["issue_table_img_missing"].format(v=t.img_path)
                )
            )
            continue
        cap_safe = safe_filename(t.caption or texts["page_label"].format(p=t.page_idx + 1))
        dest_name = f"{texts['table_word']}{t.index}_{cap_safe}{src.suffix}"
        shutil.copy2(src, raw_table_dir / dest_name)

    for i, im in enumerate(images, 1):
        src = _resolve_img(auto_dir, im.img_path)
        if src is None:
            result["issues"].append(texts["issue_figure_missing"].format(type=im.type, v=im.img_path))
            continue
        cap_safe = safe_filename(im.caption or f"p{im.page_idx + 1}", 50)
        dest_name = f"{im.type}_{i:02d}_p{im.page_idx + 1}_{cap_safe}{src.suffix}"
        shutil.copy2(src, fig_dir / dest_name)

    images_dir = auto_dir / "images"
    if images_dir.is_dir():
        used_srcs = set()
        for t in tables:
            if t.img_path:
                used_srcs.add(Path(t.img_path).name)
        for im in images:
            used_srcs.add(Path(im.img_path).name)
        for imgf in images_dir.iterdir():
            if imgf.is_file() and imgf.name not in used_srcs:
                shutil.copy2(imgf, fig_dir / f"other_{imgf.name}")

    excel_issues = write_excel(tables, xlsx_path, language=settings.output_language)
    result["issues"].extend(excel_issues)

    for t in tables:
        if t.issues:
            for iss in t.issues:
                tag = texts["issue_table_tag"].format(i=t.index, msg=iss)
                if tag not in result["issues"]:
                    result["issues"].append(tag)

    write_notes(
        out_dir,
        stem,
        pdf_path.name,
        tables,
        len(images),
        result["issues"],
        dropped_empty=dropped,
        language=settings.output_language,
    )

    result["ok"] = True
    result["out_dir"] = str(out_dir)
    return result


def run_batch(
    settings: Settings,
    pdfs: list[Path] | None = None,
    force_mineru: bool = False,
    name_filters: list[str] | None = None,
) -> list[dict[str, Any]]:
    settings.output_dir.mkdir(parents=True, exist_ok=True)
    if pdfs is None:
        if not settings.pdf_dir.is_dir():
            print(f"PDF directory not found: {settings.pdf_dir}", flush=True)
            return []
        pdfs = sorted(settings.pdf_dir.glob("*.pdf"))
        # Also accept uppercase extension on case-sensitive FS
        pdfs += sorted(p for p in settings.pdf_dir.glob("*.PDF") if p not in pdfs)
    if name_filters:
        pdfs = [p for p in pdfs if any(k in p.name for k in name_filters)]

    summary: list[dict[str, Any]] = []
    if not pdfs:
        print(f"No PDFs found in {settings.pdf_dir}", flush=True)
        return summary

    for pdf in pdfs:
        print("=" * 60, flush=True)
        print(f"Processing: {pdf.name}", flush=True)
        try:
            r = package_output(settings, pdf, force_mineru=force_mineru)
            summary.append(r)
            print(json.dumps(r, ensure_ascii=False, indent=2), flush=True)
        except Exception as e:
            traceback.print_exc()
            summary.append({"pdf": pdf.name, "ok": False, "issues": [str(e)]})

    summary_path = settings.output_dir / "_summary.json"
    summary_path.write_text(json.dumps(summary, ensure_ascii=False, indent=2), encoding="utf-8")
    print("Summary written to", summary_path, flush=True)
    return summary
