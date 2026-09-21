#!/bin/sh
set -eu

# FOR LOCAL DEVELOPMENT ONLY: root token is supplied at container runtime.
vault auth enable approle 2>/dev/null || true
vault secrets enable -path=secret kv-v2 2>/dev/null || true
vault secrets enable database 2>/dev/null || true
vault policy write demo-app /policies/app-readonly.hcl
vault policy write demo-ci /policies/cicd.hcl
vault policy write other-app /policies/other-app.hcl

vault kv put secret/products/demo/config sample_message="hello from Vault" >/dev/null
vault kv put secret/products/other/config sample_message="restricted" >/dev/null

# PostgreSQL plugin uses a Vault-managed admin connection; these credentials
# are only passed to the bootstrap service, never to the application.
vault write database/config/postgres \
  plugin_name=postgresql-database-plugin \
  allowed_roles=app-readonly \
  connection_url='postgresql://{{username}}:{{password}}@postgres:5432/appdb?sslmode=disable' \
  username=postgres password="$POSTGRES_PASSWORD" >/dev/null

vault write database/roles/app-readonly \
  db_name=postgres \
  creation_statements='CREATE ROLE "{{name}}" WITH LOGIN PASSWORD '\''{{password}}'\'' VALID UNTIL '\''{{expiration}}'\''; GRANT CONNECT ON DATABASE appdb TO "{{name}}"; GRANT USAGE ON SCHEMA public TO "{{name}}"; GRANT SELECT ON ALL TABLES IN SCHEMA public TO "{{name}}";' \
  revocation_statements='REVOKE ALL PRIVILEGES ON ALL TABLES IN SCHEMA public FROM "{{name}}"; REVOKE USAGE ON SCHEMA public FROM "{{name}}"; REVOKE CONNECT ON DATABASE appdb FROM "{{name}}"; DROP ROLE IF EXISTS "{{name}}";' \
  default_ttl=1h max_ttl=8h >/dev/null

vault write auth/approle/role/demo-app \
  token_policies=demo-app token_ttl=1h token_max_ttl=4h \
  secret_id_ttl=24h secret_id_num_uses=0 >/dev/null

# Local demo only: file-based delivery of bootstrap credentials.
umask 077
vault read -field=role_id auth/approle/role/demo-app/role-id > /bootstrap/role_id
vault write -field=secret_id -f auth/approle/role/demo-app/secret-id > /bootstrap/secret_id

# Vault's audit device captures Vault requests (not SQL traffic).
vault audit enable file file_path=stdout 2>/dev/null || true
printf '%s\n' 'Bootstrap complete (demo-only).'
