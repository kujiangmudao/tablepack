# -*- coding: utf-8 -*-
"""Runtime configuration: env vars > config.yaml > sensible defaults."""

from __future__ import annotations

import os
import shutil
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

try:
    import yaml  # type: ignore
except ImportError:  # optional dependency
    yaml = None


def _first_existing(paths: list[Path]) -> Path | None:
    for p in paths:
        if p and Path(p).exists():
            return Path(p)
    return None


def discover_mineru() -> Path | None:
    """Find mineru executable on PATH or common local install locations."""
    which = shutil.which("mineru")
    if which:
        return Path(which)

    candidates: list[Path] = []
    # Explicit env
    env = os.environ.get("MINERU_BIN") or os.environ.get("PDF_EXCEL_MINERU")
    if env:
        candidates.append(Path(env))

    # Common Windows venv layouts
    home = Path.home()
    candidates.extend(
        [
            Path(r"D:\mineru-work\mineru-env\Scripts\mineru.exe"),
            home / "mineru-work" / "mineru-env" / "Scripts" / "mineru.exe",
            home / "mineru-env" / "Scripts" / "mineru.exe",
            home / "miniconda3" / "envs" / "mineru" / "Scripts" / "mineru.exe",
            home / "anaconda3" / "envs" / "mineru" / "Scripts" / "mineru.exe",
            Path("/usr/local/bin/mineru"),
            Path.home() / ".local" / "bin" / "mineru",
        ]
    )
    return _first_existing(candidates)


def discover_python() -> Path:
    env = os.environ.get("PDF_EXCEL_PYTHON")
    if env and Path(env).exists():
        return Path(env)
    return Path(os.environ.get("PYTHON", "") or __import__("sys").executable)


def _coerce_bool(value: Any, default: bool = False) -> bool:
    if value is None:
        return default
    if isinstance(value, bool):
        return value
    if isinstance(value, (int, float)):
        return bool(value)
    if isinstance(value, str):
        return value.strip().lower() in {"1", "true", "yes", "on", "y"}
    return bool(value)


def _resolve_under_root(root: Path, value: Path | str | None, default_rel: str | None) -> Path:
    """
    Resolve a path relative to *root* (not process cwd).

    Absolute paths stay absolute. Relative paths and defaults join root first,
    so running the CLI from another directory still hits the project tree.
    """
    if value is None:
        if default_rel is None:
            raise ValueError("path value and default_rel are both None")
        return (root / default_rel).resolve()
    p = Path(value)
    if not p.is_absolute():
        p = root / p
    return p.resolve()


@dataclass
class Settings:
    """Project paths and MinerU options."""

    root: Path = field(default_factory=lambda: Path.cwd())
    pdf_dir: Path | None = None
    output_dir: Path | None = None
    work_dir: Path | None = None
    mineru_bin: Path | None = None
    python_bin: Path | None = None

    backend: str = "pipeline"
    method: str = "auto"
    language: str = "ch"
    enable_table: bool = True
    enable_formula: bool = False

    # Pipeline behavior
    drop_empty_tables: bool = True
    skip_existing_excel: bool = False
    wipe_output_package: bool = True

    def resolve(self) -> "Settings":
        root = Path(self.root).expanduser()
        if not root.is_absolute():
            root = (Path.cwd() / root).resolve()
        else:
            root = root.resolve()
        self.root = root
        self.pdf_dir = _resolve_under_root(root, self.pdf_dir, "pdf")
        self.output_dir = _resolve_under_root(root, self.output_dir, "output")
        self.work_dir = _resolve_under_root(root, self.work_dir, "work/mineru_raw")

        if self.mineru_bin:
            mb = Path(self.mineru_bin).expanduser()
            if not mb.is_absolute():
                mb = root / mb
            self.mineru_bin = mb.resolve()
        else:
            self.mineru_bin = discover_mineru()

        if self.python_bin:
            pb = Path(self.python_bin).expanduser()
            if not pb.is_absolute():
                pb = root / pb
            self.python_bin = pb.resolve()
        else:
            self.python_bin = discover_python()

        self.enable_table = _coerce_bool(self.enable_table, True)
        self.enable_formula = _coerce_bool(self.enable_formula, False)
        self.drop_empty_tables = _coerce_bool(self.drop_empty_tables, True)
        self.skip_existing_excel = _coerce_bool(self.skip_existing_excel, False)
        self.wipe_output_package = _coerce_bool(self.wipe_output_package, True)
        return self

    def as_dict(self) -> dict[str, Any]:
        return {
            "root": str(self.root),
            "pdf_dir": str(self.pdf_dir),
            "output_dir": str(self.output_dir),
            "work_dir": str(self.work_dir),
            "mineru_bin": str(self.mineru_bin) if self.mineru_bin else None,
            "python_bin": str(self.python_bin) if self.python_bin else None,
            "backend": self.backend,
            "method": self.method,
            "language": self.language,
            "enable_table": self.enable_table,
            "enable_formula": self.enable_formula,
            "drop_empty_tables": self.drop_empty_tables,
            "skip_existing_excel": self.skip_existing_excel,
            "wipe_output_package": self.wipe_output_package,
        }


def _load_yaml(path: Path) -> dict[str, Any]:
    if not path.is_file():
        return {}
    if yaml is None:
        # Minimal fallback: only support simple key: value lines
        data: dict[str, Any] = {}
        for line in path.read_text(encoding="utf-8").splitlines():
            line = line.strip()
            if not line or line.startswith("#") or ":" not in line:
                continue
            k, v = line.split(":", 1)
            data[k.strip()] = v.strip().strip("'\"")
        return data
    with path.open(encoding="utf-8") as f:
        return yaml.safe_load(f) or {}


def load_settings(
    root: Path | None = None,
    config_path: Path | None = None,
    overrides: dict[str, Any] | None = None,
) -> Settings:
    """
    Load settings with precedence:
      CLI/overrides > environment > config.yaml > defaults
    """
    root = (root or Path.cwd()).resolve()
    cfg_file = config_path or Path(os.environ.get("PDF_EXCEL_CONFIG", root / "config.yaml"))
    raw = _load_yaml(Path(cfg_file)) if cfg_file else {}

    def env_path(key: str) -> Path | None:
        v = os.environ.get(key)
        return Path(v) if v else None

    s = Settings(root=root)

    # yaml
    if raw.get("root"):
        s.root = Path(raw["root"])
    if raw.get("pdf_dir"):
        s.pdf_dir = Path(raw["pdf_dir"])
    if raw.get("output_dir"):
        s.output_dir = Path(raw["output_dir"])
    if raw.get("work_dir"):
        s.work_dir = Path(raw["work_dir"])
    if raw.get("mineru_bin"):
        s.mineru_bin = Path(raw["mineru_bin"])
    if raw.get("python_bin"):
        s.python_bin = Path(raw["python_bin"])
    for key in ("backend", "method", "language"):
        if key in raw and raw[key] is not None:
            setattr(s, key, raw[key])
    for key in (
        "enable_table",
        "enable_formula",
        "drop_empty_tables",
        "skip_existing_excel",
        "wipe_output_package",
    ):
        if key in raw and raw[key] is not None:
            setattr(s, key, _coerce_bool(raw[key]))

    # env overrides
    if env_path("PDF_EXCEL_ROOT"):
        s.root = env_path("PDF_EXCEL_ROOT")  # type: ignore
    if env_path("PDF_EXCEL_PDF_DIR"):
        s.pdf_dir = env_path("PDF_EXCEL_PDF_DIR")
    if env_path("PDF_EXCEL_OUTPUT_DIR"):
        s.output_dir = env_path("PDF_EXCEL_OUTPUT_DIR")
    if env_path("PDF_EXCEL_WORK_DIR"):
        s.work_dir = env_path("PDF_EXCEL_WORK_DIR")
    if env_path("MINERU_BIN") or env_path("PDF_EXCEL_MINERU"):
        s.mineru_bin = env_path("MINERU_BIN") or env_path("PDF_EXCEL_MINERU")
    if env_path("PDF_EXCEL_PYTHON"):
        s.python_bin = env_path("PDF_EXCEL_PYTHON")
    if os.environ.get("PDF_EXCEL_BACKEND"):
        s.backend = os.environ["PDF_EXCEL_BACKEND"]
    if os.environ.get("PDF_EXCEL_LANG"):
        s.language = os.environ["PDF_EXCEL_LANG"]

    # explicit overrides (CLI)
    if overrides:
        for k, v in overrides.items():
            if v is None:
                continue
            if k in ("root", "pdf_dir", "output_dir", "work_dir", "mineru_bin", "python_bin") and not isinstance(
                v, Path
            ):
                v = Path(v)
            if hasattr(s, k):
                setattr(s, k, v)

    return s.resolve()
