# memory/ — 프로젝트 메모리

- `MEMORY.md` 가 유일한 인덱스. 메모리 1개 = 파일 1개(frontmatter `name`/`description`/`metadata.type`).
- 타입 접두: `project_`(진행·제약) / `feedback_`(작업 방식, 왜+적용법) / `reference_`(외부 포인터) / `user_`(개인, gitignore).
- 단정형 사실(임계값·이슈 번호·활성 플래그)은 날짜를 박고, 행동 전 code/git/이슈로 재검증한다. 낡은 메모리는 `archive/` 로 옮기고 인덱스에서 뺀다.
- 다른 프로젝트의 메모리를 복사해 오지 않는다 (2026-08-25 #14: 존재하지 않는 이슈·파일을 서술하던 3개 파일 제거).
