# -*- coding: utf-8 -*-
"""Optional post-step: turn packaged workbooks into queryable SQLite data assets.

  output/<stem>/<stem>.xlsx  →  output/<stem>/<stem>.db

Design rules (conservative, aligned with AGENTS.md):
- Never fabricate: values are only *typed* (int/float) when unambiguous;
  anything else stays TEXT. Blank cells stay NULL.
- Exact duplicate data rows inside one sheet are skipped and **counted**
  (duplicates_removed is reported, extraction is never silent).
- Every row gets provenance columns: _src_pdf, _src_sheet, _src_row.
- Sheet layout comes from excel_writer: leading meta rows, then the header
  row = the first row whose cells are bold, then data rows.

The step is opt-in (`import_db: true` / `--import-db`) and purely additive.
"""

from __future__ import annotations

import argparse
import datetime as _dt
import json
import re
import sqlite3
import sys
from pathlib import Path
from typing import Any

from openpyxl import load_workbook

from . import __version__

_INT_RE = re.compile(r"^[+-]?\d+$")
_GROUPED_INT_RE = re.compile(r"^[+-]?\d{1,3}(?:,\d{3})+$")
_FLOAT_RE = re.compile(r"^[+-]?(?:\d+\.\d*|\.\d+)(?:[eE][+-]?\d+)?$")

PROVENANCE_COLUMNS = ("_src_pdf", "_src_sheet", "_src_row")


def infer_value(raw: Any) -> Any:
    """Type a single cell value; ambiguous strings stay TEXT."""
    if raw is None:
        return None
    if isinstance(raw, bool):
        return str(raw)
    if isinstance(raw, (int, float)):
        return raw
    s = str(raw).strip()
    if s == "":
        return None
    if _INT_RE.match(s):
        try:
            return int(s)
        except ValueError:
            return s
    if _GROUPED_INT_RE.match(s):
        try:
            return int(s.replace(",", ""))
        except ValueError:
            return s
    if _FLOAT_RE.match(s):
        try:
            return float(s)
        except ValueError:
            return s
    return s


def _quote_ident(name: str) -> str:
    return '"' + str(name).replace('"', '""') + '"'


def _dedupe_names(names: list[str], prefix: str) -> list[str]:
    used: dict[str, int] = {}
    out: list[str] = []
    for i, n in enumerate(names, 1):
        base = (n or "").strip() or f"{prefix}{i}"
        seen = used.get(base, 0)
        out.append(base if seen == 0 else f"{base}_{seen + 1}")
        used[base] = seen + 1
    return out


def _find_header_row(ws) -> int | None:
    """Header = first row containing a bold cell (written by excel_writer)."""
    for row in ws.iter_rows(min_row=1):
        for cell in row:
            if cell.value is not None and cell.font is not None and cell.font.bold:
                return cell.row
    return None


def _sheet_rows(ws, header_row: int, n_cols: int):
    """Yield (excel_row_number, [values]) for data rows below the header."""
    for r in range(header_row + 1, ws.max_row + 1):
        values = [ws.cell(row=r, column=c).value for c in range(1, n_cols + 1)]
        yield r, values


def import_package(
    db_path: str | Path,
    xlsx_path: str | Path,
    *,
    source_pdf: str | None = None,
    generated_at: str | None = None,
    table_prefix: str = "",
    append: bool = False,
) -> dict[str, Any]:
    """Import one packaged workbook into a fresh SQLite database.

    Returns a stats dict; nothing here raises for empty/failed sheets —
    those are recorded under ``skipped_sheets``.
    """
    db_path = Path(db_path)
    xlsx_path = Path(xlsx_path)
    result: dict[str, Any] = {
        "ok": True,
        "db": str(db_path),
        "xlsx": str(xlsx_path),
        "tables": [],
        "rows_imported": 0,
        "duplicates_removed": 0,
        "skipped_sheets": [],
    }

    wb = load_workbook(xlsx_path)
    db_path.parent.mkdir(parents=True, exist_ok=True)
    if db_path.exists() and not append:
        db_path.unlink()

    conn = sqlite3.connect(db_path)
    try:
        used_tables: set[str] = set()
        for sheet in wb.sheetnames:
            ws = wb[sheet]
            header_row = _find_header_row(ws)
            if header_row is None:
                result["skipped_sheets"].append(
                    {"sheet": sheet, "reason": "no header row (meta-only or failed sheet)"}
                )
                continue

            headers = _dedupe_names(
                [ws.cell(row=header_row, column=c).value for c in range(1, ws.max_column + 1)],
                prefix="col",
            )
            n_cols = len(headers)

            table = f"{table_prefix}{sheet}"
            if table in used_tables:
                i = 2
                while f"{table}_{i}" in used_tables:
                    i += 1
                table = f"{table}_{i}"
            used_tables.add(table)

            cols_sql = ", ".join(_quote_ident(h) for h in headers)
            prov_sql = ", ".join(f"{_quote_ident(p)} TEXT" for p in PROVENANCE_COLUMNS)
            conn.execute(f"DROP TABLE IF EXISTS {_quote_ident(table)}")
            conn.execute(f"CREATE TABLE {_quote_ident(table)} ({cols_sql}, {prov_sql})")

            seen_hashes: set[tuple] = set()
            rows_inserted = 0
            dupes = 0
            placeholders = ", ".join("?" for _ in range(n_cols + len(PROVENANCE_COLUMNS)))
            insert_sql = (
                f"INSERT INTO {_quote_ident(table)} VALUES ({placeholders})"
            )
            batch: list[tuple] = []
            for excel_row, raw_values in _sheet_rows(ws, header_row, n_cols):
                values = [infer_value(v) for v in raw_values]
                if all(v is None for v in values):
                    continue
                key = tuple(values)
                if key in seen_hashes:
                    dupes += 1
                    continue
                seen_hashes.add(key)
                batch.append(tuple(values) + (source_pdf, sheet, excel_row))
            if batch:
                conn.executemany(insert_sql, batch)
            rows_inserted = len(batch)

            result["tables"].append(
                {
                    "sheet": sheet,
                    "table": table,
                    "columns": headers,
                    "rows": rows_inserted,
                    "duplicates_removed": dupes,
                }
            )
            result["rows_imported"] += rows_inserted
            result["duplicates_removed"] += dupes

        meta_package = source_pdf or xlsx_path.stem
        meta = {
            "tablepack_version": __version__,
            "source_pdf": source_pdf or "",
            "source_xlsx": xlsx_path.name,
            "generated_at": generated_at or _dt.datetime.now().isoformat(timespec="seconds"),
            "sheets_imported": str(len(result["tables"])),
            "sheets_skipped": str(len(result["skipped_sheets"])),
            "rows_imported": str(result["rows_imported"]),
            "duplicates_removed": str(result["duplicates_removed"]),
        }
        conn.execute(
            "CREATE TABLE IF NOT EXISTS _meta "
            "(package TEXT, key TEXT, value TEXT, PRIMARY KEY (package, key))"
        )
        conn.execute("DELETE FROM _meta WHERE package = ?", (meta_package,))
        conn.executemany(
            "INSERT INTO _meta (package, key, value) VALUES (?, ?, ?)",
            [(meta_package, k, v) for k, v in meta.items()],
        )
        conn.commit()
    finally:
        conn.close()

    return result


def import_warehouse(
    warehouse_path: str | Path,
    packages: list[tuple[str, str | Path]],
    *,
    generated_at: str | None = None,
) -> dict[str, Any]:
    """Import many packaged workbooks into one shared SQLite warehouse.

    ``packages`` is a list of ``(source_label, xlsx_path)``. Table names are
    prefixed with ``"<stem>__"`` to stay collision-free; re-importing the same
    package rebuilds its tables (idempotent). The database file is reused.
    """
    warehouse_path = Path(warehouse_path)
    result: dict[str, Any] = {
        "ok": True,
        "db": str(warehouse_path),
        "packages": [],
        "tables": 0,
        "rows_imported": 0,
        "duplicates_removed": 0,
    }
    for label, xlsx in packages:
        xlsx = Path(xlsx)
        info = import_package(
            warehouse_path,
            xlsx,
            source_pdf=label,
            generated_at=generated_at,
            table_prefix=f"{xlsx.stem}__",
            append=True,
        )
        result["packages"].append(
            {"source": label, "tables": len(info["tables"]), "rows": info["rows_imported"]}
        )
        result["tables"] += len(info["tables"])
        result["rows_imported"] += info["rows_imported"]
        result["duplicates_removed"] += info["duplicates_removed"]
    return result


def main(argv: list[str] | None = None) -> int:
    """Standalone CLI: import packaged workbooks into SQLite.

        python -m pdf_excel.db_import output/<stem>/<stem>.xlsx
    """
    parser = argparse.ArgumentParser(
        prog="python -m pdf_excel.db_import",
        description="Import packaged TablePack workbooks into <stem>.db (SQLite).",
    )
    parser.add_argument("xlsx", nargs="+", type=Path, help="Path(s) to packaged <stem>.xlsx")
    parser.add_argument(
        "--db",
        type=Path,
        default=None,
        help="Database path (single input only; default: next to the xlsx)",
    )
    parser.add_argument("--source-pdf", default=None, help="Original PDF name recorded in provenance")
    args = parser.parse_args(argv)

    if args.db and len(args.xlsx) > 1:
        print("--db only makes sense with a single xlsx input", file=sys.stderr)
        return 2

    failures = 0
    for xlsx in args.xlsx:
        if not xlsx.is_file():
            print(f"not found: {xlsx}", file=sys.stderr)
            failures += 1
            continue
        db_path = args.db or xlsx.with_suffix(".db")
        try:
            info = import_package(db_path, xlsx, source_pdf=args.source_pdf)
            print(
                json.dumps(
                    {
                        "db": info["db"],
                        "tables": len(info["tables"]),
                        "rows": info["rows_imported"],
                        "duplicates_removed": info["duplicates_removed"],
                    },
                    ensure_ascii=False,
                )
            )
        except Exception as e:
            print(f"[db] import failed for {xlsx}: {e}", file=sys.stderr)
            failures += 1
    return 0 if failures == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())
