# pdf-excel

[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![MinerU](https://img.shields.io/badge/parser-MinerU-green.svg)](https://github.com/opendatalab/MinerU)
[![Agent Skill](https://img.shields.io/badge/agent-skill-purple.svg)](skills/pdf-table-to-excel/SKILL.md)

**English → [README.md](README.md)**

### PDF 表格 → 可交付的 Excel 包（给人用，也给 AI Agent 用）

不是「丢一个 CSV 碰运气」，而是可验收的交付：

| 痛点 | 你得到什么 |
|------|------------|
| 表锁在 PDF 里 | **一个 PDF → 一个 Excel**，一表一 sheet |
| OCR 结果难核对 | 同目录 **`原始表格/`** 截图，边看边对 |
| 模型爱编数据 | 规则：**弄不了就写说明，禁止造假** |
| 脚本用一次就扔 | **CLI + 配置 + Agent Skill** 可复用 |

> **一 PDF → 一 Excel → 截图+说明文件夹 → 强制视觉质检**

解析引擎用 [MinerU](https://github.com/opendatalab/MinerU)；本仓库负责编排、打包与质检纪律。

---

## 10 秒看效果

**原始表格截图**（`原始表格/`）：

![原始表格截图](docs/assets/qc-original-table.png)

**打包后的 Excel sheet**（标题/页码 + 数据区）：

![Excel 表格效果](docs/assets/qc-excel-sheet.png)

```text
output/<PDF文件名>/
  ├── <PDF文件名>.xlsx
  ├── 原始表格/            # 表截图，方便对照
  ├── 图片/                # 文中图件
  └── 转换说明.md 或 问题说明.md
```

---

## 快速开始（命令行）

```bash
git clone https://github.com/kujiangmudao/pdf-excel.git
cd pdf-excel
pip install -r requirements.txt

cp config.example.yaml config.yaml
# 若 mineru 不在 PATH，在 config.yaml 里设置 mineru_bin

# 先试仓库自带的合成样例（无数据，无版权论文）
cp examples/demo/demo_sample.pdf pdf/
python -m pdf_excel demo_sample

# 或把自己的 PDF 放进 pdf/ 后：
python -m pdf_excel
```

**依赖：** Python 3.10+、[MinerU](https://github.com/opendatalab/MinerU) CLI、`requirements.txt`。  
无 GPU 时默认 `backend: pipeline`。

不跑 MinerU 也能先看交付结构：

- [`examples/demo_output/demo_sample/`](examples/demo_output/demo_sample/)

重新生成 demo：

```bash
pip install reportlab pillow
python examples/build_demo.py
```

---

## 使用 Agent Skill（OpenCode / Cursor / Claude 等）

| 项 | 值 |
|----|-----|
| Skill 路径 | [`skills/pdf-table-to-excel/SKILL.md`](skills/pdf-table-to-excel/SKILL.md) |
| Raw 直链 | https://raw.githubusercontent.com/kujiangmudao/pdf-excel/main/skills/pdf-table-to-excel/SKILL.md |
| 项目硬规则 | [`AGENTS.md`](AGENTS.md) |

**推荐：** 把本仓库作为工作区打开（代码 + skill 一起有）。  
也可让 skill 安装器指向：`kujiangmudao/pdf-excel` → `skills/pdf-table-to-excel`。

触发词示例：`转表格`、`转excel`、`mineru`、`再转一批`、`/pdf-table-to-excel` …

### 多模态说明（重要）

| 阶段 | 是否需要看图 |
|------|----------------|
| 跑 `python -m pdf_excel` 打包 | 不需要 |
| **对照 `原始表格/` 质检、改表** | **需要** |

纯文本模型可以帮你跑命令，但**不能**声称「已严格对照原表检查」。

---

## 和 Camelot / 纯 MinerU 差在哪

| 方案 | 常见终点 | 本项目 |
|------|----------|--------|
| Camelot / Tabula | CSV/xlsx | **文件夹交付** + 原表截图 |
| 只用 MinerU | MD/JSON/HTML | Excel 包 + 说明 + Agent 规则 |
| 全自动脚本 | 「看起来行」 | **空表不造假** 写进规范 |

---

## 常用命令

```text
python -m pdf_excel --dry-config
python -m pdf_excel --force
python -m pdf_excel --skip-existing
python -m pdf_excel 关键词
```

配置见 `config.example.yaml`。质检清单：[docs/QC_CHECKLIST.md](docs/QC_CHECKLIST.md)

---

## 明确不做的事

- 不把有版权的学位论文当样例（请用 `examples/demo/`）
- 不在 MinerU 空 HTML 时编造行
- 不声称「免质检 100% 准确」
- 不替代 MinerU 解析器（我们做编排与交付）

---

## 参与

有用的话点个 Star；难表欢迎开 Issue（可打码）。贡献见 [CONTRIBUTING.md](CONTRIBUTING.md)。

## 许可

[MIT](LICENSE)

## 免责

最终数据正确性由使用者负责；发表或商用前请对照原 PDF 核实。
