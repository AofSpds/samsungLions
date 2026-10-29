# projects — 프로젝트 작업 공간

각 프로젝트의 목표·진행·작업·결정을 관리합니다. **전체 역할 정본은 [domain/ROLES.md](../domain/ROLES.md), 프로젝트 목록 정본은 [domain/PROJECTS.md](../domain/PROJECTS.md)**입니다.

## 프로젝트 기본형

~~~text
projects/
└── <project-name>/
    ├── CURRENT.md       # 지금 상태·담당·다음 할 일
    ├── PLAN.md          # 목표·범위·참여자·완료 기준
    ├── DECISIONS.md     # 사람이 확정한 결정
    ├── board/           # 실제 작업 요청이 생길 때 생성
    │   └── TASK-001.md
    └── roles/           # 별도 작업 구역이 필요할 때만
        ├── pln/
        ├── rsch/
        └── pmo/
~~~

- 처음부터 모든 하위 폴더를 만들 필요는 없지만, **프로젝트 등록 시 CURRENT/PLAN/DECISIONS 세 파일은 필수**입니다.
- 새 프로젝트를 승인받아 만들 때 [등록부](../domain/PROJECTS.md)에 ID·경로·상태를 등록합니다.
- 역할은 전역 3개(pln·rsch·pmo)로 고정합니다. 별도 roles/ 폴더는 실제 병렬 작업 기록을 분리할 때만 생성합니다.
- board/TASK-001.md에는 제목·요청자/담당·목표·상태(대기/진행/검토/완료)·산출물 경로·남은 일을 기록합니다.
- 연구가 필요 없으면 PLN → PMO로 바로 진행합니다. 상설 검증 역할은 없습니다.
- 창작물은 works/, 실행 앱·스킬은 apps/에 두고 프로젝트 문서에서 경로로 연결합니다.
- 런타임이 프로젝트 상세를 주입할 때 등록부 및 세 필수 파일이 모두 있어야 합니다.

현재 프로젝트는 등록된 것이 없습니다.
