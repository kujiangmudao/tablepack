# -*- coding: utf-8 -*-
from __future__ import annotations

from dataclasses import dataclass, field


@dataclass
class TableItem:
    index: int
    page_idx: int
    caption: str
    caption_raw: list
    footnote: list
    html_body: str
    img_path: str | None
    bbox: list | None
    issues: list[str] = field(default_factory=list)

    @property
    def is_empty(self) -> bool:
        return not (self.html_body and str(self.html_body).strip())


@dataclass
class ImageItem:
    type: str  # image | chart
    page_idx: int
    img_path: str
    caption: str
