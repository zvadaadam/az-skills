"""Shared helpers for AZ skills PostHog telemetry."""

from __future__ import annotations

import hashlib
import json
import os
import urllib.parse
import urllib.request
import uuid
from pathlib import Path
from typing import Any


POSTHOG_HOST = "https://us.i.posthog.com"
POSTHOG_PROJECT_API_KEY = "phc_sfAyXEAyfo9KqR7qdQMrqigeAHPuFvQ86Rfr56qYYfJT"
INSTALLATION_ID_PATH = Path.home() / ".az-skills" / "installation-id"


def short_hash(value: Any, length: int = 16) -> str | None:
    if not value:
        return None
    return hashlib.sha256(str(value).encode()).hexdigest()[:length]


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


def read_installation_id(create: bool = True) -> str | None:
    try:
        if INSTALLATION_ID_PATH.exists():
            existing = INSTALLATION_ID_PATH.read_text(encoding="utf-8").strip()
            if existing:
                return existing

        if not create:
            return None

        INSTALLATION_ID_PATH.parent.mkdir(parents=True, exist_ok=True)
        os.chmod(INSTALLATION_ID_PATH.parent, 0o700)

        installation_id = uuid.uuid4().hex
        if INSTALLATION_ID_PATH.exists():
            INSTALLATION_ID_PATH.write_text(installation_id + "\n", encoding="utf-8")
            os.chmod(INSTALLATION_ID_PATH, 0o600)
            return installation_id

        try:
            fd = os.open(
                INSTALLATION_ID_PATH,
                os.O_CREAT | os.O_EXCL | os.O_WRONLY,
                0o600,
            )
        except FileExistsError:
            existing = INSTALLATION_ID_PATH.read_text(encoding="utf-8").strip()
            return existing or None

        with os.fdopen(fd, "w", encoding="utf-8") as handle:
            handle.write(installation_id + "\n")

        return installation_id
    except OSError:
        return None


def installation_id_hash(create: bool = True) -> str | None:
    installation_id = read_installation_id(create=create)
    return short_hash(installation_id, length=32)


def telemetry_identity(
    agent_harness: str,
    *,
    create_installation: bool = True,
) -> tuple[str, dict[str, str]]:
    install_hash = installation_id_hash(create=create_installation)
    if install_hash:
        return (
            f"az-skills-installation:{install_hash}",
            {"installation_id_hash": install_hash},
        )

    return f"az-skills-events:{agent_harness}", {}


def send_to_posthog(payload: dict[str, Any], *, user_agent: str, timeout: int) -> None:
    url = urllib.parse.urljoin(POSTHOG_HOST.rstrip("/") + "/", "i/v0/e/")
    body = json.dumps(payload, separators=(",", ":")).encode("utf-8")
    request = urllib.request.Request(
        url,
        data=body,
        headers={
            "Content-Type": "application/json",
            "User-Agent": user_agent,
        },
        method="POST",
    )
    with urllib.request.urlopen(request, timeout=timeout) as response:
        response.read()
