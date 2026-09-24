# -*- coding: utf-8 -*-
"""Localized, user-visible output names and labels (see ``output_language``)."""

from __future__ import annotations

from typing import Any

_LANGUAGES: dict[str, dict[str, str]] = {
    "zh": {
        # --- package structure ---
        "tables_dir": "原始表格",
        "images_dir": "图片",
        "notes_file": "转换说明.md",
        "issues_file": "问题说明.md",
        "table_word": "表",
        "page_label": "第{p}页",
        "no_caption": "(无标题)",
        "none": "无",
        # --- write_notes body ---
        "notes_title": "# {stem} — 转换说明",
        "notes_source_pdf": "- 源 PDF: `{v}`",
        "notes_tables_count": "- 写入 Excel 的表格数: **{v}**",
        "notes_dropped_count": "- 丢弃空表节点: **{v}**",
        "notes_images_count": "- 识别图片/图件数: **{v}**",
        "notes_xlsx": "- Excel: `{v}`",
        "notes_tables_dir": "- 原始表格图片目录: `{v}`",
        "notes_images_dir": "- 文中图片目录: `{v}`",
        "notes_table_list_header": "## 表格清单",
        "notes_table_h3": "### 表{index}: {caption}",
        "notes_page_line": "- 页码: {v}",
        "notes_source_img": "- 原始图: `{v}`",
        "notes_issues_line": "- 问题: {v}",
        "notes_ok_line": "- 状态: 已写入 Excel",
        "notes_no_tables": "未识别到可写入的表格。",
        "notes_qc_header": "## 质检提醒",
        "notes_qc_body": "自动转换**不等于**交付完成。请对照 `{tables_dir}/` 检查表头、行列、合并单元格与数值；无法修复的问题写在下方，**不要伪造数据**。",
        "notes_limits_header": "## 问题与限制",
        "notes_mineru_empty": "- MinerU 未识别到 table 类型对象，或全部为空表。",
        "notes_limits_body": "> 表格由 MinerU 识别并结构还原。若单元格错位、合并表头不准或数值可疑，请对照 `{tables_dir}/` 截图人工核对并修改 xlsx。",
        "notes_all_ok": "本次自动转换未发现结构性失败。请仍对照 `{tables_dir}/` 做最终核验。",
        # --- failure notes ---
        "fail_header": "## 失败原因",
        "fail_no_auto": "MinerU 未能解析该 PDF，未生成 auto 输出目录。",
        "fail_source_file": "- 源文件: `{v}`",
        "fail_exit_code": "- mineru exit code: {v}",
        "fail_no_content_list": "MinerU 输出中缺少 `*_content_list.json`，无法提取表格。",
        # --- result issues (console / JSON / notes) ---
        "issue_pdf_missing": "PDF 文件不存在: {v}",
        "issue_no_auto_dir": "MinerU 未生成输出目录 (exit={v})",
        "issue_no_content_list": "找不到 content_list.json",
        "issue_empty_dropped": "表{i} ({caption}, p{page}): table_body 为空，已丢弃（不写入假数据）",
        "issue_missing_img_path": "缺少原始表格图片路径",
        "issue_table_img_missing": "原始表格图片不存在: {v}",
        "issue_table_tag": "表{i}: {msg}",
        "issue_figure_missing": "{type} 图片缺失: {v}",
        # --- excel_writer ---
        "xlsx_no_tables_sheet": "无表格",
        "xlsx_no_tables_msg": "未从该 PDF 中识别到可转换的表格",
        "xlsx_sheet_name": "表{index}_{caption}",
        "xlsx_none": "(无)",
        "xlsx_title_line": "标题: {v}",
        "xlsx_page_line": "页码: {v}",
        "xlsx_footnote_prefix": "注释: ",
        "xlsx_html_fail": "(表格 HTML 解析失败，请查看原始表格图片与问题说明)",
        "xlsx_page_table": "第{page}页表格",
        "xlsx_table_issue": "表{i} ({caption}): {msg}",
    },
    "en": {
        # --- package structure ---
        "tables_dir": "table_crops",
        "images_dir": "images",
        "notes_file": "conversion_notes.md",
        "issues_file": "issues.md",
        "table_word": "Table",
        "page_label": "page {p}",
        "no_caption": "(untitled)",
        "none": "none",
        # --- write_notes body ---
        "notes_title": "# {stem} — conversion notes",
        "notes_source_pdf": "- Source PDF: `{v}`",
        "notes_tables_count": "- Tables written to Excel: **{v}**",
        "notes_dropped_count": "- Empty table nodes dropped: **{v}**",
        "notes_images_count": "- Figures/images found: **{v}**",
        "notes_xlsx": "- Excel: `{v}`",
        "notes_tables_dir": "- Table-crop screenshots: `{v}`",
        "notes_images_dir": "- In-document figures: `{v}`",
        "notes_table_list_header": "## Table list",
        "notes_table_h3": "### Table {index}: {caption}",
        "notes_page_line": "- Page: {v}",
        "notes_source_img": "- Source image: `{v}`",
        "notes_issues_line": "- Issues: {v}",
        "notes_ok_line": "- Status: written to Excel",
        "notes_no_tables": "No tables were extracted from this PDF.",
        "notes_qc_header": "## QC reminder",
        "notes_qc_body": "Automatic conversion is **not** delivery. Check headers, rows/columns, merged cells and values against `{tables_dir}/`; log anything you cannot fix below. **Never fabricate data.**",
        "notes_limits_header": "## Issues & limitations",
        "notes_mineru_empty": "- MinerU found no `table` objects, or all tables were empty.",
        "notes_limits_body": "> Tables are detected and reconstructed by MinerU. If a cell is misplaced, a merged header is wrong, or a value looks suspicious, verify against the `{tables_dir}/` screenshots and fix the xlsx by hand.",
        "notes_all_ok": "No structural failures were found in this automatic conversion. Still do a final check against `{tables_dir}/`.",
        # --- failure notes ---
        "fail_header": "## Failure",
        "fail_no_auto": "MinerU could not parse this PDF — no auto output directory was produced.",
        "fail_source_file": "- Source file: `{v}`",
        "fail_exit_code": "- mineru exit code: {v}",
        "fail_no_content_list": "MinerU output is missing `*_content_list.json` — tables cannot be extracted.",
        # --- result issues (console / JSON / notes) ---
        "issue_pdf_missing": "PDF file not found: {v}",
        "issue_no_auto_dir": "MinerU produced no output directory (exit={v})",
        "issue_no_content_list": "content_list.json not found",
        "issue_empty_dropped": "Table {i} ({caption}, p{page}): empty table_body dropped (no invented data)",
        "issue_missing_img_path": "missing table-crop image path",
        "issue_table_img_missing": "table-crop image not found: {v}",
        "issue_table_tag": "Table {i}: {msg}",
        "issue_figure_missing": "{type} image missing: {v}",
        # --- excel_writer ---
        "xlsx_no_tables_sheet": "no_tables",
        "xlsx_no_tables_msg": "No convertible tables found in this PDF",
        "xlsx_sheet_name": "Table{index}_{caption}",
        "xlsx_none": "(none)",
        "xlsx_title_line": "Caption: {v}",
        "xlsx_page_line": "Page: {v}",
        "xlsx_footnote_prefix": "Footnote: ",
        "xlsx_html_fail": "(Table HTML failed to parse — check the table crops and the issues note)",
        "xlsx_page_table": "page {page} table",
        "xlsx_table_issue": "Table {i} ({caption}): {msg}",
    },
}

# Fail fast at import time if the two languages ever drift out of sync.
assert set(_LANGUAGES["zh"]) == set(_LANGUAGES["en"]), "output language texts are out of sync"


def normalize_language(value: Any) -> str:
    """Map any user-provided value to a supported language code (default: zh)."""
    text = str(value or "").strip().lower()
    return "en" if text.startswith("en") else "zh"


def get_texts(language: Any = "zh") -> dict[str, str]:
    """Return the label dictionary for *language* (falls back to zh)."""
    return _LANGUAGES[normalize_language(language)]
