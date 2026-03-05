# Asset Pipeline (tmp_assets 메타 기반)

`tmp_assets` 파일명 메타(`assetType/variant/cols/rows`)를 기준으로 검증/리패킹/적용을 수행하는 도구 모음입니다.

## 대상 파일명 규칙

```text
<assetType>-<variant>__c<cols>_r<rows>.<ext>
```

- 지원 확장자: `png`, `webp` (대소문자 허용, 내부적으로 소문자 정규화)
- 검증 오류 코드 예시
  - `INVALID_FILENAME`
  - `UNSUPPORTED_EXTENSION`
  - `NON_INTEGER_GRID`
  - `NON_POSITIVE_GRID`

## Canonical frame spec

- `star-idle` → `256x256`
- `star-working-spritesheet-grid` → `300x300`
- `sync-animation-v3-grid` → `256x256`
- `error-bug-spritesheet-grid` → `220x220`

---

## 1) parse/validate

```bash
python3 tools/asset_pipeline/parse_and_validate.py
```

기본 출력:
- `tools/asset_pipeline/reports/validation_report.json`
- `tools/asset_pipeline/reports/validation_report.jsonl`

커스텀 입력/출력:

```bash
python3 tools/asset_pipeline/parse_and_validate.py \
  --input-dir /home/prml-218/Star-Office-UI/tmp_assets \
  --out-json tools/asset_pipeline/reports/validation.custom.json \
  --out-jsonl tools/asset_pipeline/reports/validation.custom.jsonl
```

---

## 2) repack to canonical

드라이런:

```bash
python3 tools/asset_pipeline/repack_to_canonical.py --dry-run
```

실행:

```bash
python3 tools/asset_pipeline/repack_to_canonical.py
```

기본 출력:
- 산출물 디렉토리: `tools/asset_pipeline/repacked`
- 리포트: `tools/asset_pipeline/reports/repack_report.json`
- 스킵 상세 사유(JSONL): `tools/asset_pipeline/reports/repack_skipped_reasons.jsonl`

옵션:
- `--skip-reasons-jsonl <path>` 로 스킵 사유 파일 경로 변경 가능

동작 요약:
- 파일명 검증 통과 + canonical assetType 인 경우만 처리
- 원본 시트가 `cols/rows`로 **정수 분할 가능**할 때만 프레임 슬라이스 수행
- 각 프레임을 canonical frame size로 리사이즈 후 동일 그리드로 재배치
- 분할 불가/비정상 파일은 `skipped` + 사유 기록

---

## 3) apply variant (안전 교체)

드라이런(기본 strict):

```bash
python3 tools/asset_pipeline/apply_variant.py --variant akaja --dry-run
```

드라이런(auto-fit):

```bash
python3 tools/asset_pipeline/apply_variant.py --variant akaja --auto-fit-grid-resize --dry-run
```

실행:

```bash
python3 tools/asset_pipeline/apply_variant.py --variant akaja --run
```

기본 동작:
- 소스: `tools/asset_pipeline/repacked`
- 타겟: `/home/prml-218/Star-Office-UI/frontend`
- 백업: `tools/asset_pipeline/backups/<timestamp>/<variant>/`

canonical 파일명 매핑:
- `star-idle` → `frontend/star-idle-v5.png`
- `star-working-spritesheet-grid` → `frontend/star-working-spritesheet-grid.webp`
- `sync-animation-v3-grid` → `frontend/sync-animation-v3-grid.webp`
- `error-bug-spritesheet-grid` → `frontend/error-bug-spritesheet-grid.webp`

> `--run` 시 기존 타겟 파일을 먼저 백업한 뒤 교체합니다.
>
> 추가 안전장치(ROUND2):
> - Duplicate source 차단: 같은 variant 컨텍스트에서 동일 `assetType` 소스가 2개 이상이면 `DUPLICATE_SOURCE_FOR_ASSET_TYPE` 오류로 중단
> - Preflight 검증: 실제 적용 전에 파일명 메타/그리드/이미지 디코드/기대 시트 크기(`frame*grid`)를 확인
> - Atomic apply + rollback: staging 파일 생성 후 `os.replace`로 원자 교체, 실패 시 자동 롤백
> - Preflight 실패 또는 duplicate 감지 시 타겟 산출물은 변경되지 않음

strict vs auto-fit 동작:
- 기본(strict, 옵션 미사용): 기존과 동일하게 `PREFLIGHT_DIMENSION_MISMATCH` 발생 시 즉시 실패합니다.
- `--auto-fit-grid-resize` 사용 시: dimension mismatch를 자동 보정 경로로 처리합니다.
  1) `crop_w = width % cols`, `crop_h = height % rows` 계산
  2) 좌/우, 상/하에 1px 단위 분배 crop (`left=floor`, `right=ceil`, `top=floor`, `bottom=ceil`)
  3) crop 후 프레임 분할 → canonical frame 크기로 리사이즈 → canonical 시트 재구성 후 적용
- auto-fit 실패 코드:
  - `AUTO_FIT_INVALID_DIMENSIONS`: crop 후 유효 크기(>0) 또는 grid 정합 불가
  - `AUTO_FIT_PROCESSING_FAILED`: crop/slice/resize/repack 중 예기치 못한 오류

리포트(`apply_report*.json`) 항목별 추가 필드:
- `auto_correction.enabled/used`
- `original_size`
- `crop_pixels` (`left/right/top/bottom`)
- `post_crop_size`
- `grid`
- `inferred_frame_before_resize`
- `canonical_frame_after_resize`
- `status`, `warnings`

주의사항:
- auto-fit은 경계부 픽셀 손실(crop)과 프레임 리샘플링(resize)으로 인해 미세한 품질 저하/아티팩트가 생길 수 있습니다.
- 무손실 정합이 중요하면 strict 모드를 유지하세요.

---

## 샘플 리포트

- `reports/validation_report.json`
- `reports/validation_report.jsonl`
- `reports/validation_report.sample_invalid.json`
- `reports/validation_report.sample_invalid.jsonl`
- `reports/repack_report.dry_run.json`
- `reports/repack_report.json`
- `reports/apply_report.dry_run.json`
