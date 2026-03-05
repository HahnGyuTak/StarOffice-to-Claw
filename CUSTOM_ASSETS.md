# CUSTOM_ASSETS.md

처음 클론한 사용자를 위한 **커스텀 에셋 적용 가이드**입니다.

이 문서 목표:
- "내가 만든(또는 구한) 에셋"을 StarOffice-to-Claw에 안전하게 적용
- 깨짐 없이 검증하고, 필요하면 원복까지 가능하게 작업

---

## 0) 먼저 이해할 것 (핵심 1분 요약)

에셋 교체는 아래 4단계입니다.

1. 원하는 에셋 준비 (`tmp_assets/`에 넣기)
2. 파일명/그리드 검증 (`parse_and_validate.py`)
3. canonical 형식으로 리패킹 (`repack_to_canonical.py`)
4. 실제 프론트에 적용 (`apply_variant.py --run`)

> 추천: 처음엔 항상 `--dry-run`으로 미리 확인하세요.

---

## 1) 시작 준비

```bash
git clone https://github.com/HahnGyuTak/StarOffice-to-Claw.git
cd StarOffice-to-Claw
```

Python/Pillow 환경이 필요합니다(보통 프로젝트 기본 환경에서 사용 가능).

---

## 2) 원하는 에셋 가져오기

에셋은 직접 준비해야 합니다.

- 직접 그리기 / 외부 에셋 구매/다운로드 / 생성형 도구 사용 모두 가능
- 생성형 도구 팁: **Nanobanana** 계열(예: nanobanana-pro, nanobanana-2)로 스타일 통일해서 뽑으면 결과 일관성이 좋습니다.

### 생성형 에셋 만들 때 팁
- 배경 투명 여부를 미리 결정(캐릭터/오브젝트는 보통 투명 권장)
- 프레임 애니메이션은 같은 크기/스타일로 통일
- 너무 다른 비율/해상도는 후처리 품질 저하 가능

---

## 3) 어떤 타입을 교체할 수 있나? (권장 형식)

현재 파이프라인의 canonical 대상은 아래 4종입니다.

| assetType (파일명 prefix) | 의미(사용자 관점) | 프레임별 픽셀 크기 | 권장 그리드 (cols×rows) | 권장 총 시트 픽셀 크기 (가로×세로) | 최종 적용 파일 |
|---|---|---:|---:|---:|---|
| `star-idle` | **대기 상태** 캐릭터 | 256×256 | 8×6 | 2048×1536 | `frontend/star-idle-v5.png` |
| `star-working-spritesheet-grid` | **작업 상태** 애니메이션 | 300×300 | 8×5 *(권장 예시)* | 2400×1500 *(권장 예시)* | `frontend/star-working-spritesheet-grid.webp` |
| `sync-animation-v3-grid` | **쉬는 상태**(동기화/휴식 연출) | 256×256 | 9×5 *(권장 예시)* | 2304×1280 *(권장 예시)* | `frontend/sync-animation-v3-grid.webp` |
| `error-bug-spritesheet-grid` | **에러 상태** 애니메이션 | 220×220 | 11×4 *(권장 예시)* | 2420×880 *(권장 예시)* | `frontend/error-bug-spritesheet-grid.webp` |

권장 확장자:
- 입력(`tmp_assets`): `.png` 또는 `.webp`
- 출력(최종): 파이프라인이 target 파일 규격에 맞춰 교체

설명:
- 프레임별 픽셀 크기는 canonical 기준입니다(리패킹 시 이 크기로 맞춰짐).
- 권장 그리드/총 시트 크기는 현재 프로젝트에서 검증된 안정적인 예시입니다.
- 다른 그리드도 파일명 메타(`__c<cols>_r<rows>`)와 실제 이미지가 정확히 맞으면 처리 가능하지만, 품질/호환성 측면에서 위 값을 우선 권장합니다.

---

## 4) 파일명 규칙 (가장 중요)

`tmp_assets/`에 넣을 때 파일명은 아래 형식을 지켜야 합니다.

```text
<assetType>-<variant>__c<cols>_r<rows>.<ext>
```

예시:
```text
star-idle-akaja__c8_r6.png
sync-animation-v3-grid-akaja__c9_r5.png
error-bug-spritesheet-grid-akaja__c11_r4.png
```

의미:
- `assetType`: 위 표의 타입 이름
- `variant`: 내가 붙이는 버전 이름(예: `akaja`, `v2`, `mytheme`)
- `c<cols>_r<rows>`: 스프라이트 시트의 열/행 개수
- `ext`: png/webp

---

## 5) 내 에셋 넣는 위치

### 입력 폴더
- `tmp_assets/`

여기에 내가 준비한 파일을 복사합니다.

```bash
cp /path/to/my_assets/* ./tmp_assets/
```

---

## 6) 검증 → 리패킹 → 적용 (전체 절차)

### 6-1. 검증 (필수)

```bash
python3 tools/asset_pipeline/parse_and_validate.py
```

결과 리포트:
- `tools/asset_pipeline/reports/validation_report.json`
- `tools/asset_pipeline/reports/validation_report.jsonl`

오류가 있으면 파일명/그리드부터 수정하세요.

---

### 6-2. canonical 리패킹

먼저 드라이런:

```bash
python3 tools/asset_pipeline/repack_to_canonical.py --dry-run
```

실행:

```bash
python3 tools/asset_pipeline/repack_to_canonical.py
```

산출물:
- `tools/asset_pipeline/repacked/`

---

### 6-3. variant 적용 (실제 교체)

먼저 드라이런:

```bash
python3 tools/asset_pipeline/apply_variant.py --variant <variant명> --dry-run
```

예:

```bash
python3 tools/asset_pipeline/apply_variant.py --variant akaja --dry-run
```

문제 없으면 실제 적용:

```bash
python3 tools/asset_pipeline/apply_variant.py --variant <variant명> --run
```

적용 시 백업 자동 생성:
- `tools/asset_pipeline/backups/<timestamp>/<variant>/`

---

## 7) auto-fit 옵션은 언제 쓰나?

그리드 크기가 딱 안 맞아 strict 모드에서 실패하면 다음 사용:

```bash
python3 tools/asset_pipeline/apply_variant.py --variant <variant명> --auto-fit-grid-resize --dry-run
```

주의:
- auto-fit은 crop/resize가 들어가므로 미세 품질 저하가 생길 수 있습니다.
- 품질 최우선이면 원본 에셋을 그리드 맞춰 다시 준비 후 strict 모드 권장.

---

## 8) 적용 후 확인

서버 실행 후 UI에서 확인:

```bash
python3 backend/app.py
```

브라우저:
- `http://127.0.0.1:18793`

확인 포인트:
- idle 캐릭터가 새 에셋으로 보이는지
- working/sync/error 애니메이션이 프레임 깨짐 없이 재생되는지

---

## 9) 실패 시 복구

- `tools/asset_pipeline/backups/...`에 백업이 있으므로 재적용/수동 복구 가능
- `--dry-run`부터 다시 시작해 어느 단계에서 깨지는지 확인

---

## 10) 추천 작업 루틴

1. 새 variant 이름 하나 정하기 (`mytheme`)
2. `tmp_assets/`에 파일명 규칙 맞춰 넣기
3. validate → repack → apply(dry-run)
4. 이상 없으면 apply(run)
5. UI 확인 후 필요시 리터치 반복

---

## 참고 문서

- 파이프라인 상세: `tools/asset_pipeline/README.md`
- 전체 프로젝트/연동: `README.md`, `SKILL.md`
