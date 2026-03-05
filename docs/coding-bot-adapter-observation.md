# coding_bot adapter 관찰 모드 운영 메모

## 서비스 유닛
- 파일: `~/.config/systemd/user/star-office-coding-bot-adapter.service`
- 실행 대상: `python3 /home/prml-218/Star-Office-UI/openclaw_coding_bot_adapter.py --interval 5`

## 제어 명령
```bash
# 반영/재시작
systemctl --user daemon-reload
systemctl --user restart star-office-coding-bot-adapter.service

# 시작/중지
systemctl --user start star-office-coding-bot-adapter.service
systemctl --user stop star-office-coding-bot-adapter.service

# 부팅 후 자동 시작
systemctl --user enable star-office-coding-bot-adapter.service

# 상태 확인
systemctl --user status star-office-coding-bot-adapter.service
```

## 로그 확인
```bash
# 최근 로그
journalctl --user -u star-office-coding-bot-adapter.service -n 100 --no-pager

# 실시간 tail
journalctl --user -u star-office-coding-bot-adapter.service -f
```

## 상태 반영 데이터 위치
- UI 반영 파일: `/home/prml-218/Star-Office-UI/agents-state.json`
- 어댑터 캐시: `/home/prml-218/Star-Office-UI/memory/openclaw-coding-bot-adapter-cache.json`

## 임계치 튜닝 위치
파일: `openclaw_coding_bot_adapter.py`

- `ERROR_ABORT_WINDOW_SEC` (기본: 1800초)
- `WORKING_RECENT_WINDOW_SEC` (기본: 180초)
- `VERY_RECENT_WORKING_SEC` (기본: 20초)
- `WAITING_RECENT_WINDOW_SEC` (기본: 90초)

관찰 단계에서는 위 3개만 조정하고, 나머지 구조는 유지한다.
