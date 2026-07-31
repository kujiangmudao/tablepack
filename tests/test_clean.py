# -*- coding: utf-8 -*-
from pdf_excel.clean import clean_cell_text, safe_filename


def test_oxide_cleanup():
    assert clean_cell_text("Al₂O₃") == "Al2O3"
    assert "Al2O3" in clean_cell_text("Al2O{3")
    assert clean_cell_text("w1%") == "w/%"


def test_safe_filename():
    assert ":" not in safe_filename('表1: a/b')
    assert len(safe_filename("x" * 100)) <= 60
