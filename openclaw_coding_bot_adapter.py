#!/usr/bin/env python3
"""
Spike adapter: expose one OpenClaw target agent as a Star-Office guest agent.

Goal: minimal, low-risk integration without touching target agent workflow.
- Reads OpenClaw session metadata via `openclaw sessions --all-agents --json`.
- Maps a minimal schema to Star-Office `agents-state.json`.
- Supports mock mode for deterministic status transition checks.
"""

from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
import time
import urllib.error
import urllib.request
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

ROOT = Path(__file__).resolve().parent
AGENTS_STATE_FILE = ROOT / "agents-state.json"

TARGET_AGENT_ID = (os.getenv("STAR_OFFICE_TARGET_AGENT") or "coding_bot").strip() or "coding_bot"
DISPLAY_NAME = (os.getenv("STAR_OFFICE_DISPLAY_NAME") or TARGET_AGENT_ID).strip() or TARGET_AGENT_ID
ADAPTER_ID = (os.getenv("STAR_OFFICE_ADAPTER_ID") or f"openclaw_{TARGET_AGENT_ID}").strip() or f"openclaw_{TARGET_AGENT_ID}"
ADAPTER_CACHE_FILE = ROOT / "memory" / f"openclaw-{TARGET_AGENT_ID}-adapter-cache.json"

# Heuristic thresholds (observation-mode tuning points)
ERROR_ABORT_WINDOW_SEC = 30 * 60
WORKING_RECENT_WINDOW_SEC = 180
VERY_RECENT_WORKING_SEC = 20
WAITING_RECENT_WINDOW_SEC = 90

PUSH_ENABLED = os.getenv("STAR_OFFICE_PUSH_ENABLED", "1") != "0"
PUSH_URL = os.getenv("STAR_OFFICE_PUSH_URL", "http://127.0.0.1:18793/openclaw/agent-status")
PUSH_TIMEOUT_SEC = float(os.getenv("STAR_OFFICE_PUSH_TIMEOUT_SEC", "1.5"))
PUSH_TOKEN = os.getenv("STAR_OFFICE_PUSH_TOKEN", "").strip()
PUSH_MERGE_TTL_SEC = int(os.getenv("STAR_OFFICE_PUSH_TTL_SEC", "45"))

# Requested minimal schema (adapter-level canonical shape)
# name, role, status, task, updated_at


def now_iso() -> str:
    return datetime.now().isoformat(timespec="seconds")


def now_ts() -> int:
    return int(time.time())


def push_status_event(event: str, status: str, minimal: Dict[str, Any], key: str) -> None:
    if not PUSH_ENABLED:
        return

    payload = {
        "source": "openclaw_coding_bot_adapter",
        "agent_id": TARGET_AGENT_ID,
        "event": event,
        "status": status,
        "observed_status": minimal.get("status"),
        "task": minimal.get("task", ""),
        "session_key": key,
        "updated_at": minimal.get("updated_at") or now_iso(),
        "ttl_seconds": PUSH_MERGE_TTL_SEC,
    }

    data = json.dumps(payload, ensure_ascii=False).encode("utf-8")
    headers = {"Content-Type": "application/json"}
    if PUSH_TOKEN:
        headers["X-OpenClaw-Token"] = PUSH_TOKEN

    req = urllib.request.Request(PUSH_URL, data=data, headers=headers, method="POST")
    try:
        with urllib.request.urlopen(req, timeout=PUSH_TIMEOUT_SEC) as resp:
            _ = resp.read()
        print(f"[push] ok event={event} status={status}")
    except (urllib.error.URLError, urllib.error.HTTPError, TimeoutError) as e:
        # best-effort: only log, never interrupt adapter flow
        print(f"[push] failed event={event} status={status} err={e}")


def apply_push_overlay(minimal: Dict[str, Any], cache: Dict[str, Any]) -> Dict[str, Any]:
    overlay = (cache.get("pushOverlay") or {}) if isinstance(cache, dict) else {}
    if not overlay:
        return minimal

    expires_at = int(overlay.get("expiresAt") or 0)
    if now_ts() > expires_at:
        cache["pushOverlay"] = {}
        return minimal

    status = overlay.get("status")
    if not status:
        return minimal

    merged = dict(minimal)
    merged["status"] = status
    merged["task"] = f"[push-ttl] {minimal.get('task', '')}"
    return merged


def run_openclaw_sessions() -> Dict[str, Any]:
    # NOTE: --all-agents can omit some subagent keys in practice.
    # For this adapter we query the selected agent store directly.
    cmd = ["openclaw", "sessions", "--agent", TARGET_AGENT_ID, "--json"]
    proc = subprocess.run(cmd, capture_output=True, text=True)
    if proc.returncode != 0:
        raise RuntimeError((proc.stderr or proc.stdout or "openclaw sessions failed").strip())
    return json.loads(proc.stdout)


def load_cache() -> Dict[str, Any]:
    try:
        if ADAPTER_CACHE_FILE.exists():
            return json.loads(ADAPTER_CACHE_FILE.read_text(encoding="utf-8"))
    except Exception:
        pass
    return {"last": {}}


def save_cache(cache: Dict[str, Any]) -> None:
    ADAPTER_CACHE_FILE.parent.mkdir(parents=True, exist_ok=True)
    ADAPTER_CACHE_FILE.write_text(json.dumps(cache, ensure_ascii=False, indent=2), encoding="utf-8")


def pick_latest_target_session(payload: Dict[str, Any]) -> Tuple[Optional[Dict[str, Any]], List[Dict[str, Any]]]:
    sessions = payload.get("sessions") or []
    cands = [s for s in sessions if s.get("agentId") == TARGET_AGENT_ID]
    # noise reduction: drop lightweight coordination key agent:<id>:main when possible
    filtered = [s for s in cands if not str(s.get("key", "")).endswith(":main")]
    pool = filtered if filtered else cands
    if not pool:
        return None, []
    pool.sort(key=lambda x: x.get("updatedAt", 0), reverse=True)
    return pool[0], pool


def map_to_minimal_schema(latest: Optional[Dict[str, Any]], all_cands: List[Dict[str, Any]], poll_error: Optional[str], cache: Dict[str, Any]) -> Dict[str, Any]:
    # status set requested by user: idle | working | waiting | error
    if poll_error:
        return {
            "name": DISPLAY_NAME,
            "role": "dev",
            "status": "error",
            "task": f"OpenClaw 세션 조회 실패: {poll_error[:80]}",
            "updated_at": now_iso(),
        }

    if not latest:
        return {
            "name": DISPLAY_NAME,
            "role": "dev",
            "status": "idle",
            "task": "활성 작업 세션 없음",
            "updated_at": now_iso(),
        }

    # stronger error signal: any very-recent aborted session => error
    for s in all_cands:
        if bool(s.get("abortedLastRun", False)) and int(s.get("ageMs") or 10**12) <= ERROR_ABORT_WINDOW_SEC * 1000:
            return {
                "name": DISPLAY_NAME,
                "role": "dev",
                "status": "error",
                "task": f"최근 실행 중단 감지 · {s.get('key', 'unknown')}",
                "updated_at": now_iso(),
            }

    key = latest.get("key", "unknown")
    kind = latest.get("kind", "direct")
    age_ms = int(latest.get("ageMs") or 10**12)
    age_sec = max(0, age_ms // 1000)
    updated_at_ms = int(latest.get("updatedAt") or 0)
    total_tokens = latest.get("totalTokens")
    input_tokens = latest.get("inputTokens")
    output_tokens = latest.get("outputTokens")

    cache_last = (cache.get("last") or {}) if isinstance(cache, dict) else {}
    prev = cache_last.get(key, {})
    prev_updated = int(prev.get("updatedAt") or 0)
    prev_total = prev.get("totalTokens")
    prev_in = prev.get("inputTokens")
    prev_out = prev.get("outputTokens")

    progressed = False
    if updated_at_ms and prev_updated and updated_at_ms > prev_updated:
        progressed = True
    for cur, old in [(total_tokens, prev_total), (input_tokens, prev_in), (output_tokens, prev_out)]:
        if isinstance(cur, int) and isinstance(old, int) and cur > old:
            progressed = True

    is_new_session_key = key not in cache_last
    is_very_recent = age_sec <= VERY_RECENT_WORKING_SEC

    # fast-reflect heuristic (no hold):
    # - enter working quickly on fresh update/new session/progress
    # - drop quickly to waiting/idle when activity disappears
    if age_sec <= WORKING_RECENT_WINDOW_SEC and (progressed or is_new_session_key or is_very_recent):
        status = "working"
    elif age_sec <= WAITING_RECENT_WINDOW_SEC:
        status = "waiting"
    else:
        status = "idle"

    task = (
        f"{kind} 세션 관찰 ({age_sec}s 전, progressed={str(progressed).lower()}, "
        f"new={str(is_new_session_key).lower()}, recent={str(is_very_recent).lower()}) · {key}"
    )

    # persist latest snapshot for next-delta inference
    cache.setdefault("last", {})
    cache["last"][key] = {
        "updatedAt": updated_at_ms,
        "totalTokens": total_tokens,
        "inputTokens": input_tokens,
        "outputTokens": output_tokens,
    }

    return {
        "name": DISPLAY_NAME,
        "role": "dev",
        "status": status,
        "task": task,
        "updated_at": now_iso(),
    }


def minimal_status_to_ui_state(status: str) -> str:
    # Observation-mode consistency mapping
    # idle -> idle, working -> writing, waiting -> waiting, error -> error
    return {
        "idle": "idle",
        "working": "writing",
        "waiting": "waiting",
        "error": "error",
    }.get(status, "idle")


def load_agents_state() -> List[Dict[str, Any]]:
    if not AGENTS_STATE_FILE.exists():
        return []
    try:
        return json.loads(AGENTS_STATE_FILE.read_text(encoding="utf-8"))
    except Exception:
        return []


def save_agents_state(items: List[Dict[str, Any]]) -> None:
    AGENTS_STATE_FILE.write_text(json.dumps(items, ensure_ascii=False, indent=2), encoding="utf-8")


def upsert_adapter_agent(minimal: Dict[str, Any]) -> None:
    agents = load_agents_state()

    # Merge rule with push endpoint: if push priority window is active, do not override.
    existing = next((a for a in agents if a.get("agentId") == ADAPTER_ID), None)
    if existing:
        until = existing.get("pushPriorityUntil")
        if isinstance(until, str):
            try:
                if datetime.now() < datetime.fromisoformat(until):
                    return
            except Exception:
                pass

    ui_state = minimal_status_to_ui_state(minimal["status"])
    status = minimal["status"]
    detail_line = f"[{status}] {minimal['task']}"
    area_by_status = {
        "error": "error",
        "working": "writing",
        "waiting": "breakroom",
        "idle": "syncing",
    }

    entry = {
        "agentId": ADAPTER_ID,
        "name": minimal["name"],
        "role": minimal["role"],
        "status": status,
        "task": minimal["task"],
        "updated_at": minimal["updated_at"],
        # Fields consumed by Star-Office UI renderer
        "isMain": False,
        "state": ui_state,
        "detail": detail_line,
        "area": area_by_status.get(status, "syncing"),
        "source": "openclaw-adapter",
        "authStatus": "approved",
        "lastPushAt": minimal["updated_at"],
        "avatar": "guest_role_2",
    }

    replaced = False
    out: List[Dict[str, Any]] = []
    for a in agents:
        if a.get("agentId") == ADAPTER_ID:
            out.append(entry)
            replaced = True
        else:
            out.append(a)
    if not replaced:
        out.append(entry)

    save_agents_state(out)


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description="OpenClaw target-agent -> Star-Office adapter")
    p.add_argument("--interval", type=int, default=15, help="poll interval seconds")
    p.add_argument("--once", action="store_true", help="run once and exit")
    p.add_argument("--mock-status", choices=["idle", "working", "waiting", "error"], help="force fixed mock status")
    p.add_argument("--target-agent", default=TARGET_AGENT_ID, help="OpenClaw agent id to observe (default: env STAR_OFFICE_TARGET_AGENT or coding_bot)")
    p.add_argument("--display-name", default=DISPLAY_NAME, help="Name shown in Star Office guest list")
    p.add_argument("--adapter-id", default=ADAPTER_ID, help="Internal guest agentId used in Star Office")
    return p.parse_args()


def main() -> int:
    global TARGET_AGENT_ID, DISPLAY_NAME, ADAPTER_ID, ADAPTER_CACHE_FILE
    args = parse_args()
    TARGET_AGENT_ID = (args.target_agent or TARGET_AGENT_ID).strip() or TARGET_AGENT_ID
    DISPLAY_NAME = (args.display_name or DISPLAY_NAME).strip() or TARGET_AGENT_ID
    ADAPTER_ID = (args.adapter_id or ADAPTER_ID).strip() or f"openclaw_{TARGET_AGENT_ID}"
    ADAPTER_CACHE_FILE = ROOT / "memory" / f"openclaw-{TARGET_AGENT_ID}-adapter-cache.json"

    while True:
        poll_error = None
        latest = None
        all_cands: List[Dict[str, Any]] = []
        cache = load_cache()
        try:
            payload = run_openclaw_sessions()
            latest, all_cands = pick_latest_target_session(payload)
        except Exception as e:
            poll_error = str(e)

        minimal = map_to_minimal_schema(latest, all_cands, poll_error, cache)
        if args.mock_status:
            minimal["status"] = args.mock_status
            minimal["task"] = f"[mock] {args.mock_status} 상태 검증"
            minimal["updated_at"] = now_iso()

        prev_effective = str(cache.get("last_effective_status") or "idle")
        cur_observed = str(minimal.get("status") or "idle")
        session_key = (latest or {}).get("key", "unknown") if isinstance(latest, dict) else "unknown"

        if prev_effective != "working" and cur_observed == "working":
            cache["pushOverlay"] = {
                "status": "working",
                "expiresAt": now_ts() + max(5, PUSH_MERGE_TTL_SEC),
            }
            push_status_event("task_started", "working", minimal, session_key)
        elif prev_effective == "working" and cur_observed != "working":
            end_status = "idle" if cur_observed in {"idle", "waiting", "error"} else cur_observed
            cache["pushOverlay"] = {
                "status": end_status,
                "expiresAt": now_ts() + max(5, PUSH_MERGE_TTL_SEC),
            }
            push_status_event("task_finished", end_status, minimal, session_key)

        effective = apply_push_overlay(minimal, cache)
        cache["last_effective_status"] = effective.get("status", "idle")

        upsert_adapter_agent(effective)
        save_cache(cache)
        print(f"[{effective['updated_at']}] {effective['status']} | {effective['task']}")

        if args.once:
            return 0
        time.sleep(max(3, args.interval))


if __name__ == "__main__":
    sys.exit(main())
