# AGENTS.md — ai-sdlc-skills

이 파일은 이 저장소에서 작업할 때 Codex 등 AGENTS.md 호환 AI 에이전트가 따르는
**단일 진실원천(SSOT)** 이다. 프로젝트 브레인.

이 파일은 **자체 완결**이어야 한다 — 아래 P0/P1 은 다른 파일 로딩 없이 여기서 읽힌다.
`@` import 같은 특정 하네스 전용 문법은 여기에 두지 않는다.

## 메모리·하네스

- 프로젝트 메모리 SSOT 는 `.claude/memory/`(`MEMORY.md` 인덱스). 시스템 기본 메모리 경로는 쓰지 않는다.
- `.claude/` 는 **동작하는 최소**만 둔다 (#14): `rules/`(스코프 룰), `hooks/pre-commit.sh`(`.env` 스테이징 차단, `settings.json` 에 배선), `memory/`. 설명만 있고 배선되지 않은 훅·스크립트·스킬을 두지 않는다.
- 설계 결정·비목표·세션 시작 시 읽을 파일은 [CONTEXT.md](CONTEXT.md).

## 프로젝트 개요

운영 중인 기존 저장소에서 버그·기능 요청을 저장소 분석 → BA → 전체 영향도 → 명세 →
구현 → QA → 로컬 배포 → 무중단 운영 배포 준비 순서로 처리하는 재사용 가능한 Codex
SDLC 스킬 모음.

## 스택

- Agent Skills 표준 Markdown/YAML
- Python 3 표준 라이브러리(결정적 파이프라인 상태 관리)
- Bash(소비자 저장소 설치와 테스트)

## 명령

- 전체 검증: `tests/test.sh` (스킬 frontmatter·설치·상태머신·핸드오프 포함)
- 스킬 단독 검증: `python3 tests/validate_skill.py <skill-dir>`

## 컨벤션

- skill/agent 신규 생성 시 `ai-sdlc-skills-` prefix 네임스페이스
- 세부 규약은 `.claude/rules/` 의 paths 스코프 룰 참조

## 우선순위 체계 (P0/P1/P2)

### P0 — 절대 규칙 (AI/사람 모두, 예외 없음)
P0 위반 시 즉시 작업 중단 + 사용자 에스컬레이션.

- **보안**: 시크릿/토큰/비밀번호를 코드·로그·이슈에 노출 금지
- **데이터**: 프로덕션 DB에 `DELETE/DROP/TRUNCATE` 전 사용자 명시 동의
- **git**: `force push` / `reset --hard` 전 확인. `.env` 스테이징 금지
- **인증**: 인증 없는 API 엔드포인트 신규 추가 금지


### P1 — 필수 (AI 자율 실행 범위, 위반 시 PR 차단)

- 이슈 번호를 브랜치명·커밋·PR/MR 제목에 반드시 포함
- 커밋 전 `tests/test.sh` 통과. `.env` 스테이징은 `.claude/hooks/pre-commit.sh` 가 자동 차단하고, 나머지는 규율
- 새 기능에 최소 1개 테스트 동반
- `main`/`develop` 직접 커밋 금지 → 항상 feature/fix/chore 브랜치

### P2 — 권장 (리뷰 지적 사항, 예외 협의 가능)

- 함수당 인지 복잡도(CC) 15 이하
- 파일 1개 = 단일 책임 (300줄 초과 시 분리 검토)
- TODO/FIXME 에 이슈 번호 병기

## 워크플로

1. **이슈 등록** → 2. **브랜치 생성** (`feat/issue-<N>-<slug>`) → 3. **구현** →
4. **`tests/test.sh` 통과** → 5. **PR/MR 생성** → 6. **리뷰** → 7. **머지 + 이슈 클로즈**

이 저장소의 forge 는 GitHub — PR 본문 `Closes #N` 으로 머지 시 자동 클로즈. 상세는 `.claude/rules/forge.md`.

## 멀티 에이전트 · 병렬 세션

이 레포를 동시에 만지는 모든 워커(세션·서브에이전트·페르소나)는 **각자의 git worktree** 로 격리한다(근거: [CONTEXT.md](CONTEXT.md)).

- `git worktree add ../ai-sdlc-skills-<slug> -b <type>/issue-<N>` — 1세션 = 1worktree = 1이슈 = 1브랜치.
- 정식 클론은 default 브랜치 미러(pull·읽기만). 거기서 `checkout`/`switch` **금지**.
- `git add` 는 명시 파일만 — 디렉터리·`-A` 금지.
- `git status` 에 내가 만들지 않은 변경이 보이면 진행 전에 병렬 세션 여부부터 확인.
- 병렬 서브에이전트가 파일을 동시에 수정하면 `isolation: "worktree"` 필수.
- 머지 후 worktree 제거 + 로컬 브랜치 삭제를 그 자리에서 수행.
- worktree 오케스트레이터(예: Orca) 사용 시 생성·정리는 도구에 위임, 수동 `worktree add/remove` 금지.
