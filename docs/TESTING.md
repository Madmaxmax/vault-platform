# Проверка проекта

## Быстрые тесты Python

```bash
python -m pip install -r app/requirements-dev.txt
PYTHONPATH=app python -m pytest -q app/tests
python -m compileall -q app/src
```

В PowerShell вместо `PYTHONPATH=app` используйте `$env:PYTHONPATH="app"` или запустите `python -m pytest` из папки `app`.

## Интеграционный сценарий на Docker Desktop

1. Скопируйте `.env.example` в `.env`, задайте локальные пароли.
2. Выполните `docker compose config --quiet`, затем `docker compose up --build -d`.
3. Проверьте `docker compose ps` и журналы `docker compose logs --tail=100 bootstrap vault-agent app`.
4. Выполните `bash scripts/smoke-test.sh` и `bash scripts/access-check.sh` (Git Bash/WSL2).
5. Убедитесь, что `/db/check` возвращает имя временного пользователя, а чужой путь Vault не читается.
6. Выполните `docker compose down` без `-v`, если необходимо сохранить базу.

## Известные ограничения

Конфигурация Vault `-dev` и HTTP допустимы только внутри локального изолированного стенда. Проверка SSL/TLS, HA, восстановления, обновления и отзыва реальных секретов требует отдельного тестирования. CI выполняет Python-тесты и проверку схемы Docker Compose, но не заменяет интеграционный прогон.
