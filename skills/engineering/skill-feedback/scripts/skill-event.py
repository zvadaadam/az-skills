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
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from telemetry_common import (
    POSTHOG_PROJECT_API_KEY,
    parse_context,
    send_to_posthog,
    short_hash,
    telemetry_identity,
)

EVENTS = ("skill_read", "skill_activated")


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


def hook_file_path(hook_input: dict[str, Any]) -> str:
    tool_input = hook_input.get("tool_input")
    if not isinstance(tool_input, dict):
        return ""
    return str(tool_input.get("file_path") or tool_input.get("path") or "").strip()


def skill_from_file_path(file_path: str) -> str:
    if not file_path:
        return ""

    path = Path(file_path)
    if path.name != "SKILL.md":
        return ""

    parts = path.parts
    for index, part in enumerate(parts):
        if part != "skills":
            continue
        if index + 2 < len(parts) and parts[index + 2] == "SKILL.md":
            return parts[index + 1]
        if index + 3 < len(parts) and parts[index + 3] == "SKILL.md":
            return parts[index + 2]

    return ""


def resolve_event(args: argparse.Namespace) -> str:
    if args.event:
        return args.event

    legacy_action = (args.action or "").strip()
    if legacy_action == "started":
        return "skill_activated"
    if legacy_action in {"skill_read", "skill_activated"}:
        return legacy_action
    if legacy_action == "completed":
        return ""
    raise ValueError("--event is required")


def event_payload(
    args: argparse.Namespace,
    hook_input: dict[str, Any],
) -> dict[str, Any]:
    event_name = resolve_event(args)
    skill = args.skill.strip()
    if event_name == "skill_read" and skill == "auto":
        skill = skill_from_file_path(hook_file_path(hook_input))

    agent_harness = args.agent_harness.strip() or "unknown"
    model_config = args.model_config.strip() or "unknown"

    if not skill:
        raise ValueError("--skill cannot be empty")
    if event_name not in EVENTS:
        raise ValueError(f"--event must be one of: {', '.join(EVENTS)}")

    timestamp = datetime.now(timezone.utc).isoformat()
    session_id_hash = short_hash(hook_input.get("session_id"))
    distinct_id, identity_properties = telemetry_identity(
        agent_harness,
        create_installation=not args.dry_run,
    )

    properties: dict[str, Any] = {
        "$process_person_profile": False,
        "$insert_id": f"{event_name}:"
        + hashlib.sha256(
            json.dumps(
                {
                    "skill": skill,
                    "event": event_name,
                    "agent_harness": agent_harness,
                    "model_config": model_config,
                    "session_id_hash": session_id_hash,
                    "timestamp": timestamp,
                },
                sort_keys=True,
            ).encode()
        ).hexdigest()[:32],
        "source": "az-skills",
        "schema_version": 2,
        "skill": skill,
        "agent_harness": agent_harness,
        "model_config": model_config,
    }
    properties.update(identity_properties)

    if session_id_hash:
        properties["session_id_hash"] = session_id_hash

    context = parse_context(args.context)
    if context:
        properties["context"] = context

    return {
        "api_key": POSTHOG_PROJECT_API_KEY,
        "event": event_name,
        "distinct_id": distinct_id,
        "timestamp": timestamp,
        "properties": properties,
    }


def activation_marker_path(skill: str, session_id_hash: str) -> str:
    marker_id = hashlib.sha256(f"{skill}:{session_id_hash}".encode()).hexdigest()[:24]
    return os.path.join(tempfile.gettempdir(), f"az-skills-activated-{marker_id}")


def should_send_activation(
    args: argparse.Namespace,
    hook_input: dict[str, Any],
    dry_run: bool = False,
) -> bool:
    if resolve_event(args) != "skill_activated":
        return False

    session_id_hash = short_hash(hook_input.get("session_id"))
    if not session_id_hash:
        return True
    if dry_run:
        return True

    marker = activation_marker_path(args.skill.strip(), session_id_hash)
    try:
        fd = os.open(marker, os.O_CREAT | os.O_EXCL | os.O_WRONLY, 0o600)
    except FileExistsError:
        return False

    with os.fdopen(fd, "w", encoding="utf-8") as handle:
        handle.write(datetime.now(timezone.utc).isoformat())

    return True


def parse_args(argv: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--skill", required=True)
    parser.add_argument("--event", choices=EVENTS)
    parser.add_argument("--action", help=argparse.SUPPRESS)
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
        event_name = resolve_event(args)
        if not event_name:
            return 0
        if event_name == "skill_read" and args.skill.strip() == "auto":
            if not skill_from_file_path(hook_file_path(hook_input)):
                return 0
        if event_name == "skill_activated" and not should_send_activation(
            args, hook_input, args.dry_run
        ):
            if not args.quiet:
                print(f"skill-event: skipped duplicate activation event for {args.skill}")
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
        send_to_posthog(payload, user_agent="az-skills/skill-event", timeout=5)
    except (OSError, urllib.error.HTTPError, urllib.error.URLError) as exc:
        if not args.quiet:
            print(f"skill-event: {exc}", file=sys.stderr)
        return 0 if args.quiet else 1

    if not args.quiet:
        print(f"sent {payload['event']}: {payload['properties']['skill']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
