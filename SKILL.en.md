---
name: star-office-to-claw
description: StarOffice-to-Claw custom integration guide. Use this when users clone this repo and want to connect their OpenClaw bot to Star Office for visual status tracking. Base Star Office installation should follow upstream first; this guide focuses on custom integration steps (join key, push, adapter, security/port).
---

# StarOffice-to-Claw Integration Guide

[KOR ver](./SKILL.md)

This document explains how to connect your OpenClaw bot to Star Office **after cloning this custom repo**.

## 0) First: use upstream guide for base install

For dependency install and first run, follow upstream first.

- Upstream repo: https://github.com/ringhyacinth/Star-Office-UI
- Upstream README: https://github.com/ringhyacinth/Star-Office-UI/blob/master/README.md

This repo focuses on OpenClaw-specific custom integration.

---

## 1) Clone and run server

```bash
git clone https://github.com/HahnGyuTak/StarOffice-to-Claw.git
cd StarOffice-to-Claw
python3 -m pip install -r backend/requirements.txt
cp state.sample.json state.json
python3 backend/app.py
```

Custom backend port: **18793**

- Local URL: `http://127.0.0.1:18793`

---

## 2) Choose integration mode

### A. Simple bridge (recommended first): `office-agent-push.py`
- External/OpenClaw agents periodically push status over HTTP
- Easy setup and debugging

### B. Advanced automation: `openclaw_coding_bot_adapter.py`
- Reads local OpenClaw sessions directly
- Auto-maps `idle / working / waiting / error`
- Can emit lifecycle push events as well

Recommended order: validate quickly with A, then harden with B.

---

## 3) Shared concept: join key + status pipeline

Uses keys from `join-keys.json` (example: `ocj_starteam01`).

Typical flow:
1. `POST /join-agent` → register guest
2. `POST /agent-push` (or adapter push endpoint) → update state
3. optional `POST /leave-agent` → leave

UI pipeline:
`status push -> agents-state.json update -> frontend polling/render update`

---

## 4) Option A guide (`office-agent-push.py`)

Good when:
- You need quick onboarding for multiple bots
- You want explicit/manual status control
- You want request-level debugging

Set these values in script/env:
- `OFFICE_URL` (ex: `http://127.0.0.1:18793`)
- `JOIN_KEY`
- `AGENT_NAME`

Run:
```bash
python3 office-agent-push.py
```

Success checks:
- join/push requests appear in backend logs
- guest appears in UI list
- state/detail updates are reflected in UI

---

## 5) Option B guide (`openclaw_coding_bot_adapter.py`)

Good when:
- You want coding_bot state auto-sync
- You want faster start/end visual reaction
- You want less manual operation

Core flow:
1. `openclaw sessions --agent <target> --json`
2. infer state from recent activity/tokens/abort signals
3. upsert Star Office agent state
4. optionally push lifecycle events to `/openclaw/agent-status`

Run:
```bash
python3 openclaw_coding_bot_adapter.py --interval 15
```

Useful options:
- `--once`
- `--mock-status idle|working|waiting|error`

Customize target/name without code edits:
```bash
python3 openclaw_coding_bot_adapter.py \
  --target-agent pm_bot \
  --display-name "PM Bot" \
  --adapter-id openclaw_pm_bot \
  --interval 15
```

Or environment variables:
```bash
export STAR_OFFICE_TARGET_AGENT=pm_bot
export STAR_OFFICE_DISPLAY_NAME="PM Bot"
export STAR_OFFICE_ADAPTER_ID=openclaw_pm_bot
python3 openclaw_coding_bot_adapter.py --interval 15
```

Endpoint notes:
- Legacy: `/openclaw/coding-bot-status` (kept)
- Preferred: `/openclaw/agent-status`

---

## 6) Security / operations checklist

1. Change drawer password:
```bash
export ASSET_DRAWER_PASS="strong-pass"
```

2. Protect push endpoint (recommended):
```bash
export OPENCLAW_PUSH_TOKEN="strong-token"
```

3. For public exposure:
- Use reverse proxy/tunnel
- Do not expose internal backend port without auth

---

## 7) Quick troubleshooting

- UI not loading → verify `http://127.0.0.1:18793`
- Guest missing → check join key / URL / port
- State stuck → check push interval or adapter process
- Auth errors → verify `OPENCLAW_PUSH_TOKEN`

---

## 8) One-line user summary

Install base Star Office via upstream docs, then connect your OpenClaw bot to port 18793 using A (push bridge) or B (session adapter) for live status visualization.
