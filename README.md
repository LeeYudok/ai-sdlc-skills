# ai-sdlc-skills

운영 중인 기존 저장소에서 한 줄 버그 수정·기능 요청을 분석, BA 문서화, 전체 영향도 평가,
명세, 구현, QA, 로컬 배포, 운영 배포 준비까지 추적 가능한 파이프라인으로 처리하는 Codex
스킬 모음이다.

## 파이프라인

```text
요청
  → 저장소 분석
  → 다중 도구 증거 교차검증
  → BA 문서
  → 전체 영향도
  → 기능 명세
  → 구현
  → QA
  → 로컬 배포·스모크 테스트
  → 무중단 배포 준비
```

각 실행은 소비자 저장소의 `.ai-sdlc/runs/<run>/`에 상태와 근거 문서를 남긴다.
배포 준비 완료는 실제 배포 승인이 아니며, 운영 배포·실거래·프로덕션 데이터 변경은
사용자의 별도 명시 승인이 필요하다.

파이프라인 완료 후, 사용자가 요청하면 선택적으로 `ai-sdlc-skills-commit`(로컬 커밋)과
`ai-sdlc-skills-pr`(PR/MR 오픈)을 실행한다 — 둘 다 게이트 상태머신 밖의 독립 단계이며
자동으로 커밋·푸시·머지하지 않는다.

긴 실행이 한 세션의 컨텍스트 윈도우를 넘길 때는 `ai-sdlc-skills-handoff`로
`HANDOFF.md` 상태 스냅샷(목표·현재 상태·결정·남은 일·함정·재개 절차)을 남기고
새 세션에서 그 문서부터 읽어 재개한다.

스킬별 입력/출력 한눈에 보려면 [docs/REFERENCE.md](docs/REFERENCE.md) 참고.

CodeGraph, Graphify, Code-Graph-RAG, OpenCodeReview가 설치되고 사용 승인을 받은 환경에서는
각 도구를 선택적으로 활용한다. 도구가 없어도 Git·소스·스키마·테스트 기반 폴백으로
파이프라인이 동작하며, 외부 전송이나 무거운 서비스 실행은 자동으로 활성화하지 않는다.

## 모델 공급자

doksam 환경에서는 사내 vLLM의 OpenAI-compatible endpoint를 사용한다.

```bash
export AI_SDLC_LLM_PROVIDER=vllm
export AI_SDLC_LLM_BASE_URL=<internal-url>
export AI_SDLC_LLM_MODEL=<served-model>
```

외부 사용자는 OpenAI API 키와 승인된 모델을 설정한다.

```bash
export AI_SDLC_LLM_PROVIDER=openai
export OPENAI_API_KEY=<secret>
export AI_SDLC_LLM_MODEL=<model>
```

키와 내부 URL은 저장소나 생성 문서에 기록하지 않는다. 모델 공급자가 없어도 로컬 분석,
결정적 검사, QA, 로컬 배포 단계는 동작한다.

## 대상 프로젝트에서 사용

```bash
cd /path/to/your-project

# 팀과 함께 커밋할 복사 설치
/path/to/ai-sdlc-skills/bin/install.sh . --mode copy

# 또는 스킬을 개발하며 즉시 반영하는 로컬 링크 설치
/path/to/ai-sdlc-skills/bin/install.sh . --mode link
```

Codex를 다시 시작한 뒤 자연어로 요청한다.

```text
주식자동매매 만들어줘
```

명시적으로 호출하려면:

```text
$ai-sdlc-skills-pipeline 주식자동매매 만들어줘
```

Codex가 저장소의 `.agents/skills`를 탐색하므로 설치 결과는
`your-project/.agents/skills/ai-sdlc-skills-*`에 위치한다.

## 검증

```bash
tests/test.sh
```
