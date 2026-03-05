# Star Office UI — Custom Change Report

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

- 코드 라이선스는 원본 정책을 따릅니다. 자세한 내용은 `LICENSE`를 확인하세요.
- 본 레포는 원본 라이선스 및 크레딧을 유지하며, 파생 변경 사항만 별도로 문서화합니다.
- 상업적 사용 제한이 걸린 아트 에셋 관련 고지는 원본/프로젝트 문서의 가이드를 준수하세요.

참고: `NOTICE` 파일에 업스트림 및 파생 작업 고지를 함께 제공합니다.

---

## 3) What changed vs upstream (핵심 변경점)

### A. OpenClaw 연동 확장
- `openclaw_coding_bot_adapter.py` 추가
- OpenClaw 세션을 읽어 `idle/working/waiting/error` 상태로 매핑
- task 시작/종료 이벤트 기반 푸시 + TTL 병합 로직 추가
- OpenClaw 세션 추적 기반 실시간 연동 방법은 [SKILL.md](./SKILL.md)에 사용자 가이드로 정리

### B. 백엔드 상태/엔드포인트 강화
- `backend/app.py` 확장
- `waiting` 상태 추가 및 상태 정규화 로직 보강
- `/openclaw/coding-bot-status` 엔드포인트 추가(옵션 토큰 인증)
- 게스트 join/push/offline 처리 로직 개선

### C. 에셋 파이프라인/꾸미기 기능 고도화
- `tools/asset_pipeline/*` 신규 추가
- 변형 에셋 검증/리팩/적용 스크립트 도입
- `tmp_assets/*`를 통한 실험/교체 자산 운용
- 배경 생성/복구/히스토리/즐겨찾기 흐름 강화

### D. UI/UX 개편
- `frontend/index.html`, `frontend/game.js`, `frontend/layout.js` 등 대규모 수정
- 다국어/모바일 대응 및 드로어 UX 개선
- 상태 스프라이트/애니메이션 에셋 교체

### E. 운영 문서화
- 변경 관찰/운영 노트 문서 추가
- 커스텀 변경 근거와 흐름을 재현 가능하게 정리

---

## 4) Repository intent

이 저장소의 목적은 다음 두 가지입니다.
1. 원본 대비 변경점을 투명하게 기록
2. 커스텀 기능을 재현/확장 가능한 형태로 공유

원본 자체의 정통 배포/소개는 업스트림 레포를 우선 참고하세요.

---

## 5) Included reference files

- `README.upstream.original.md` : 업스트림 원본 README 보관본
- `README.previous.custom.md` : 초기 커스텀 README 백업

