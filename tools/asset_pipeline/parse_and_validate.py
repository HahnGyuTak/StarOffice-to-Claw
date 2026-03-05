#!/usr/bin/env python3
"""Parse and validate tmp_assets filenames into JSON/JSONL reports."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from common import parse_asset_filename, resolve_cli_path


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--input-dir",
        default="tmp_assets",
        help="Directory containing source assets.",
    )
    parser.add_argument(
        "--out-json",
        default="tools/asset_pipeline/reports/validation_report.json",
        help="Summary JSON output path.",
    )
    parser.add_argument(
        "--out-jsonl",
        default="tools/asset_pipeline/reports/validation_report.jsonl",
        help="Per-file JSONL output path.",
    )
    return parser


def gather_files(input_dir: Path) -> list[Path]:
    return sorted([p for p in input_dir.iterdir() if p.is_file()])


def main() -> int:
    args = build_parser().parse_args()
    input_dir = resolve_cli_path(args.input_dir)

    if not input_dir.exists() or not input_dir.is_dir():
        raise SystemExit(f"Input directory not found: {input_dir}")

    results = [parse_asset_filename(p) for p in gather_files(input_dir)]
    valid_count = sum(1 for r in results if r.valid)
    invalid_count = len(results) - valid_count

    reason_counts: dict[str, int] = {}
    for result in results:
        if result.reason:
            reason_counts[result.reason] = reason_counts.get(result.reason, 0) + 1

    out_json = resolve_cli_path(args.out_json)
    out_json.parent.mkdir(parents=True, exist_ok=True)
    out_jsonl = resolve_cli_path(args.out_jsonl)
    out_jsonl.parent.mkdir(parents=True, exist_ok=True)

    summary = {
        "input_dir": str(input_dir.resolve()),
        "total": len(results),
        "valid": valid_count,
        "invalid": invalid_count,
        "reason_counts": reason_counts,
        "items": [r.to_dict() for r in results],
    }

    out_json.write_text(json.dumps(summary, ensure_ascii=False, indent=2), encoding="utf-8")

    with out_jsonl.open("w", encoding="utf-8") as fp:
        for result in results:
            fp.write(json.dumps(result.to_dict(), ensure_ascii=False) + "\n")

    print(f"[OK] total={len(results)} valid={valid_count} invalid={invalid_count}")
    print(f"[OK] json:  {out_json.resolve()}")
    print(f"[OK] jsonl: {out_jsonl.resolve()}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
