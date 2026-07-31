# Troubleshooting

## MinerU not found

```
FileNotFoundError: MinerU CLI not found
```

- Install MinerU per upstream docs: https://github.com/opendatalab/MinerU
- Put `mineru` on `PATH`, or set:

```yaml
# config.yaml
mineru_bin: C:/path/to/mineru.exe
```

```bash
# or
set MINERU_BIN=C:\path\to\mineru.exe   # Windows
export MINERU_BIN=/usr/local/bin/mineru  # Unix
```

Check: `python -m pdf_excel --dry-config`

## No tables detected

- PDF may be pure figure/chart pages → expect `问题说明.md`
- Scanned low quality → try MinerU VLM backend if you have GPU
- Confirm `work/mineru_raw/<stem>/auto/*_content_list.json` exists and contains `"type": "table"`

## Empty sheets / empty HTML

Default: empty `table_body` nodes are **dropped** and listed in notes.  
To keep them as placeholder sheets: `--keep-empty-tables`.

## Columns shifted / merged headers wrong

Known hard case. Actions:

1. Open `原始表格/表N_*.jpg`
2. Manually rebuild the sheet
3. Optionally rotate if the crop is sideways

## Cross-page tables split into multiple sheets

Pipeline currently treats MinerU nodes independently. Merge manually in Excel or with a small openpyxl script when captions/columns match.

## Windows PowerShell “errors” from MinerU

Progress bars on stderr can look like `NativeCommandError` even when exit code is 0. Prefer running via `python -m pdf_excel` (subprocess without treating stderr as failure).

## Dependencies missing

```bash
pip install -r requirements.txt
```

Need `lxml` for BeautifulSoup table parsing.

## Copyright / sample data

This repo **does not** ship third-party theses/PDFs. Use your own licensed materials for demos.
