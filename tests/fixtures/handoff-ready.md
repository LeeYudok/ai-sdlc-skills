# HANDOFF — stock-auto-trading

Written: 2026-08-25 11:20:31 | Branch: `feat/issue-42-order-router` | HEAD: `9f31ac2`

## 1. Goal (do not change)
- Request: 주식자동매매 만들어줘
- Pipeline stage: `implemented` (in_progress; completed: initialized → analyzed → specified → implemented)
- Acceptance criteria:
  - [x] AC-1 시장가 주문이 브로커 어댑터를 통해 전송되고 체결 응답이 저장된다
  - [ ] AC-2 일일 손실 한도를 넘으면 신규 주문이 차단된다

## 2. Current state
- Last commit: `9f31ac2` feat: 주문 라우터에 손실 한도 게이트 추가 (#42)
- Uncommitted changes:
  - `src/trading/limits.py`
- Verification status: typecheck ✅ / unit ✅ (42 passed) / e2e ❌ (not run)
- Confirmed working: `pytest tests/trading` 로 주문 라우터와 손실 한도 게이트를 실행해 통과 확인

## 3. Decisions (do not reopen)
| Decision | Reason | Rejected alternative and why |
|---|---|---|
| 주문 상태를 PostgreSQL 에 저장 | 체결 감사 로그가 재기동 후에도 남아야 함 | 인메모리 큐 — 프로세스 재시작 시 체결 이력 소실 |
| 손실 한도를 주문 라우터에서 평가 | 모든 주문 경로가 라우터를 통과해 우회가 불가능 | 전략 모듈별 검사 — 신규 전략이 검사를 빠뜨릴 수 있음 |

## 4. Remaining work (in order)
1. `src/trading/limits.py` 의 `DailyLossLimit.evaluate` 에 미체결 주문 반영
2. `tests/trading/test_limits.py` 에 AC-2 회귀 테스트 추가
3. Final: verification command → PR → `Closes #N`

## 5. Traps
- 브로커 샌드박스는 09:00 이전 주문을 거부한다 — 재현 시 `FakeBroker` 를 쓴다
- `src/trading/legacy_router.py` 는 건드리지 않는다. 구 전략이 아직 참조 중

## 6. Resume procedure
```bash
git switch feat/issue-42-order-router
pytest tests/trading   # passing proves section 2 is accurate
```

## 7. Files to load (only these)
- `src/trading/limits.py` — 손실 한도 게이트 구현 지점
- `tests/trading/test_limits.py` — AC-2 를 검증하는 테스트
