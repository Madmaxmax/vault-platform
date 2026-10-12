#!/usr/bin/env bash
set -euo pipefail
# Run from repo root after docker compose up. Does not output secret values.
# Vault CLI -policy via restricted token, with stdout of successful reads discarded.
TOKEN="$(docker compose exec -T vault vault token create -policy=demo-app -field=token)"
trap 'unset TOKEN' EXIT
if ! docker compose exec -T -e VAULT_TOKEN="$TOKEN" vault vault read database/creds/app-readonly >/dev/null 2>&1; then
  echo 'FAIL: permitted credentials path not readable' >&2
  exit 1
fi
if docker compose exec -T -e VAULT_TOKEN="$TOKEN" vault vault kv get secret/products/other/config >/dev/null 2>&1; then
  echo 'FAIL: forbidden path is accessible' >&2
  exit 1
fi
echo 'PASS: permitted path read, other product denied'
