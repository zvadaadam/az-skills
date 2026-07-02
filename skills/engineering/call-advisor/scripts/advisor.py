#!/usr/bin/env python3
"""Run the Fable advisor with explicit cost guardrails."""

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
STATE_KEY = "advisor"
LEGACY_STATE_KEYS = ("claude-fable",)


def state_path() -> Path:
    override = os.environ.get("AI_AGENT_SESSIONS_PATH")
    if override:
        return Path(override).expanduser()
    codex_home = Path(os.environ.get("CODEX_HOME", Path.home() / ".codex")).expanduser()
    return codex_home / "external-agent-sessions.json"


def load_state() -> dict[str, Any]:
    path = state_path()
    if not path.exists():
        return {}
    try:
        data = json.loads(path.read_text())
    except (OSError, json.JSONDecodeError):
        return {}
    return data if isinstance(data, dict) else {}


def output_root() -> Path:
    override = os.environ.get("AI_AGENT_OUTPUT_DIR")
    if override:
        return Path(override).expanduser()
    codex_home = Path(os.environ.get("CODEX_HOME", Path.home() / ".codex")).expanduser()
    return codex_home / "external-agent-outputs"


def timestamp_slug() -> str:
    return datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")


def write_artifact(
    *,
    cmd: list[str],
    stdout: str,
    stderr: str,
    returncode: int,
    summary: dict[str, Any],
) -> Path:
    run_id = summary.get("session_id") or "no-session"
    artifact_dir = output_root() / STATE_KEY / f"{timestamp_slug()}-{run_id}"
    artifact_dir.mkdir(parents=True, exist_ok=True)
    (artifact_dir / "stdout.txt").write_text(stdout)
    (artifact_dir / "stderr.txt").write_text(stderr)
    payload = {
        "agent": STATE_KEY,
        "created_at": datetime.now(timezone.utc).isoformat(),
        "cwd": os.getcwd(),
        "command": cmd,
        "returncode": returncode,
        "summary": summary,
        "stdout_path": str(artifact_dir / "stdout.txt"),
        "stderr_path": str(artifact_dir / "stderr.txt"),
    }
    summary_path = artifact_dir / "summary.json"
    summary_path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n")
    return summary_path


def save_last_session(
    session_id: str,
    payload: dict[str, Any],
    *,
    output_path: Path | None = None,
) -> None:
    if not session_id:
        return
    path = state_path()
    state = load_state()
    agent = state.setdefault(STATE_KEY, {})
    entry = {
        "session_id": session_id,
        "cwd": os.getcwd(),
        "updated_at": datetime.now(timezone.utc).isoformat(),
        "model": payload.get("model") or payload.get("model_name") or "fable",
        "is_error": payload.get("is_error"),
        "total_cost_usd": payload.get("total_cost_usd"),
        "stop_reason": payload.get("stop_reason"),
    }
    if output_path:
        entry["output_path"] = str(output_path)
        entry["artifact_dir"] = str(output_path.parent)
    agent["last"] = entry
    agent.setdefault("by_cwd", {})[os.getcwd()] = entry
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(state, indent=2, sort_keys=True) + "\n")


def last_session(cwd_first: bool = True) -> dict[str, Any] | None:
    state = load_state()
    for key in (STATE_KEY, *LEGACY_STATE_KEYS):
        agent = state.get(key)
        if not isinstance(agent, dict):
            continue
        if cwd_first:
            by_cwd = agent.get("by_cwd")
            if isinstance(by_cwd, dict):
                entry = by_cwd.get(os.getcwd())
                if isinstance(entry, dict) and entry.get("session_id"):
                    return {"state_key": key, **entry}
        entry = agent.get("last")
        if isinstance(entry, dict) and entry.get("session_id"):
            return {"state_key": key, **entry}
    return None


def print_last_session() -> int:
    entry = last_session(cwd_first=True)
    if not entry:
        print(json.dumps({"session_id": None, "state_path": str(state_path())}, indent=2))
        return 1
    print(json.dumps({"state_path": str(state_path()), **entry}, indent=2, sort_keys=True))
    return 0


def positive_budget(value: str) -> str:
    try:
        parsed = float(value)
    except ValueError as exc:
        raise argparse.ArgumentTypeError("budget must be a number") from exc
    if parsed <= 0:
        raise argparse.ArgumentTypeError("budget must be greater than zero")
    return value


def print_command(cmd: list[str]) -> None:
    print(" ".join(shlex.quote(part) for part in cmd))


def parse_output(stdout: str) -> tuple[dict[str, Any], dict[str, Any] | None, bool]:
    try:
        payload: Any = json.loads(stdout)
    except json.JSONDecodeError:
        return {"parsed": False}, None, False

    if not isinstance(payload, dict):
        return {"parsed": True, "result_type": type(payload).__name__}, None, True

    fields = {
        "parsed": True,
        "is_error": payload.get("is_error"),
        "api_error_status": payload.get("api_error_status"),
        "session_id": payload.get("session_id"),
        "total_cost_usd": payload.get("total_cost_usd"),
        "stop_reason": payload.get("stop_reason"),
        "terminal_reason": payload.get("terminal_reason"),
    }
    result = payload.get("result")
    if result:
        fields["result_preview"] = str(result)[:4000]
        fields["result_chars"] = len(str(result))
    return fields, payload, True


def prompt_from_args(prompt: str | None) -> str:
    if prompt is not None:
        return prompt
    if sys.stdin.isatty():
        raise SystemExit("Provide a prompt argument or pipe prompt text on stdin.")
    prompt = sys.stdin.read().strip()
    if not prompt:
        raise SystemExit("Prompt from stdin was empty.")
    return prompt


def build_run_command(args: argparse.Namespace) -> list[str]:
    prompt = prompt_from_args(args.prompt)
    if args.resume and args.resume_last:
        raise SystemExit("Use either --resume SESSION_ID or --resume-last, not both.")
    cmd = [
        args.claude_bin,
        "-p",
        prompt,
        "--model",
        args.model,
        "--effort",
        args.effort,
        "--max-budget-usd",
        args.max_budget_usd,
        "--output-format",
        args.output_format,
    ]

    if args.resume:
        cmd.extend(["--resume", args.resume])
    if args.resume_last:
        entry = last_session(cwd_first=not args.global_last)
        if not entry:
            if not args.dry_run:
                raise SystemExit(f"No saved {STATE_KEY} session found at {state_path()}.")
            cmd.extend(["--resume", "SAVED_LAST_SESSION_ID"])
        else:
            cmd.extend(["--resume", entry["session_id"]])
    if args.continue_latest:
        cmd.append("--continue")
    if args.fork_session:
        cmd.append("--fork-session")
    if args.session_id:
        cmd.extend(["--session-id", args.session_id])
    if args.name:
        cmd.extend(["--name", args.name])
    if args.permission_mode:
        cmd.extend(["--permission-mode", args.permission_mode])
    if args.system_prompt:
        cmd.extend(["--system-prompt", args.system_prompt])
    if args.append_system_prompt:
        cmd.extend(["--append-system-prompt", args.append_system_prompt])
    if args.no_session_persistence:
        cmd.append("--no-session-persistence")

    for directory in args.add_dir:
        cmd.extend(["--add-dir", directory])

    # Keep --tools last. Claude Code treats it as variadic and may consume
    # following positional prompt text or flags as tool names.
    if args.tools is not None:
        cmd.extend(["--tools", args.tools])

    return cmd


def run_command(
    cmd: list[str],
    *,
    raw: bool,
    dry_run: bool,
    save_output: bool,
) -> int:
    if dry_run:
        print_command(cmd)
        return 0

    completed = subprocess.run(cmd, text=True, capture_output=True, check=False)
    stdout = completed.stdout
    stderr = completed.stderr
    summary, payload, parsed = parse_output(stdout.strip())
    summary["returncode"] = completed.returncode

    output_path = None
    if save_output:
        output_path = write_artifact(
            cmd=cmd,
            stdout=stdout,
            stderr=stderr,
            returncode=completed.returncode,
            summary=summary,
        )
        summary["output_path"] = str(output_path)
        summary["artifact_dir"] = str(output_path.parent)

    if payload:
        session_id = payload.get("session_id")
        if isinstance(session_id, str):
            save_last_session(session_id, payload, output_path=output_path)

    if raw:
        if stdout:
            print(stdout, end="")
        if stderr:
            print(stderr, end="", file=sys.stderr)
        if output_path:
            print(f"\noutput_path: {output_path}", file=sys.stderr)
        return completed.returncode

    if not parsed and stdout:
        summary["stdout_preview"] = stdout[:4000]
        summary["stdout_chars"] = len(stdout)
    if stderr:
        summary["stderr_preview"] = stderr[:4000]
        summary["stderr_chars"] = len(stderr)
    print(json.dumps(summary, indent=2, sort_keys=True))
    return completed.returncode


def build_agents_command(args: argparse.Namespace) -> list[str]:
    cmd = [args.claude_bin, "agents", "--json"]
    if args.cwd:
        cmd.extend(["--cwd", args.cwd])
    if args.all:
        cmd.append("--all")
    return cmd


def add_common_run_args(parser: argparse.ArgumentParser) -> None:
    parser.add_argument("prompt", nargs="?", help="Prompt text. Reads stdin when omitted.")
    parser.add_argument("--claude-bin", default="claude", help="Claude Code executable.")
    parser.add_argument("--model", default="fable", help="Claude model alias or full name.")
    parser.add_argument(
        "--effort",
        "--thinking",
        dest="effort",
        default="high",
        choices=EFFORTS,
        help="Claude Code effort/thinking size.",
    )
    parser.add_argument(
        "--max-budget-usd",
        default="0.50",
        type=positive_budget,
        help="Hard spend cap for this print-mode run.",
    )
    parser.add_argument(
        "--output-format",
        default="json",
        choices=("text", "json", "stream-json"),
        help="Claude print-mode output format.",
    )
    parser.add_argument("--resume", help="Resume a session by id or search value.")
    parser.add_argument(
        "--resume-last",
        action="store_true",
        help="Resume the last wrapper-saved advisor session.",
    )
    parser.add_argument(
        "--global-last",
        action="store_true",
        help="With --resume-last, ignore cwd-specific state and use global latest.",
    )
    parser.add_argument(
        "--continue-latest",
        action="store_true",
        help="Continue the most recent conversation in this directory.",
    )
    parser.add_argument(
        "--fork-session",
        action="store_true",
        help="Fork when resuming instead of mutating the original session.",
    )
    parser.add_argument("--session-id", help="Start or reuse a specific UUID session id.")
    parser.add_argument("--name", help="Display name for the Claude Code session.")
    parser.add_argument(
        "--tools",
        default="",
        help='Tool list for Claude Code. Default "" disables tools.',
    )
    parser.add_argument(
        "--permission-mode",
        choices=("acceptEdits", "auto", "bypassPermissions", "default", "dontAsk", "plan"),
        help="Claude Code permission mode when tools are enabled.",
    )
    parser.add_argument("--add-dir", action="append", default=[], help="Additional allowed dir.")
    parser.add_argument("--system-prompt", help="Override Claude Code system prompt.")
    parser.add_argument("--append-system-prompt", help="Append to Claude Code system prompt.")
    parser.add_argument(
        "--no-session-persistence",
        action="store_true",
        help="Do not save the session; disables resume for this run.",
    )
    parser.add_argument("--raw", action="store_true", help="Print raw Claude output.")
    parser.add_argument("--dry-run", action="store_true", help="Print command without running.")
    parser.add_argument(
        "--save-output",
        action=argparse.BooleanOptionalAction,
        default=True,
        help="Save stdout/stderr and summary to an artifact file.",
    )


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    subparsers = parser.add_subparsers(dest="command", required=True)

    run_parser = subparsers.add_parser("run", help="Run an advisor print-mode prompt.")
    add_common_run_args(run_parser)

    agents_parser = subparsers.add_parser("agents", help="List Claude background agents.")
    agents_parser.add_argument("--claude-bin", default="claude", help="Claude Code executable.")
    agents_parser.add_argument("--cwd", help="Filter agents to this workspace.")
    agents_parser.add_argument("--all", action="store_true", help="Include completed sessions.")
    agents_parser.add_argument("--raw", action="store_true", help="Print raw Claude output.")
    agents_parser.add_argument("--dry-run", action="store_true", help="Print command without running.")

    last_parser = subparsers.add_parser("last", help="Print the last saved advisor session.")
    last_parser.add_argument("--claude-bin", default="claude", help=argparse.SUPPRESS)

    return parser.parse_args()


def main() -> int:
    args = parse_args()
    if args.command == "run":
        return run_command(
            build_run_command(args),
            raw=args.raw,
            dry_run=args.dry_run,
            save_output=args.save_output,
        )
    if args.command == "agents":
        return run_command(
            build_agents_command(args),
            raw=args.raw,
            dry_run=args.dry_run,
            save_output=True,
        )
    if args.command == "last":
        return print_last_session()
    raise SystemExit(f"Unknown command: {args.command}")


if __name__ == "__main__":
    raise SystemExit(main())
