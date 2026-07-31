# TablePack（表格交付包）

[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![MinerU](https://img.shields.io/badge/powered%20by-MinerU-green.svg)](https://github.com/opendatalab/MinerU)
[![Agent Skill](https://img.shields.io/badge/agent-skill-purple.svg)](skills/pdf-table-to-excel/SKILL.md)

**English → [README.md](README.md)** · **安装双路径 → [docs/INSTALL.md](docs/INSTALL.md)**

> **PDF 表格 → 可验收的多 sheet Excel 交付包**  
> 一 PDF 一表簿 · 原始表格截图 · 成败说明 · Agent Skill  
> 解析引擎：[MinerU](https://github.com/opendatalab/MinerU) —— **你不必学 MinerU 怎么用**

**产品与仓库：[TablePack](https://github.com/kujiangmudao/tablepack)** · Python 包名/命令仍为 `pdf_excel` / `python -m pdf_excel`。

### 零 MinerU 学习成本

TablePack **替你调用 MinerU**。只要环境里装好了 MinerU（或走下面路径 B 一键装好）：

1. PDF 放进 `pdf/`
2. **一条命令**：`python -m pdf_excel`
3. 打开 `output/` —— 已是 Excel + `原始表格/` 截图 + 说明

**不需要**去学 MinerU 的命令行参数、backend、JSON 中间结果、导出格式。  
这些都封在 TablePack 里。（有经验的用户仍可改 `config.yaml`。）

---

## 你能得到什么

| 需求 | TablePack |
|------|-----------|
| 从 PDF 取表 | **一个 PDF → 一个 Excel**，一表一 sheet |
| 方便核对 | 同目录 **`原始表格/`** 截图 |
| 自动化可信 | 空表/坏表写说明，**不编造数据** |
| 不想学 MinerU | **装好即可一键打包**，不用啃 MinerU 教程 |
| 给 AI 用 | 自带 skill，同一套 SOP |

```text
output/<文件名>/
  ├── <文件名>.xlsx
  ├── 原始表格/
  ├── 图片/
  └── 转换说明.md 或 问题说明.md
```

### 效果预览

![原始表格截图](docs/assets/qc-original-table.png)

![Excel 效果](docs/assets/qc-excel-sheet.png)

---

## 两条安装路径

### 路径 A — 已经装好了 MinerU（不必会用）

只需本仓库。**不必再学 MinerU 怎么敲命令** —— TablePack 会自动找到 `mineru`（或不在 PATH 时读 `config.yaml` 里的 `mineru_bin`）。

```bash
git clone https://github.com/kujiangmudao/tablepack.git
cd tablepack
pip install -r requirements.txt
cp config.example.yaml config.yaml   # 可选；仅当 mineru 不在 PATH 时需要

cp examples/demo/demo_sample.pdf pdf/
python -m pdf_excel demo_sample      # 一键打包
```

**Agent（OpenCode 等）**

1. 用本仓库当工作区  
2. 加载 `skills/pdf-table-to-excel/SKILL.md`  
3. 说：`转表格` / `再转一批` / `/pdf-table-to-excel`

Raw：

```text
https://raw.githubusercontent.com/kujiangmudao/tablepack/main/skills/pdf-table-to-excel/SKILL.md
```

### 路径 B — 还没有 MinerU（一键安装 + 仍然不用学 MinerU）

脚本在项目内创建 **独立虚拟环境** `.venv-mineru`，安装官方 `mineru[all]` + 本项目依赖，并写好 `config.yaml`。  
装完后你**只用 TablePack 一条命令转表**，不必去学 MinerU 官方 CLI。  
虚拟环境**不污染**系统全局 site-packages。

**Windows（PowerShell）**

```powershell
git clone https://github.com/kujiangmudao/tablepack.git
cd tablepack
powershell -ExecutionPolicy Bypass -File scripts\install_mineru.ps1
.\.venv-mineru\Scripts\Activate.ps1
python -m pdf_excel --dry-config
```

**Linux / macOS**

```bash
git clone https://github.com/kujiangmudao/tablepack.git
cd tablepack
chmod +x scripts/install_mineru.sh
./scripts/install_mineru.sh
source .venv-mineru/bin/activate
python -m pdf_excel --dry-config
```

然后：

```bash
cp examples/demo/demo_sample.pdf pdf/
python -m pdf_excel demo_sample
```

细节见 **[docs/INSTALL.md](docs/INSTALL.md)**。

---

## Agent Skill

| 项 | 路径 |
|----|------|
| Skill | [`skills/pdf-table-to-excel/SKILL.md`](skills/pdf-table-to-excel/SKILL.md) |
| 硬规则 | [`AGENTS.md`](AGENTS.md) |

路径 B 用户请让 Agent 在 **已激活 `.venv-mineru`** 的终端里跑命令。  
对照 `原始表格/` 做质检时，建议使用 **支持看图的多模态模型**。

---

## 常用命令

```text
python -m pdf_excel
python -m pdf_excel --force
python -m pdf_excel --dry-config
python -m pdf_excel 关键词
```

不跑解析也能先看交付结构：[`examples/demo_output/demo_sample/`](examples/demo_output/demo_sample/)

---

## 文档

- [安装双路径](docs/INSTALL.md)
- [质检清单](docs/QC_CHECKLIST.md)
- [架构](docs/ARCHITECTURE.md)
- [排错](docs/TROUBLESHOOTING.md)

## 许可

[MIT](LICENSE) · 致谢 [MinerU](https://github.com/opendatalab/MinerU)

最终数据请以原 PDF 为准。
