# -*- coding: utf-8 -*-
"""
Backward-compatible entry point.

Prefer:
  python -m pdf_excel [options] [name filters...]

This script forwards to the packaged CLI.
"""

from __future__ import annotations

import sys
from pathlib import Path

# Allow running without install: repo root on sys.path
_ROOT = Path(__file__).resolve().parent
if str(_ROOT) not in sys.path:
    sys.path.insert(0, str(_ROOT))

from pdf_excel.cli import main

if __name__ == "__main__":
    raise SystemExit(main())
