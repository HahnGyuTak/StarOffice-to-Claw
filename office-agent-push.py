#!/usr/bin/env python3
"""
EN - Agent EN

EN：
1. EN JOIN_KEY（EN join key）
2. EN AGENT_NAME（EN）
3. EN：python office-agent-push.py
4. EN join（EN），EN 30s EN
"""

import json
import os
import time
import sys
from datetime import datetime

# === EN ===
JOIN_KEY = ""   # EN：EN join key
AGENT_NAME = "" # EN：EN
OFFICE_URL = "https://office.example.com"  # EN（EN）

# === EN ===
PUSH_INTERVAL_SECONDS = 15  # EN（EN）
STATUS_ENDPOINT = "/status"
JOIN_ENDPOINT = "/join-agent"
PUSH_ENDPOINT = "/agent-push"

# EN（EN join EN agentId）
STATE_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "office-agent-state.json")

# EN OpenClaw WorkEN（EN AGENTS.md ENWorkEN）
# EN，EN。
DEFAULT_STATE_CANDIDATES = [
    "/root/.openclaw/workspace/star-office-ui/state.json",
    "/root/.openclaw/workspace/state.json",
    os.path.join(os.getcwd(), "state.json"),
    os.path.join(os.path.dirname(os.path.abspath(__file__)), "state.json"),
]

# EN /status EN，EN token（EN OFFICE_LOCAL_STATUS_TOKEN）
LOCAL_STATUS_TOKEN = os.environ.get("OFFICE_LOCAL_STATUS_TOKEN", "")
LOCAL_STATUS_URL = os.environ.get("OFFICE_LOCAL_STATUS_URL", "http://127.0.0.1:18791/status")
# EN：EN（EN：EN /status EN）
LOCAL_STATE_FILE = os.environ.get("OFFICE_LOCAL_STATE_FILE", "")
VERBOSE = os.environ.get("OFFICE_VERBOSE", "0") in {"1", "true", "TRUE", "yes", "YES"}


def load_local_state():
    if os.path.exists(STATE_FILE):
        try:
            with open(STATE_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            pass
    return {
        "agentId": None,
        "joined": False,
        "joinKey": JOIN_KEY,
        "agentName": AGENT_NAME
    }


def save_local_state(data):
    with open(STATE_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


def normalize_state(s):
    """EN，EN。"""
    s = (s or "").strip().lower()
    if s in {"writing", "researching", "executing", "syncing", "error", "idle"}:
        return s
    if s in {"working", "busy", "write"}:
        return "writing"
    if s in {"run", "running", "execute", "exec"}:
        return "executing"
    if s in {"research", "search"}:
        return "researching"
    if s in {"sync"}:
        return "syncing"
    return "idle"


def map_detail_to_state(detail, fallback_state="idle"):
    """EN detail EN，EN（EN AGENTS.md EN）。"""
    d = (detail or "").lower()
    if any(k in d for k in ["EN", "error", "bug", "EN", "Alert"]):
        return "error"
    if any(k in d for k in ["Sync", "sync", "EN"]):
        return "syncing"
    if any(k in d for k in ["Research", "research", "EN", "EN"]):
        return "researching"
    if any(k in d for k in ["Execute", "run", "EN", "EN", "Working", "writing"]):
        return "writing"
    if any(k in d for k in ["Idle", "EN", "idle", "EN", "done"]):
        return "idle"
    return fallback_state


def fetch_local_status():
    """EN：
    1) EN state.json（EN AGENTS.md：EN writing，EN idle）
    2) EN HTTP /status
    3) EN fallback idle
    """
    # 1) EN state.json（EN，EN）
    candidate_files = []
    if LOCAL_STATE_FILE:
        candidate_files.append(LOCAL_STATE_FILE)
    for fp in DEFAULT_STATE_CANDIDATES:
        if fp not in candidate_files:
            candidate_files.append(fp)

    for fp in candidate_files:
        try:
            if fp and os.path.exists(fp):
                with open(fp, "r", encoding="utf-8") as f:
                    data = json.load(f)

                    # EN“EN”EN；EN office-agent-state.json（EN agentId）EN
                    if not isinstance(data, dict):
                        continue
                    has_state = "state" in data
                    has_detail = "detail" in data
                    if (not has_state) and (not has_detail):
                        continue

                    state = normalize_state(data.get("state", "idle"))
                    detail = data.get("detail", "") or ""
                    # detail EN，EN“Work/EN/Alert”EN
                    state = map_detail_to_state(detail, fallback_state=state)
                    if VERBOSE:
                        print(f"[status-source:file] path={fp} state={state} detail={detail[:60]}")
                    return {"state": state, "detail": detail}
        except Exception:
            pass

    # 2) EN /status（EN）
    try:
        import requests
        headers = {}
        if LOCAL_STATUS_TOKEN:
            headers["Authorization"] = f"Bearer {LOCAL_STATUS_TOKEN}"
        r = requests.get(LOCAL_STATUS_URL, headers=headers, timeout=5)
        if r.status_code == 200:
            data = r.json()
            state = normalize_state(data.get("state", "idle"))
            detail = data.get("detail", "") or ""
            state = map_detail_to_state(detail, fallback_state=state)
            if VERBOSE:
                print(f"[status-source:http] url={LOCAL_STATUS_URL} state={state} detail={detail[:60]}")
            return {"state": state, "detail": detail}
        # EN 401，EN token
        if r.status_code == 401:
            return {"state": "idle", "detail": "EN/statusEN（401），EN OFFICE_LOCAL_STATUS_TOKEN"}
    except Exception:
        pass

    # 3) EN fallback
    if VERBOSE:
        print("[status-source:fallback] state=idle detail=IdleEN")
    return {"state": "idle", "detail": "IdleEN"}


def do_join(local):
    import requests
    payload = {
        "name": local.get("agentName", AGENT_NAME),
        "joinKey": local.get("joinKey", JOIN_KEY),
        "state": "idle",
        "detail": "EN"
    }
    r = requests.post(f"{OFFICE_URL}{JOIN_ENDPOINT}", json=payload, timeout=10)
    if r.status_code in (200, 201):
        data = r.json()
        if data.get("ok"):
            local["joined"] = True
            local["agentId"] = data.get("agentId")
            save_local_state(local)
            print(f"✅ EN，agentId={local['agentId']}")
            return True
    print(f"❌ EN：{r.text}")
    return False


def do_push(local, status_data):
    import requests
    payload = {
        "agentId": local.get("agentId"),
        "joinKey": local.get("joinKey", JOIN_KEY),
        "state": status_data.get("state", "idle"),
        "detail": status_data.get("detail", ""),
        "name": local.get("agentName", AGENT_NAME)
    }
    r = requests.post(f"{OFFICE_URL}{PUSH_ENDPOINT}", json=payload, timeout=10)
    if r.status_code in (200, 201):
        data = r.json()
        if data.get("ok"):
            area = data.get("area", "breakroom")
            print(f"✅ ENSync，EN={area}")
            return True

    # 403/404：EN/EN → EN
    if r.status_code in (403, 404):
        msg = ""
        try:
            msg = (r.json() or {}).get("msg", "")
        except Exception:
            msg = r.text
        print(f"⚠️  EN（{r.status_code}），EN：{msg}")
        local["joined"] = False
        local["agentId"] = None
        save_local_state(local)
        sys.exit(1)

    print(f"⚠️  EN：{r.text}")
    return False


def main():
    local = load_local_state()

    # EN
    if not JOIN_KEY or not AGENT_NAME:
        print("❌ EN JOIN_KEY EN AGENT_NAME")
        sys.exit(1)

    # EN join，EN join
    if not local.get("joined") or not local.get("agentId"):
        ok = do_join(local)
        if not ok:
            sys.exit(1)

    # EN
    print(f"🚀 EN，EN={PUSH_INTERVAL_SECONDS}EN")
    print("🧭 EN：EN→WorkEN；Idle/EN→EN；EN→bugEN")
    print("🔐 EN /status EN Unauthorized(401)，EN：OFFICE_LOCAL_STATUS_TOKEN EN OFFICE_LOCAL_STATUS_URL")
    try:
        while True:
            try:
                status_data = fetch_local_status()
                do_push(local, status_data)
            except Exception as e:
                print(f"⚠️  EN：{e}")
            time.sleep(PUSH_INTERVAL_SECONDS)
    except KeyboardInterrupt:
        print("\n👋 EN")
        sys.exit(0)


if __name__ == "__main__":
    main()
