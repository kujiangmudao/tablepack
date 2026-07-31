# Architecture

## Goals

1. Use **MinerU** for layout-aware table HTML + table crops.
2. Emit a **reviewable package** (Excel + screenshots + notes), not a lone spreadsheet.
3. Make the process **agent-friendly**: deterministic rules in `AGENTS.md` + skill.
4. Stay **portable**: config/env instead of hardcoded machine paths.

## Data flow

```text
pdf/*.pdf
    │
    ▼
 MinerU CLI  ─────────────────────────────┐
    │                                     │
    ▼                                     ▼
work/mineru_raw/<stem>/auto/        (cache reusable)
  *_content_list.json
  images/*
    │
    ▼
pdf_excel.parse_mineru
  TableItem[]  ImageItem[]
    │
    ├─ drop empty table_body (default)
    ├─ html_table_to_grid (rowspan/colspan)
    ├─ write multi-sheet xlsx
    └─ copy 原始表格/ + 图片/
    │
    ▼
output/<stem>/
  ├── <stem>.xlsx
  ├── 原始表格/
  ├── 图片/
  └── 转换说明.md | 问题说明.md
    │
    ▼
 Human / agent visual QC  →  fix sheets / amend notes
```

## Module responsibilities

| Module | Responsibility |
|--------|----------------|
| `config.py` | Resolve paths & MinerU options (CLI > env > yaml > defaults) |
| `parse_mineru.py` | content_list → structured table/image items |
| `html_table.py` | Expand HTML merges into a 2D grid |
| `clean.py` | OCR / formula text normalization |
| `excel_writer.py` | openpyxl multi-sheet workbook |
| `pipeline.py` | Orchestrate MinerU, package, notes, summary |
| `cli.py` | User-facing CLI |

## Design choices

### Why not “Excel only”?

Reviewers need the **original table crop** next to the grid. Packaging both cuts back-and-forth and makes agent QC possible (read image + edit sheet).

### Why drop empty tables by default?

MinerU sometimes emits `type=table` with empty `table_body` / missing `img_path` (multi-page tails, false positives). Writing blank sheets looks like success. We **drop and document** instead of inventing rows.

### Why keep MinerU as a subprocess?

MinerU’s install (models, CUDA, backends) is heavy. Coupling via CLI keeps this repo small and version-flexible.

### Agent skill vs code

| Layer | What it enforces |
|-------|------------------|
| Code | Automated packaging, empty-table policy, OCR cleanups |
| Skill / AGENTS.md | Visual QC, honesty about failures, batch discipline |

Code cannot fully replace visual judgment on multi-level Chinese headers.

## Extension points

- **`clean.OCR_REPLACEMENTS`**: domain normalizations
- **`pipeline.write_notes`**: issue taxonomy / bilingual notes
- **Post-hooks**: user scripts that rewrite specific sheets after package (keep private data out of git)
- **Fallback extractors**: call img2table/Camelot only for failed tables (roadmap)
