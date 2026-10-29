# 도메인·세션·런타임 맥락 주입 계약 — Lite v0.2

목적: 어느 AI로 들어와도 도메인의 **세 역할 전부와 프로젝트 전체 목록**을 알도록 하고, 배정된 역할/프로젝트의 상세를 읽도록 한다.

## 구분

- **정본:** `domain/CONTEXT.md`, `domain/ROLES.md`, `domain/PROJECTS.md`, 각 프로젝트의 `CURRENT.md` 등.
- **정적 진입:** `AGENTS.md`(Codex), `CLAUDE.md`의 `@...` imports(Claude Code).
- **동적 진입:** `scripts/context_bootstrap.py`가 현재 정본을 읽고 SHA-256 지문과 함께 구성. 네트워크·쓰기 없음.
- **실행기 연결:** `.claude/settings.json`과 `.codex/hooks.json`의 SessionStart/SubagentStart. startup·resume·clear·compact·fork에서 재주입되도록 설계.
- **웹 ChatGPT/기타:** 저장소 훅이 자동 실행되지 않는다. [WEB_BOOTSTRAP.md](WEB_BOOTSTRAP.md)의 요청을 사용해 GitHub 읽기 결과를 세션 맥락으로 전달한다.

## 역할·프로젝트 선택

1. 런타임을 실행하기 **전에** 환경변수 `SL_ROLE=pln|rsch|pmo`, `SL_PROJECT=<등록 ID>`를 지정할 수 있다.
2. 환경변수가 없으면 프로젝트 하위 경로에서 시작한 경우에만 프로젝트를 추론하고, `roles/<role>` 하위에서 시작한 경우에만 역할을 추론한다.
3. 그 밖은 `unassigned`로 유지. 배정되지 않은 프로젝트의 `CURRENT.md`를 전부 불러오거나 역할을 지어내지 않는다.
4. 잘못된 프로젝트, 누락 파일, 등록부 불일치는 `CONTEXT FAILED`로 표시하고 해당 프로젝트 쓰기를 시작하지 않는다.

## 확인 방법 (Python 3 필요)

리포지토리 루트에서:

```sh
python scripts/context_bootstrap.py --check
python scripts/context_bootstrap.py --check --role rsch
python scripts/context_bootstrap.py --print
python -m unittest discover -s tests -v
```

프로젝트가 등록된 뒤:

```sh
python scripts/context_bootstrap.py --check --role pmo --project family-album
```

`--check`는 파일 경로와 **내용 지문**을 출력. `--print`는 실제 주입될 본문을 출력. `--hook`는 런타임이 넘기는 JSON을 표준입력으로 받아 `additionalContext`를 반환한다.

## 환경별 주의

- **Claude Code:** 저장소 `.claude/settings.json`을 사용. 프로젝트 훅은 사용자 환경에서 신뢰/승인이 필요할 수 있다. Python 실행 가능해야 한다.
- **Codex 로컬:** 저장소 `.codex/hooks.json`을 사용. 프로젝트 로컬 훅이 신뢰/활성화돼야 하며 `/hooks`에서 확인한다. Codex는 루트 `AGENTS.md`를 별도 읽는다.
- **웹 ChatGPT:** GitHub 커넥터만으로 시작 훅을 실행하거나 읽기 완료를 강제할 수 없다. 웹 부트스트랩 요청과 실제 소스 확인으로 처리한다.
- **모든 환경:** 훅 실행 실패·무시·중단, 세션 중 파일 변경, 도구 미지원 시 '주입 완료'가 아니다. SHA 지문과 세션의 확인 응답은 **내용 선택·전달을 확인할 수 있는 단서**일 뿐, 모델의 이해나 정책 준수를 증명하지 않는다.
- **실행 확인:** 처음 실행한 각 런타임에서 `[SL-CONTEXT]` 표식, 전체 역할 3개, 프로젝트 목록, 선택된 역할/프로젝트, source SHA를 실제 대화에서 확인한다. 편집 전 한 번 더 관련 프로젝트 문서를 대조한다.
- **보안:** 훅은 로컬 Python 코드를 실행한다. 신뢰할 수 있는 코드를 검토한 뒤 승인한다. 키·비밀번호·개인정보를 맥락 파일에 기록하지 않는다.
