# SamsungLions Workspace

친구와 각자의 AI가 함께 기획하고 사진·소설·음악·아이 교육자료 등 작업물을 만들고 관리하는 범용 공간입니다.

| 영역 | 용도 |
| --- | --- |
| [projects/](projects/) | 프로젝트 목표·상태·작업·결정 |
| [works/](works/) | 실제 창작물과 교육자료 |
| [apps/](apps/) | 필요할 때 추가할 앱·도구·AI 스킬 |
| [shared/](shared/) | 공통 참고자료·템플릿 |
| [domain/](domain/CONTEXT.md) | 전체 맥락·역할·프로젝트 등록부 |

## AI와 시작하기

- **전역 역할:** 총괄(PLN), 연구(RSCH), 범용 작업자(PMO) — [역할 등록부](domain/ROLES.md)
- **전체 프로젝트 목록:** [프로젝트 등록부](domain/PROJECTS.md)
- **공통 지침:** [AGENTS.md](AGENTS.md), Claude Code용 [CLAUDE.md](CLAUDE.md)
- **세션/런타임 주입:** [주입·검증 안내](domain/INJECTION.md)
- **웹 ChatGPT:** [웹 세션 시작 패킷](domain/WEB_BOOTSTRAP.md) 사용
- **전체 현황:** [STATUS.md](STATUS.md)

새 프로젝트는 `domain/PROJECTS.md`에 등록하고 `projects/<id>/CURRENT.md`·`PLAN.md`·`DECISIONS.md`를 갖춥니다. 작품은 `works/`, 실행 가능한 앱·스킬은 `apps/`에 보관하고 프로젝트 문서에서 연결합니다.

로컬 Claude Code/Codex 훅을 사용하려면 **Python 3과 실행기에서의 훅 신뢰·승인**이 필요합니다. 이 저장소만 연결한 웹 ChatGPT에서는 훅이 자동 실행되지 않습니다.

> 저장소는 현재 **Public**입니다. 아이 사진·개인정보·비공개 창작물·토큰·비밀 키 등은 올리지 마세요. 대용량 미디어는 Git LFS 또는 별도 저장소를 검토하세요.
