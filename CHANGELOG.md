# Changelog

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
