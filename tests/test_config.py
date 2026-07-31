# -*- coding: utf-8 -*-
from pathlib import Path

from pdf_excel.config import load_settings


def test_defaults(tmp_path: Path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    # clear env that might leak from user machine
    for k in list(__import__("os").environ):
        if k.startswith("PDF_EXCEL") or k == "MINERU_BIN":
            monkeypatch.delenv(k, raising=False)
    s = load_settings(root=tmp_path)
    assert s.pdf_dir == (tmp_path / "pdf").resolve()
    assert s.output_dir == (tmp_path / "output").resolve()
    assert s.backend == "pipeline"
    assert s.drop_empty_tables is True


def test_env_override(tmp_path: Path, monkeypatch):
    custom = tmp_path / "my_pdfs"
    custom.mkdir()
    monkeypatch.setenv("PDF_EXCEL_PDF_DIR", str(custom))
    s = load_settings(root=tmp_path)
    assert s.pdf_dir == custom.resolve()
