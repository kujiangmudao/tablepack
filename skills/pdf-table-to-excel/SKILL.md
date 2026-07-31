---
name: pdf-table-to-excel
description: >
  Convert PDF tables to multi-sheet Excel packages with MinerU: original table
  screenshots, figures, QC notes, no fabricated data. Use in this repo for any
  PDF→Excel / batch table extraction / visual table QC task.
  Triggers: 转表格, 转excel, 转Excel, PDF表格, pdf转excel, mineru, 原始表格,
  批量转换, 继续转, 再转一批, 表格转excel, /pdf-table-to-excel
---

# PDF tables → Excel (MinerU packaging pipeline)

**Read root `AGENTS.md` first** for hard rules. This skill is the executable checklist.

## Environment (portable)

Prefer `config.yaml` / env / CLI — do **not** hardcode another machine’s paths.

| Item | Default |
|------|---------|
| Entry | `python -m pdf_excel` or `python convert_pipeline.py` |
| PDFs | `pdf/` |
| Output | `output/` |
| MinerU cache | `work/mineru_raw/` |
| MinerU | `MINERU_BIN` or auto-discover on PATH |

Recommended MinerU flags (also set in config):

```text
mineru -p <pdf> -o work/mineru_raw -b pipeline -m auto -l ch -t true -f false
```

CPU-only → `pipeline`. Higher-accuracy VLM/hybrid only if installed and requested; **QC still mandatory**.

## Required package layout

```text
output/<PDF_STEM>/
  ├── <PDF_STEM>.xlsx
  ├── 原始表格/          # required screenshots
  ├── 图片/
  └── 转换说明.md | 问题说明.md
```

## Business rules

1. MinerU is primary parser; OCR/pdfplumber only for repair.
2. One PDF → one Excel (same stem).
3. All tables → sheets in that one workbook.
4. Always include `原始表格/` images for human comparison.
5. After auto convert: **visual QC vs screenshots**; rewrite bad sheets.
6. Unrecoverable → markdown explanation; **never invent cells**.

## Workflow

### 1. Prepare

- PDFs in `pdf/` (or user path)
- List work items; respect skip-existing only if user asks

### 2. Parse

```bash
python -m pdf_excel --force   # or without --force to reuse cache
# filters:
python -m pdf_excel 关键词
```

- Read `*_content_list.json` (prefer non-v2 with `table_body` HTML)
- Collect `type==table` and `image`/`chart`

### 3. Excel

- HTML (+ rowspan/colspan) → grid → openpyxl multi-sheet
- Sheet names: `表N_中文标题` (≤31 chars)
- Empty `table_body` → drop by default (`drop_empty_tables`)

### 4. Package

- xlsx + `原始表格/` + `图片/` + notes
- Rotate unreadable table crops before QC when needed

### 5. Forced QC (never skip)

For each sheet:

1. Open matching `原始表格/` image (agent `read_file` on image) or PDF page
2. Check headers, dims, IDs, numbers
3. Fix xlsx immediately when wrong
4. Print conflicts → keep print + note
5. Landscape disasters → rotate + OCR + manual rebuild

Checklist:

- [ ] Sheet count / titles
- [ ] Headers & dimensions
- [ ] Symbols / subscripts
- [ ] Values
- [ ] Assets complete
- [ ] Notes file present

### 6. Failures

| Case | Action |
|------|--------|
| No table objects | Placeholder xlsx + `问题说明.md` |
| Empty/broken HTML | Repair from image if possible; else document |
| Full fail | Keep folder + notes + partial assets |

### 7. Close-out

- Update `output/_summary.json` (pipeline writes it)
- Report per-PDF table counts, fixes, known gaps

## Forbidden

- Deliver auto-only without QC
- Mix multiple PDFs into one xlsx (unless user asks)
- Omit `原始表格/`
- Fabricate data
- Claim “strictly checked” without reading table images/values

## Code map

| Module | Role |
|--------|------|
| `pdf_excel/pipeline.py` | End-to-end packaging |
| `pdf_excel/html_table.py` | HTML → grid |
| `pdf_excel/excel_writer.py` | Multi-sheet xlsx |
| `pdf_excel/clean.py` | OCR normalizations |
| `pdf_excel/cli.py` | CLI |
| `convert_pipeline.py` | Thin entry wrapper |

New batches: **pipeline → visual fix → notes**. Optional local fix scripts stay out of git if they contain private data.
