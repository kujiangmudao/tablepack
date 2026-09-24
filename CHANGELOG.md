# Changelog

## 0.3.0 — 2026-09-24

### Added

- `output_language: zh | en` config option (env: `PDF_EXCEL_OUTPUT_LANGUAGE`) — localizes the whole delivery surface; default `zh` keeps existing output unchanged:
  - Names: `原始表格/`, `图片/`, `转换说明.md`, `问题说明.md` → `table_crops/`, `images/`, `conversion_notes.md`, `issues.md`
  - Note contents, Excel sheet names/row labels, failure notes and batch result messages
  - Crop file names: `表N_*` → `TableN_*`
- English mode verified end-to-end on a real cached batch

## 0.2.4 — 2026-09-24

### Docs

- **English is the default landing page**: root `README.md` is now the English full text; Chinese moved to `README.zh-CN.md` (language switcher in both)
- READMEs revamped: hero layout, workflow diagram (EN / zh-CN), CLI table, project layout
- Fixed stale references: repo homepage link, `CONTRIBUTING.md` (`pdf-excel` → `tablepack`, wrong clone path), `docs/INSTALL.md` language links

## 0.2.3 — 2026-08-01

### Docs

- **Chinese default landing page**: root `README.md` is 简体中文 (view on GitHub homepage, no download)
- English full text: `README.en.md` with language switcher links
- `README.zh-CN.md` kept only as a short pointer for old bookmarks

## 0.2.2 — 2026-08-01

### Docs

- Spotlight promise: **install MinerU → one-click package; no MinerU usage tutorial required**
- Fix clone `cd` path to `tablepack` after rename

## 0.2.1 — 2026-07-31

### Changed

- GitHub repository renamed: `pdf-excel` → **`tablepack`**
  - https://github.com/kujiangmudao/tablepack
  - Old URL redirects on GitHub when possible; update bookmarks/clones to the new name

## 0.2.0 — 2026-07-31

### Added

- Product name **TablePack**
- Dual install paths in README + `docs/INSTALL.md`
  - Path A: existing MinerU users → skill/CLI directly
  - Path B: `scripts/install_mineru.ps1` / `scripts/install_mineru.sh` (isolated `.venv-mineru`)
- Strengths-focused MinerU Discussion update

## 0.1.2 — 2026-07-31

### Added (growth / onboarding)

- README pitch block + product screenshots under `docs/assets/`
- Chinese README: `README.zh-CN.md`
- Synthetic demo PDF + sample package: `examples/demo/`, `examples/demo_output/`
- `examples/build_demo.py` to regenerate demo assets
- Clearer agent-skill install links (raw URL + OpenCode notes)

## 0.1.1 — 2026-07-31

### Fixed

- Relative `pdf_dir` / `output_dir` / `work_dir` now resolve against **project root**, not process cwd (broke when CLI launched from another directory)
- YAML/env boolean coercion for `true`/`false` strings
- CLI exit codes: `1` no work / missing pdf dir, `2` partial package failures
- Safer image path resolution (backslash / basename fallback)
- Sheet name sanitization (quotes, reserved `History`)
- `rowspan`/`colspan` values like `"2.0"` no longer crash
- Defensive parse when content_list JSON is wrapped in a dict
- Missing PDF file / missing `pdf/` directory reported clearly

### Docs

- Skill + AGENTS: explicit **multimodal/vision required for QC**

## 0.1.0 — 2026-07-31

### Added

- Installable package `pdf_excel` with CLI (`python -m pdf_excel`)
- Configurable paths via `config.yaml`, env vars, and CLI flags
- Auto-discover MinerU on PATH / common locations
- Drop empty `table_body` nodes by default (document in notes)
- Portable agent skill under `skills/pdf-table-to-excel/`
- Docs: architecture, QC checklist, troubleshooting
- Unit tests for HTML table expansion and text cleaning
- MIT license, contribution guide, strict `.gitignore` for private corpora

### Notes

- Evolved from production multi-batch conversion of technical/academic PDFs
- Backward-compatible entry: `convert_pipeline.py`
