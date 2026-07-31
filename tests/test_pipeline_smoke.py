# -*- coding: utf-8 -*-
"""Smoke: rebuild one package from existing MinerU cache when available."""

from __future__ import annotations

from pathlib import Path

import pytest

from pdf_excel.config import load_settings
from pdf_excel.pipeline import find_auto_dir, package_output


REPO = Path(__file__).resolve().parents[1]


@pytest.mark.skipif(
    not (REPO / "work" / "mineru_raw").is_dir(),
    reason="no local MinerU cache",
)
def test_package_from_cache(tmp_path: Path, monkeypatch):
    monkeypatch.chdir(REPO)
    s = load_settings(root=REPO)
    # Prefer a small known stem if present
    preferred = "大同矿区5~#煤层煤岩煤质特征及其清洁利用方式_赵彦"
    stem = preferred if find_auto_dir(s, preferred) else None
    if stem is None:
        for d in sorted(s.work_dir.iterdir()):
            if d.is_dir() and (d / "auto").is_dir():
                stem = d.name
                break
    if stem is None:
        pytest.skip("no auto/ cache dirs")

    pdf = s.pdf_dir / f"{stem}.pdf"
    if not pdf.is_file():
        # create a dummy path only if cache exists — package needs file
        # Skip rather than invent PDF bytes
        pytest.skip(f"source PDF missing for cached stem: {stem}")

    s.output_dir = tmp_path / "out"
    s.wipe_output_package = True
    r = package_output(s, pdf, force_mineru=False)
    assert r["ok"] is True
    out = Path(r["out_dir"])
    assert (out / f"{stem}.xlsx").is_file()
    assert (out / "原始表格").is_dir()
    notes = list(out.glob("*.md"))
    assert notes, "expected 转换说明.md or 问题说明.md"
