"""Offline tests for read-only context selection and lifecycle payloads."""
from pathlib import Path
import json
import subprocess
import sys
import tempfile
import unittest

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO / "scripts"))
import context_bootstrap as cb


class ContextTests(unittest.TestCase):
    def test_real_domain_loads_without_project(self):
        ctx = cb.build_context(REPO, environment={})
        self.assertEqual(ctx["role"], "unassigned")
        self.assertEqual(ctx["project"], "unassigned")
        self.assertIn("domain/ROLES.md", ctx["sources"])
        self.assertIn("domain/PROJECTS.md", ctx["sources"])
        self.assertIn("all_roles=pln", ctx["text"])

    def test_three_roles_validate(self):
        for role in ("pln", "rsch", "pmo"):
            self.assertEqual(cb.build_context(REPO, role=role, environment={})["role"], role)
        with self.assertRaises(cb.ContextError):
            cb.build_context(REPO, role="arch", environment={})

    def test_unregistered_project_rejected(self):
        with self.assertRaises(cb.ContextError):
            cb.build_context(REPO, project="unregistered", environment={})
        with self.assertRaises(cb.ContextError):
            cb.build_context(REPO, project="../unsafe", environment={})

    def test_project_requires_all_docs_and_registry(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            for rel in cb.BASE_DOCS:
                path = root / rel
                path.parent.mkdir(parents=True, exist_ok=True)
                path.write_text("# base\n", encoding="utf-8")
            (root / "domain/PROJECTS.md").write_text(
                "| ID | Project | Path | State |\n"
                "| --- | --- | --- | --- |\n"
                "| demo | Demo | " + chr(96) + "projects/demo/" + chr(96) + " | Active |\n",
                encoding="utf-8",
            )
            project_dir = root / "projects/demo"
            project_dir.mkdir(parents=True)
            for rel in cb.PROJECT_DOCS[:-1]:
                (project_dir / rel).write_text("# " + rel, encoding="utf-8")
            with self.assertRaises(cb.ContextError):
                cb.build_context(root, project="demo", environment={})
            (project_dir / "DECISIONS.md").write_text("# None yet", encoding="utf-8")
            ctx = cb.build_context(root, cwd=project_dir / "roles/pmo", environment={})
            self.assertEqual((ctx["project"], ctx["role"]), ("demo", "pmo"))
            self.assertIn("projects/demo/CURRENT.md", ctx["sources"])
            original = ctx["digest"]
            (project_dir / "CURRENT.md").write_text("# Updated", encoding="utf-8")
            self.assertNotEqual(original, cb.build_context(root, project="demo", environment={})["digest"])

    def test_selection_conflicts_are_rejected(self):
        with self.assertRaisesRegex(cb.ContextError, "Project selection conflict"):
            cb.build_context(
                REPO,
                cwd=REPO / "projects/album/roles/pln",
                environment={"SL_PROJECT": "education"},
            )
        with self.assertRaisesRegex(cb.ContextError, "Role selection conflict"):
            cb.build_context(
                REPO,
                cwd=REPO / "projects/album/roles/pln",
                environment={"SL_ROLE": "pmo"},
            )

    def test_registry_and_hooks_are_consistent(self):
        registered = cb._registered_projects(
            (REPO / "domain/PROJECTS.md").read_text(encoding="utf-8")
        )
        local_projects = {
            path.name for path in (REPO / "projects").iterdir()
            if path.is_dir() and not path.name.startswith(".")
        }
        self.assertEqual(registered, local_projects)
        for project in registered:
            for filename in cb.PROJECT_DOCS:
                self.assertTrue((REPO / "projects" / project / filename).is_file())
        for filename in (".claude/settings.json", ".codex/hooks.json"):
            data = json.loads((REPO / filename).read_text(encoding="utf-8"))
            self.assertIn("SessionStart", data["hooks"])
            self.assertIn("SubagentStart", data["hooks"])
            group = data["hooks"]["SessionStart"][0]
            for trigger in ("startup", "resume", "compact", "clear", "fork"):
                self.assertIn(trigger, group["matcher"])
            self.assertIn("context_bootstrap.py", group["hooks"][0]["command"])

    def test_hook_json(self):
        payload = json.dumps({"hook_event_name": "SubagentStart", "cwd": str(REPO)})
        call = subprocess.run(
            [sys.executable, str(REPO / "scripts/context_bootstrap.py"), "--hook"],
            input=payload, capture_output=True, text=True, check=True,
        )
        data = json.loads(call.stdout)
        self.assertEqual(data["hookSpecificOutput"]["hookEventName"], "SubagentStart")
        self.assertIn("[SL-CONTEXT v0.2]", data["hookSpecificOutput"]["additionalContext"])

    def test_bad_project_hook_reports_failure(self):
        payload = json.dumps({"hook_event_name": "SessionStart", "cwd": str(REPO)})
        call = subprocess.run(
            [sys.executable, str(REPO / "scripts/context_bootstrap.py"), "--hook"],
            input=payload, capture_output=True, text=True, check=True,
            env={"SL_PROJECT": "missing"},
        )
        data = json.loads(call.stdout)
        self.assertIn("[SL-CONTEXT FAILED]", data["hookSpecificOutput"]["additionalContext"])


if __name__ == "__main__":
    unittest.main()
