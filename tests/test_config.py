# -*- coding: utf-8 -*-
from pathlib import Path

from pdf_excel.config import _coerce_bool, load_settings


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


def test_relative_paths_under_root_not_cwd(tmp_path: Path, monkeypatch):
    """Regression: relative pdf_dir must join project root, not process cwd."""
    project = tmp_path / "proj"
    project.mkdir()
    (project / "pdf").mkdir()
    other = tmp_path / "other"
    other.mkdir()
    monkeypatch.chdir(other)
    for k in list(__import__("os").environ):
        if k.startswith("PDF_EXCEL") or k == "MINERU_BIN":
            monkeypatch.delenv(k, raising=False)
    s = load_settings(
        root=project,
        overrides={"pdf_dir": Path("pdf"), "output_dir": Path("output"), "work_dir": Path("work/mineru_raw")},
    )
    assert s.pdf_dir == (project / "pdf").resolve()
    assert s.output_dir == (project / "output").resolve()
    assert s.work_dir == (project / "work" / "mineru_raw").resolve()
    assert s.pdf_dir.exists()


def test_coerce_bool():
    assert _coerce_bool("true") is True
    assert _coerce_bool("false") is False
    assert _coerce_bool(True) is True
    assert _coerce_bool("yes") is True


def test_output_language_default_and_overrides(tmp_path: Path, monkeypatch):
    for k in list(__import__("os").environ):
        if k.startswith("PDF_EXCEL") or k == "MINERU_BIN":
            monkeypatch.delenv(k, raising=False)
    s = load_settings(root=tmp_path)
    assert s.output_language == "zh"
    s2 = load_settings(root=tmp_path, overrides={"output_language": "en"})
    assert s2.output_language == "en"
    monkeypatch.setenv("PDF_EXCEL_OUTPUT_LANGUAGE", "en")
    s3 = load_settings(root=tmp_path)
    assert s3.output_language == "en"


def test_output_language_normalize():
    from pdf_excel.names import normalize_language

    assert normalize_language("EN") == "en"
    assert normalize_language("en-US") == "en"
    assert normalize_language("fr") == "zh"
    assert normalize_language(None) == "zh"
