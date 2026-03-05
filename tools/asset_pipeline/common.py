#!/usr/bin/env python3
"""Shared domain logic for character asset pipeline tools."""

from __future__ import annotations

from dataclasses import dataclass, asdict
from pathlib import Path
from typing import Optional
import os
import re

SUPPORTED_EXTENSIONS = {"png", "webp"}

CANONICAL_FRAME_SPECS = {
    "star-idle": (256, 256),
    "star-working-spritesheet-grid": (300, 300),
    "sync-animation-v3-grid": (256, 256),
    "error-bug-spritesheet-grid": (220, 220),
}

PROJECT_ROOT = Path(__file__).resolve().parents[2]

FILENAME_META_PATTERN = re.compile(r"^.+__c[^_]+_r[^.]+\.[^.]+$")
GRID_META_PATTERN = re.compile(r"^c(?P<cols>[^_]+)_r(?P<rows>[^.]+)$")


@dataclass
class ParseResult:
    file_name: str
    file_path: str
    valid: bool
    reason: Optional[str]
    assetType: Optional[str]
    variant: Optional[str]
    cols: Optional[int]
    rows: Optional[int]
    ext: Optional[str]

    def to_dict(self) -> dict:
        return asdict(self)


def resolve_cli_path(raw_path: str, *, base_dir: Path | None = None) -> Path:
    """Resolve env/home/relative path from CLI argument into absolute path."""
    expanded = os.path.expandvars(os.path.expanduser(raw_path))
    path = Path(expanded)
    if path.is_absolute():
        return path
    root = base_dir or PROJECT_ROOT
    return (root / path).resolve()


def parse_asset_filename(path: Path) -> ParseResult:
    file_name = path.name
    stem, dot, ext_raw = file_name.rpartition(".")
    if dot == "":
        return _invalid(path, "INVALID_FILENAME")

    ext = ext_raw.lower()
    if ext not in SUPPORTED_EXTENSIONS:
        return _invalid(path, "UNSUPPORTED_EXTENSION")

    if not FILENAME_META_PATTERN.match(file_name):
        return _invalid(path, "INVALID_FILENAME")

    main_part, sep, meta_part = stem.partition("__")
    if sep == "":
        return _invalid(path, "INVALID_FILENAME")

    asset_type, dash, variant = main_part.rpartition("-")
    if dash == "" or not asset_type or not variant:
        return _invalid(path, "INVALID_FILENAME")

    grid_match = GRID_META_PATTERN.match(meta_part)
    if not grid_match:
        return _invalid(path, "INVALID_FILENAME")

    cols_raw = grid_match.group("cols")
    rows_raw = grid_match.group("rows")

    try:
        cols = int(cols_raw)
        rows = int(rows_raw)
    except ValueError:
        return _invalid(path, "NON_INTEGER_GRID", asset_type, variant, ext=ext)

    if cols <= 0 or rows <= 0:
        return _invalid(path, "NON_POSITIVE_GRID", asset_type, variant, ext=ext)

    return ParseResult(
        file_name=file_name,
        file_path=str(path.resolve()),
        valid=True,
        reason=None,
        assetType=asset_type,
        variant=variant,
        cols=cols,
        rows=rows,
        ext=ext,
    )


def _invalid(
    path: Path,
    reason: str,
    asset_type: Optional[str] = None,
    variant: Optional[str] = None,
    ext: Optional[str] = None,
) -> ParseResult:
    return ParseResult(
        file_name=path.name,
        file_path=str(path.resolve()),
        valid=False,
        reason=reason,
        assetType=asset_type,
        variant=variant,
        cols=None,
        rows=None,
        ext=ext,
    )
