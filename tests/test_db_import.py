# -*- coding: utf-8 -*-
"""Tests for the optional Excel → SQLite import step."""

from __future__ import annotations

import sqlite3

from pdf_excel.db_import import infer_value, import_package
from pdf_excel.excel_writer import write_excel
from pdf_excel.models import TableItem


def _table(index: int, caption: str, html: str) -> TableItem:
    return TableItem(
        index=index,
        page_idx=0,
        caption=caption,
        caption_raw=[],
        footnote=[],
        html_body=html,
        img_path=None,
        bbox=None,
    )


def test_infer_value() -> None:
    assert infer_value("42") == 42
    assert infer_value("-3") == -3
    assert infer_value("1,234") == 1234
    assert infer_value("45.2") == 45.2
    assert infer_value(" 3.5 ") == 3.5
    assert infer_value("S-01") == "S-01"
    assert infer_value("1.2.3") == "1.2.3"
    assert infer_value("") is None
    assert infer_value(None) is None
    assert infer_value(7) == 7
    assert infer_value(2.5) == 2.5


def test_import_package_basic(tmp_path) -> None:
    html_t1 = (
        "<table><tr><th>Sample</th><th>SiO2</th><th>Note</th></tr>"
        "<tr><td>S-01</td><td>45.2</td><td>ok</td></tr>"
        "<tr><td>S-01</td><td>45.2</td><td>ok</td></tr>"
        "<tr><td>S-02</td><td>48.0</td><td></td></tr>"
        "</table>"
    )
    html_t2 = "<table><tr><th>A</th><th>B</th></tr><tr><td>1</td><td>x</td></tr></table>"
    tables = [
        _table(1, "Sample oxide composition", html_t1),
        _table(2, "Second table", html_t2),
    ]
    xlsx = tmp_path / "demo.xlsx"
    write_excel(tables, xlsx, language="en")

    db = tmp_path / "demo.db"
    info = import_package(db, xlsx, source_pdf="demo.pdf")

    assert info["ok"] is True
    assert info["rows_imported"] == 3
    assert info["duplicates_removed"] == 1
    assert len(info["tables"]) == 2

    conn = sqlite3.connect(db)
    try:
        cur = conn.cursor()
        names = {r[0] for r in cur.execute("SELECT name FROM sqlite_master WHERE type='table'")}
        assert "_meta" in names

        t1 = info["tables"][0]["table"]
        cur.execute(f'SELECT * FROM "{t1}"')
        cols = [d[0] for d in cur.description]
        assert "_src_pdf" in cols and "_src_sheet" in cols and "_src_row" in cols
        rows = cur.fetchall()
        assert len(rows) == 2
        assert rows[0][0] == "S-01"
        assert rows[0][1] == 45.2
        assert rows[1][2] is None

        meta = dict(cur.execute("SELECT key, value FROM _meta").fetchall())
        assert meta["rows_imported"] == "3"
        assert meta["duplicates_removed"] == "1"
        assert meta["source_pdf"] == "demo.pdf"
    finally:
        conn.close()


def test_import_empty_workbook(tmp_path) -> None:
    xlsx = tmp_path / "empty.xlsx"
    write_excel([], xlsx, language="en")

    db = tmp_path / "empty.db"
    info = import_package(db, xlsx)

    assert info["rows_imported"] == 0
    assert len(info["tables"]) == 0
    assert len(info["skipped_sheets"]) == 1


def test_cli_flag() -> None:
    from pdf_excel.cli import build_parser

    args = build_parser().parse_args(["--import-db"])
    assert args.import_db is True


def test_standalone_main(tmp_path) -> None:
    from pdf_excel.db_import import main

    html = "<table><tr><th>A</th></tr><tr><td>1</td></tr></table>"
    xlsx = tmp_path / "solo.xlsx"
    write_excel([_table(1, "Solo", html)], xlsx, language="en")

    rc = main([str(xlsx)])
    assert rc == 0
    assert xlsx.with_suffix(".db").is_file()


def test_warehouse_aggregate(tmp_path) -> None:
    from pdf_excel.db_import import import_warehouse

    xa = tmp_path / "doc_a.xlsx"
    xb = tmp_path / "doc_b.xlsx"
    write_excel(
        [_table(1, "Alpha", "<table><tr><th>A</th></tr><tr><td>1</td></tr></table>")],
        xa,
        language="en",
    )
    write_excel(
        [_table(1, "Beta", "<table><tr><th>B</th></tr><tr><td>2</td></tr></table>")],
        xb,
        language="en",
    )

    wh = tmp_path / "warehouse.db"
    stats = import_warehouse(wh, [("doc_a.pdf", xa), ("doc_b.pdf", xb)])
    assert stats["tables"] == 2
    assert stats["rows_imported"] == 2

    conn = sqlite3.connect(wh)
    try:
        names = [r[0] for r in conn.execute("SELECT name FROM sqlite_master WHERE type='table'")]
        assert any(n.startswith("doc_a__") for n in names)
        assert any(n.startswith("doc_b__") for n in names)
        pkgs = {r[0] for r in conn.execute("SELECT DISTINCT package FROM _meta")}
        assert pkgs == {"doc_a.pdf", "doc_b.pdf"}
    finally:
        conn.close()

    # re-importing one package is idempotent: its tables are rebuilt, not duplicated
    stats2 = import_warehouse(wh, [("doc_a.pdf", xa)])
    assert stats2["rows_imported"] == 1
    conn = sqlite3.connect(wh)
    try:
        names = [r[0] for r in conn.execute("SELECT name FROM sqlite_master WHERE type='table'")]
        assert sum(1 for n in names if n.startswith("doc_a__")) == 1
    finally:
        conn.close()
