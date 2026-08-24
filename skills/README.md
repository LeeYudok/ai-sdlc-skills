# skills/ — ai-sdlc-skills 스킬 목록

각 디렉터리는 `ai-sdlc-skills-` prefix를 가진 독립 스킬(`SKILL.md` + `agents/openai.yaml`)이다.
설치는 [bin/install.sh](../bin/install.sh)가 이 디렉터리 전체를 소비자 저장소의
`.agents/skills/`로 복사·링크한다. 입력/출력 아티팩트까지 한눈에 보려면
[docs/REFERENCE.md](../docs/REFERENCE.md) 참고.

## 파이프라인

게이트 상태머신 순서(`ai-sdlc-skills-pipeline/scripts/pipeline_state.py`)대로:

| 스킬 | 역할 |
|---|---|
| [ai-sdlc-skills-pipeline](ai-sdlc-skills-pipeline/SKILL.md) | 전체 파이프라인 오케스트레이션 |
| [ai-sdlc-skills-analyze](ai-sdlc-skills-analyze/SKILL.md) | 저장소 분석 |
| [ai-sdlc-skills-evidence](ai-sdlc-skills-evidence/SKILL.md) | 다중 도구 증거 교차검증 |
| [ai-sdlc-skills-ba](ai-sdlc-skills-ba/SKILL.md) | 비즈니스 분석 문서 |
| [ai-sdlc-skills-impact](ai-sdlc-skills-impact/SKILL.md) | 전체 영향도 평가 |
| [ai-sdlc-skills-specify](ai-sdlc-skills-specify/SKILL.md) | 기능 명세 |
| [ai-sdlc-skills-implement](ai-sdlc-skills-implement/SKILL.md) | 구현 |
| [ai-sdlc-skills-verify](ai-sdlc-skills-verify/SKILL.md) | QA 검증(스택별 리뷰가이드 온디맨드 로드) |
| [ai-sdlc-skills-local-deploy](ai-sdlc-skills-local-deploy/SKILL.md) | 로컬 배포·스모크 테스트 |
| [ai-sdlc-skills-release](ai-sdlc-skills-release/SKILL.md) | 운영 배포 준비 평가 |

## 딜리버리 (선택, 사용자 트리거, 게이트 상태머신 밖)

| 스킬 | 역할 |
|---|---|
| [ai-sdlc-skills-commit](ai-sdlc-skills-commit/SKILL.md) | 로컬 conventional commit — push 하지 않음 |
| [ai-sdlc-skills-pr](ai-sdlc-skills-pr/SKILL.md) | PR/MR 오픈 — 머지하지 않음 |
| [ai-sdlc-skills-handoff](ai-sdlc-skills-handoff/SKILL.md) | 컨텍스트 소진 전 `HANDOFF.md` 상태 스냅샷 작성·검증, 새 세션 재개 |
