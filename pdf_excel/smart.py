# -*- coding: utf-8 -*-
"""Optional LLM smart layer: normalize messy multi-level / merged headers.

Why this exists (see AGENTS.md "Known pitfalls"): MinerU's HTML tables often
carry multi-level headers, merged cells and broken column names. The classic
fix is human/vision QC by hand. This module offers an *opt-in* alternative:

  1. ``enhance_grid`` — ask an LLM to infer how many leading rows are headers
     and produce one flat, normalized header row (merging multi-level names).
  2. ``apply_smart`` — replace those header rows with the normalized row,
     leaving all data rows untouched.

Design rules:
- **Never blocks**: any failure returns warnings; callers keep the original grid.
- **Validated**: out-of-range or malformed LLM output is clamped or ignored.
- **Provider-agnostic**: any OpenAI-compatible /chat/completions endpoint
  works; the HTTP call uses only the stdlib (no new dependencies).
- Off by default — wiring into the pipeline happens behind an explicit flag.
"""

from __future__ import annotations

import json
import re
import urllib.request
from dataclasses import dataclass, field
from typing import Any, Protocol

MAX_PREVIEW_ROWS = 12
MAX_PREVIEW_COLS = 24
MAX_HEADER_ROWS = 4

SYSTEM_PROMPT = (
    "You are a precise data engineer working on Chinese/English scientific tables. "
    "You receive a table grid extracted from a PDF (first rows preview; empty strings "
    "usually come from merged cells). "
    "Reply with ONE JSON object only, no prose, no markdown fences. Schema: "
    '{"header_rows": <int, how many leading rows are the table header>, '
    '"columns": [<flat normalized column names, one per grid column, merge multi-level '
    'names with a short separator like "_">], '
    '"warnings": [<short strings, optional>]}'
)


class LLMClient(Protocol):
    """Minimal client contract — implement this to plug any model."""

    def complete_json(self, prompt: str) -> dict[str, Any]:  # pragma: no cover
        ...


def extract_json(text: str) -> dict[str, Any]:
    """Pull the first JSON object out of a model reply (tolerates fences/prose)."""
    t = str(text or "").strip()
    t = re.sub(r"^```(?:json)?", "", t).strip()
    t = re.sub(r"```$", "", t).strip()
    try:
        obj = json.loads(t)
        if isinstance(obj, dict):
            return obj
    except json.JSONDecodeError:
        pass
    start = t.find("{")
    end = t.rfind("}")
    if start != -1 and end > start:
        try:
            obj = json.loads(t[start : end + 1])
            if isinstance(obj, dict):
                return obj
        except json.JSONDecodeError:
            pass
    return {}


class OpenAICompatClient:
    """Any OpenAI-compatible provider (OpenAI/DeepSeek/GLM/Kimi/local...)."""

    def __init__(
        self,
        *,
        base_url: str,
        api_key: str,
        model: str,
        timeout: float = 60.0,
    ) -> None:
        self.base_url = str(base_url).rstrip("/")
        self.api_key = api_key
        self.model = model
        self.timeout = timeout

    def complete_json(self, prompt: str) -> dict[str, Any]:
        payload = {
            "model": self.model,
            "temperature": 0,
            "messages": [
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": prompt},
            ],
        }
        req = urllib.request.Request(
            f"{self.base_url}/chat/completions",
            data=json.dumps(payload, ensure_ascii=False).encode("utf-8"),
            headers={
                "Content-Type": "application/json",
                "Authorization": f"Bearer {self.api_key}",
            },
            method="POST",
        )
        with urllib.request.urlopen(req, timeout=self.timeout) as resp:
            data = json.loads(resp.read().decode("utf-8"))
        content = data["choices"][0]["message"]["content"]
        return extract_json(content)


@dataclass
class SmartResult:
    columns: list[str] = field(default_factory=list)
    header_rows: int = 1
    warnings: list[str] = field(default_factory=list)


def _clean_columns(raw: Any, ncols: int) -> tuple[list[str], list[str]]:
    warnings: list[str] = []
    if not isinstance(raw, list):
        return [], ["llm output: 'columns' missing or not a list"]
    cols = [str(c).strip() for c in raw if c is not None]
    if not cols:
        return [], ["llm output: 'columns' is empty"]
    if len(cols) > ncols:
        cols = cols[:ncols]
        warnings.append(f"columns truncated to {ncols}")
    if len(cols) < ncols:
        cols += [""] * (ncols - len(cols))
        warnings.append(f"columns padded to {ncols}")
    return cols, warnings


def enhance_grid(
    grid: list[list[str]],
    caption: str,
    client: LLMClient,
) -> SmartResult:
    """Ask the LLM for a normalized header row. Never raises."""
    if not grid or not grid[0]:
        return SmartResult(warnings=["empty grid"])
    ncols = len(grid[0])
    preview = [row[:MAX_PREVIEW_COLS] for row in grid[:MAX_PREVIEW_ROWS]]
    prompt = json.dumps(
        {"caption": caption or "", "n_columns": ncols, "rows_preview": preview},
        ensure_ascii=False,
    )
    try:
        data = client.complete_json(prompt)
    except Exception as e:  # network/API/model errors must not break packaging
        return SmartResult(warnings=[f"llm call failed: {e}"])

    if not data:
        return SmartResult(warnings=["llm output: no JSON object found"])

    try:
        header_rows = int(data.get("header_rows") or 1)
    except (TypeError, ValueError):
        header_rows = 1
    header_rows = max(1, min(header_rows, MAX_HEADER_ROWS, len(grid)))

    cols, warnings = _clean_columns(data.get("columns"), ncols)
    raw_warnings = data.get("warnings")
    if isinstance(raw_warnings, list):
        warnings += [str(w) for w in raw_warnings if w]
    return SmartResult(columns=cols, header_rows=header_rows, warnings=warnings)


def apply_smart(grid: list[list[str]], result: SmartResult) -> list[list[str]]:
    """Replace the first ``header_rows`` rows with one normalized header row."""
    if not grid or not result.columns:
        return grid
    ncols = len(grid[0])
    cols = list(result.columns)[:ncols]
    cols += [""] * (ncols - len(cols))
    hr = max(1, min(result.header_rows, len(grid)))
    return [cols] + grid[hr:]


def should_enhance(grid: list[list[str]]) -> bool:
    """Cheap signal for merged / multi-level headers: gaps in the header row."""
    if len(grid) < 2 or not grid[0]:
        return False
    return any(not ("" if cell is None else str(cell).strip()) for cell in grid[0])


class SmartEnhancer:
    """Applies LLM header normalization, but only where the grid asks for it.

    Clean tables cost zero API calls; messy ones get one call. All failures
    degrade to warnings and the original grid is kept.
    """

    def __init__(self, client: LLMClient) -> None:
        self.client = client
        self.enhanced_count = 0
        self.warnings: list[str] = []

    def enhance(
        self, grid: list[list[str]], caption: str
    ) -> tuple[list[list[str]], list[str]]:
        if not should_enhance(grid):
            return grid, []
        result = enhance_grid(grid, caption, self.client)
        self.warnings.extend(result.warnings)
        if not result.columns:
            return grid, result.warnings
        self.enhanced_count += 1
        return apply_smart(grid, result), result.warnings
