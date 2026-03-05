# ✨ Star Office UI

🌐 Language: **한국어** | [English](./README.en.md) | [日本語](./README.ja.md)

![Star Office UI 封面 2](docs/screenshots/readme-cover-2.jpg)

다중 Agent 협업을 위한 픽셀 오피스 보드입니다. AI 어시스턴트(OpenClaw / 랍스터)의 작업 상태를 실시간으로 시각화해, 팀이 “누가 무엇을 하고 있는지, 어제 무엇을 했는지, 지금 온라인인지”를 직관적으로 확인할 수 있도록 돕습니다.

> 본 프로젝트는 **Ring Hyacinth와 Simon Lee의 공동 프로젝트(co-created project)**입니다.

---

## 이 프로젝트는 무엇인가요? (한 줄 요약)

Star Office UI는 “다중 협업 상태 보드”입니다. 쉽게 말해:
> 실시간으로 업데이트되는 “픽셀 오피스 대시보드”입니다. AI 어시스턴트(및 초대한 다른 Agent)가 상태에 따라 자동으로 서로 다른 위치(휴식 구역 / 작업 구역 / bug 구역)로 이동하며, 어제의 작업 메모도 확인할 수 있습니다.

---

## ✨ 30초 빠른 체험 (먼저 보는 것을 추천)

```bash
# 1) 下载仓库
git clone https://github.com/ringhyacinth/Star-Office-UI.git
cd Star-Office-UI

# 2) 安装依赖
python3 -m pip install -r backend/requirements.txt

# 3) 准备状态文件（首次）
cp state.sample.json state.json

# 4) 启动后端
cd backend
python3 app.py
```

열기: **http://127.0.0.1:18791**

상태 전환 테스트(프로젝트 루트 디렉터리에서 실행):
```bash
python3 set_state.py writing "正在整理文档"
python3 set_state.py syncing "同步进度中"
python3 set_state.py error "发现问题，排查中"
python3 set_state.py idle "待命中"
```

![Star Office UI 封面 1](docs/screenshots/readme-cover-1.jpg)

---

## 1. 이 프로젝트에서 구현된 내용

현재 Star Office UI에서 구현된 기능은 다음과 같습니다:

1. **랍스터 작업 상태 시각화**
   - 상태: `idle`(대기), `writing`(작업), `researching`(연구), `executing`(실행), `syncing`(동기화), `error`(bug 보고)
   - 상태는 오피스 내 서로 다른 구역에 매핑되며, 애니메이션/말풍선으로 표시됩니다.

2. **“어제의 메모” 마이크로 요약**
   - 프런트엔드에 “어제의 메모” 카드가 표시됩니다.
   - 백엔드는 `memory/*.md`에서 어제(또는 최근 사용 가능한) 기록을 읽어, 기본 비식별화 후 표시합니다.

3. **다른 방문자(Agent) 오피스 초대 지원 (기능 지속 개선 중)**
   - join key로 참여합니다.
   - 방문자는 자신의 상태를 오피스 보드에 지속적으로 push할 수 있습니다.
   - 현재 사용 가능하며, 상호작용 및 온보딩 경험은 계속 최적화 중입니다.

4. **모바일 접속 지원 완료**
   - 모바일에서도 직접 접속해 상태를 확인할 수 있습니다(외부에서 빠르게 확인하기에 적합).

5. **중/영/일 3개 언어 전환 지원**
   - CN / EN / JP 3개 언어 전환을 지원합니다.
   - 언어 전환은 UI 문구, 로딩 안내, 캐릭터 말풍선에 실시간 반영됩니다.

6. **커스텀 아트 에셋 지원**
   - 에셋 사이드바에서 캐릭터/장면 소재를 교체할 수 있습니다.
   - 동적 소재의 프레임 재분할 및 파라미터 동기화(frame size / frame range)를 지원해 깜빡임을 줄입니다.

7. **자체 이미지 생성 API 연동 지원 (배경 무제한 교체 가능)**
   - 자체 이미지 생성 API를 연동해 “이사하기/중개인 찾기” 방식의 배경 업데이트를 할 수 있습니다.
   - 권장 모델: `nanobanana-pro` 또는 `nanobanana-2`(구조 유지가 더 안정적).
   - 기본 보드 기능은 API에 의존하지 않으며, API를 연결하지 않아도 핵심 상태 보드 및 에셋 관리를 정상적으로 사용할 수 있습니다.

8. **유연한 퍼블릭 접속 방식**
   - Skill 기본 권장은 Cloudflare Tunnel을 사용한 빠른 퍼블릭 노출입니다.
   - 자체 퍼블릭 도메인/리버스 프록시 구성도 사용할 수 있습니다.

---

## 2. 이번 리빌드(2026-03)의 핵심 변경사항

이번 버전은 단편적 패치가 아니라, 원본 프로젝트를 기반으로 한 전체 리빌드입니다. 핵심 변경은 아래 4가지 방향에 집중되었습니다:

1. **중/영/일 3개 언어(CN / EN / JP) 신규 지원**
   - 전역 UI 문구 3개 언어화
   - 상태 문구, 안내 문구, 에셋 표시명이 연동 전환됨

2. **에셋 관리 기능 추가(사용자가 전체 아트 에셋 커스터마이즈 가능)**
   - 에셋 사이드바에서 선택, 교체, 기본값 관리 지원
   - 캐릭터, 장면, 장식, 버튼 등 소재를 사용자 정의 가능

3. **이미지 생성 API 연동(방 자동 인테리어 + 수동 인테리어 지원)**
   - “이사하기 / 중개인 찾기 / 직접 꾸미기” 흐름 지원
   - 랍스터가 이미지 생성 기능으로 방 디자인을 변경할 수 있고, 사용자도 테마를 직접 입력해 리모델링할 수 있음

4. **아트 에셋 교체 및 최적화(중점)**
   - 핵심 에셋 대규모 교체 및 리드로잉 완료
   - 에셋 네이밍 및 인덱스 매핑 재구성으로 교체 안정성과 유지보수성 향상
   - 동적 소재 프레임 분할/표시 로직 최적화로 프레임 오류 및 캐시 간섭 감소

---

## 3. 빠른 시작

### 1) 의존성 설치

```bash
cd star-office-ui
python3 -m pip install -r backend/requirements.txt
```

### 2) 상태 파일 초기화

```bash
cp state.sample.json state.json
```

### 3) 백엔드 실행

```bash
cd backend
python3 app.py
```

열기: `http://127.0.0.1:18791`

### 4) 메인 Agent 상태 전환(예시)

```bash
python3 set_state.py writing "正在整理文档"
python3 set_state.py syncing "同步进度中"
python3 set_state.py error "发现问题，排查中"
python3 set_state.py idle "待命中"
```

---

## 4. 자주 쓰는 API

- `GET /health`: 헬스 체크
- `GET /status`: 메인 Agent 상태
- `POST /set_state`: 메인 Agent 상태 설정
- `GET /agents`: 다중 Agent 목록 조회
- `POST /join-agent`: 방문자 참여
- `POST /agent-push`: 방문자 상태 푸시
- `POST /leave-agent`: 방문자 나가기
- `GET /yesterday-memo`: 어제의 메모

---

## 5. 아트 에셋 사용 안내(반드시 읽어주세요)

### 방문자 캐릭터 에셋 출처

방문자 캐릭터 애니메이션은 LimeZu의 무료 에셋을 사용했습니다:
- **Animated Mini Characters 2 (Platformer) [FREE]**
- https://limezu.itch.io/animated-mini-characters-2-platform-free

재배포/데모 시 출처 표기를 유지하고, 원작자 라이선스 조항을 준수해 주세요.

### 상업적 사용 제한(중요)

- 코드와 게임플레이 로직은 MIT에 따라 사용 및 2차 개발이 가능합니다.
- **이 저장소의 모든 아트 에셋(메인 캐릭터/장면/소재 전체 포함)은 상업적 사용이 금지됩니다.**
- 상업적 용도로 사용하려면 반드시 직접 제작한 오리지널 아트 에셋으로 교체해 주세요.

---

## 6. 오픈소스 라이선스 및 고지

- **Code / Logic: MIT** (`LICENSE` 참고)
- **Art Assets: 비상업용, 학습/데모 용도 한정**

Fork, 아이디어 교류, PR은 환영합니다. 다만 에셋 사용 경계를 엄격히 지켜 주세요.

---

## 7. 더 많은 확장을 기대합니다

다음과 같은 방향으로 이 프레임워크를 확장해 보세요:
- 더 풍부한 상태 의미 체계와 자동 오케스트레이션
- 다중 방/다중 팀 협업 맵
- 작업 보드, 타임라인, 일일 리포트 자동 생성
- 더 완성도 높은 접근 제어 및 권한 체계

재미있는 개조를 하셨다면 공유해 주세요!

---

## 8. 프로젝트 저자

본 프로젝트는 **Ring Hyacinth**와 **Simon Lee**가 공동 창작 및 유지보수하고 있습니다.

- **X: Ring Hyacinth (@ring_hyacinth)**  
  https://x.com/ring_hyacinth
- **X: Simon Lee (@simonxxoo)**  
  https://x.com/simonxxoo

---

## 9. 2026-03 증분 업데이트(원본 기반 보강)

> 이 섹션은 “신규/변경” 내용만 기록하며, 그 외 내용은 원본 구조를 유지합니다.

### A) 방 인테리어 이미지 생성 모델 추천(신규)

“이사하기 / 중개인 찾기” 기능에서는, 자체 Gemini를 우선 연동하고 다음 모델 사용을 권장합니다:

1. **gemini nanobanana pro**
2. **gemini nanobanana 2**

다른 모델은 “기존 방 구조 유지 + 스타일 전이 일관성” 측면에서 기대에 못 미칠 수 있습니다.

권장 설정:

- `GEMINI_API_KEY`
- `GEMINI_MODEL`(권장: `nanobanana-pro` 또는 `nanobanana-2`)

또한, 프로젝트는 런타임 설정 엔드포인트를 지원합니다:
- `GET /config/gemini`
- `POST /config/gemini`

API key가 없으면 사이드바에 입력 UI가 나타나며, 사용자가 바로 입력 후 재시도할 수 있습니다.

### B) 에셋 편집 사이드바 비밀번호(신규)

사이드바에서 레이아웃, 장식, 기본 위치를 수정할 수 있습니다.

현재 기본값:
- `ASSET_DRAWER_PASS=1234`

사용자 안내 권장 문구:
1. 기본 비밀번호 `1234`로 먼저 체험 가능;
2. 사용자는 언제든 비밀번호 변경을 요청할 수 있음;
3. 보안을 위해 가능한 한 빨리 강한 비밀번호로 변경 권장.

예시:

```bash
export ASSET_DRAWER_PASS="your-strong-pass"
```

필요성:
- 접근 링크를 가진 사람이 방 레이아웃과 소재를 임의 변경하는 것을 방지합니다.

### C) 에셋 소스 확장(신규)

에셋 사이드바(`방 꾸미기`)의 목록은 이제 2개 소스를 함께 보여줍니다.

- `frontend/*` : 실제 UI에 즉시 반영 가능한 앱 에셋(APP)
- `tmp_assets/*` : 파이프라인 검수/리패킹 후보(TMP)

백엔드 `GET /assets/list` 응답의 각 item에는 다음 필드가 포함됩니다.
- `source`: `frontend` | `tmp_assets`
- `path`: 표시/선택용 경로 (`tmp_assets/...` 포함 가능)
- `url`: 썸네일/프리뷰용 안전 URL

참고:
- TMP 항목은 사이드바에서 선택/미리보기 대상이며, 직접 업로드 적용 대상은 아닙니다.
- 기존 canonical(frontend 경로) 동작은 그대로 유지됩니다.

### D) 설치 완료 후 오너에게 전달할 3가지 안내(신규)

1. **임시 퍼블릭 링크**
   - `trycloudflare` 임시 링크를 오너에게 전달;
   - 이후 자체 도메인 배포도 가능하며, 단계별로 안내 가능하다고 설명.

2. **방 꾸미기 진입점**
   - “방 꾸미기” 버튼으로 시작 가능하다고 안내;
   - 기본 비밀번호는 `1234`;
   - 오너가 변경을 원하면 언제든 지원 가능;
   - 강한 비밀번호로 변경 권장.

3. **이미지 생성 API 설정**
   - 이미지 생성은 사용자의 자체 API가 필요;
   - 현재 연동은 Gemini 공식 API 형식/주소 기준;
   - 다른 API 유형으로 바꾸려면 먼저 협의하고 관련 API 문서를 제공받아야 원활히 연동 가능.

### E) 실행 상태 운영 권장사항(신규)

Agent가 자신의 상태를 적극적으로 관리하는 것을 권장합니다:

1. 작업 수락 전, 먼저 “작업 중”(예: writing / researching / executing)으로 전환한 뒤 작업 시작;
2. 작업 완료 후, 먼저 “대기(idle)”로 전환한 뒤 휴식/다음 작업 대기.

이렇게 하면 오너가 오피스 보드에서 보는 상태가 더 실제 흐름에 가깝고 연속적으로 보입니다.

### F) 아트 및 저작권 가이드 업데이트(중요)

이번 리빌드의 핵심 중 하나는 아트 에셋 시스템 업그레이드입니다(대규모 교체 + 네이밍/인덱스 재구성).

유지 원칙:
- 코드 로직: MIT
- 아트 에셋: 상업적 사용 금지(학습/데모/교류 용도 한정)

## 프로젝트 구조(간략)

```text
star-office-ui/
  backend/
    app.py
    requirements.txt
    run.sh
  frontend/
    index.html
    join.html
    invite.html
    layout.js
    ...assets
  docs/
    screenshots/
  office-agent-push.py
  set_state.py
  state.sample.json
  join-keys.json
  SKILL.md
  README.md
  LICENSE
```
---

## Attribution / Credits

- Original project: https://github.com/ringhyacinth/Star-Office-UI
- Upstream authors: **Ring Hyacinth**, **Simon Lee**
- This repository is a customized derivative maintained by **HahnGyuTak**.

### Contributor handling policy

- We keep original authorship and contribution context by:
  1. preserving upstream reference,
  2. maintaining clear attribution in README/CONTRIBUTORS,
  3. keeping `upstream` remote for traceability.
- We do **not** manually add all historical upstream contributors as repository collaborators by default.

See also: `CONTRIBUTORS.md`.
