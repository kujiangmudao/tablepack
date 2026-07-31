# 故事文草稿（知乎 / 掘金 / 公众号可用）

> 使用说明：标题三选一；正文可直接复制。文中图片请从仓库 `docs/assets/` 上传，或截你自己的 `output/` 包。  
> 仓库：https://github.com/kujiangmudao/tablepack  
> 语气：场景 → 做法 → 交付物 → 怎么试；少吹牛，多给路径。

---

## 标题备选

1. **PDF 里的表格，怎样收成「能交差」的 Excel 包？我开源了 TablePack**
2. **不只是转 Excel：给 MinerU 补上「原始表格截图 + 质检说明」这一层**
3. **用 Agent Skill 批量处理 PDF 表格：一 PDF 一表簿，还能对照原表**

推荐用 **1**（更易被非开发读者点开）。

---

## 正文

### 开头：真实场景

做资料、写论文、整理行业报告时，最烦的不是「没有表」，而是：

**表都在 PDF 里。**

复制粘贴会乱列；截图又没法筛选；丢给普通「PDF 转 Excel」工具，出来一堆对不上的格子，还说不清错在哪一页。

我这边连续处理过多批中文学术/技术 PDF：多级表头、合并单元格、氧化物符号、跨页表……需求其实很朴素：

1. **一个 PDF 对应一个 Excel**（不要拆成几十个零散文件）  
2. **每张表一个 sheet**  
3. 交出去时，对方能**对照原表核对**  
4. 实在认不出来的，**写清楚问题**，不要瞎填数字  

于是有了这个开源小项目：**TablePack**。

> 仓库：https://github.com/kujiangmudao/tablepack  
> 定位：在优秀 PDF 解析（MinerU）之上，做**可验收的表格交付包** + 给 AI Agent 用的 Skill。  
> **卖点一句：只要装好 MinerU，就能一键打包转 PDF 表——不必学习任何 MinerU 的用法。**

---

### 核心想法：交付的不是「一个 xlsx」，而是「一包证据」

很多工具停在「尽量识别成表格」。  
TablePack 多走了半步——每次转换固定产出：

```text
output/某论文名/
  ├── 某论文名.xlsx      ← 全部表格，多 sheet
  ├── 原始表格/          ← 表的截图，方便人对、也方便多模态 Agent 看
  ├── 图片/              ← 文中的图/chart
  └── 转换说明.md        ← 成功说明
      或 问题说明.md     ← 部分失败时写清卡在哪
```

直觉上就三点：

| 点 | 为什么重要 |
|----|------------|
| 一 PDF 一 Excel | 整理、归档、交给甲方都清晰 |
| `原始表格/` | 质检有对照物，不是空口说「转好了」 |
| 问题说明 | **不编造数据**——认不出就写原因 |

---

### 效果长什么样

**原表截图（`原始表格/` 里的那种）：**

（此处插入：`docs/assets/qc-original-table.png`）

**打包进 Excel 后的 sheet（带标题、页码、数据区）：**

（此处插入：`docs/assets/qc-excel-sheet.png`）

一眼能对上行列，才叫「能交差」；对不上就改 sheet，或写进问题说明——这是项目里写死的规矩，也写进了 Agent Skill。

---

### 和「只跑 MinerU / 只转 CSV」差在哪

[MinerU](https://github.com/opendatalab/MinerU) 本身已经很强：版面、表格 HTML、表图都能出。  
很多团队缺的是**最后一公里**：

- 怎么固定成业务要的 Excel 结构？  
- 怎么让人工/AI **按同一套 SOP** 验收？  
- 空表、坏表时，怎样避免模型「补假数」？

TablePack 不替代 MinerU，而是：

**MinerU 负责解析 → TablePack 负责打包成交付物 + 质检纪律 + Agent 可执行清单。**

也支持你已经装好 MinerU 的环境；没有的话，仓库里有**隔离安装脚本**（独立虚拟环境，不乱动系统 Python）。

---

### 两条使用路径（按你情况选）

#### 路径 A：你已经会用 MinerU

```bash
git clone https://github.com/kujiangmudao/tablepack.git
cd tablepack
pip install -r requirements.txt

# 把 PDF 放进 pdf/
python -m pdf_excel
```

给 OpenCode / Cursor / Claude 等 Agent 用时：打开本仓库，加载 skill：

`skills/pdf-table-to-excel/SKILL.md`  

或 raw 链接：

https://raw.githubusercontent.com/kujiangmudao/tablepack/main/skills/pdf-table-to-excel/SKILL.md

直接说：「转表格 / 再转一批」即可按 SOP 跑。

#### 路径 B：还没有 MinerU

Windows：

```powershell
git clone https://github.com/kujiangmudao/tablepack.git
cd tablepack
powershell -ExecutionPolicy Bypass -File scripts\install_mineru.ps1
.\.venv-mineru\Scripts\Activate.ps1
```

Linux / macOS：

```bash
git clone https://github.com/kujiangmudao/tablepack.git
cd tablepack
chmod +x scripts/install_mineru.sh && ./scripts/install_mineru.sh
source .venv-mineru/bin/activate
```

然后同样：`python -m pdf_excel`。  
详细说明见仓库 `docs/INSTALL.md`。

#### 只想先看交付长什么样

仓库里有合成样例（虚构数据，无版权论文）：

- 示例 PDF：`examples/demo/demo_sample.pdf`  
- 示例产出包：`examples/demo_output/demo_sample/`  

不用先跑解析也能打开文件夹结构感受一下。

---

### Agent Skill 特别适合什么人

如果你已经在用 AI 编程助手批量干活，最怕两件事：

1. 助手「转完就交差」，从不对照原表  
2. 识别失败时默默编数字  

Skill 里把规矩写死了，例如：

- 必须出 `原始表格/`  
- 质检要**打开截图**看（多模态更合适）  
- 弄不了就写 `问题说明.md`，禁止假表  

纯文本模型可以帮忙跑命令、整理目录；**对照原表改格子**，更推荐带视觉的模型，或你自己扫一眼截图。

---

### 什么情况要老实写「问题说明」

项目明确：**致命/无法可靠还原的表，不硬凑。**

比如解析结果空表体、只有图没有表结构、合并表头严重错位又暂时修不好——输出里会保留能保留的，并在 md 里写清原因。  

这不是甩锅，是交付诚信：宁可不完整，也不交一份「看起来很满」的假表。

---

### 写在最后

TablePack 解决的是一个很具体的工作流问题：

> **把 PDF 表格，变成「Excel + 原表截图 + 说明」的可验收包裹，并让人和 Agent 按同一标准执行。**

如果你也在批量抠表、给业务交数、或给 Agent 派「转表」任务，欢迎试试：

**https://github.com/kujiangmudao/tablepack**

有难表、好想法，欢迎开 Issue（可打码）。觉得有用的话点个 Star，也是对开源最直接的支持。

解析能力致敬 [MinerU](https://github.com/opendatalab/MinerU)；TablePack 只做交付与质检这一层。

---

## 发布时检查清单（给你自己）

- [ ] 标题用备选 1 或自改更口语版  
- [ ] 上传两张 `docs/assets` 图（或你自己的包内截图）  
- [ ] 文末仓库链接可点  
- [ ] 标签建议：`PDF` `Excel` `MinerU` `开源` `Agent` `OCR` `表格提取`  
- [ ] 不要主动写「很慢/掉帧」——读者问性能时再诚实回答「主要耗时在解析引擎与机器配置」  
- [ ] 若发知乎：可加目录；若发掘金：选「开源」或「后端」栏目均可  

## 评论区可预置回复

**Q：必须 GPU 吗？**  
A：默认走 MinerU 的 pipeline 配置，CPU 也能用；有 GPU 可按 MinerU 文档升级后端。TablePack 负责打包与规则。

**Q：和直接 MinerU 导出有何不同？**  
A：MinerU 强在解析；TablePack 固定「一 PDF 一 Excel + 原始表格目录 + 说明 + Agent Skill」。

**Q：商业论文能当 demo 吗？**  
A：仓库 demo 是合成数据。你自己的 PDF 本地转即可，请注意版权，不要把未授权全文推到公开仓库。
