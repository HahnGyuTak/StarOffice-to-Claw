# Star Office UI — Custom Change Report

[KOR ver](./README.md)

> **Based on** the original project: https://github.com/ringhyacinth/Star-Office-UI

This repository is a customized derivative of Star-Office-UI.  
Its purpose is to document what was changed and added compared to upstream.

---

## 1) Upstream / Credits

- Original repository: https://github.com/ringhyacinth/Star-Office-UI
- Original README: https://github.com/ringhyacinth/Star-Office-UI/blob/master/README.md
- Upstream credit: Ring Hyacinth, Simon Lee

---

## 2) License / Notice

- Code license follows upstream policy. See [`LICENSE`](./LICENSE).
- This repo keeps original license/credits and documents only derivative changes.
- For art asset usage/commercial restrictions, follow upstream/project guidance.
- See [`NOTICE`](./NOTICE) for upstream + derivative notices.

---

## 3) What changed vs upstream

### A. OpenClaw integration
- Added [`openclaw_coding_bot_adapter.py`](./openclaw_coding_bot_adapter.py)
- Reads OpenClaw sessions and maps to `idle/working/waiting/error`
- Added task start/end push + TTL merge behavior
- User-facing integration guide in [`SKILL.md`](./SKILL.md)

### B. Backend endpoints/state
- Extended [`backend/app.py`](./backend/app.py)
- Added `waiting` state and stronger state normalization
- Added `/openclaw/agent-status` (legacy `/openclaw/coding-bot-status` compatible)
- Improved guest join/push/offline flow

### C. Asset pipeline and decoration flow
- Added [`tools/asset_pipeline/`](./tools/asset_pipeline/)
- Added validation/repack/apply scripts:
  - [`apply_variant.py`](./tools/asset_pipeline/apply_variant.py)
  - [`parse_and_validate.py`](./tools/asset_pipeline/parse_and_validate.py)
  - [`repack_to_canonical.py`](./tools/asset_pipeline/repack_to_canonical.py)
- Uses [`tmp_assets/`](./tmp_assets/) for custom asset intake
- Improved background generation/restore/history/favorites flow
- End-user asset guide: [`CUSTOM_ASSETS.md`](./CUSTOM_ASSETS.md)

### D. UI/UX refresh
- Major updates in:
  - [`frontend/index.html`](./frontend/index.html)
  - [`frontend/game.js`](./frontend/game.js)
  - [`frontend/layout.js`](./frontend/layout.js)
- Better language/mobile support and drawer UX
- Replaced state sprite/animation assets
- Office name unified to English-only with clear override method

### E. Operational docs
- Added operation/observation notes for reproducibility

### F. Final state-area-asset mapping (Round2)

| Standard state | Legacy-compatible internal keys | area | Main asset |
|---|---|---|---|
| idle | idle, waiting | breakroom | `idle-asset-grid` |
| working | writing, researching, executing | writing | `working-asset-grid` |
| rest | syncing | writing (rendering fixed at bottom-right) | `rest-asset-grid` |
| error | error | error | `error-asset-grid` |

> Internal legacy keys are still kept for compatibility. User-facing docs/UI should use `idle / working / rest / error`.

---

## 4) Office name policy (English-only)

Office name is unified to a single English value regardless of language mode.

- Default: `Star Office`
- Current custom: `Hahn Office`

Resolution order in frontend:
1. `window.STAR_OFFICE_NAME` (runtime override)
2. `CUSTOM_OFFICE_NAME` (code-level custom default)
3. `DEFAULT_OFFICE_NAME` (`Star Office`)

Where to change:
- Code default:
  - `frontend/index.html` (`CUSTOM_OFFICE_NAME`, `DEFAULT_OFFICE_NAME`)
  - `frontend/game.js` (`CUSTOM_OFFICE_NAME`, `DEFAULT_OFFICE_NAME`)
- Runtime override:
  - Browser console: `window.STAR_OFFICE_NAME = 'Your Name'` then refresh
  - Or inject in `index.html`: `<script>window.STAR_OFFICE_NAME='Your Name'</script>`

Applied to:
- Loading text
- In-game plaque text
- `officeTitle` display output

---

## 5) Repository intent

1. Transparently track differences from upstream
2. Keep custom features reproducible and extensible

For vanilla/original usage, refer to upstream first.

---

## 6) Documentation Map

Start with these 3 files:

- [`README.md`](./README.md)
- [`SKILL.md`](./SKILL.md)
- [`CUSTOM_ASSETS.md`](./CUSTOM_ASSETS.md)

Historical drafts/records are archived in `docs/archive/`.
