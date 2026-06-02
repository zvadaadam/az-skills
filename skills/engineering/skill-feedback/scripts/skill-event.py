#!/usr/bin/env python3
"""Submit skill lifecycle telemetry to PostHog."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import tempfile
import sys
import urllib.error
import urllib.parse
import urllib.request
from datetime import datetime, timezone
from typing import Any


POSTHOG_HOST = "https://us.i.posthog.com"
POSTHOG_PROJECT_API_KEY = "phc_sfAyXEAyfo9KqR7qdQMrqigeAHPuFvQ86Rfr56qYYfJT"
EVENT_NAME = "skill_event"
ACTIONS = ("started", "completed")


def read_hook_input() -> dict[str, Any]:
    if sys.stdin.isatty():
        return {}

    raw = sys.stdin.read().strip()
    if not raw:
        return {}

    try:
        parsed = json.loads(raw)
    except json.JSONDecodeError:
        return {}

    return parsed if isinstance(parsed, dict) else {}


def short_hash(value: Any) -> str | None:
    if not value:
        return None
    return hashlib.sha256(str(value).encode()).hexdigest()[:16]


def parse_context(values: list[str]) -> dict[str, str]:
    context: dict[str, str] = {}
    for value in values:
        if "=" not in value:
            raise ValueError("--context must be key=value")
        key, raw = value.split("=", 1)
        key = key.strip()
        if not key:
            raise ValueError("--context key cannot be empty")
        context[key] = raw.strip()[:500]
    return context


def event_payload(
    args: argparse.Namespace,
    hook_input: dict[str, Any],
) -> dict[str, Any]:
    action = args.action.strip()
    skill = args.skill.strip()
    agent_harness = args.agent_harness.strip() or "unknown"
    model_config = args.model_config.strip() or "unknown"

    if not skill:
        raise ValueError("--skill cannot be empty")
    if action not in ACTIONS:
        raise ValueError(f"--action must be one of: {', '.join(ACTIONS)}")

    timestamp = datetime.now(timezone.utc).isoformat()
    session_id_hash = short_hash(hook_input.get("session_id"))

    properties: dict[str, Any] = {
        "$process_person_profile": False,
        "$insert_id": "skill-event:"
        + hashlib.sha256(
            json.dumps(
                {
                    "skill": skill,
                    "action": action,
                    "agent_harness": agent_harness,
                    "model_config": model_config,
                    "session_id_hash": session_id_hash,
                    "timestamp": timestamp,
                },
                sort_keys=True,
            ).encode()
        ).hexdigest()[:32],
        "source": "az-skills",
        "schema_version": 1,
        "skill": skill,
        "action": action,
        "agent_harness": agent_harness,
        "model_config": model_config,
    }

    if session_id_hash:
        properties["session_id_hash"] = session_id_hash

    context = parse_context(args.context)
    if context:
        properties["context"] = context

    return {
        "api_key": POSTHOG_PROJECT_API_KEY,
        "event": EVENT_NAME,
        "distinct_id": f"az-skills-events:{agent_harness}",
        "timestamp": timestamp,
        "properties": properties,
    }


def started_marker_path(skill: str, session_id_hash: str) -> str:
    marker_id = hashlib.sha256(f"{skill}:{session_id_hash}".encode()).hexdigest()[:24]
    return os.path.join(tempfile.gettempdir(), f"az-skills-started-{marker_id}")


def should_send_started(
    args: argparse.Namespace,
    hook_input: dict[str, Any],
    dry_run: bool = False,
) -> bool:
    if args.action != "started":
        return False

    session_id_hash = short_hash(hook_input.get("session_id"))
    if not session_id_hash:
        return True
    if dry_run:
        return True

    marker = started_marker_path(args.skill.strip(), session_id_hash)
    try:
        fd = os.open(marker, os.O_CREAT | os.O_EXCL | os.O_WRONLY, 0o600)
    except FileExistsError:
        return False

    with os.fdopen(fd, "w", encoding="utf-8") as handle:
        handle.write(datetime.now(timezone.utc).isoformat())

    return True


def send(payload: dict[str, Any]) -> None:
    url = urllib.parse.urljoin(POSTHOG_HOST.rstrip("/") + "/", "i/v0/e/")
    body = json.dumps(payload, separators=(",", ":")).encode("utf-8")
    request = urllib.request.Request(
        url,
        data=body,
        headers={
            "Content-Type": "application/json",
            "User-Agent": "az-skills/skill-event",
        },
        method="POST",
    )
    with urllib.request.urlopen(request, timeout=5) as response:
        response.read()


def parse_args(argv: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--skill", required=True)
    parser.add_argument("--action", required=True, choices=ACTIONS)
    parser.add_argument("--agent-harness", default="unknown")
    parser.add_argument("--model-config", default="unknown")
    parser.add_argument(
        "--context",
        action="append",
        default=[],
        help="Small metadata as key=value. Repeatable.",
    )
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--quiet", action="store_true")
    return parser.parse_args(argv)


def main(argv: list[str]) -> int:
    args = parse_args(argv)
    hook_input = read_hook_input()

    try:
        if args.action == "started" and not should_send_started(args, hook_input, args.dry_run):
            if not args.quiet:
                print(f"skill-event: skipped duplicate started event for {args.skill}")
            return 0
        payload = event_payload(args, hook_input)
    except ValueError as exc:
        if not args.quiet:
            print(f"skill-event: {exc}", file=sys.stderr)
        return 2

    if args.dry_run:
        redacted = dict(payload)
        redacted["api_key"] = "phc_..."
        print(json.dumps(redacted, indent=2, sort_keys=True))
        return 0

    try:
        send(payload)
    except (OSError, urllib.error.HTTPError, urllib.error.URLError) as exc:
        if not args.quiet:
            print(f"skill-event: {exc}", file=sys.stderr)
        return 0 if args.quiet else 1

    if not args.quiet:
        print(f"sent skill event: {args.skill} {payload['properties']['action']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
