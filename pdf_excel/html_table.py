# -*- coding: utf-8 -*-
"""HTML table (rowspan/colspan) → 2D string grid."""

from __future__ import annotations

from bs4 import BeautifulSoup

from .clean import clean_cell_text


def html_table_to_grid(table_html: str) -> tuple[list[list[str]], list[str]]:
    """
    Convert HTML table with rowspan/colspan into a 2D grid of strings.
    Merged cells: value written only at top-left; other span cells left empty.
    Returns (grid, issues).
    """
    issues: list[str] = []
    if not table_html or not str(table_html).strip():
        return [], ["empty HTML table_body"]

    soup = BeautifulSoup(table_html, "lxml")
    table = soup.find("table")
    if table is None:
        soup2 = BeautifulSoup(f"<table>{table_html}</table>", "lxml")
        table = soup2.find("table")
    if table is None:
        return [], ["no <table> found in table_body"]

    rows = table.find_all("tr")
    if not rows:
        return [], ["table has no rows"]

    occupied: dict[tuple[int, int], str | None] = {}
    max_r = 0
    max_c = 0

    for r_idx, tr in enumerate(rows):
        c_idx = 0
        cells = tr.find_all(["td", "th"], recursive=False)
        if not cells:
            cells = tr.find_all(["td", "th"])

        for cell in cells:
            while (r_idx, c_idx) in occupied:
                c_idx += 1
            try:
                rowspan = max(1, int(cell.get("rowspan", 1) or 1))
            except ValueError:
                rowspan = 1
            try:
                colspan = max(1, int(cell.get("colspan", 1) or 1))
            except ValueError:
                colspan = 1

            text = clean_cell_text(cell.get_text(separator=" ", strip=True))

            for dr in range(rowspan):
                for dc in range(colspan):
                    rr, cc = r_idx + dr, c_idx + dc
                    if (rr, cc) in occupied and occupied[(rr, cc)] is not None and (dr, dc) != (0, 0):
                        issues.append(f"cell overlap at row={rr + 1} col={cc + 1}")
                    if dr == 0 and dc == 0:
                        occupied[(rr, cc)] = text
                    else:
                        occupied.setdefault((rr, cc), None)
                    max_r = max(max_r, rr)
                    max_c = max(max_c, cc)
            c_idx += colspan

    nrows, ncols = max_r + 1, max_c + 1
    grid = [["" for _ in range(ncols)] for _ in range(nrows)]
    for (r, c), v in occupied.items():
        if v is not None and 0 <= r < nrows and 0 <= c < ncols:
            grid[r][c] = v

    while grid and all(not cell for cell in grid[-1]):
        grid.pop()
    if grid:
        while ncols > 0 and all(len(row) >= ncols and not row[ncols - 1] for row in grid):
            for row in grid:
                row.pop()
            ncols -= 1
            if ncols == 0:
                break

    if not grid:
        issues.append("parsed grid is empty")
    return grid, issues
