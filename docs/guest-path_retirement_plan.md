# Guest override / push / polling 경로 정리 계획 (Main=/set_state 확정)

## 목적
메인 상태 경로를 `/set_state -> state.json -> /status`로 확정한 상태에서,
기존 guest 기반 경로(override/push/polling)의 유지/퇴역/아카이브 범위를 명확히 분리한다.

## 결론 요약
- 메인 구동: `/set_state` 단일 경로로 고정
- guest 경로: 메인 상태 결정에서 분리, 패널/관찰 기능으로만 유지
- 브릿지 polling: 기본 OFF, 운영 필요 시 수동 실행

---

## 1) 유지(Keep)

### A. 메인 상태 API
- `backend/app.py`
  - `POST /set_state`
  - `GET /status`
- 이유: 메인 Star 상태의 단일 소스 오브 트루스

### B. guest 표시 기능(보조)
- `GET /agents` 및 guest panel 렌더
- 이유: 방문자/보조 상태 시각화는 유용하므로 기능 유지
- 단, 메인 상태 결정에 영향 주면 안 됨

### C. lifecycle -> /set_state 전송 코드(코어 훅)
- OpenClaw lifecycle sender (start/done/error -> writing/idle/error)
- 이유: 브릿지 없이 실시간 반영을 위한 정식 경로

---

## 2) 퇴역(Retire)

### A. primary guest override (메인처럼 보이게 하는 트릭)
- 프론트의 `PRIMARY_OFFICE_AGENT_ID` 기반 메인 오버라이드 로직
- 조치:
  - 기본 OFF 유지
  - 다음 단계에서 코드 제거(또는 내부 실험 플래그로만 유지)

### B. `/openclaw/coding-bot-status`를 메인 경로로 사용하는 운영 방식
- 조치:
  - 메인 상태 목적에서는 사용 중단
  - 필요 시 guest 관찰/디버그 목적 전용으로만 잔존

### C. 상시 polling 브릿지 운영
- `openclaw_coding_bot_adapter.py --interval ...` 상시 실행
- 조치:
  - 기본 운영에서 중단
  - 비상 진단/테스트 시에만 수동 실행

---

## 3) 아카이브(Archive)

아래는 삭제 대신 `docs/archive/` 기준으로 보관:

1. 브릿지/하이브리드 설계 문서
- `docs/coding-bot-adapter-observation.md` (필요 시 `docs/archive/misc/` 이동)
- `tools/asset_pipeline/reports/spike_push_A_round1.md`
- `tools/asset_pipeline/reports/spike_push_A_round2.md`
- `tools/asset_pipeline/reports/dispatch_push_*.md`

2. dist 직접 패치 재적용 문서
- `tools/asset_pipeline/reports/dispatch_push_patch_reapply.md`
- `tools/asset_pipeline/reports/dispatch_push_round2.diff`

아카이브 원칙:
- 운영 경로에서 참조 제거
- 회귀 분석/장애 대응을 위해 기록만 보존

---

## 4) 단계별 실행 계획

### Phase 1 (즉시)
1. README/SKILL에 메인 경로 단일화 명시
2. 브릿지 실행 중지 상태 유지
3. primary override 기본 OFF 확인

### Phase 2 (정리)
1. primary override 코드 제거 또는 `experimental` 경로로 격리
2. `/openclaw/coding-bot-status` 메인 목적 설명 제거
3. 관련 문서 archive 이동

### Phase 3 (안정화)
1. lifecycle sender `/set_state` 경로 E2E 스모크 자동화
2. 배포 게이트: start/done/error 3개 상태 반영 체크

---

## 5) 검증 체크리스트

1. start 이벤트 발생 시 `/status.state=writing`
2. done 이벤트 발생 시 `/status.state=idle`
3. error 이벤트 발생 시 `/status.state=error`
4. `/agents` 변화가 메인 `/status`를 덮어쓰지 않음
5. 브릿지 프로세스 미실행 상태에서도 메인 반영 정상

---

## 6) 롤백

문제 발생 시 임시 롤백:
1. lifecycle sender 비활성화 (`OPENCLAW_SET_STATE_PUSH_ENABLED=0`)
2. 수동 `/set_state` 운영
3. 필요 시 guest 경로만 복구(메인 오버라이드 금지)
