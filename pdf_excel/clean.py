# -*- coding: utf-8 -*-
"""Text normalization for OCR / MinerU artifacts."""

from __future__ import annotations

import html
import re

# Order matters for some overlapping patterns.
OCR_REPLACEMENTS: list[tuple[str, str]] = [
    # oxide formulas
    ("Al2O{3", "Al2O3"),
    ("Al{2O_3", "Al2O3"),
    ("Al{2}O{3}", "Al2O3"),
    ("Al₂O₃", "Al2O3"),
    ("Fe₂O₃", "Fe2O3"),
    ("Fe2O{3", "Fe2O3"),
    ("SiO₂", "SiO2"),
    ("SiO{2", "SiO2"),
    ("TiO₂", "TiO2"),
    ("CaO", "CaO"),  # no-op anchor for doc
    ("K₂O", "K2O"),
    ("Na₂O", "Na2O"),
    ("MgO", "MgO"),
    ("P₂O₅", "P2O5"),
    ("MnO", "MnO"),
    ("SO₃", "SO3"),
    # weight percent labels
    ("w1%", "w/%"),
    ("w₁%", "w/%"),
    ("w₁ /%", "w/%"),
    ("ω/%", "w/%"),
    # coal seam / sample noise
    ("~#", "#"),
    ("＃", "#"),
]

# Extra regex cleanups
OCR_REGEX: list[tuple[re.Pattern[str], str]] = [
    (re.compile(r"Al\s*2\s*O\s*3", re.I), "Al2O3"),
    (re.compile(r"Fe\s*2\s*O\s*3", re.I), "Fe2O3"),
    (re.compile(r"</?sub>|</?sup>|</?b>|</?i>", re.I), ""),
]


def clean_cell_text(text: str | None) -> str:
    if text is None:
        return ""
    t = html.unescape(str(text))
    t = t.replace("\xa0", " ")
    t = re.sub(r"\s+", " ", t).strip()
    for a, b in OCR_REPLACEMENTS:
        if a != b:
            t = t.replace(a, b)
    for pat, repl in OCR_REGEX:
        t = pat.sub(repl, t)
    return t


def safe_filename(name: str, max_len: int = 60) -> str:
    name = re.sub(r'[<>:"/\\|?*\s]+', "_", name or "untitled")
    name = re.sub(r"_+", "_", name).strip("._")
    return (name or "untitled")[:max_len]
