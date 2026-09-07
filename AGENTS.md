# AGENTS.md — ai-sdlc-skills

이 저장소에서 작업하는 AI 에이전트의 **단일 진실원천(SSOT)**. 자체 완결 — 다른 파일 로딩·하네스 전용 문법 없이 읽힌다(근거: [CONTEXT.md](CONTEXT.md)). P0/P1/P2 규칙의 정본은 이 문서다.

## 프로젝트 개요

운영 중인 기존 저장소에서 버그·기능 요청을 저장소 분석 → 증거 교차검증 → BA → 전체 영향도
→ 명세 → 구현 → QA → 로컬 배포 → 무중단 운영 배포 준비 순서로 처리하는 재사용 가능한 Codex
SDLC 스킬 모음. 산출물은 소비자 저장소의 `.ai-sdlc/runs/<run>/` 에 쌓인다.

## 문서 지도

| 문서 | 담당 |
|---|---|
| `AGENTS.md`(이 문서) | 규칙·명령·워크플로 — 에이전트가 지켜야 할 것 |
| [CONTEXT.md](CONTEXT.md) | 설계 결정과 근거, 비목표, 불변 제약, 세션 시작 시 읽을 최소 파일 |
| [README.md](README.md) | 무엇을 하는 도구인지, 소비자 저장소 설치·사용법 |
| [docs/REFERENCE.md](docs/REFERENCE.md) | 스킬별 입력/출력 아티팩트와 단계 게이트 순서 |
| [skills/README.md](skills/README.md) | 스킬 목록과 각 `SKILL.md` 링크 |
| [docs/ADOPTION.md](docs/ADOPTION.md) | 큰 저장소에 단계적으로 도입하는 순서 |
| `.claude/rules/` | 이 문서 규칙의 스코프별 상세(보장 범위·한계) — 요약이 아니라 보충 |

## 스택

- Agent Skills 표준 Markdown/YAML
- Python 3 표준 라이브러리(결정적 파이프라인 상태 관리)
- Bash(소비자 저장소 설치와 테스트)

## 명령

- 전체 검증: `tests/test.sh` — 아래를 모두 실행한다
  - `tests/test_harness.sh` — 하네스 구성 불변식(CLAUDE.md 위임, AGENTS.md 자체 완결, 훅 배선, 룰 스코프, 메모리 구조, 문서-스킬 동기화, 상대 링크 유효성)
  - `tests/test_hook.sh` — `.env` 스테이징 차단 훅 회귀 테스트
  - `tests/validate_skill.py <skill-dir>` — 스킬별 frontmatter 검증
  - 설치(copy/link)·상태머신 게이트·핸드오프 작성/검증 시나리오
- 스킬 단독 검증: `python3 tests/validate_skill.py <skill-dir>`
- 하네스 불변식 단독 실행: `tests/test_harness.sh`
- 훅 회귀 테스트 단독 실행: `tests/test_hook.sh`

## 메모리·하네스

- 프로젝트 메모리 SSOT 는 `.claude/memory/`(`MEMORY.md` 인덱스). 시스템 기본 메모리 경로는 쓰지 않는다.
- `.claude/` 는 **동작하는 최소**만 둔다 (#14): `rules/`(스코프 룰), `hooks/pre-commit.sh`(커밋 대상 저장소의 `.env` 스테이징 차단), `settings.json`(그 훅을 `PreToolUse(Bash)` 로 배선), `memory/`. 설명만 있고 배선되지 않은 훅·스크립트·스킬을 두지 않는다 — `tests/test_harness.sh` 가 검사한다.
- 설계 결정·비목표·세션 시작 시 읽을 파일은 [CONTEXT.md](CONTEXT.md).

## 컨벤션

- skill/agent 신규 생성 시 `ai-sdlc-skills-` prefix 네임스페이스
- 스킬을 추가·삭제하면 [docs/REFERENCE.md](docs/REFERENCE.md) 와 [skills/README.md](skills/README.md) 를 같은 커밋에서 갱신한다(누락 시 `tests/test_harness.sh` 실패)
- 세부 규약은 `.claude/rules/` 의 paths 스코프 룰 참조

## 우선순위 체계 (P0/P1/P2)

| 등급 | 의미 | 위반 시 |
|------|------|---------|
| **P0** | 절대 규칙 — 보안·데이터 파괴·시크릿 노출 | 즉시 중단, 사용자 에스컬레이션 |
| **P1** | 필수 — AI 자율 실행 범위 | PR 차단 |
| **P2** | 권장 — 리뷰 지적, 예외 협의 가능 | 리뷰 코멘트 |

### P0 — 절대 규칙 (AI/사람 모두, 예외 없음)

- **보안**: 시크릿/토큰/비밀번호를 코드·로그·이슈·채팅에 노출 금지. `source` 경유 간접 사용만. `curl` 에 `-v`/`-sv` 금지 — 헤더가 마스킹을 우회한다.
- **데이터**: 프로덕션 DB에 `DELETE/DROP/TRUNCATE` 전 사용자 명시 동의
- **git**: `force push` / `reset --hard` 전 확인. `.env` 스테이징 금지
- **인증**: 인증 없는 API 엔드포인트 신규 추가 금지

### P1 — 필수 (AI 자율 실행 범위, 위반 시 PR 차단)

- **이슈 우선**: 이슈를 먼저 등록하고 그 번호를 브랜치명·커밋·PR 제목에 박는다. trivial typo만 예외.
- **브랜치**: `main`(prod) / `develop`(통합) / `<type>/issue-<N>-<slug>`(작업) / `hotfix`(main 직접). `main`·`develop` 직접 커밋 금지.
- **commit 직전 브랜치 재확인**: 자동 프로세스가 `main` 으로 checkout 했을 수 있다.
- **git 동사 즉시 실행**: "푸시/머지/커밋/싱크/풀/배포" 명령엔 바로 실행. 파괴적 git 만 별도 확인.
- **커밋 전 `tests/test.sh` 통과.** `.env` 스테이징은 `.claude/hooks/pre-commit.sh` 가 커밋 대상 저장소의 index 를 검사해 자동 차단(대상 판별 불가 시 fail closed)하고, 나머지는 규율 — 보장 범위·한계는 `.claude/rules/common.md`.
- **새 기능 = 테스트 동반**: 최소 1개 unit/integration 테스트.
- **이슈 클로즈**: PR 본문 `Closes #N` 으로 머지 시 자동 클로즈(GitHub). 상세는 `.claude/rules/forge.md`.

### P2 — 권장 (리뷰 지적 사항, 예외 협의 가능)

- 함수당 인지 복잡도(CC) 15 이하
- 파일 1개 = 단일 책임 (300줄 초과 시 분리 검토)
- TODO/FIXME 에 이슈 번호 병기

## 워크플로

1. **이슈 등록**(`gh issue create`) → 2. **워크트리·브랜치 생성**(`<type>/issue-<N>-<slug>`) → 3. **구현** →
4. **`tests/test.sh` 통과** → 5. **PR 생성**(본문에 `Closes #<N>`) → 6. **리뷰 반영** → 7. **머지 + worktree 정리**

- 이 저장소의 forge 는 GitHub. CLI 는 `gh`, 긴 본문은 파일로 써서 `-F body.md`. 상세는 `.claude/rules/forge.md`.
- CI: pull request 와 `main` 대상 push 마다 `.github/workflows/test.yml` 이 `tests/test.sh` 를 실행한다. 필수 check 이름은 **`test`** (#27).
- 리뷰 finding 은 finding 별로 "반영 / 오탐(이유 한 줄)" 을 PR 답글로 남긴 뒤 머지한다 — 조용히 넘기지 않는다.

## 멀티 에이전트 · 병렬 세션

이 레포를 동시에 만지는 모든 워커(세션·서브에이전트·페르소나)는 **각자의 git worktree** 로 격리한다(근거: [CONTEXT.md](CONTEXT.md)).

- `git worktree add ../ai-sdlc-skills-<slug> -b <type>/issue-<N>-<slug>` — 1세션 = 1worktree = 1이슈 = 1브랜치.
- 정식 클론은 default 브랜치 미러(pull·읽기만). 거기서 `checkout`/`switch` **금지**.
- `git add` 는 명시 파일만 — 디렉터리·`-A` 금지.
- `git status` 에 내가 만들지 않은 변경이 보이면 진행 전에 병렬 세션 여부부터 확인.
- 병렬 서브에이전트가 파일을 동시에 수정하면 `isolation: "worktree"` 필수.
- 머지 후 worktree 제거 + 로컬 브랜치 삭제를 그 자리에서 수행.
- worktree 오케스트레이터(예: Orca) 사용 시 생성·정리는 도구에 위임, 수동 `worktree add/remove` 금지.
