# -*- coding: utf-8 -*-
"""Tests for MinerU content_list parsing (incl. defensive coercion)."""

from __future__ import annotations

import json
from pathlib import Path

from pdf_excel.parse_mineru import find_content_list, parse_content_list, reindex_tables


def _write(path: Path, data) -> Path:
    path.write_text(json.dumps(data, ensure_ascii=False), encoding="utf-8")
    return path


def test_parse_basic(tmp_path: Path) -> None:
    data = [
        {
            "type": "table",
            "page_idx": "3.0",  # string float from some MinerU builds
            "table_caption": ["表1 测试"],
            "table_body": "<table><tr><td>a</td></tr></table>",
            "img_path": "images/t1.jpg",
        },
        {"type": "image", "page_idx": 0, "img_path": "images/fig1.jpg", "image_caption": ["图1"]},
        {"type": "text", "page_idx": 0, "text": "ignored"},
    ]
    cl = _write(tmp_path / "doc_content_list.json", data)

    tables, images = parse_content_list(cl)
    assert len(tables) == 1
    assert len(images) == 1

    t = tables[0]
    assert t.page_idx == 3  # coerced safely, no crash
    assert "表1" in t.caption
    assert t.html_body.startswith("<table")

    im = images[0]
    assert im.type == "image"
    assert "图1" in im.caption

    t.index = 99
    reindexed = reindex_tables(tables)
    assert reindexed[0].index == 1


def test_parse_dict_wrapped(tmp_path: Path) -> None:
    cl = _write(
        tmp_path / "doc_content_list.json",
        {
            "content_list": [
                {"type": "table", "page_idx": 1, "table_body": "<table><tr><td>x</td></tr></table>"}
            ]
        },
    )
    tables, images = parse_content_list(cl)
    assert len(tables) == 1
    assert images == []


def test_parse_bad_page_idx_uses_default(tmp_path: Path) -> None:
    cl = _write(
        tmp_path / "doc_content_list.json",
        [{"type": "table", "page_idx": "not-a-number", "table_body": "<table><tr><td>x</td></tr></table>"}],
    )
    tables, _ = parse_content_list(cl)
    assert tables[0].page_idx == 0


def test_find_content_list_prefers_v1(tmp_path: Path) -> None:
    v1 = _write(tmp_path / "doc_content_list.json", [])
    _write(tmp_path / "doc_content_list_v2.json", [])
    assert find_content_list(tmp_path) == v1
