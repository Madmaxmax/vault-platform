# Таблица доступа к ключам HashiCorp Vault

| Субъект | Права | Путь (куда обращается) |
|---|---|---|
| DevOps-инженер | `create`, `read`, `update`, `delete`, `sudo` | `*` |
| Разработчик | `read` | `secret/data/app/*` |
| AI-агент | `read` | `secret/data/app/*` |
| Приложение | `read` | `secret/data/app/*` |
| CI/CD Runner | `create`, `read`, `update` | `secret/data/ci-cd/*` |
| Сервис резервного копирования | `read`, `create`, `update` | `sys/storage/raft/snapshot` |