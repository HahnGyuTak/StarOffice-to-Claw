# CUSTOM_ASSETS.md

[KOR ver](./CUSTOM_ASSETS.md)

Quick guide for safely applying custom assets to this project.

## 0) 1-minute flow

1. Put assets into `tmp_assets/`
2. Validate filename/grid metadata
3. Repack to canonical format
4. Apply selected variant to frontend

Always test with `--dry-run` first.

---

## 1) Setup

```bash
git clone https://github.com/HahnGyuTak/StarOffice-to-Claw.git
cd StarOffice-to-Claw
```

Python + Pillow environment is required.

---

## 2) Supported state types (canonical)

| state prefix | user meaning | frame size | recommended grid | recommended sheet size | final frontend file |
|---|---|---:|---:|---:|---|
| `idle` | idle state | 256×256 | 8×6 | 2048×1536 | `frontend/idle-asset-grid.png` |
| `working` | working animation | 300×300 | 8×5 (recommended) | 2400×1500 | `frontend/working-asset-grid.webp` |
| `rest` | resting/sync animation | 256×256 | 9×5 (recommended) | 2304×1280 | `frontend/rest-asset-grid.webp` |
| `error` | error animation | 220×220 | 11×4 (recommended) | 2420×880 | `frontend/error-asset-grid.webp` |

Input extensions: `.png`, `.webp`.

---

## 3) Filename rule (important)

### New rule

```text
{state}-asset-grid-{variant}__c<cols>_r<rows>.<ext>
```

Examples:
```text
idle-asset-grid-akaja__c8_r6.png
working-asset-grid-akaja__c8_r5.webp
rest-asset-grid-akaja__c9_r5.png
error-asset-grid-akaja__c11_r4.png
```

### Legacy rule (still accepted)

```text
star-idle-akaja__c8_r6.png
star-working-spritesheet-grid-akaja__c10_r5.png
sync-animation-v3-grid-akaja__c9_r5.png
error-bug-spritesheet-grid-akaja__c11_r4.png
```

Metadata meaning:
- `state`: `idle | working | rest | error`
- `variant`: your theme/version key (ex: `akaja`, `v2`, `mytheme`)
- `c<cols>_r<rows>`: grid columns/rows
- `ext`: `png|webp`

---

## 4) Place assets

Input folder:
- `tmp_assets/`

```bash
cp /path/to/my_assets/* ./tmp_assets/
```

---

## 5) Validate → repack → apply

### 5-1 Validate

```bash
python3 tools/asset_pipeline/parse_and_validate.py
```

Reports:
- `tools/asset_pipeline/reports/validation_report.json`
- `tools/asset_pipeline/reports/validation_report.jsonl`

### 5-2 Repack

Dry run:
```bash
python3 tools/asset_pipeline/repack_to_canonical.py --dry-run
```

Run:
```bash
python3 tools/asset_pipeline/repack_to_canonical.py
```

Output:
- `tools/asset_pipeline/repacked/`

### 5-3 Apply variant to frontend

Dry run:
```bash
python3 tools/asset_pipeline/apply_variant.py --variant <variant> --dry-run
```

Run:
```bash
python3 tools/asset_pipeline/apply_variant.py --variant <variant> --run
```

Backup path:
- `tools/asset_pipeline/backups/<timestamp>/<variant>/`

---

## 6) Auto-fit option

If strict mode fails due to grid mismatch:

```bash
python3 tools/asset_pipeline/apply_variant.py --variant <variant> --auto-fit-grid-resize --dry-run
```

Note: auto-fit may reduce quality slightly due to crop/resize.

---

## 7) Verify in UI

Run backend:
```bash
python3 backend/app.py
```

Open:
- `http://127.0.0.1:18793`

Check:
- idle/working/rest/error render correctly
- no frame break or obvious animation corruption

---

## 8) Recovery

If something breaks, restore from backup in:
- `tools/asset_pipeline/backups/...`

---

## 9) Recommended routine

1. Pick a new variant name (ex: `mytheme`)
2. Put files in `tmp_assets/` with valid names
3. validate → repack → apply(dry-run)
4. apply(run)
5. verify in UI and iterate

---

## References

- Pipeline details: `tools/asset_pipeline/README.md`
- Integration docs: `README.md`, `SKILL.md`
