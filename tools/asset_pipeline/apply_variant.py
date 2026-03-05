#!/usr/bin/env python3
"""Safely apply a chosen variant into canonical frontend filenames with backup."""

from __future__ import annotations

import argparse
import json
import os
import shutil
from dataclasses import asdict, dataclass
from datetime import datetime
from pathlib import Path

from PIL import Image, UnidentifiedImageError

from common import CANONICAL_FRAME_SPECS, parse_asset_filename, resolve_cli_path

CANONICAL_TARGETS = {
    "star-idle": "star-idle-v5.png",
    "star-working-spritesheet-grid": "star-working-spritesheet-grid.webp",
    "sync-animation-v3-grid": "sync-animation-v3-grid.webp",
    "error-bug-spritesheet-grid": "error-bug-spritesheet-grid.webp",
}


@dataclass
class PreflightIssue:
    code: str
    message: str
    assetType: str | None
    source: str | None
    details: dict | None = None


class ApplyPipelineError(Exception):
    def __init__(self, code: str, message: str, *, details: dict | None = None):
        super().__init__(message)
        self.code = code
        self.message = message
        self.details = details or {}


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--variant", required=True, help="Variant name to apply, e.g. akaja")
    parser.add_argument("--source-dir", default="tools/asset_pipeline/repacked")
    parser.add_argument("--target-dir", default="/home/prml-218/Star-Office-UI/frontend")
    parser.add_argument("--backup-root", default="tools/asset_pipeline/backups")
    parser.add_argument("--report-json", default="tools/asset_pipeline/reports/apply_report.json")
    parser.add_argument(
        "--auto-fit-grid-resize",
        action="store_true",
        help="When dimension mismatch exists, auto-crop to grid divisibility and resize per-frame to canonical size.",
    )

    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--dry-run", action="store_true")
    mode.add_argument("--run", action="store_true")
    return parser


def collect_variant_sources(source_dir: Path, variant: str) -> tuple[dict[str, Path], list[dict]]:
    selected: dict[str, Path] = {}
    duplicate_conflicts: list[dict] = []

    for path in sorted(source_dir.iterdir()):
        if not path.is_file():
            continue

        parsed = parse_asset_filename(path)
        if not parsed.valid or parsed.variant != variant:
            continue
        if parsed.assetType not in CANONICAL_TARGETS:
            continue

        asset_type = parsed.assetType
        existing = selected.get(asset_type)
        if existing is not None:
            duplicate_conflicts.append(
                {
                    "assetType": asset_type,
                    "variant": variant,
                    "entries": sorted([str(existing.resolve()), str(path.resolve())]),
                }
            )
            continue

        selected[asset_type] = path

    if duplicate_conflicts:
        by_key: dict[tuple[str, str], set[str]] = {}
        for item in duplicate_conflicts:
            key = (item["assetType"], item["variant"])
            by_key.setdefault(key, set()).update(item["entries"])

        normalized = [
            {
                "assetType": asset_type,
                "variant": item_variant,
                "entries": sorted(entries),
            }
            for (asset_type, item_variant), entries in sorted(by_key.items())
        ]
        raise ApplyPipelineError(
            "DUPLICATE_SOURCE_FOR_ASSET_TYPE",
            "Duplicate source detected for same assetType in apply variant context.",
            details={"conflicts": normalized},
        )

    return selected, []


def convert_and_write(src_path: Path, target_path: Path) -> None:
    target_ext = target_path.suffix.lower()
    with Image.open(src_path) as image:
        if target_ext == ".png":
            image.save(target_path, format="PNG")
            return

        if image.mode not in ("RGB", "RGBA"):
            image = image.convert("RGBA")
        image.save(target_path, format="WEBP", quality=95, method=6)




def convert_and_write_image(image: Image.Image, target_path: Path) -> None:
    target_ext = target_path.suffix.lower()
    if target_ext == ".png":
        image.save(target_path, format="PNG")
        return

    to_save = image
    if to_save.mode not in ("RGB", "RGBA"):
        to_save = to_save.convert("RGBA")
    to_save.save(target_path, format="WEBP", quality=95, method=6)


def _compute_auto_fit_params(width: int, height: int, cols: int, rows: int) -> dict:
    crop_w = width % cols
    crop_h = height % rows
    left = crop_w // 2
    right = crop_w - left
    top = crop_h // 2
    bottom = crop_h - top
    post_w = width - crop_w
    post_h = height - crop_h
    return {
        "crop_pixels": {"left": left, "right": right, "top": top, "bottom": bottom},
        "post_crop_size": [post_w, post_h],
    }

def build_plan(selected: dict[str, Path], target_dir: Path) -> list[dict]:
    plan: list[dict] = []
    for asset_type, target_name in CANONICAL_TARGETS.items():
        src = selected.get(asset_type)
        if src is None:
            plan.append({"assetType": asset_type, "status": "missing_source", "source": None, "target": str((target_dir / target_name).resolve())})
            continue

        frame_w, frame_h = CANONICAL_FRAME_SPECS[asset_type]
        plan.append(
            {
                "assetType": asset_type,
                "status": "planned",
                "source": str(src.resolve()),
                "target": str((target_dir / target_name).resolve()),
                "expected_frame": [frame_w, frame_h],
            }
        )
    return plan


def preflight_validate_apply_sources(plan: list[dict], *, auto_fit_grid_resize: bool) -> list[PreflightIssue]:
    issues: list[PreflightIssue] = []
    for item in plan:
        if item["status"] != "planned":
            continue

        source = Path(item["source"])
        asset_type = item["assetType"]
        expected_frame = CANONICAL_FRAME_SPECS[asset_type]

        parsed = parse_asset_filename(source)
        if not parsed.valid:
            issues.append(
                PreflightIssue(
                    code="PREFLIGHT_INVALID_FILENAME",
                    message=f"Invalid source filename metadata: {parsed.reason}",
                    assetType=asset_type,
                    source=str(source),
                    details={"reason": parsed.reason},
                )
            )
            continue

        if parsed.assetType != asset_type:
            issues.append(
                PreflightIssue(
                    code="PREFLIGHT_ASSET_TYPE_MISMATCH",
                    message="Asset type mismatch between plan and source metadata.",
                    assetType=asset_type,
                    source=str(source),
                    details={"parsed_assetType": parsed.assetType},
                )
            )
            continue

        cols = int(parsed.cols or 0)
        rows = int(parsed.rows or 0)
        if cols <= 0 or rows <= 0:
            issues.append(
                PreflightIssue(
                    code="PREFLIGHT_NON_POSITIVE_GRID",
                    message="Grid metadata must be positive integers.",
                    assetType=asset_type,
                    source=str(source),
                    details={"cols": parsed.cols, "rows": parsed.rows},
                )
            )
            continue

        try:
            with Image.open(source) as image:
                width, height = image.size
        except UnidentifiedImageError:
            issues.append(
                PreflightIssue(
                    code="PREFLIGHT_IMAGE_DECODE_ERROR",
                    message="Image cannot be decoded.",
                    assetType=asset_type,
                    source=str(source),
                )
            )
            continue
        except OSError as exc:
            issues.append(
                PreflightIssue(
                    code="PREFLIGHT_IMAGE_IO_ERROR",
                    message="Image cannot be opened.",
                    assetType=asset_type,
                    source=str(source),
                    details={"error": str(exc)},
                )
            )
            continue

        expected_w = expected_frame[0] * cols
        expected_h = expected_frame[1] * rows

        item["auto_correction"] = {
            "enabled": bool(auto_fit_grid_resize),
            "used": False,
            "original_size": [width, height],
            "crop_pixels": {"left": 0, "right": 0, "top": 0, "bottom": 0},
            "post_crop_size": [width, height],
            "grid": [cols, rows],
            "inferred_frame_before_resize": [width // cols, height // rows],
            "canonical_frame_after_resize": list(expected_frame),
            "warnings": [],
            "status": "strict_match",
        }

        if width != expected_w or height != expected_h:
            if auto_fit_grid_resize:
                auto_fit = _compute_auto_fit_params(width, height, cols, rows)
                post_w, post_h = auto_fit["post_crop_size"]
                if post_w <= 0 or post_h <= 0:
                    issues.append(
                        PreflightIssue(
                            code="AUTO_FIT_INVALID_DIMENSIONS",
                            message="Auto-fit crop would lead to non-positive dimensions.",
                            assetType=asset_type,
                            source=str(source),
                            details={
                                "original_size": [width, height],
                                "crop_pixels": auto_fit["crop_pixels"],
                                "post_crop_size": [post_w, post_h],
                                "grid": [cols, rows],
                            },
                        )
                    )
                    item["auto_correction"].update(
                        {
                            "crop_pixels": auto_fit["crop_pixels"],
                            "post_crop_size": [post_w, post_h],
                            "status": "invalid_dimensions",
                            "warnings": ["auto-fit invalid dimensions"],
                        }
                    )
                    continue

                item["auto_correction"].update(
                    {
                        "used": True,
                        "crop_pixels": auto_fit["crop_pixels"],
                        "post_crop_size": [post_w, post_h],
                        "inferred_frame_before_resize": [post_w // cols, post_h // rows],
                        "status": "auto_corrected",
                        "warnings": ["dimension mismatch corrected by crop+resize"],
                    }
                )
                continue

            issues.append(
                PreflightIssue(
                    code="PREFLIGHT_DIMENSION_MISMATCH",
                    message="Image dimensions do not match canonical frame/grid expectation.",
                    assetType=asset_type,
                    source=str(source),
                    details={
                        "image_size": [width, height],
                        "expected_size": [expected_w, expected_h],
                        "grid": [cols, rows],
                        "expected_frame": list(expected_frame),
                    },
                )
            )
            item["auto_correction"].update(
                {
                    "status": "strict_mismatch_error",
                    "warnings": ["dimension mismatch in strict mode"],
                }
            )

    return issues


def stage_outputs(plan: list[dict], staging_dir: Path, *, auto_fit_grid_resize: bool) -> None:
    staging_dir.mkdir(parents=True, exist_ok=True)
    for item in plan:
        if item["status"] != "planned":
            continue
        source = Path(item["source"])
        target = Path(item["target"])
        staged_path = staging_dir / target.name

        if not auto_fit_grid_resize or not item.get("auto_correction", {}).get("used"):
            convert_and_write(source, staged_path)
            item.setdefault("auto_correction", {})
            item["auto_correction"].setdefault("processing", "passthrough")
            item["staged"] = str(staged_path.resolve())
            continue

        parsed = parse_asset_filename(source)
        cols = int(parsed.cols or 0)
        rows = int(parsed.rows or 0)
        target_frame = CANONICAL_FRAME_SPECS[item["assetType"]]
        crop = item["auto_correction"]["crop_pixels"]

        try:
            with Image.open(source) as source_image:
                left = int(crop["left"])
                right = int(crop["right"])
                top = int(crop["top"])
                bottom = int(crop["bottom"])
                width, height = source_image.size
                cropped = source_image.crop((left, top, width - right, height - bottom))
                post_w, post_h = cropped.size
                if post_w <= 0 or post_h <= 0 or post_w % cols != 0 or post_h % rows != 0:
                    raise ApplyPipelineError(
                        "AUTO_FIT_INVALID_DIMENSIONS",
                        "Auto-fit processing produced invalid post-crop dimensions.",
                        details={
                            "source": str(source),
                            "post_crop_size": [post_w, post_h],
                            "grid": [cols, rows],
                            "crop_pixels": crop,
                        },
                    )

                src_frame_w = post_w // cols
                src_frame_h = post_h // rows
                target_sheet = Image.new("RGBA", (target_frame[0] * cols, target_frame[1] * rows), (0, 0, 0, 0))

                for row in range(rows):
                    for col in range(cols):
                        frame_left = col * src_frame_w
                        frame_top = row * src_frame_h
                        frame = cropped.crop((frame_left, frame_top, frame_left + src_frame_w, frame_top + src_frame_h))
                        resized = frame.resize((target_frame[0], target_frame[1]), Image.Resampling.LANCZOS)
                        target_sheet.paste(resized, (col * target_frame[0], row * target_frame[1]))

                convert_and_write_image(target_sheet, staged_path)
                item["auto_correction"]["processing"] = "auto_fit_grid_resize"
        except ApplyPipelineError:
            raise
        except Exception as exc:
            raise ApplyPipelineError(
                "AUTO_FIT_PROCESSING_FAILED",
                "Unexpected failure while auto-fitting source image.",
                details={
                    "source": str(source),
                    "assetType": item["assetType"],
                    "error": str(exc),
                },
            ) from exc

        item["staged"] = str(staged_path.resolve())


def atomic_apply_with_rollback(plan: list[dict], backup_dir: Path, *, auto_fit_grid_resize: bool) -> dict:
    backups_dir = backup_dir / "original"
    staging_dir = backup_dir / "staging"
    backups_dir.mkdir(parents=True, exist_ok=True)

    stage_outputs(plan, staging_dir, auto_fit_grid_resize=auto_fit_grid_resize)

    swapped: list[dict] = []
    for item in plan:
        if item["status"] != "planned":
            continue
        target = Path(item["target"])
        staged = Path(item["staged"])
        existed = target.exists()

        if existed:
            shutil.copy2(target, backups_dir / target.name)

        try:
            os.replace(staged, target)
        except Exception as exc:
            rollback_results = rollback_targets(swapped, backups_dir)
            raise ApplyPipelineError(
                "APPLY_ATOMIC_SWAP_FAILED",
                "Atomic swap failed during apply, rollback executed.",
                details={
                    "failed_target": str(target),
                    "error": str(exc),
                    "rollback": rollback_results,
                },
            ) from exc

        swapped.append({"target": str(target), "existed": existed})
        item["status"] = "applied"

    return {
        "backup_original_dir": str(backups_dir.resolve()),
        "staging_dir": str(staging_dir.resolve()),
        "swapped_count": len(swapped),
    }


def rollback_targets(swapped: list[dict], backups_dir: Path) -> dict:
    restored = 0
    deleted = 0
    failures: list[dict] = []

    for entry in reversed(swapped):
        target = Path(entry["target"])
        backup_file = backups_dir / target.name
        try:
            if entry["existed"] and backup_file.exists():
                os.replace(backup_file, target)
                restored += 1
            elif not entry["existed"] and target.exists():
                target.unlink()
                deleted += 1
        except Exception as exc:
            failures.append({"target": str(target), "error": str(exc)})

    return {
        "restored": restored,
        "deleted": deleted,
        "failures": failures,
    }


def main() -> int:
    args = build_parser().parse_args()
    source_dir = resolve_cli_path(args.source_dir)
    target_dir = resolve_cli_path(args.target_dir)
    backup_root = resolve_cli_path(args.backup_root)
    report_path = resolve_cli_path(args.report_json)

    if not source_dir.exists() or not source_dir.is_dir():
        raise SystemExit(f"Source directory not found: {source_dir}")
    if not target_dir.exists() or not target_dir.is_dir():
        raise SystemExit(f"Target directory not found: {target_dir}")

    mode = "dry-run" if args.dry_run else "run"
    backup_dir = backup_root / datetime.now().strftime("%Y%m%d-%H%M%S") / args.variant

    report = {
        "mode": mode,
        "variant": args.variant,
        "auto_fit_grid_resize": bool(args.auto_fit_grid_resize),
        "source_dir": str(source_dir.resolve()),
        "target_dir": str(target_dir.resolve()),
        "backup_dir": str(backup_dir.resolve()),
        "items": [],
        "errors": [],
        "preflight": {"ok": False, "issues": []},
    }

    try:
        selected, _ = collect_variant_sources(source_dir, args.variant)
        plan = build_plan(selected, target_dir)
        report["items"] = plan

        preflight_issues = preflight_validate_apply_sources(plan, auto_fit_grid_resize=args.auto_fit_grid_resize)
        report["preflight"] = {
            "ok": len(preflight_issues) == 0,
            "issues": [asdict(issue) for issue in preflight_issues],
        }
        if preflight_issues:
            raise ApplyPipelineError(
                "PREFLIGHT_VALIDATION_FAILED",
                "Preflight validation failed. No target mutation performed.",
                details={"issues": [asdict(issue) for issue in preflight_issues]},
            )

        if args.run:
            apply_result = atomic_apply_with_rollback(plan, backup_dir, auto_fit_grid_resize=args.auto_fit_grid_resize)
            report["apply"] = apply_result

    except ApplyPipelineError as exc:
        report["errors"].append({"code": exc.code, "message": exc.message, "details": exc.details})

    report_path.parent.mkdir(parents=True, exist_ok=True)
    report_path.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")

    counts = {
        "planned": sum(1 for i in report["items"] if i.get("status") in {"planned", "applied"}),
        "applied": sum(1 for i in report["items"] if i.get("status") == "applied"),
        "missing_source": sum(1 for i in report["items"] if i.get("status") == "missing_source"),
        "errors": len(report["errors"]),
    }
    print(json.dumps({"mode": mode, **counts}, ensure_ascii=False))
    if report["errors"]:
        first = report["errors"][0]
        print(f"[ERROR] {first['code']}: {first['message']}")
    print(f"[OK] report: {report_path.resolve()}")
    return 1 if report["errors"] else 0


if __name__ == "__main__":
    raise SystemExit(main())
