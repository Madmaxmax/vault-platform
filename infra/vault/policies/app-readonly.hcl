path "database/creds/app-readonly" {
  capabilities = ["read"]
}

path "secret/data/products/demo/*" {
  capabilities = ["read"]
}
