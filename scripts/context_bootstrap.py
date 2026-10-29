#!/usr/bin/env python3
"""Read-only SamsungLions context loader for CLI and agent lifecycle hooks."""
from __future__ import annotations

import argparse
import hashlib
import json
import os
from pathlib import Path
import re
import sys

ROOT = Path(__file__).resolve().parents[1]
ROLES = {"pln", "rsch", "pmo"}
NAME_RE = re.compile(r"^[a-z0-9][a-z0-9_-]{0,63}$")
BASE_DOCS = (
    "AGENTS.md",
    "domain/CONTEXT.md",
    "domain/ROLES.md",
    "domain/PROJECTS.md",
    "STATUS.md",
    "projects/README.md",
)
PROJECT_DOCS = ("CURRENT.md", "PLAN.md", "DECISIONS.md")
MAX_DOC_CHARS = 16000
MAX_TOTAL_CHARS = 50000


class ContextError(Exception):
    pass


def _name(value: str | None, kind: str) -> str | None:
    if value is None or value == "":
        return None
    if not NAME_RE.fullmatch(value):
        raise ContextError(f"Invalid {kind}: {value!r}; expected a simple lowercase ID")
    if kind == "role" and value not in ROLES:
        raise ContextError(f"Unknown role: {value}; expected pln, rsch, or pmo")
    return value


def _from_cwd(root: Path, cwd: Path | None) -> tuple[str | None, str | None]:
    if cwd is None:
        return None, None
    try:
        parts = cwd.resolve().relative_to(root.resolve()).parts
    except (ValueError, OSError):
        return None, None
    if len(parts) < 2 or parts[0] != "projects" or not NAME_RE.fullmatch(parts[1]):
        return None, None
    project = parts[1]
    role = parts[3] if len(parts) >= 4 and parts[2] == "roles" and parts[3] in ROLES else None
    return project, role


def _read(root: Path, rel: str) -> str:
    candidate = (root / rel).resolve()
    if not candidate.is_relative_to(root.resolve()):
        raise ContextError(f"Document path escapes repository: {rel}")
    if not candidate.is_file():
        raise ContextError(f"Required document not found: {rel}")
    try:
        content = candidate.read_text(encoding="utf-8")
    except (OSError, UnicodeError) as exc:
        raise ContextError(f"Cannot read {rel}: {exc}") from exc
    if len(content) > MAX_DOC_CHARS:
        raise ContextError(f"Document exceeds injection budget: {rel}")
    return content


def _registered_projects(index: str) -> set[str]:
    result: set[str] = set()
    for line in index.splitlines():
        if not line.strip().startswith("|"):
            continue
        cells = [c.strip().strip(chr(96)) for c in line.strip().strip("|").split("|")]
        if len(cells) < 4:
            continue
        match = re.fullmatch(r"projects/([a-z0-9][a-z0-9_-]{0,63})/", cells[2])
        if match and cells[0] == match.group(1):
            result.add(match.group(1))
    return result


def build_context(
    root: Path,
    *,
    project: str | None = None,
    role: str | None = None,
    cwd: Path | None = None,
    environment: dict[str, str] | None = None,
) -> dict[str, object]:
    root = root.resolve()
    env = os.environ if environment is None else environment
    cwd_project, cwd_role = _from_cwd(root, cwd)
    env_project = _name(env.get("SL_PROJECT"), "project")
    env_role = _name(env.get("SL_ROLE"), "role")
    if project is None and env_project and cwd_project and env_project != cwd_project:
        raise ContextError(
            f"Project selection conflict: environment={env_project}, directory={cwd_project}"
        )
    if role is None and env_role and cwd_role and env_role != cwd_role:
        raise ContextError(
            f"Role selection conflict: environment={env_role}, directory={cwd_role}"
        )
    project = _name(project or env_project or cwd_project, "project")
    role = _name(role or env_role or cwd_role, "role")

    documents: list[tuple[str, str]] = [(path, _read(root, path)) for path in BASE_DOCS]
    registered = _registered_projects(dict(documents)["domain/PROJECTS.md"])

    if project:
        if project not in registered:
            raise ContextError(f"Project {project!r} is not listed in domain/PROJECTS.md")
        for filename in PROJECT_DOCS:
            path = f"projects/{project}/{filename}"
            documents.append((path, _read(root, path)))

    if sum(len(content) for _, content in documents) > MAX_TOTAL_CHARS:
        raise ContextError("Total context exceeds injection budget; split or shorten source docs")

    h = hashlib.sha256()
    for path, content in documents:
        h.update(path.encode("utf-8") + b"\x00")
        h.update(content.encode("utf-8") + b"\x00")
    digest = h.hexdigest()
    label_role = role or "unassigned"
    label_project = project or "unassigned"
    lines = [
        "[SL-CONTEXT v0.2] Source-backed session context",
        f"domain=samsung_lions; role={label_role}; project={label_project}",
        f"context_sha256={digest}",
        "all_roles=pln(total lead), rsch(research), pmo(general producer)",
        "registered_projects=" + (", ".join(sorted(registered)) or "(none)"),
        "Agent must not claim a role/project assignment unless explicitly selected.",
        "Before project edits, confirm CURRENT/PLAN/DECISIONS and relevant board tasks.",
        "An injection receipt confirms file selection, not model comprehension or permission.",
    ]
    for path, content in documents:
        lines.extend((f"\n--- SOURCE: {path} ---", content))
    return {
        "domain": "samsung_lions",
        "role": label_role,
        "project": label_project,
        "registered_projects": sorted(registered),
        "digest": digest,
        "sources": [p for p, _ in documents],
        "text": "\n".join(lines),
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Build verified SamsungLions session context.")
    parser.add_argument("--role", choices=sorted(ROLES), help="Explicit role for this session")
    parser.add_argument("--project", help="Registered project ID")
    mode = parser.add_mutually_exclusive_group()
    mode.add_argument("--check", action="store_true", help="Validate files and show a receipt")
    mode.add_argument("--print", action="store_true", help="Show full context text (default)")
    mode.add_argument("--hook", action="store_true", help="Emit lifecycle hook JSON")
    args = parser.parse_args(argv)

    event: dict[str, object] = {}
    event_name = "SessionStart"
    if args.hook:
        try:
            raw = sys.stdin.read(65536)
            event = json.loads(raw) if raw.strip() else {}
            if not isinstance(event, dict):
                raise ValueError("hook input must be a JSON object")
            candidate = event.get("hook_event_name")
            if candidate in ("SessionStart", "SubagentStart"):
                event_name = candidate
        except (ValueError, UnicodeError) as exc:
            msg = f"[SL-CONTEXT FAILED] Invalid hook event: {exc}. Do not start project writes."
            print(json.dumps({"systemMessage": msg, "hookSpecificOutput": {
                "hookEventName": event_name, "additionalContext": msg
            }}, ensure_ascii=False))
            return 0

    cwd = event.get("cwd") if args.hook else os.getcwd()
    try:
        context = build_context(
            ROOT,
            role=args.role,
            project=args.project,
            cwd=Path(cwd) if isinstance(cwd, str) else None,
        )
    except ContextError as exc:
        msg = f"[SL-CONTEXT FAILED] {exc}. Stop project writes and fix source/selection."
        if args.hook:
            print(json.dumps({"systemMessage": msg, "hookSpecificOutput": {
                "hookEventName": event_name, "additionalContext": msg
            }}, ensure_ascii=False))
            return 0
        print(msg, file=sys.stderr)
        return 2

    if args.check:
        print(f"OK [SL-CONTEXT] domain={context['domain']} role={context['role']} "
              f"project={context['project']} sha256={context['digest']}")
        for name in context["sources"]:
            print(f"  {name}")
    elif args.hook:
        print(json.dumps({"hookSpecificOutput": {
            "hookEventName": event_name, "additionalContext": context["text"]
        }}, ensure_ascii=False))
    else:
        print(context["text"])
    return 0


if __name__ == "__main__":
    sys.exit(main())
