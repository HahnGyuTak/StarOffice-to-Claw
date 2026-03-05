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
git clone https://github.com/HahnGyuTak/StarOffice-to-Claw.git
cd StarOffice-to-Claw
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
- 다른 OpenClaw(또는 외부 에이전트)가 HTTP API로 상태를 주기적으로 push
- 설정이 단순하고, 디버깅이 쉬워서 **처음 붙일 때 가장 적합**

### B. 고급 연동: `openclaw_coding_bot_adapter.py`
- 로컬 OpenClaw 세션을 직접 읽어 상태를 자동 판단
- `idle / working / waiting / error`를 자동 반영하고 이벤트 기반 push까지 수행

처음에는 **A안으로 빠르게 동작 확인**하고, 이후 **B안으로 자동화 고도화**를 권장합니다.

---

## 3) 공통 개념: join key와 상태 반영 구조

`join-keys.json`의 키를 사용합니다(예: `ocj_starteam01`).

연동 봇의 공통 동작 순서:
1. `POST /join-agent` → 오피스에 “게스트 등록”
2. `POST /agent-push` (또는 adapter push 엔드포인트) → 상태 업데이트
3. 필요 시 `POST /leave-agent` → 게스트 이탈

UI 반영 방식(핵심):
- 상태 값이 바뀌면 서버의 `agents-state.json`이 갱신됨
- 프론트엔드는 주기적으로 게스트 상태를 읽어 캐릭터 위치/말풍선/목록을 업데이트
- 즉, “상태 push → 서버 상태 갱신 → UI 반영”의 파이프라인으로 동작

---

## 4) A안: `office-agent-push.py`로 연결 (친절 가이드)

### 4-1. 언제 쓰면 좋은가?
- 여러 봇을 빠르게 붙여야 할 때
- 특정 상태를 명시적으로 보내고 싶을 때
- 문제 발생 시 요청/응답을 직접 확인하며 디버깅하고 싶을 때

### 4-2. 어떻게 연결되는가?
`office-agent-push.py`는 아래를 반복합니다.
- 최초 1회 `join-agent` 호출로 게스트 등록
- 이후 주기적으로 `agent-push` 호출하여 상태 전송

즉, **봇이 스스로 상태를 “밀어넣는(push)” 방식**입니다.

### 4-3. UI에는 어떻게 보이나?
- Guest 리스트에 `AGENT_NAME`으로 새로운 게스트가 나타남
- push한 상태(`idle/writing/researching/executing/syncing/error`)에 따라
  - 캐릭터 위치(휴식/작업/에러 구역)
  - 말풍선(detail)
  - 상태 텍스트
  가 바뀝니다.

### 4-4. 설정/실행
`office-agent-push.py`에서 아래 값 설정:
- `OFFICE_URL` → `http://127.0.0.1:18793` (또는 실제 배포 URL)
- `JOIN_KEY` → join key
- `AGENT_NAME` → 표시 이름

실행:
```bash
python3 office-agent-push.py
```

### 4-5. 성공 확인 체크
- 서버 로그에 join/push 요청이 찍힘
- UI Guest 리스트에 새 에이전트 등장
- 상태 변경 시 위치/말풍선이 따라 바뀜

---

## 5) B안: `openclaw_coding_bot_adapter.py`로 연결 (친절 가이드)

### 5-1. 언제 쓰면 좋은가?
- coding_bot 상태를 수동 입력 없이 자동으로 반영하고 싶을 때
- 작업 시작/종료를 이벤트로 잡아 UI 반응성을 높이고 싶을 때
- 관찰/운영 자동화를 하고 싶을 때

### 5-2. 어떻게 연결되는가?
어댑터는 다음 흐름으로 동작합니다.
1. `openclaw sessions --agent coding_bot --json`로 세션 상태 조회
2. 최근 활동/토큰 변화/중단 여부를 바탕으로 상태 추론
3. 추론 결과를 Star Office 게스트 상태로 업데이트
4. 필요 시 `/openclaw/coding-bot-status`로 이벤트 push

즉, **OpenClaw 내부 상태를 읽어서 자동으로 UI 상태를 동기화**합니다.

### 5-3. UI에는 어떻게 보이나?
- 게스트 이름은 보통 `coding_bot`(또는 adapter 엔트리명)으로 표시
- 상태 매핑:
  - `working` → 작업 구역(실행 중처럼 보임)
  - `waiting` → 대기 구역(짧은 유휴/대기)
  - `idle` → 유휴 상태
  - `error` → 에러 구역
- 작업 시작/종료 전환 시 상태 변화가 더 빠르게 반영됩니다(TTL 오버레이 병합 로직)

### 5-4. 실행
```bash
python3 openclaw_coding_bot_adapter.py --interval 15
```

옵션:
- `--once` : 1회 실행 테스트
- `--mock-status idle|working|waiting|error` : UI 반영 검증

예시:
```bash
python3 openclaw_coding_bot_adapter.py --mock-status working --once
```

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

> 기본 Star Office는 원본 README대로 설치하고, 이 레포에서는 OpenClaw 봇을 18793 포트의 Star Office에 A안(직접 push) 또는 B안(세션 자동 연동)으로 연결해 실시간 상태 시각화를 완성합니다.
