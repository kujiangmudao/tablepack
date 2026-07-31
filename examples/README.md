# Examples

## Synthetic demo (safe to ship)

| Path | What it is |
|------|------------|
| [`demo/demo_sample.pdf`](demo/demo_sample.pdf) | Tiny synthetic PDF with one oxide table (fictional numbers) |
| [`demo_output/demo_sample/`](demo_output/demo_sample/) | Example deliverable package: xlsx + `原始表格/` + `转换说明.md` |
| [`build_demo.py`](build_demo.py) | Regenerates the PDF and sample package |

```bash
# inspect package layout without MinerU
ls examples/demo_output/demo_sample

# regenerate
pip install reportlab pillow
python examples/build_demo.py

# run full pipeline on the demo PDF (needs MinerU)
cp examples/demo/demo_sample.pdf pdf/
python -m pdf_excel demo_sample
```

## README screenshots

Product screenshots live in [`docs/assets/`](../docs/assets/):

- `qc-original-table.png` — table crop as used for visual QC
- `qc-excel-sheet.png` — multi-sheet Excel view after packaging

## Agent skill

See [`skills/pdf-table-to-excel/SKILL.md`](../skills/pdf-table-to-excel/SKILL.md).

## Privacy

Do **not** commit private theses under `pdf/` or production `output/`.  
Local folders such as `gh贴图/` / `问题/` are for author staging and stay gitignored.
