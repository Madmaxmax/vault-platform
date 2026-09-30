import json
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

from src.main import app, read_credentials

client = TestClient(app)


def test_health():
    assert client.get("/health").json() == {"status": "ok"}


def test_credentials_from_vault_rendered_file(tmp_path: Path, monkeypatch):
    creds = tmp_path / "postgres.json"
    creds.write_text(json.dumps({"username": "test_user", "password": "secret", "lease_id": "x"}))
    monkeypatch.setenv("CREDENTIALS_FILE", str(creds))
    assert read_credentials() == ("test_user", "secret")


def test_bad_credentials_are_rejected(tmp_path: Path, monkeypatch):
    creds = tmp_path / "postgres.json"
    creds.write_text('{"username":"", "password":""}')
    monkeypatch.setenv("CREDENTIALS_FILE", str(creds))
    with pytest.raises(ValueError):
        read_credentials()


def test_missing_secret_is_safe_error(tmp_path: Path, monkeypatch):
    monkeypatch.setenv("CREDENTIALS_FILE", str(tmp_path / "missing.json"))
    res = client.get("/db/check")
    assert res.status_code == 503
    assert "password" not in res.text.lower()
