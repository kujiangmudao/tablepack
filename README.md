# TablePack

[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![MinerU](https://img.shields.io/badge/powered%20by-MinerU-green.svg)](https://github.com/opendatalab/MinerU)
[![Agent Skill](https://img.shields.io/badge/agent-skill-purple.svg)](skills/pdf-table-to-excel/SKILL.md)

**中文 → [README.zh-CN.md](README.zh-CN.md)** · **Install paths → [docs/INSTALL.md](docs/INSTALL.md)**

> **PDF tables → multi-sheet Excel packages you can actually accept.**  
> One PDF · one workbook · original table screenshots · QC notes · agent skill.  
> Powered by [MinerU](https://github.com/opendatalab/MinerU).

**Product & repo: [TablePack](https://github.com/kujiangmudao/tablepack)** · Python package import/CLI still use `pdf_excel` / `python -m pdf_excel`.

---

## Why TablePack

| You need | TablePack delivers |
|----------|-------------------|
| Tables out of PDFs | **One Excel per PDF**, one sheet per table |
| Proof for review | **`原始表格/`** crops next to every package |
| Trustworthy automation | Empty/broken tables → notes, **never invent cells** |
| AI agents that follow SOP | Ready skill: `skills/pdf-table-to-excel/` |

```text
output/<name>/
  ├── <name>.xlsx
  ├── 原始表格/          # table screenshots for QC
  ├── 图片/
  └── 转换说明.md | 问题说明.md
```

### Preview

**Table crop (`原始表格/`)**

![Original table screenshot](docs/assets/qc-original-table.png)

**Excel sheet after packaging**

![Excel sheet](docs/assets/qc-excel-sheet.png)

---

## Choose your path

### Path A — You already use MinerU

Install this repo and load the skill. Point `mineru_bin` only if `mineru` is not on `PATH`.

```bash
git clone https://github.com/kujiangmudao/tablepack.git
cd pdf-excel
pip install -r requirements.txt
cp config.example.yaml config.yaml   # optional

# Agent: open this repo + load skills/pdf-table-to-excel/SKILL.md
# CLI:
cp examples/demo/demo_sample.pdf pdf/
python -m pdf_excel demo_sample
```

Skill raw URL:

```text
https://raw.githubusercontent.com/kujiangmudao/tablepack/main/skills/pdf-table-to-excel/SKILL.md
```

### Path B — No MinerU yet (isolated one-shot setup)

Official MinerU goes into a **project-local venv** (`.venv-mineru`). Safe: does not replace your system Python packages.

**Windows (PowerShell)**

```powershell
git clone https://github.com/kujiangmudao/tablepack.git
cd pdf-excel
powershell -ExecutionPolicy Bypass -File scripts\install_mineru.ps1
.\.venv-mineru\Scripts\Activate.ps1
python -m pdf_excel --dry-config
```

**Linux / macOS**

```bash
git clone https://github.com/kujiangmudao/tablepack.git
cd pdf-excel
chmod +x scripts/install_mineru.sh
./scripts/install_mineru.sh
source .venv-mineru/bin/activate
python -m pdf_excel --dry-config
```

Then:

```bash
cp examples/demo/demo_sample.pdf pdf/
python -m pdf_excel demo_sample
```

Full detail: **[docs/INSTALL.md](docs/INSTALL.md)**

---

## Agent skill (OpenCode / Cursor / Claude / …)

| | |
|--|--|
| Skill | [`skills/pdf-table-to-excel/SKILL.md`](skills/pdf-table-to-excel/SKILL.md) |
| Rules | [`AGENTS.md`](AGENTS.md) |
| Triggers | `转表格`, `转excel`, `mineru`, `再转一批`, `/pdf-table-to-excel` |

1. Prefer opening **this repo as the workspace** (CLI + skill together).  
2. Path A users: use your existing MinerU.  
3. Path B users: activate `.venv-mineru` so agents run the same environment.  
4. **Visual QC** (opening `原始表格/*.jpg`) works best with a **multimodal** model.

---

## CLI

```text
python -m pdf_excel
python -m pdf_excel --force
python -m pdf_excel --skip-existing
python -m pdf_excel --dry-config
python -m pdf_excel 关键词
```

Sample package without running anything: [`examples/demo_output/demo_sample/`](examples/demo_output/demo_sample/)

---

## Project layout

```text
tablepack / pdf-excel
├── pdf_excel/                 # Python package (python -m pdf_excel)
├── skills/pdf-table-to-excel/ # agent skill
├── scripts/install_mineru.*   # Path B setup
├── examples/demo/             # synthetic demo PDF
├── docs/INSTALL.md
├── docs/assets/               # README screenshots
└── AGENTS.md
```

---

## Docs

- [Install (Path A / B)](docs/INSTALL.md)
- [QC checklist](docs/QC_CHECKLIST.md)
- [Architecture](docs/ARCHITECTURE.md)
- [Troubleshooting](docs/TROUBLESHOOTING.md)
- [Contributing](CONTRIBUTING.md)

---

## License & credits

[MIT](LICENSE) · Parsing engine: [MinerU](https://github.com/opendatalab/MinerU) · Excel: [openpyxl](https://openpyxl.readthedocs.io/)

**Disclaimer:** You own final data correctness. Verify against source PDFs before publication or production use.
