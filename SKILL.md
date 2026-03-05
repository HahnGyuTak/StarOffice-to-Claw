---
name: star-office-to-claw
description: StarOffice-to-Claw 커스텀 연동 가이드. 사용자가 이 레포를 클론한 뒤 자신의 OpenClaw 봇과 Star Office를 연결하고 상태를 시각화하려고 할 때 사용합니다. 기본 Star Office UI 설치 자체는 원본 레포 가이드를 우선 따르게 하고, 그 다음 필요한 커스텀 연동 단계(join key, agent push, adapter, 보안/포트 설정)를 안내합니다.
---

# StarOffice-to-Claw 연동 가이드

이 문서는 **이 커스텀 레포를 클론한 뒤**, 사용자의 OpenClaw 봇을 Star Office에 연결하는 방법을 설명합니다.

## 0) 먼저: 기본 Star Office UI 설치는 원본 가이드 사용

기본 설치/실행(의존성 설치, 초기 실행)은 원본 문서를 먼저 따라주세요.

- 원본 레포: https://github.com/ringhyacinth/Star-Office-UI
- 원본 README: https://github.com/ringhyacinth/Star-Office-UI/blob/master/README.md

> 이 레포는 “기본 설치법”보다 “OpenClaw 연동 커스텀”에 초점을 둡니다.

---

## 1) 이 레포 클론 후 서버 실행

```bash
git clone https://github.com/HahnGyuTak/Star-Office-UI-DeltaLab.git
cd Star-Office-UI-DeltaLab
python3 -m pip install -r backend/requirements.txt
cp state.sample.json state.json
python3 backend/app.py
```

현재 커스텀 백엔드 포트는 **18793** 입니다.

- 로컬 접속: `http://127.0.0.1:18793`
- app.py 기준: `app.run(... port=18793 ...)`

---

## 2) OpenClaw 봇 연동 방식 선택

연동은 보통 아래 2가지 중 하나입니다.

### A. 간단 연동(권장 시작): `office-agent-push.py`
- 외부/다른 OpenClaw 봇이 주기적으로 상태를 push
- 빠르게 붙여볼 때 유용

### B. 고급 연동: `openclaw_coding_bot_adapter.py`
- 로컬 OpenClaw 세션을 읽어 상태를 자동 매핑
- `idle / working / waiting / error` 흐름을 더 정교하게 반영

처음에는 A로 붙이고, 안정화 후 B로 넘어가세요.

---

## 3) join key 확인

`join-keys.json`의 키를 사용합니다(예: `ocj_starteam01`).

연동 봇은 아래 순서로 동작합니다.
1. `POST /join-agent` (참여)
2. `POST /agent-push` (상태 푸시)
3. 필요 시 `POST /leave-agent` (이탈)

---

## 4) A안: office-agent-push.py로 연결

`office-agent-push.py`에서 아래 값 설정:
- `OFFICE_URL` → `http://127.0.0.1:18793` (또는 실제 배포 URL)
- `JOIN_KEY` → join key
- `AGENT_NAME` → 표시 이름

실행:
```bash
python3 office-agent-push.py
```

정상 연결되면 오피스 화면 Guest 리스트에 봇이 보입니다.

---

## 5) B안: OpenClaw coding_bot adapter 연결

```bash
python3 openclaw_coding_bot_adapter.py --interval 15
```

옵션:
- `--once` : 1회 실행 테스트
- `--mock-status idle|working|waiting|error` : 상태 표시 검증

이 어댑터는 OpenClaw 세션을 읽고 Star Office의 게스트 상태로 반영합니다.

---

## 6) 보안/운영 필수 체크

1. 드로어 비밀번호 변경
```bash
export ASSET_DRAWER_PASS="strong-pass"
```

2. push endpoint 보호(선택 권장)
```bash
export OPENCLAW_PUSH_TOKEN="strong-token"
```
- 설정 시 `/openclaw/coding-bot-status`에 토큰 헤더 필요

3. 공용망 노출 시
- reverse proxy/tunnel 사용
- 인증 없이 내부 포트를 직접 공개하지 않기

---

## 7) 문제 해결 빠른 체크리스트

- 화면이 안 뜸 → `http://127.0.0.1:18793` 접속 확인
- 게스트가 안 보임 → join key/URL/포트 확인
- 상태가 고정됨 → push 주기 또는 adapter 실행 여부 확인
- 권한 오류 → 토큰 설정값(`OPENCLAW_PUSH_TOKEN`) 일치 확인

---

## 8) 사용자 안내용 한 줄 요약

> 기본 Star Office는 원본 README대로 설치하고, 이 레포에서는 OpenClaw 봇을 18793 포트의 Star Office에 join/push(adapter) 방식으로 연결해 실시간 상태 시각화를 완성합니다.
