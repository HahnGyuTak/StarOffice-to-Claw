# Star Office UI — Custom Change Report

[EN ver](./README.en.md)

> **Based on** the original project: https://github.com/ringhyacinth/Star-Office-UI

이 저장소는 원본 Star-Office-UI를 그대로 재배포하는 목적이 아니라, **원본 대비 어떤 기능을 바꿨고 무엇을 추가했는지**를 정리/공유하기 위한 커스텀 변경판입니다.

---
<img width="1041" height="591" alt="screenshot 3" src="https://github.com/user-attachments/assets/8b048ba8-57b3-4009-a75a-ec73448b6272" />

## 1) Upstream / Credits

- Original repository: https://github.com/ringhyacinth/Star-Office-UI
- Original README: https://github.com/ringhyacinth/Star-Office-UI/blob/master/README.md
- Upstream credit: Ring Hyacinth, Simon Lee

이 레포는 업스트림 코드를 기반으로 한 파생 작업이며, 원본 기여 맥락은 업스트림 저장소에서 확인할 수 있습니다.

---

## 2) License / Notice

- 코드 라이선스는 원본 정책을 따릅니다. 자세한 내용은 [`LICENSE`](./LICENSE)를 확인하세요.
- 본 레포는 원본 라이선스 및 크레딧을 유지하며, 파생 변경 사항만 별도로 문서화합니다.
- 상업적 사용 제한이 걸린 아트 에셋 관련 고지는 원본/프로젝트 문서의 가이드를 준수하세요.

참고: [`NOTICE`](./NOTICE) 파일에 업스트림 및 파생 작업 고지를 함께 제공합니다.

---

## 3) What changed vs upstream (핵심 변경점)

### A. OpenClaw 연동 확장
- [`openclaw_coding_bot_adapter.py`](./openclaw_coding_bot_adapter.py) 추가
- OpenClaw 세션을 읽어 `idle/working/waiting/error` 상태로 매핑
- task 시작/종료 이벤트 기반 푸시 + TTL 병합 로직 추가
- OpenClaw 세션 추적 기반 실시간 연동 방법은 [SKILL.md](./SKILL.md)에 사용자 가이드로 정리

### B. 백엔드 상태/엔드포인트 강화
- [`backend/app.py`](./backend/app.py) 확장
- `waiting` 상태 추가 및 상태 정규화 로직 보강
- `/openclaw/agent-status` 엔드포인트 추가(구형 `/openclaw/coding-bot-status` 호환, 옵션 토큰 인증)
- 게스트 join/push/offline 처리 로직 개선

### C. 에셋 파이프라인/꾸미기 기능 고도화
- [`tools/asset_pipeline/`](./tools/asset_pipeline/) 신규 추가
- 변형 에셋 검증/리팩/적용 스크립트 도입 ([`apply_variant.py`](./tools/asset_pipeline/apply_variant.py), [`parse_and_validate.py`](./tools/asset_pipeline/parse_and_validate.py), [`repack_to_canonical.py`](./tools/asset_pipeline/repack_to_canonical.py))
- [`tmp_assets/`](./tmp_assets/)를 통한 실험/교체 자산 운용
- 배경 생성/복구/히스토리/즐겨찾기 흐름 강화 (서버 로직: [`backend/app.py`](./backend/app.py), 즐겨찾기 저장 경로: [`assets/home-favorites/`](./assets/home-favorites/))
- 에셋 꾸미기/교체를 실제로 따라하는 사용자 가이드는 [`CUSTOM_ASSETS.md`](./CUSTOM_ASSETS.md) 참고

### D. UI/UX 개편
- [`frontend/index.html`](./frontend/index.html), [`frontend/game.js`](./frontend/game.js), [`frontend/layout.js`](./frontend/layout.js) 등 대규모 수정
- 다국어/모바일 대응 및 드로어 UX 개선
- 상태 스프라이트/애니메이션 에셋 교체
- **오피스 이름 영어 단일화 + 변경 방법 문서화**
  - 기본값: `Star Office`
  - 커스텀값: `Hahn Office`
  - 변경 위치/런타임 오버라이드는 아래 `Office name policy (English-only)` 섹션 참고

### E. 운영 문서화
- 변경 관찰/운영 노트 문서 추가
- 커스텀 변경 근거와 흐름을 재현 가능하게 정리

### F. 상태-영역-에셋 최종 매핑 (Round2 기준)

| 표준 상태 | 내부 호환 키(legacy) | 영역(area) | 메인 에셋(asset) |
|---|---|---|---|
| idle | idle, waiting | breakroom | `idle-asset-grid` |
| working | writing, researching, executing | writing | `working-asset-grid` |
| rest | syncing | writing (렌더링은 우하단 고정) | `rest-asset-grid` |
| error | error | error | `error-asset-grid` |

> 참고: 내부 상태 키는 호환을 위해 유지되며, UI/문서 표기는 `idle / working / rest / error`를 기준으로 합니다.

---

## 4) Office name policy (English-only)

사무실 이름은 언어 모드와 관계없이 **영어 단일 값**으로 통일합니다.

- Default: `Star Office`
- Current custom: `Hahn Office`

현재 구현은 프론트에서 아래 우선순위로 이름을 결정합니다.
1. `window.STAR_OFFICE_NAME` (런타임 오버라이드)
2. `CUSTOM_OFFICE_NAME` (코드 기본 커스텀값)
3. `DEFAULT_OFFICE_NAME` (`Star Office`)

어디서 바꿀 수 있나:
- 코드 기본값 변경
  - `frontend/index.html` 상단 스크립트의 `CUSTOM_OFFICE_NAME`, `DEFAULT_OFFICE_NAME`
  - `frontend/game.js` 상단의 동일 상수
- 런타임에서 즉시 덮어쓰기(배포 후 임시 변경)
  - 브라우저 콘솔에서 `window.STAR_OFFICE_NAME = '원하는이름'` 설정 후 새로고침
  - 또는 `index.html`에 `<script>window.STAR_OFFICE_NAME='원하는이름'</script>` 주입

적용 위치:
- 로딩 텍스트
- 게임 내 명패(plaque) 텍스트
- `officeTitle` 번역 키 출력값(언어와 무관하게 동일 영어명)

## 5) Repository intent

이 저장소의 목적은 다음 두 가지입니다.
1. 원본 대비 변경점을 투명하게 기록
2. 커스텀 기능을 재현/확장 가능한 형태로 공유

원본 자체의 정통 배포/소개는 업스트림 레포를 우선 참고하세요.

---

## 6) Documentation Map

핵심 문서는 아래 3개만 먼저 보면 됩니다.

- [`README.md`](./README.md)
- [`SKILL.md`](./SKILL.md)
- [`CUSTOM_ASSETS.md`](./CUSTOM_ASSETS.md)

그 외 과거 기록/초안/보관 문서는 `docs/archive/`에 정리되어 있습니다.

