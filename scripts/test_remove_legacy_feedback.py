import json
import tempfile
import unittest
from contextlib import redirect_stderr, redirect_stdout
from io import StringIO
from pathlib import Path

from remove_legacy_feedback import cleanup


class CleanupTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.home = Path(self.temp.name) / "user"
        self.home.mkdir()
        self.repo = Path(self.temp.name) / "repo"
        self.repo.mkdir()
        self.settings = self.home / ".claude" / "settings.json"
        self.retired_skill = self.repo / "skills" / "engineering" / "skill-feedback"

    def run_cleanup(self):
        with redirect_stdout(StringIO()), redirect_stderr(StringIO()) as errors:
            cleanup(self.home, self.repo)
        return errors.getvalue()

    def write_settings(self, value):
        self.settings.parent.mkdir(parents=True, exist_ok=True)
        self.settings.write_text(json.dumps(value))

    def test_fresh_install_creates_no_settings_or_identity(self):
        self.run_cleanup()
        self.assertEqual(list(self.home.iterdir()), [])

    def test_removes_old_and_current_hooks_preserving_unrelated_settings(self):
        old_command = 'python3 "$HOME/.claude/skills/skill-feedback/scripts/skill-event.py" --skill auto --action skill_read --agent-harness claude-code --quiet'
        current_command = 'python3 "$HOME/.claude/skills/skill-feedback/scripts/skill-event.py" --skill auto --event skill_read --agent-harness claude-code --quiet'
        unrelated = {"type": "command", "command": "python3 local-audit.py", "timeout": 20}
        same_name_elsewhere = {"type": "command", "command": "python3 /another/skill-event.py"}
        value = {
            "permissions": {"allow": ["Read"]},
            "hooks": {
                "SessionStart": [{"hooks": [unrelated]}],
                "PostToolUse": [
                    {"matcher": "Read", "hooks": [{"type": "command", "command": old_command}]},
                    {"matcher": "Read", "timeout": 30, "hooks": [unrelated, {"type": "command", "command": current_command}]},
                    {"matcher": "Bash", "hooks": [same_name_elsewhere]},
                    {"matcher": "Write", "hooks": []},
                ],
            },
        }
        self.write_settings(value)
        self.settings.chmod(0o600)
        self.run_cleanup()
        value["hooks"]["PostToolUse"] = [
            {"matcher": "Read", "timeout": 30, "hooks": [unrelated]},
            {"matcher": "Bash", "hooks": [same_name_elsewhere]},
            {"matcher": "Write", "hooks": []},
        ]
        self.assertEqual(json.loads(self.settings.read_text()), value)
        self.assertEqual(self.settings.stat().st_mode & 0o777, 0o600)
        contents = self.settings.read_bytes()
        modified = self.settings.stat().st_mtime_ns
        self.run_cleanup()
        self.assertEqual(self.settings.read_bytes(), contents)
        self.assertEqual(self.settings.stat().st_mtime_ns, modified)

    def test_removes_empty_owned_hook_containers(self):
        self.write_settings({
            "theme": "dark",
            "hooks": {"PostToolUse": [{"matcher": "Read", "hooks": [{
                "type": "command",
                "command": 'python3 "$HOME/.claude/skills/skill-feedback/scripts/skill-event.py" --skill auto --event skill_read --agent-harness claude-code --quiet',
            }]}]},
        })
        self.run_cleanup()
        self.assertEqual(json.loads(self.settings.read_text()), {"theme": "dark"})

    def test_preserves_invalid_or_unrecognized_settings(self):
        self.settings.parent.mkdir()
        for contents in ('{"hooks":', '[]', '{"hooks": []}', '{"hooks": {"PostToolUse": {}}}', '{"hooks": {"PostToolUse": [null, {"hooks": "custom"}]}}'):
            with self.subTest(contents=contents):
                self.settings.write_text(contents)
                self.run_cleanup()
                self.assertEqual(self.settings.read_text(), contents)

    def test_removes_dangling_links_owned_by_this_checkout(self):
        links = []
        for harness in (".claude", ".agents", ".codex"):
            link = self.home / harness / "skills" / "skill-feedback"
            link.parent.mkdir(parents=True)
            link.symlink_to(self.retired_skill)
            links.append(link)
        self.run_cleanup()
        self.assertTrue(all(not link.is_symlink() for link in links))

    def test_preserves_other_checkouts_and_regular_directories(self):
        foreign = self.home / ".claude" / "skills" / "skill-feedback"
        foreign.parent.mkdir(parents=True)
        foreign.symlink_to(Path(self.temp.name) / "other-checkout" / "skills" / "engineering" / "skill-feedback")
        custom = self.home / ".agents" / "skills" / "skill-feedback"
        custom.mkdir(parents=True)
        contents = custom / "SKILL.md"
        contents.write_text("User-managed skill")
        self.run_cleanup()
        self.assertTrue(foreign.is_symlink())
        self.assertEqual(contents.read_text(), "User-managed skill")

    def test_removes_only_retired_installation_identity(self):
        state = self.home / ".az-skills"
        state.mkdir()
        identity = state / "installation-id"
        identity.write_text("anonymous-test-id")
        preferences = state / "preferences.json"
        preferences.write_text("{}")
        self.run_cleanup()
        self.assertFalse(identity.exists())
        self.assertEqual(preferences.read_text(), "{}")


if __name__ == "__main__":
    unittest.main()
