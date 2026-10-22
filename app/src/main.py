"""Read transient database credentials rendered by Vault Agent in tmpfs.

This example intentionally never returns passwords or lease identifiers over HTTP.
"""
from __future__ import annotations

import os

import psycopg
from fastapi import FastAPI, HTTPException

from .credentials import read_credentials

app = FastAPI(title="Vault integration demo", docs_url="/docs")


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
    except (OSError, ValueError, psycopg.Error):
        raise HTTPException(status_code=503, detail="Database credentials or connection unavailable") from None
    return {"status": "connected", "database_user": current_user}
