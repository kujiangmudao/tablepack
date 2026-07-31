# Contributing

Thanks for helping improve **pdf-excel**.

## Ground rules

1. **Do not commit copyrighted PDFs**, personal research corpora, or full `output/` / `work/` trees.
2. Prefer synthetic HTML fixtures in `tests/` for regressions.
3. Keep the **no fabricated data** policy when changing empty-table behavior.
4. Document user-facing changes in `README.md` / `CHANGELOG.md`.

## Dev setup

```bash
git clone https://github.com/kujiangmudao/tablepack.git
cd pdf-excel
python -m venv .venv
# Windows: .venv\Scripts\activate
# Unix: source .venv/bin/activate
pip install -r requirements.txt
pip install -e ".[dev]"
pytest
```

## Suggested PR types

- Bug fixes in HTML grid expansion / sheet naming
- Better OCR cleanups (with tests)
- CLI/config improvements
- Docs / skill wording (especially QC guidance)
- Optional fallback extractors behind flags

## Code style

- Python 3.10+, type hints welcomed
- Keep modules focused; avoid dumping private batch scripts with real table data
- New features should work without your local absolute paths

## Reporting issues

Include when possible:

- OS + Python version
- MinerU version / backend
- Whether the PDF is text-based or scanned
- Redacted snippet of `content_list` table entry (HTML only, no full private PDF)
- Screenshot of **one** problematic table crop (if you can share)
