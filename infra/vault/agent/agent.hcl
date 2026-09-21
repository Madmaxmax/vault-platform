pid_file = "/tmp/vault-agent.pid"
vault {
  address = "http://vault:8200"
}
auto_auth {
  method "approle" {
    mount_path = "auth/approle"
    config = {
      role_id_file_path = "/bootstrap/role_id"
      secret_id_file_path = "/bootstrap/secret_id"
      remove_secret_id_file_after_reading = false
    }
  }
}
template {
  destination = "/run/rendered/postgres.json"
  perms = "0644"
  contents = <<EOT
{{ with secret "database/creds/app-readonly" }}{"username":{{ .Data.username | toJSON }},"password":{{ .Data.password | toJSON }},"lease_id":{{ .LeaseID | toJSON }}} {{ end }}
EOT
}
