#!/usr/bin/env python3
"""Repack valid spritesheets into canonical frame specs per asset type."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from PIL import Image, UnidentifiedImageError

from common import CANONICAL_FRAME_SPECS, ParseResult, parse_asset_filename, resolve_cli_path


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input-dir", default="tmp_assets")
    parser.add_argument("--output-dir", default="tools/asset_pipeline/repacked")
    parser.add_argument("--report-json", default="tools/asset_pipeline/reports/repack_report.json")
    parser.add_argument(
        "--skip-reasons-jsonl",
        default="tools/asset_pipeline/reports/repack_skipped_reasons.jsonl",
        help="Detailed skipped-reasons log in JSONL format.",
    )
    parser.add_argument("--dry-run", action="store_true")
    return parser


def iter_files(input_dir: Path) -> list[Path]:
    return sorted(p for p in input_dir.iterdir() if p.is_file())


def _parsed_payload(parsed: ParseResult) -> dict:
    return {
        "valid": parsed.valid,
        "reason": parsed.reason,
        "assetType": parsed.assetType,
        "variant": parsed.variant,
        "cols": parsed.cols,
        "rows": parsed.rows,
        "ext": parsed.ext,
    }


def _build_skip_entry(
    src_path: Path,
    parsed: ParseResult,
    reason_code: str,
    *,
    image_size: tuple[int, int] | None = None,
    frame_size: tuple[int, int] | None = None,
) -> dict:
    cols = int(parsed.cols or 0)
    rows = int(parsed.rows or 0)
    payload = {
        "file": src_path.name,
        "reason_code": reason_code,
        "parsed": _parsed_payload(parsed),
        "image_size": list(image_size) if image_size else None,
        "grid": [cols, rows] if cols > 0 and rows > 0 else None,
        "frame_size": list(frame_size) if frame_size else None,
    }
    return payload


def repack_one(src_path: Path, output_dir: Path, dry_run: bool) -> dict:
    parsed = parse_asset_filename(src_path)
    if not parsed.valid:
        return {
            "file": src_path.name,
            "status": "skipped",
            "reason": parsed.reason,
            "skip_reason": _build_skip_entry(src_path, parsed, parsed.reason or "INVALID_PARSE_RESULT"),
        }

    frame_spec = CANONICAL_FRAME_SPECS.get(parsed.assetType or "")
    if frame_spec is None:
        reason = "UNKNOWN_ASSET_TYPE"
        return {
            "file": src_path.name,
            "status": "skipped",
            "reason": reason,
            "skip_reason": _build_skip_entry(src_path, parsed, reason),
        }

    try:
        with Image.open(src_path) as source_image:
            width, height = source_image.size
            cols = int(parsed.cols or 0)
            rows = int(parsed.rows or 0)

            if cols <= 0 or rows <= 0:
                reason = "NON_POSITIVE_GRID"
                return {
                    "file": src_path.name,
                    "status": "skipped",
                    "reason": reason,
                    "skip_reason": _build_skip_entry(src_path, parsed, reason, image_size=(width, height)),
                }

            if width % cols != 0 or height % rows != 0:
                reason = "NON_DIVISIBLE_DIMENSIONS"
                return {
                    "file": src_path.name,
                    "status": "skipped",
                    "reason": reason,
                    "image_size": [width, height],
                    "grid": [cols, rows],
                    "skip_reason": _build_skip_entry(src_path, parsed, reason, image_size=(width, height)),
                }

            src_frame_w = width // cols
            src_frame_h = height // rows
            target_w, target_h = frame_spec
            target_sheet = Image.new("RGBA", (target_w * cols, target_h * rows), (0, 0, 0, 0))

            for row in range(rows):
                for col in range(cols):
                    left = col * src_frame_w
                    top = row * src_frame_h
                    frame = source_image.crop((left, top, left + src_frame_w, top + src_frame_h))
                    resized = frame.resize((target_w, target_h), Image.Resampling.LANCZOS)
                    target_sheet.paste(resized, (col * target_w, row * target_h))
    except UnidentifiedImageError:
        reason = "IMAGE_DECODE_ERROR"
        return {
            "file": src_path.name,
            "status": "skipped",
            "reason": reason,
            "skip_reason": _build_skip_entry(src_path, parsed, reason),
        }
    except OSError:
        reason = "IMAGE_IO_ERROR"
        return {
            "file": src_path.name,
            "status": "skipped",
            "reason": reason,
            "skip_reason": _build_skip_entry(src_path, parsed, reason),
        }
    except Exception:
        reason = "REPACK_UNEXPECTED_ERROR"
        return {
            "file": src_path.name,
            "status": "skipped",
            "reason": reason,
            "skip_reason": _build_skip_entry(src_path, parsed, reason),
        }

    out_name = f"{parsed.assetType}-{parsed.variant}__c{cols}_r{rows}.png"
    out_path = output_dir / out_name
    action = {
        "file": src_path.name,
        "status": "ready" if dry_run else "written",
        "reason": None,
        "output": str(out_path.resolve()),
        "assetType": parsed.assetType,
        "variant": parsed.variant,
        "grid": [cols, rows],
        "src_frame": [src_frame_w, src_frame_h],
        "target_frame": [target_w, target_h],
        "sheet_size": [target_w * cols, target_h * rows],
    }

    if not dry_run:
        output_dir.mkdir(parents=True, exist_ok=True)
        try:
            target_sheet.save(out_path, format="PNG")
        except OSError:
            reason = "OUTPUT_WRITE_ERROR"
            return {
                "file": src_path.name,
                "status": "skipped",
                "reason": reason,
                "output": str(out_path.resolve()),
                "skip_reason": _build_skip_entry(
                    src_path,
                    parsed,
                    reason,
                    frame_size=(src_frame_w, src_frame_h),
                ),
            }

    return action


def main() -> int:
    args = build_parser().parse_args()
    input_dir = resolve_cli_path(args.input_dir)
    output_dir = resolve_cli_path(args.output_dir)
    report_json = resolve_cli_path(args.report_json)
    skip_reasons_jsonl = resolve_cli_path(args.skip_reasons_jsonl)

    if not input_dir.exists() or not input_dir.is_dir():
        raise SystemExit(f"Input directory not found: {input_dir}")

    results = [repack_one(path, output_dir, args.dry_run) for path in iter_files(input_dir)]
    skipped_reasons = [r["skip_reason"] for r in results if r.get("status") == "skipped" and r.get("skip_reason")]

    report = {
        "input_dir": str(input_dir.resolve()),
        "output_dir": str(output_dir.resolve()),
        "dry_run": bool(args.dry_run),
        "summary": {
            "total": len(results),
            "written": sum(1 for r in results if r["status"] == "written"),
            "ready": sum(1 for r in results if r["status"] == "ready"),
            "skipped": sum(1 for r in results if r["status"] == "skipped"),
        },
        "items": results,
    }

    report_json.parent.mkdir(parents=True, exist_ok=True)
    report_json.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")

    skip_reasons_jsonl.parent.mkdir(parents=True, exist_ok=True)
    lines = [json.dumps(item, ensure_ascii=False) for item in skipped_reasons]
    skip_reasons_jsonl.write_text("\n".join(lines) + ("\n" if lines else ""), encoding="utf-8")

    print(json.dumps(report["summary"], ensure_ascii=False))
    print(f"[OK] report: {report_json.resolve()}")
    print(f"[OK] skipped reasons: {skip_reasons_jsonl.resolve()}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
