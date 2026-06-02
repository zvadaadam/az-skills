#!/usr/bin/env python3
"""Submit feedback about an AZ skill to PostHog."""

from __future__ import annotations

import argparse
import hashlib
import json
import sys
import urllib.error
from datetime import datetime, timezone

from telemetry_common import (
    POSTHOG_PROJECT_API_KEY,
    parse_context,
    send_to_posthog,
    telemetry_identity,
)

EVENT_NAME = "skill_feedback"
RATINGS = ("useful", "confusing", "bug", "idea", "other")
MAX_FEEDBACK_CHARS = 4000


def event_payload(args: argparse.Namespace) -> dict:
    feedback = args.text.strip()[:MAX_FEEDBACK_CHARS]
    skill = args.skill.strip()
    agent_harness = args.agent_harness.strip() or "unknown"
    model_config = args.model_config.strip() or "unknown"

    if not feedback:
        raise ValueError("--text cannot be empty")
    if not skill:
        raise ValueError("--skill cannot be empty")

    timestamp = datetime.now(timezone.utc).isoformat()
    distinct_id, identity_properties = telemetry_identity(
        agent_harness,
        create_installation=not args.dry_run,
    )
    insert_source = json.dumps(
        {
            "agent_harness": agent_harness,
            "model_config": model_config,
            "skill": skill,
            "rating": args.rating,
            "feedback": feedback,
            "timestamp": timestamp,
        },
        sort_keys=True,
    )

    return {
        "api_key": POSTHOG_PROJECT_API_KEY,
        "event": EVENT_NAME,
        "distinct_id": distinct_id,
        "timestamp": timestamp,
        "properties": {
            "$process_person_profile": False,
            "$insert_id": "skill-feedback:"
            + hashlib.sha256(insert_source.encode()).hexdigest()[:32],
            "source": "az-skills",
            "schema_version": 2,
            **identity_properties,
            "agent_harness": agent_harness,
            "model_config": model_config,
            "skill": skill,
            "rating": args.rating,
            "feedback_text": feedback,
            "context": parse_context(args.context),
        },
    }


def parse_args(argv: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--skill", required=True)
    parser.add_argument("--rating", required=True, choices=RATINGS)
    parser.add_argument("--text", required=True)
    parser.add_argument("--agent-harness", default="unknown")
    parser.add_argument("--model-config", default="unknown")
    parser.add_argument(
        "--context",
        action="append",
        default=[],
        help="Small metadata as key=value. Repeatable.",
    )
    parser.add_argument("--dry-run", action="store_true")
    return parser.parse_args(argv)


def main(argv: list[str]) -> int:
    args = parse_args(argv)

    try:
        payload = event_payload(args)
    except ValueError as exc:
        print(f"skill-feedback: {exc}", file=sys.stderr)
        return 2

    if payload["properties"]["context"] == {}:
        payload["properties"].pop("context")

    if args.dry_run:
        redacted = dict(payload)
        redacted["api_key"] = "phc_..."
        print(json.dumps(redacted, indent=2, sort_keys=True))
        return 0

    try:
        send_to_posthog(payload, user_agent="az-skills/skill-feedback", timeout=10)
    except urllib.error.HTTPError as exc:
        detail = exc.read().decode("utf-8", errors="replace")
        print(f"skill-feedback: HTTP {exc.code} {detail}", file=sys.stderr)
        return 1
    except (OSError, urllib.error.URLError) as exc:
        print(f"skill-feedback: {exc}", file=sys.stderr)
        return 1

    print(f"sent skill feedback: {payload['properties']['skill']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
