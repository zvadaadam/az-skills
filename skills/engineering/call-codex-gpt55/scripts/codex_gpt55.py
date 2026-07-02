#!/usr/bin/env python3
"""Run Codex CLI with GPT-5.5 high-effort defaults."""

from __future__ import annotations

import argparse
from datetime import datetime, timezone
import json
import os
from pathlib import Path
import shlex
import subprocess
import sys
from typing import Any


EFFORTS = ("low", "medium", "high", "xhigh", "max")
SANDBOXES = ("read-only", "workspace-write", "danger-full-access")
APPROVAL_POLICIES = ("untrusted", "on-request", "never")
STATE_KEY = "codex-gpt55"


def state_path() -> Path:
    override = os.environ.get("AI_AGENT_SESSIONS_PATH")
    if override:
        return Path(override).expanduser()
    codex_home = Path(os.environ.get("CODEX_HOME", Path.home() / ".codex")).expanduser()
    return codex_home / "external-agent-sessions.json"


def output_root() -> Path:
    override = os.environ.get("AI_AGENT_OUTPUT_DIR")
    if override:
        return Path(override).expanduser()
    codex_home = Path(os.environ.get("CODEX_HOME", Path.home() / ".codex")).expanduser()
    return codex_home / "external-agent-outputs"


def timestamp_slug() -> str:
    return datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")


def load_state() -> dict[str, Any]:
    path = state_path()
    if not path.exists():
        return {}
    try:
        data = json.loads(path.read_text())
    except (OSError, json.JSONDecodeError):
        return {}
    return data if isinstance(data, dict) else {}


def write_artifact(
    *,
    cmd: list[str],
    prompt: str | None,
    stdout: str,
    stderr: str,
    returncode: int,
    summary: dict[str, Any],
) -> Path:
    run_id = summary.get("thread_id") or "no-thread"
    artifact_dir = output_root() / STATE_KEY / f"{timestamp_slug()}-{run_id}"
    artifact_dir.mkdir(parents=True, exist_ok=True)
    (artifact_dir / "prompt.txt").write_text(prompt or "")
    (artifact_dir / "stdout.jsonl").write_text(stdout)
    (artifact_dir / "stderr.txt").write_text(stderr)
    payload = {
        "worker": STATE_KEY,
        "created_at": datetime.now(timezone.utc).isoformat(),
        "cwd": os.getcwd(),
        "command": cmd,
        "returncode": returncode,
        "summary": summary,
        "prompt_path": str(artifact_dir / "prompt.txt"),
        "stdout_path": str(artifact_dir / "stdout.jsonl"),
        "stderr_path": str(artifact_dir / "stderr.txt"),
    }
    summary_path = artifact_dir / "summary.json"
    summary_path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n")
    return summary_path


def save_last_thread(
    thread_id: str,
    summary: dict[str, Any],
    *,
    output_path: Path | None = None,
) -> None:
    if not thread_id:
        return
    path = state_path()
    state = load_state()
    worker = state.setdefault(STATE_KEY, {})
    entry = {
        "thread_id": thread_id,
        "cwd": os.getcwd(),
        "updated_at": datetime.now(timezone.utc).isoformat(),
        "model": summary.get("model") or "gpt-5.5",
        "usage": summary.get("usage"),
    }
    if output_path:
        entry["output_path"] = str(output_path)
        entry["artifact_dir"] = str(output_path.parent)
    worker["last"] = entry
    worker.setdefault("by_cwd", {})[os.getcwd()] = entry
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(state, indent=2, sort_keys=True) + "\n")


def last_thread(cwd_first: bool = True) -> dict[str, Any] | None:
    worker = load_state().get(STATE_KEY)
    if not isinstance(worker, dict):
        return None
    if cwd_first:
        by_cwd = worker.get("by_cwd")
        if isinstance(by_cwd, dict):
            entry = by_cwd.get(os.getcwd())
            if isinstance(entry, dict) and entry.get("thread_id"):
                return entry
    entry = worker.get("last")
    if isinstance(entry, dict) and entry.get("thread_id"):
        return entry
    return None


def print_last_thread() -> int:
    entry = last_thread(cwd_first=True)
    if not entry:
        print(json.dumps({"thread_id": None, "state_path": str(state_path())}, indent=2))
        return 1
    print(json.dumps({"state_path": str(state_path()), **entry}, indent=2, sort_keys=True))
    return 0


def shell_join(cmd: list[str]) -> str:
    return " ".join(shlex.quote(part) for part in cmd)


def toml_string(value: str) -> str:
    escaped = value.replace("\\", "\\\\").replace('"', '\\"')
    return f'"{escaped}"'


def prompt_from_args(prompt: str | None) -> str:
    if prompt is not None:
        return prompt
    if sys.stdin.isatty():
        raise SystemExit("Provide a prompt argument or pipe prompt text on stdin.")
    prompt = sys.stdin.read().strip()
    if not prompt:
        raise SystemExit("Prompt from stdin was empty.")
    return prompt


def add_config(cmd: list[str], key: str, value: str) -> None:
    cmd.extend(["--config", f"{key}={toml_string(value)}"])


def add_common_exec_options(cmd: list[str], args: argparse.Namespace) -> None:
    cmd.extend(["--model", args.model])
    add_config(cmd, "model_reasoning_effort", args.effort)
    add_config(cmd, "approval_policy", args.approval_policy)

    if getattr(args, "skip_git_repo_check", False):
        cmd.append("--skip-git-repo-check")
    if getattr(args, "ephemeral", False):
        cmd.append("--ephemeral")
    if getattr(args, "ignore_user_config", False):
        cmd.append("--ignore-user-config")
    if getattr(args, "strict_config", False):
        cmd.append("--strict-config")
    if getattr(args, "output_schema", None):
        cmd.extend(["--output-schema", args.output_schema])
    if getattr(args, "output_last_message", None):
        cmd.extend(["--output-last-message", args.output_last_message])
    if getattr(args, "json", True):
        cmd.append("--json")
    for image in getattr(args, "image", []) or []:
        cmd.extend(["--image", image])
    for key_value in getattr(args, "config", []) or []:
        cmd.extend(["--config", key_value])


def build_run_command(args: argparse.Namespace) -> tuple[list[str], str]:
    prompt = prompt_from_args(args.prompt)
    cmd = [args.codex_bin, "exec", "-"]
    add_common_exec_options(cmd, args)
    cmd.extend(["--sandbox", args.sandbox])

    if args.cd:
        cmd.extend(["--cd", args.cd])
    for directory in args.add_dir:
        cmd.extend(["--add-dir", directory])
    if args.ignore_rules:
        cmd.append("--ignore-rules")
    if args.dangerously_bypass_approvals_and_sandbox:
        cmd.append("--dangerously-bypass-approvals-and-sandbox")

    return cmd, prompt


def build_resume_command(args: argparse.Namespace) -> tuple[list[str], str | None]:
    cmd = [args.codex_bin, "exec", "resume"]
    if (args.saved_last or args.last) and args.thread_id and args.prompt is None:
        args.prompt = args.thread_id
        args.thread_id = None
    selected = sum(bool(value) for value in (args.saved_last, args.last, args.thread_id))
    if selected != 1:
        raise SystemExit("Use exactly one of THREAD_ID, --last, or --saved-last.")
    if args.saved_last:
        entry = last_thread(cwd_first=not args.global_last)
        if not entry:
            if not args.dry_run:
                raise SystemExit(f"No saved {STATE_KEY} thread found at {state_path()}.")
            cmd.append("SAVED_LAST_THREAD_ID")
        else:
            cmd.append(entry["thread_id"])
    elif args.last:
        cmd.append("--last")
    elif args.thread_id:
        cmd.append(args.thread_id)

    prompt = None
    if args.prompt is not None:
        cmd.append("-")
        prompt = args.prompt
    elif not sys.stdin.isatty():
        prompt_text = sys.stdin.read().strip()
        if prompt_text:
            cmd.append("-")
            prompt = prompt_text

    add_common_exec_options(cmd, args)
    if args.all:
        cmd.append("--all")
    if args.dangerously_bypass_approvals_and_sandbox:
        cmd.append("--dangerously-bypass-approvals-and-sandbox")

    return cmd, prompt


def build_tui_command(args: argparse.Namespace) -> list[str]:
    cmd = [args.codex_bin]
    if args.prompt:
        cmd.append(args.prompt)
    cmd.extend(["--model", args.model])
    add_config(cmd, "model_reasoning_effort", args.effort)
    if args.cd:
        cmd.extend(["--cd", args.cd])
    for directory in args.add_dir:
        cmd.extend(["--add-dir", directory])
    cmd.extend(["--sandbox", args.sandbox])
    cmd.extend(["--ask-for-approval", args.approval_policy])
    if args.no_alt_screen:
        cmd.append("--no-alt-screen")
    if args.search:
        cmd.append("--search")
    for image in args.image:
        cmd.extend(["--image", image])
    for key_value in args.config:
        cmd.extend(["--config", key_value])
    return cmd


def parse_jsonl(stdout: str, stderr: str) -> dict[str, Any]:
    summary: dict[str, Any] = {
        "thread_id": None,
        "last_agent_message": None,
        "last_agent_message_chars": None,
        "usage": None,
        "warning_count": 0,
        "warnings_sample": [],
        "events_seen": 0,
    }

    def add_warning(stream_name: str, text: str) -> None:
        summary["warning_count"] += 1
        if len(summary["warnings_sample"]) < 5:
            summary["warnings_sample"].append({"stream": stream_name, "text": text})

    for stream_name, text in (("stdout", stdout), ("stderr", stderr)):
        for line in text.splitlines():
            stripped = line.strip()
            if not stripped:
                continue
            if not stripped.startswith("{"):
                add_warning(stream_name, stripped)
                continue
            try:
                event = json.loads(stripped)
            except json.JSONDecodeError:
                add_warning(stream_name, stripped)
                continue

            summary["events_seen"] += 1
            event_type = event.get("type")
            if event_type == "thread.started":
                summary["thread_id"] = event.get("thread_id")
            elif event_type == "item.completed":
                item = event.get("item") or {}
                if item.get("type") == "agent_message":
                    text = str(item.get("text") or "")
                    summary["last_agent_message"] = text[:4000]
                    summary["last_agent_message_chars"] = len(text)
            elif event_type == "turn.completed":
                summary["usage"] = event.get("usage")
            elif event_type in {"turn.failed", "error"}:
                summary["error"] = event

    if not summary["warning_count"]:
        summary.pop("warning_count")
        summary.pop("warnings_sample")
    return summary


def run_exec_command(
    cmd: list[str],
    *,
    prompt: str | None,
    dry_run: bool,
    raw: bool,
    save_output: bool,
) -> int:
    if dry_run:
        if prompt is None:
            print(shell_join(cmd))
        else:
            print(f"printf %s {shlex.quote(prompt)} | {shell_join(cmd)}")
        return 0

    completed = subprocess.run(
        cmd,
        input=prompt,
        text=True,
        capture_output=True,
        check=False,
    )

    summary = parse_jsonl(completed.stdout, completed.stderr)
    summary["returncode"] = completed.returncode
    model = None
    if "--model" in cmd:
        model_index = cmd.index("--model") + 1
        if model_index < len(cmd):
            model = cmd[model_index]
    if model:
        summary["model"] = model

    output_path = None
    if save_output:
        output_path = write_artifact(
            cmd=cmd,
            prompt=prompt,
            stdout=completed.stdout,
            stderr=completed.stderr,
            returncode=completed.returncode,
            summary=summary,
        )
        summary["output_path"] = str(output_path)
        summary["artifact_dir"] = str(output_path.parent)

    thread_id = summary.get("thread_id")
    if isinstance(thread_id, str):
        save_last_thread(thread_id, summary, output_path=output_path)

    if raw:
        if completed.stdout:
            print(completed.stdout, end="")
        if completed.stderr:
            print(completed.stderr, end="", file=sys.stderr)
        if output_path:
            print(f"\noutput_path: {output_path}", file=sys.stderr)
        return completed.returncode

    print(json.dumps(summary, indent=2, sort_keys=True))
    return completed.returncode


def run_passthrough(cmd: list[str], *, dry_run: bool) -> int:
    if dry_run:
        print(shell_join(cmd))
        return 0
    os.execvp(cmd[0], cmd)
    return 127


def add_shared_args(parser: argparse.ArgumentParser) -> None:
    parser.add_argument("--codex-bin", default="codex", help="Codex CLI executable.")
    parser.add_argument("--model", default="gpt-5.5", help="Codex model.")
    parser.add_argument(
        "--effort",
        default="high",
        choices=EFFORTS,
        help="Reasoning effort mapped to model_reasoning_effort.",
    )
    parser.add_argument(
        "--approval-policy",
        default="never",
        choices=APPROVAL_POLICIES,
        help="Approval policy config override.",
    )
    parser.add_argument(
        "--config",
        action="append",
        default=[],
        metavar="KEY=VALUE",
        help="Additional raw Codex config override.",
    )
    parser.add_argument("--image", action="append", default=[], help="Image to attach.")


def add_exec_args(parser: argparse.ArgumentParser) -> None:
    add_shared_args(parser)
    parser.add_argument(
        "--skip-git-repo-check",
        action=argparse.BooleanOptionalAction,
        default=True,
        help="Allow running outside a git repository.",
    )
    parser.add_argument("--ephemeral", action="store_true", help="Do not persist the session.")
    parser.add_argument("--ignore-user-config", action="store_true", help="Do not load config.toml.")
    parser.add_argument("--strict-config", action="store_true", help="Reject unknown config keys.")
    parser.add_argument("--output-schema", help="JSON schema file for the final response.")
    parser.add_argument("-o", "--output-last-message", help="Write final message to this file.")
    parser.add_argument("--json", action=argparse.BooleanOptionalAction, default=True)
    parser.add_argument("--raw", action="store_true", help="Print raw Codex output.")
    parser.add_argument("--dry-run", action="store_true", help="Print command without running.")
    parser.add_argument(
        "--save-output",
        action=argparse.BooleanOptionalAction,
        default=True,
        help="Save prompt, stdout/stderr, and summary to an artifact file.",
    )
    parser.add_argument(
        "--dangerously-bypass-approvals-and-sandbox",
        action="store_true",
        help="Pass Codex's dangerous bypass flag.",
    )


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    subparsers = parser.add_subparsers(dest="command", required=True)

    run_parser = subparsers.add_parser("run", help="Run codex exec with GPT-5.5 defaults.")
    run_parser.add_argument("prompt", nargs="?", help="Prompt text. Reads stdin when omitted.")
    add_exec_args(run_parser)
    run_parser.add_argument("--sandbox", default="read-only", choices=SANDBOXES)
    run_parser.add_argument("--cd", help="Working root for Codex.")
    run_parser.add_argument("--add-dir", action="append", default=[], help="Additional writable dir.")
    run_parser.add_argument("--ignore-rules", action="store_true", help="Ignore execpolicy rules.")

    resume_parser = subparsers.add_parser("resume", help="Resume codex exec by thread id.")
    resume_parser.add_argument("thread_id", nargs="?", help="Thread/session id to resume.")
    resume_parser.add_argument("prompt", nargs="?", help="Prompt text. Reads stdin when omitted.")
    add_exec_args(resume_parser)
    resume_parser.add_argument("--last", action="store_true", help="Resume most recent thread.")
    resume_parser.add_argument(
        "--saved-last",
        action="store_true",
        help="Resume the last wrapper-saved Codex thread.",
    )
    resume_parser.add_argument(
        "--global-last",
        action="store_true",
        help="With --saved-last, ignore cwd-specific state and use global latest.",
    )
    resume_parser.add_argument("--all", action="store_true", help="Disable cwd filtering.")

    tui_parser = subparsers.add_parser("tui", help="Launch interactive Codex CLI.")
    tui_parser.add_argument("prompt", nargs="?", help="Initial prompt.")
    add_shared_args(tui_parser)
    tui_parser.add_argument("--sandbox", default="workspace-write", choices=SANDBOXES)
    tui_parser.add_argument("--cd", help="Working root for Codex.")
    tui_parser.add_argument("--add-dir", action="append", default=[], help="Additional writable dir.")
    tui_parser.add_argument("--no-alt-screen", action="store_true")
    tui_parser.add_argument("--search", action="store_true")
    tui_parser.add_argument("--dry-run", action="store_true")

    doctor_parser = subparsers.add_parser("doctor", help="Run codex doctor.")
    doctor_parser.add_argument("--codex-bin", default="codex", help="Codex CLI executable.")
    doctor_parser.add_argument("--json", action="store_true", help="Request JSON doctor output.")
    doctor_parser.add_argument("--dry-run", action="store_true")

    last_parser = subparsers.add_parser("last", help="Print the last saved Codex thread.")
    last_parser.add_argument("--codex-bin", default="codex", help=argparse.SUPPRESS)

    return parser.parse_args()


def main() -> int:
    args = parse_args()
    if args.command == "run":
        cmd, prompt = build_run_command(args)
        return run_exec_command(
            cmd,
            prompt=prompt,
            dry_run=args.dry_run,
            raw=args.raw,
            save_output=args.save_output,
        )
    if args.command == "resume":
        cmd, prompt = build_resume_command(args)
        return run_exec_command(
            cmd,
            prompt=prompt,
            dry_run=args.dry_run,
            raw=args.raw,
            save_output=args.save_output,
        )
    if args.command == "tui":
        return run_passthrough(build_tui_command(args), dry_run=args.dry_run)
    if args.command == "doctor":
        cmd = [args.codex_bin, "doctor"]
        if args.json:
            cmd.append("--json")
        return run_passthrough(cmd, dry_run=args.dry_run)
    if args.command == "last":
        return print_last_thread()
    raise SystemExit(f"Unknown command: {args.command}")


if __name__ == "__main__":
    raise SystemExit(main())
