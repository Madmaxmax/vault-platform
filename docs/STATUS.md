# Матрица реализации относительно требований

| Возможность | Статус в текущем репозитории | Как проверить |
|---|---|---|
| FastAPI + PostgreSQL | Подготовлена реализация, не проверена в Docker в этой среде | `docker compose up --build`; `/db/check` |
| AppRole + ACL | Bootstrap-конфигурация | Проверить чтение разрешённого пути и 403 на чужом |
| Vault Agent + tmpfs | Config + Compose | Файл creds в tmpfs; чтение приложения |
| Динамические роли PostgreSQL | Bootstrap-конфигурация | `vault read database/creds/app-readonly` |
| Audit device | Конфигурация bootstrap | `vault audit list`; события лога |
| Token lease / revoke | Примеры CLI | Ручные тесты TTL, `vault lease revoke` |
| Раздельные приложения/среды | Целевая модель, **не реализована** | Создать отдельные роли и политики |
| Static Roles | Описано, **не реализовано** | Реализовать отдельную роль |
| Yandex Cloud, KMS Auto Unseal | Только дизайн, **не развернуто** | Проверка после создания ВМ |
| TLS/HA/backup/restore | **Не реализовано** | Отдельный эксплуатационный этап |
| Демонстрационный frontend React | **Не реализован** | Дополнительная задача |
| CI | Workflow тестов | GitHub Actions после push |

Отметки «подготовлено» не равны подтверждённому успешному интеграционному тесту.
