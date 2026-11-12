# Результаты проверки

Дата: 24 ноября 2026 года.

| Проверка | Результат | Ограничение |
|---|---|---|
| `PYTHONPATH=app pytest -q app/tests` | 12 passed, 1 skipped | API-тесты пропущены, так как нет установленного `psycopg` |
| `python -m compileall -q app/src` | Успешно | Проверяет синтаксис, а не runtime |
| `bash -n scripts/*.sh infra/vault/scripts/*.sh` | Успешно | Не исполняет скрипты |
| Парсинг `compose.yaml` библиотекой PyYAML | Успешно | Не заменяет `docker compose config` |
| `docker compose up --build` | Не выполнено | Docker CLI/daemon недоступны в среде проверки |
| Проверка доступа AppRole / PostgreSQL Lease | Не выполнено | Требует запущенных Vault и PostgreSQL |

## Проверка после клонирования

Инструкция по интеграционному прогону: [TESTING.md](TESTING.md).

Результаты отражают только фактически выполненные проверки и не подтверждают работоспособность всей контейнерной системы.
