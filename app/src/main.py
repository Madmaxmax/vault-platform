"""Read transient database credentials rendered by Vault Agent in tmpfs.

This example intentionally never returns passwords or lease identifiers over HTTP.
"""
from __future__ import annotations

import json
import os
from pathlib import Path

import psycopg
from fastapi import FastAPI, HTTPException

app = FastAPI(title="Vault integration demo", docs_url="/docs")


def credentials_path() -> Path:
    return Path(os.getenv("CREDENTIALS_FILE", "/run/rendered/postgres.json"))


def read_credentials() -> tuple[str, str]:
    """Re-read on every connection to support credential rotation."""
    data = json.loads(credentials_path().read_text(encoding="utf-8"))
    username = data.get("username")
    password = data.get("password")
    if not isinstance(username, str) or not username:
        raise ValueError("Vault rendered file does not contain a valid username")
    if not isinstance(password, str) or not password:
        raise ValueError("Vault rendered file does not contain a valid password")
    return username, password


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


@app.get("/db/check")
def check_database() -> dict[str, str]:
    try:
        username, password = read_credentials()
        with psycopg.connect(
            host=os.getenv("DATABASE_HOST", "postgres"),
            port=int(os.getenv("DATABASE_PORT", "5432")),
            dbname=os.getenv("DATABASE_NAME", "appdb"),
            user=username,
            password=password,
            connect_timeout=5,
        ) as conn:
            with conn.cursor() as cursor:
                cursor.execute("SELECT current_user")
                current_user = cursor.fetchone()[0]
    except (OSError, ValueError, json.JSONDecodeError, psycopg.Error):
        raise HTTPException(status_code=503, detail="Database credentials or connection unavailable") from None
    return {"status": "connected", "database_user": current_user}
