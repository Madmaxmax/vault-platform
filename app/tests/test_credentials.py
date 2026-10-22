import json
from pathlib import Path

import pytest

from src.credentials import read_credentials


@pytest.fixture
def credentials_file(tmp_path: Path, monkeypatch):
    path = tmp_path / "postgres.json"
    monkeypatch.setenv("CREDENTIALS_FILE", str(path))
    return path


def test_reads_valid_credentials(credentials_file):
    credentials_file.write_text(json.dumps({"username": "alice", "password": "example"}))
    assert read_credentials() == ("alice", "example")


def test_rereads_after_rotation(credentials_file):
    credentials_file.write_text('{"username":"first","password":"old"}')
    assert read_credentials() == ("first", "old")
    credentials_file.write_text('{"username":"second","password":"new"}')
    assert read_credentials() == ("second", "new")


@pytest.mark.parametrize("content", [
    "[]", "null", '"text"', "{", "{}",
    '{"username": "", "password":"x"}',
    '{"username": "x", "password": ""}',
    '{"username": ["x"], "password": "y"}',
    '{"username": "x", "password": null}',
])
def test_rejects_invalid_credentials(credentials_file, content):
    credentials_file.write_text(content)
    with pytest.raises((ValueError, json.JSONDecodeError)):
        read_credentials()


def test_rejects_missing_file(credentials_file):
    with pytest.raises(FileNotFoundError):
        read_credentials()
