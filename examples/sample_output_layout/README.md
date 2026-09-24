# Sample package layout (structure only)

`output_language: zh` (default):

```text
示例论文_作者/
  ├── 示例论文_作者.xlsx
  ├── 原始表格/
  │     ├── 表1_煤岩组分统计.jpg
  │     └── 表2_常量元素氧化物.jpg
  ├── 图片/
  │     └── chart_01_p12_柱状图.jpg
  └── 转换说明.md
```

`output_language: en`:

```text
paper_stem/
  ├── paper_stem.xlsx
  ├── table_crops/
  │     ├── Table1_component_statistics.jpg
  │     └── Table2_oxide_composition.jpg
  ├── images/
  │     └── chart_01_p12_bar_chart.jpg
  └── conversion_notes.md
```

Place your real PDFs under repo `pdf/` (gitignored) and run `python -m pdf_excel`.
