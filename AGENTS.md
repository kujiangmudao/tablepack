# pdf-excel — Agent / operator rules (must follow)

This project turns **PDF tables → Excel packages** using **MinerU**.  
When the user asks to convert PDFs, **always** follow this file + `skills/pdf-table-to-excel/SKILL.md`.

## Multimodal requirement

- **Auto pipeline** (`python -m pdf_excel`): text/CLI is enough.
- **Quality control / sheet repair**: **requires a vision-capable model** that can open `原始表格/` screenshots (or PDF pages).
- Text-only models (some free OpenCode backends): may run packaging, but **must not** claim visual QC was done; ask user to re-run QC with multimodal or review manually.

## Environment

Resolve paths via (in order): CLI flags → env vars → `config.yaml` → defaults.

| Item | Default / note |
|------|----------------|
| Source PDFs | `pdf/` |
| Output packages | `output/` |
| MinerU cache | `work/mineru_raw/` |
| MinerU CLI | `MINERU_BIN` or `config.yaml` → `mineru_bin` (auto-discover if on PATH) |
| Backend | `pipeline` (CPU-friendly); tables on (`-t true`); language `ch` unless configured |
| Code entry | `python -m pdf_excel` or `convert_pipeline.py` |

Local machine tip: copy `config.example.yaml` → `config.yaml` (gitignored).

## Hard requirements (never skip)

1. **MinerU** is the primary parser (helpers OK for repair only).
2. **One PDF → one Excel**, same basename.
3. **All tables of one PDF** in **one** workbook as **different sheets**.
4. Package structure:

```text
output/<PDF_STEM>/
  ├── <PDF_STEM>.xlsx
  ├── 原始表格/          # table screenshots (required)
  ├── 图片/              # non-table figures
  └── 转换说明.md        # success
      or 问题说明.md     # fail / partial fail
```

5. **Strict visual QC** after auto convert: compare each sheet vs `原始表格/` (or PDF). Fix misaligned columns, bad headers, merges, suspicious numbers **immediately**.
6. **Unrecoverable tables**: write markdown explaining why — **never fabricate data**.
7. PDFs with no tables: still emit folder + placeholder xlsx + `问题说明.md` + keep figures when possible.

## QC checklist (every PDF)

- [ ] Sheet count matches real tables (no merged captions across tables)
- [ ] Headers / row-col counts match source (rowspan/colspan readable after expand)
- [ ] Symbols/subscripts correct (e.g. 3₂, 8#, Ro)
- [ ] Cell values match print; if print itself conflicts → keep print + note in md
- [ ] `原始表格/` complete with readable names (`表N_标题`)
- [ ] `图片/` has in-document figures
- [ ] Success → `转换说明.md`; fail/partial → `问题说明.md`

## Known pitfalls

- Landscape / sideways tables → whole-grid shift → rotate crop + OCR + manual rebuild
- Multi-level headers / merges → HTML may need hand fix
- Caption glue (table 2+3 one caption) → split sheet names
- Chart/image only, no `table` type → problem note, no fake tables
- Empty `table_body` / missing `img_path` → drop node, document (pipeline default)
- OCR noise: `Al{2O_3` → `Al2O3`, `w1%` → `w/%`

## Interaction defaults

- “再转一批 / 继续转 / 新 PDF” → full pipeline + QC
- Prefer incremental: reuse `work/mineru_raw/` when present, but **re-QC Excel**
- Batch order: MinerU all → convert packages → per-table visual fix

## Privacy when contributing / open-sourcing

- Do **not** commit copyrighted PDFs, personal corpora, or filled `output/` / `work/`
- Do **not** commit `config.yaml` with absolute private paths if you prefer (example file only)
- Local-only fix scripts with private numbers stay gitignored (`fix_batch*.py`, etc.)
