# -*- coding: utf-8 -*-
"""Parse MinerU content_list JSON into TableItem / ImageItem."""

from __future__ import annotations

import json
import re
from pathlib import Path

from bs4 import BeautifulSoup

from .clean import clean_cell_text
from .models import ImageItem, TableItem


def find_content_list(auto_dir: Path) -> Path | None:
    cl_candidates = list(auto_dir.glob("*_content_list.json"))
    # prefer non-v2 (v1 has table_body HTML)
    for p in cl_candidates:
        if not p.name.endswith("_content_list_v2.json") and "v2" not in p.name:
            return p
    return cl_candidates[0] if cl_candidates else None


def parse_content_list(content_list_path: Path) -> tuple[list[TableItem], list[ImageItem]]:
    data = json.loads(content_list_path.read_text(encoding="utf-8"))
    tables: list[TableItem] = []
    images: list[ImageItem] = []
    t_idx = 0
    for item in data:
        typ = item.get("type")
        page_idx = int(item.get("page_idx", 0) or 0)
        if typ == "table":
            t_idx += 1
            caps = item.get("table_caption") or []
            if isinstance(caps, str):
                caps = [caps]
            cap_texts = []
            for c in caps:
                if not c:
                    continue
                txt = BeautifulSoup(str(c), "lxml").get_text(" ", strip=True)
                txt = clean_cell_text(txt)
                cap_texts.append(txt)
            caption = " | ".join(cap_texts) if cap_texts else ""
            zh = [c for c in cap_texts if re.search(r"[\u4e00-\u9fff]", c)]
            if zh:
                caption = zh[0] if len(zh) == 1 else " ".join(zh)

            footnotes = item.get("table_footnote") or []
            tables.append(
                TableItem(
                    index=t_idx,
                    page_idx=page_idx,
                    caption=caption,
                    caption_raw=caps,
                    footnote=footnotes if isinstance(footnotes, list) else [footnotes],
                    html_body=item.get("table_body") or "",
                    img_path=item.get("img_path"),
                    bbox=item.get("bbox"),
                )
            )
        elif typ in ("image", "chart"):
            img_rel = item.get("img_path")
            if not img_rel:
                continue
            caps = item.get("image_caption") or item.get("table_caption") or item.get("caption") or []
            if isinstance(caps, str):
                caps = [caps]
            cap = " ".join(
                clean_cell_text(BeautifulSoup(str(c), "lxml").get_text(" ", strip=True)) for c in caps if c
            )
            images.append(ImageItem(type=typ, page_idx=page_idx, img_path=img_rel, caption=cap))
    return tables, images


def reindex_tables(tables: list[TableItem]) -> list[TableItem]:
    for i, t in enumerate(tables, 1):
        t.index = i
    return tables
