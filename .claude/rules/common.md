# 공통 규칙 (ai-sdlc-skills)

P0/P1/P2 **규칙 목록의 정본은 [`AGENTS.md`](../../AGENTS.md)** 다 — Codex 등 `.claude/` 를 로드하지 않는 하네스도 절대 규칙에 닿아야 하므로 그 문서가 자체 완결이어야 한다(근거: `CONTEXT.md`).
이 파일은 그 규칙을 **되풀이하지 않고**, 자동 강제 범위·한계·판단 기준만 보충한다. 규칙 자체를 바꾸려면 `AGENTS.md` 를 고친다.

## 자동 강제 vs 규율

- 자동 차단은 `.claude/hooks/pre-commit.sh` 하나뿐(`settings.json` 의 `PreToolUse(Bash)` 에 배선). 그 외 P0/P1 은 전부 **규율**이며, `tests/test.sh` 를 직접 돌려야 확인된다.
- **훅의 보장 범위**: Bash 도구가 실행하려는 명령줄을 파싱해 **실제 커밋 대상 저장소**의 index 를 검사한다 — `git -C <repo>` 커밋, `cd <repo> &&` 후의 커밋, 대상이 `CLAUDE_PROJECT_DIR` 인 일반 커밋 모두. `.env`/`.env.*` 가 staged 면 exit 2 로 차단하고, `-a`/`-am` 은 tracked 수정본까지 함께 본다.
- **fail closed**: 대상 저장소를 안전하게 판별할 수 없으면 커밋을 거부한다(exit 2) — 변수·명령치환이 섞인 경로, `--git-dir`/`--work-tree`/`GIT_DIR` 류 index 재배치, 존재하지 않는 디렉터리, 저장소가 아닌 경로, 훅 payload 파싱 실패.
- **한계(우회 가능)**: ① Bash 도구를 거치지 않는 커밋(IDE·별도 터미널·MCP) ② 이전 Bash 호출에서 바뀐 세션 작업 디렉터리 — 훅은 세션 cwd 를 알 수 없어 `CLAUDE_PROJECT_DIR` 를 기준으로 삼는다 ③ 커밋으로 확장되는 git alias·래퍼 스크립트 ④ `.env` 이름을 쓰지 않는 시크릿 파일.
- **오탐**: 훅은 Bash 명령줄 전체를 훑으므로 heredoc 본문처럼 커밋과 무관한 텍스트에 커밋 명령 문자열이 섞여 있으면 fail closed 로 막힌다. 그런 파일은 Bash heredoc 대신 파일 쓰기 도구로 만든다. 회귀 테스트는 `tests/test_hook.sh`.
- **문서-코드 동기화**는 `tests/test_harness.sh` 가 강제한다 — 스킬이 `docs/REFERENCE.md`·`skills/README.md` 에 빠지거나 저장소 마크다운의 상대 링크가 깨지면 실패한다.

## 이 저장소에 적용되지 않는 규칙

- **배포 전 버전 bump**: 소비자 저장소용 규율이다. 이 저장소에는 버전 매니페스트(`package.json`/`pyproject.toml`/`Cargo.toml`/`build.gradle`)도 배포 파이프라인도 없으므로 대상이 아니다. 매니페스트가 생기는 순간 `AGENTS.md` P1 에 올린다.

## 소통

- 대화형 응답은 가벼운 구어체. **코드·커밋·이슈/PR 본문·문서는 표준/전문 톤** 유지.
- 상태 질문엔 yes/no + 짧은 근거. 디버깅은 실제 에러 원문 먼저 확보 후 행동.
- 부수효과 큰 작업(DB write·push·배포)은 사용자 명시 실행 신호 후 시작. `AGENTS.md` 의 "git 동사 즉시 실행" 은 그 명시 명령 자체를 가리키므로 예외가 아니다.

## 코드 탐색

- 레포 루트에 `.codegraph/` 디렉터리(CodeGraph 사전 인덱싱 지식 그래프)가 있으면, 코드 위치 파악·이해에는 grep/find/파일 순회보다 `codegraph explore "<심볼 또는 질문>"`(또는 `codegraph` MCP 도구)을 우선한다. `.codegraph/` 가 없으면 건너뜀 — 인덱싱 여부는 사용자 결정.

## 메모리

- SSOT는 `.claude/memory/`. 타입접두 `project_`/`feedback_`/`reference_`/`user_`. 자세히는 `memory/README.md`.
- `user_*.md` 만 개인(gitignore), 그 외 팀 공유. 구조 위반은 `tests/test_harness.sh` 가 차단한다.
