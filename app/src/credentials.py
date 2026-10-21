"""Read database credentials rendered by Vault Agent."""
from __future__ import annotations

import json
import os
from pathlib import Path


def credentials_path() -> Path:
    return Path(os.getenv("CREDENTIALS_FILE", "/run/rendered/postgres.json"))


def read_credentials() -> tuple[str, str]:
    """Load the current credential file for each new database connection."""
    data = json.loads(credentials_path().read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        raise ValueError("Invalid credentials structure")
    username, password = data.get("username"), data.get("password")
    if not isinstance(username, str) or not username:
        raise ValueError("Missing database username")
    if not isinstance(password, str) or not password:
        raise ValueError("Missing database password")
    return username, password
