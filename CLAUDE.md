# SamsungLions — Claude Code 진입 지침

Claude Code는 다음 `@path` 가져오기로 공통 맥락을 읽습니다. 실제 세션 훅은 `.claude/settings.json`에 별도로 있습니다.

@AGENTS.md
@domain/CONTEXT.md
@domain/ROLES.md
@domain/PROJECTS.md
@STATUS.md

- 현재 역할 및 프로젝트는 세션에서 명시적으로 지정된 경우에만 배정된 것으로 취급합니다.
- 새 세션·재개·압축·포크 및 서브에이전트 시작에서 `[SL-CONTEXT]` 표식과 선택된 역할·프로젝트를 확인합니다.
- 훅이 지원되지 않는 웹 환경에서는 [웹 시작 패킷](domain/WEB_BOOTSTRAP.md)을 사용해 정본 문서를 직접 읽습니다.
