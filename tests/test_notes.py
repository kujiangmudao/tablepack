# -*- coding: utf-8 -*-
from pathlib import Path

from pdf_excel.pipeline import write_notes


def test_write_notes_zh_and_en(tmp_path: Path):
    zh_dir = tmp_path / "zh"
    zh_dir.mkdir()
    p_zh = write_notes(zh_dir, "demo", "demo.pdf", [], 0, [], language="zh")
    assert p_zh.name == "问题说明.md"
    body_zh = p_zh.read_text(encoding="utf-8")
    assert "## 问题与限制" in body_zh

    en_dir = tmp_path / "en"
    en_dir.mkdir()
    p_en = write_notes(en_dir, "demo", "demo.pdf", [], 0, [], language="en")
    assert p_en.name == "issues.md"
    body_en = p_en.read_text(encoding="utf-8")
    assert "## Issues & limitations" in body_en
    assert "## 问题与限制" not in body_en
