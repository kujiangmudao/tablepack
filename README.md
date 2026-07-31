# pdf-excel

[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![MinerU](https://img.shields.io/badge/parser-MinerU-green.svg)](https://github.com/opendatalab/MinerU)

**PDF tables to multi-sheet Excel packages**, powered by [MinerU](https://github.com/opendatalab/MinerU), with **original table screenshots**, figure assets, and **honest QC notes**.

Not just "dump CSV and pray." This project encodes a **deliverable workflow** used on real multi-batch academic/technical PDFs:

> one PDF → one Excel (all tables as sheets) → folder with `原始表格/` + `图片/` + `转换说明.md` / `问题说明.md` → **mandatory visual QC**.

Also ships as an **AI agent skill** (`skills/pdf-table-to-excel/`) so coding agents follow the same rules every batch.

---

## Why this exists

| Common tools | This project |
|--------------|--------------|
| Camelot / Tabula → CSV/xlsx | Full **package layout** for human review |
| MinerU → Markdown/JSON | MinerU tables → **Excel + screenshots + notes** |
| Auto-only pipelines | **QC checklist** + "no fabricated rows" policy |
| One-off scripts | Reusable **CLI + config + agent skill** |

Built from multi-batch production experience (complex Chinese theses, multi-level headers, empty MinerU nodes, cross-page tables, OCR oxide formulas like `Al2O3`, etc.).

---

## Output package layout

For each `foo.pdf`:

```text
output/foo/
  ├── foo.xlsx           # all tables, one sheet each
  ├── 原始表格/          # cropped table images for visual QC
  ├── 图片/              # figures / charts from the PDF
  └── 转换说明.md        # success note
      or 问题说明.md     # partial/failed cases — never invent data
```

---

## Requirements

1. **Python 3.10+**
2. **[MinerU](https://github.com/opendatalab/MinerU)** installed and on `PATH`, or set `mineru_bin` / `MINERU_BIN`
3. Pipeline dependencies (this repo):

```bash
pip install -r requirements.txt
# or editable install
pip install -e .
```

> MinerU is a separate project with its own GPU/CPU backends. On CPU-only machines, `backend: pipeline` is the usual choice.

---

## Quick start

```bash
git clone https://github.com/kujiangmudao/pdf-excel.git
cd pdf-excel
pip install -r requirements.txt

# configure paths (optional but recommended)
cp config.example.yaml config.yaml
# edit config.yaml → set mineru_bin if not on PATH

# put PDFs here
mkdir -p pdf
cp /path/to/*.pdf pdf/

# convert
python -m pdf_excel
# or
python convert_pipeline.py

# filter by filename substring
python -m pdf_excel 张珂 何建国

# force re-parse with MinerU
python -m pdf_excel --force

# show resolved config
python -m pdf_excel --dry-config
```

Environment variables (override config):

| Variable | Meaning |
|----------|---------|
| `MINERU_BIN` / `PDF_EXCEL_MINERU` | MinerU CLI path |
| `PDF_EXCEL_PDF_DIR` | Source PDF directory |
| `PDF_EXCEL_OUTPUT_DIR` | Output directory |
| `PDF_EXCEL_WORK_DIR` | MinerU cache directory |
| `PDF_EXCEL_BACKEND` | e.g. `pipeline` |
| `PDF_EXCEL_LANG` | e.g. `ch` |
| `PDF_EXCEL_CONFIG` | Path to YAML config |

---

## CLI options

```text
python -m pdf_excel [-h] [-c CONFIG] [--root ROOT]
                    [--pdf-dir DIR] [--output-dir DIR] [--work-dir DIR]
                    [--mineru PATH] [-b BACKEND] [-l LANG]
                    [--force] [--keep-empty-tables] [--skip-existing]
                    [--dry-config] [filters ...]
```

| Flag | Effect |
|------|--------|
| `--force` | Re-run MinerU even if cache exists |
| `--keep-empty-tables` | Keep empty `table_body` nodes (default: drop them) |
| `--skip-existing` | Skip packages that already have xlsx |
| `filters` | Only process PDFs whose names contain any substring |

---

## Quality control (the hard part)

Automation gets you ~70–90% of the way. **Deliverable quality** needs visual QC:

1. Open `原始表格/表N_*.jpg` (or the PDF page)
2. Compare headers, row/col counts, merged cells, numbers, symbols (`3₂`, `8#`, `Ro`…)
3. Fix the sheet in Excel / openpyxl when wrong
4. If unrecoverable → document in `问题说明.md` — **do not invent numbers**

### Agent / LLM note

| Task | Model need |
|------|------------|
| Run CLI + package folders | Any coding agent |
| **Compare sheets to table screenshots** | **Multimodal / vision** |

Text-only models can still orchestrate MinerU and write notes, but they **cannot** honestly finish the QC step. The shipped skill (`skills/pdf-table-to-excel/`) states this explicitly.

Full checklist: [docs/QC_CHECKLIST.md](docs/QC_CHECKLIST.md)  
Architecture notes: [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md)  
Troubleshooting: [docs/TROUBLESHOOTING.md](docs/TROUBLESHOOTING.md)

---

## Agent skill

For Cursor / Claude / Grok / OpenCode / other agents:

- Portable skill: [`skills/pdf-table-to-excel/SKILL.md`](skills/pdf-table-to-excel/SKILL.md)
- Project hard rules: [`AGENTS.md`](AGENTS.md)

Raw skill URL:

```text
https://raw.githubusercontent.com/kujiangmudao/pdf-excel/main/skills/pdf-table-to-excel/SKILL.md
```

Copy the skill into your agent's skills directory, or keep the repo as the working project so agents load `AGENTS.md` automatically.

---

## Project layout

```text
pdf-excel/
├── pdf_excel/              # installable package
│   ├── cli.py              # CLI
│   ├── pipeline.py         # MinerU → package
│   ├── html_table.py       # rowspan/colspan → grid
│   ├── excel_writer.py
│   ├── parse_mineru.py
│   └── config.py
├── convert_pipeline.py     # thin backward-compatible entry
├── skills/pdf-table-to-excel/
├── docs/
├── examples/
├── tests/
├── config.example.yaml
├── AGENTS.md
└── README.md
```

---

## What we deliberately do not do

- Do **not** ship copyrighted sample PDFs (use your own)
- Do **not** invent table rows when MinerU returns empty HTML
- Do **not** claim 100% accuracy without visual QC
- Do **not** replace MinerU's parser (we orchestrate + package + enforce QC)

---

## Roadmap ideas

- [ ] Optional cross-page table merge heuristics
- [ ] Structured issue taxonomy in notes (JSON + MD)
- [ ] Fallback extractors (img2table / Camelot) for failed tables
- [ ] Domain dictionaries (oxides, coal seam labels) as plugins
- [ ] Simple HTML report for batch summaries

PRs welcome — see [CONTRIBUTING.md](CONTRIBUTING.md).

---

## Citation / acknowledgment

- Document parsing: **[MinerU](https://github.com/opendatalab/MinerU)** (OpenDataLab)
- Excel I/O: [openpyxl](https://openpyxl.readthedocs.io/)

If this workflow helps your research or data engineering, star the repo and open issues with hard tables — those drive improvements.

---

## License

[MIT](LICENSE)

---

## Disclaimer

This tool assists extraction; **you** own the correctness of final data. Always verify against original PDFs before publication, regulatory, or commercial use.
