# -*- coding: utf-8 -*-
"""End-to-end package: MinerU → Excel → 原始表格/图片 → notes."""

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


def _resolve_img(auto_dir: Path, rel: str) -> Path | None:
    src = auto_dir / rel
    if src.exists():
        return src
    alt = auto_dir / "images" / Path(rel).name
    return alt if alt.exists() else None


def write_notes(
    out_dir: Path,
    stem: str,
    pdf_name: str,
    tables: list[TableItem],
    image_count: int,
    issues: list[str],
    dropped_empty: int = 0,
) -> Path:
    md_lines = [
        f"# {stem} — 转换说明",
        "",
        f"- 源 PDF: `{pdf_name}`",
        f"- 写入 Excel 的表格数: **{len(tables)}**",
        f"- 丢弃空表节点: **{dropped_empty}**" if dropped_empty else None,
        f"- 识别图片/图件数: **{image_count}**",
        f"- Excel: `{stem}.xlsx`",
        f"- 原始表格图片目录: `原始表格/`",
        f"- 文中图片目录: `图片/`",
        "",
        "## 表格清单",
        "",
    ]
    md_lines = [x for x in md_lines if x is not None]

    if tables:
        for t in tables:
            md_lines.append(f"### 表{t.index}: {t.caption or '(无标题)'}")
            md_lines.append(f"- 页码: {t.page_idx + 1}")
            md_lines.append(f"- 原始图: `{t.img_path or '无'}`")
            if t.issues:
                md_lines.append(f"- 问题: {'; '.join(t.issues)}")
            else:
                md_lines.append("- 状态: 已写入 Excel")
            md_lines.append("")
    else:
        md_lines.append("未识别到可写入的表格。")
        md_lines.append("")

    md_lines.append("## 质检提醒")
    md_lines.append("")
    md_lines.append(
        "自动转换**不等于**交付完成。请对照 `原始表格/` 检查表头、行列、合并单元格与数值；"
        "无法修复的问题写在下方，**不要伪造数据**。"
    )
    md_lines.append("")

    if issues or not tables:
        md_lines.append("## 问题与限制")
        md_lines.append("")
        for iss in issues:
            md_lines.append(f"- {iss}")
        if not issues and not tables:
            md_lines.append("- MinerU 未识别到 table 类型对象，或全部为空表。")
        md_lines.append("")
        md_lines.append(
            "> 表格由 MinerU 识别并结构还原。若单元格错位、合并表头不准或数值可疑，"
            "请对照 `原始表格/` 截图人工核对并修改 xlsx。"
        )
        path = out_dir / "问题说明.md"
    else:
        md_lines.append("## 问题与限制")
        md_lines.append("")
        md_lines.append("本次自动转换未发现结构性失败。请仍对照 `原始表格/` 做最终核验。")
        path = out_dir / "转换说明.md"

    path.write_text("\n".join(md_lines), encoding="utf-8")
    return path


def package_output(settings: Settings, pdf_path: Path, force_mineru: bool = False) -> dict[str, Any]:
    stem = pdf_path.stem
    result: dict[str, Any] = {
        "pdf": pdf_path.name,
        "stem": stem,
        "ok": False,
        "tables": 0,
        "images": 0,
        "dropped_empty": 0,
        "issues": [],
    }

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
            (out_dir / "问题说明.md").write_text(
                f"# {stem}\n\n## 失败原因\n\n{e}\n",
                encoding="utf-8",
            )
            return result
        auto_dir = find_auto_dir(settings, stem)
        if auto_dir is None:
            result["issues"].append(f"MinerU 未生成输出目录 (exit={code})")
            out_dir.mkdir(parents=True, exist_ok=True)
            (out_dir / "问题说明.md").write_text(
                f"# {stem}\n\n## 失败原因\n\nMinerU 未能解析该 PDF，未生成 auto 输出目录。\n\n"
                f"- 源文件: `{pdf_path}`\n"
                f"- mineru exit code: {code}\n",
                encoding="utf-8",
            )
            return result

    cl_path = find_content_list(auto_dir)
    if cl_path is None:
        result["issues"].append("找不到 content_list.json")
        out_dir.mkdir(parents=True, exist_ok=True)
        (out_dir / "问题说明.md").write_text(
            f"# {stem}\n\n## 失败原因\n\nMinerU 输出中缺少 `*_content_list.json`，无法提取表格。\n",
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
                    f"表{t.index} ({t.caption or '无标题'}, p{t.page_idx + 1}): "
                    "table_body 为空，已丢弃（不写入假数据）"
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
    raw_table_dir = out_dir / "原始表格"
    raw_table_dir.mkdir(parents=True, exist_ok=True)
    fig_dir = out_dir / "图片"
    fig_dir.mkdir(parents=True, exist_ok=True)

    for t in tables:
        if not t.img_path:
            t.issues.append("缺少原始表格图片路径")
            result["issues"].append(f"表{t.index}: 缺少 img_path")
            continue
        src = _resolve_img(auto_dir, t.img_path)
        if src is None:
            t.issues.append(f"原始表格图片不存在: {t.img_path}")
            result["issues"].append(f"表{t.index}: 图片缺失 {t.img_path}")
            continue
        cap_safe = safe_filename(t.caption or f"第{t.page_idx + 1}页")
        dest_name = f"表{t.index}_{cap_safe}{src.suffix}"
        shutil.copy2(src, raw_table_dir / dest_name)

    for i, im in enumerate(images, 1):
        src = _resolve_img(auto_dir, im.img_path)
        if src is None:
            result["issues"].append(f"{im.type} 图片缺失: {im.img_path}")
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

    excel_issues = write_excel(tables, xlsx_path)
    result["issues"].extend(excel_issues)

    for t in tables:
        if t.issues:
            for iss in t.issues:
                tag = f"表{t.index}: {iss}"
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
        pdfs = sorted(settings.pdf_dir.glob("*.pdf"))
    if name_filters:
        pdfs = [p for p in pdfs if any(k in p.name for k in name_filters)]

    summary: list[dict[str, Any]] = []
    if not pdfs:
        print("No PDFs found", flush=True)
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
