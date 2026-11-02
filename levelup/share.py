"""Persistence for shareable CV analysis results.

Completed analyses are stored under an unguessable identifier so they can be
viewed again through a share link without re-running the analysis. Results are
kept as JSON files inside ``config.SHARED_RESULTS_DIR``; the storage lives
behind this module so it can be swapped for a database later without touching
the UI.
"""

import json
import re
import secrets
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Optional

from levelup import config

# 16 bytes -> 128 bits of entropy, rendered as a 22-char URL-safe token.
_SHARE_ID_NUM_BYTES = 16

# token_urlsafe alphabet only; also guards against path traversal.
_SHARE_ID_PATTERN = re.compile(r"^[A-Za-z0-9_-]{16,64}$")


def _share_dir() -> Path:
    """Returns the directory where shared analyses are stored."""
    return Path(config.SHARED_RESULTS_DIR)


def is_valid_share_id(share_id: str) -> bool:
    """Checks that a share id looks like one we generated."""
    return bool(_SHARE_ID_PATTERN.fullmatch(share_id))


def generate_share_id() -> str:
    """Generates a cryptographically unguessable share id."""
    return secrets.token_urlsafe(_SHARE_ID_NUM_BYTES)


def save_shared_analysis(
    result: dict[str, Any],
    report_language: str,
    target_role: Optional[str] = None,
) -> str:
    """Persists a completed analysis and returns its share id.

    Only the analysis result and the report settings are stored; the uploaded
    CV itself is never persisted.
    """
    share_id = generate_share_id()
    payload = {
        "share_id": share_id,
        "result": result,
        "report_language": report_language,
        "target_role": target_role,
        "created_at": datetime.now(timezone.utc).isoformat(),
    }
    share_dir = _share_dir()
    share_dir.mkdir(parents=True, exist_ok=True)
    path = share_dir / f"{share_id}.json"
    path.write_text(json.dumps(payload, ensure_ascii=False), encoding="utf-8")
    return share_id


def load_shared_analysis(share_id: str) -> dict[str, Any] | None:
    """Loads a previously shared analysis, or None if it does not exist."""
    if not is_valid_share_id(share_id):
        return None
    path = _share_dir() / f"{share_id}.json"
    if not path.is_file():
        return None
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return None
    if not isinstance(payload, dict) or not isinstance(payload.get("result"), dict):
        return None
    return payload
