# HashiCorp Vault + PostgreSQL: пользователи, права, TTL и шаблоны

## 1. Создание пользователей

Vault Database Secrets Engine поддерживает два способа управления пользователями PostgreSQL: **динамические роли (Dynamic Roles)** и **статические роли (Static Roles)**.

### Динамические роли

При каждом запросе секрета Vault создаёт **нового уникального пользователя** в PostgreSQL на основе SQL-шаблона, заданного в `creation_statements`. Имя пользователя и пароль генерируются автоматически.

**Ключевая особенность:** каждый запрос получает отдельные учётные данные. Это обеспечивает изоляцию подключений, позволяет ограничивать время доступа и упрощает аудит пользователей.

### Статические роли

Статическая роль — это сопоставление между ролью Vault и уже существующим пользователем PostgreSQL. Vault не создаёт нового пользователя, а управляет паролем существующей учётной записи посредством периодической ротации.

---

## 2. Права пользователей

Права задаются в SQL-шаблонах, которые Vault выполняет в PostgreSQL при создании пользователя.

**Пример**

```sql
CREATE ROLE "{{name}}"
WITH LOGIN
PASSWORD '{{password}}'
VALID UNTIL '{{expiration}}';

GRANT CONNECT ON DATABASE app_db TO "{{name}}";
GRANT USAGE ON SCHEMA public TO "{{name}}";
GRANT SELECT ON ALL TABLES IN SCHEMA public TO "{{name}}";
```

Этот подход позволяет централизованно управлять правами в PostgreSQL, а Vault использовать для назначения этих прав временным пользователям.

---

## 3. Время жизни пользователей (TTL)

Для динамических ролей Vault поддерживает управление временем жизни учётных данных через механизм **Lease**.

Основные параметры:

| Параметр | Описание |
|---|---|
| `default_ttl` | Время действия учётных данных по умолчанию |
| `max_ttl` | Максимально допустимое время действия с учётом продлений |
| `lease_duration` | Фактическое время действия выданных учётных данных |
| `lease_renewable` | Возможность продления Lease |

**Пример настройки:**

```bash
vault write database/roles/app-readonly \
    db_name="postgres" \
    creation_statements=@readonly.sql \
    default_ttl="1h" \
    max_ttl="8h"
```

В данном примере:
- первоначально пользователь создаётся на 1 час;
- при разрешённом продлении Lease его срок действия может быть увеличен;
- общее время действия не должно превышать `max_ttl`.

При истечении Lease Vault выполняет `revocation_statements` и отзывает учётные данные.
---

## 4. Шаблоны создания и удаления пользователей

Для управления жизненным циклом динамических пользователей Vault использует SQL-шаблоны.

Основные переменные шаблонов:

| Переменная | Описание |
|---|---|
| `{{name}}` | Автоматически сгенерированное имя пользователя |
| `{{password}}` | Сгенерированный пароль |
| `{{expiration}}` | Время истечения действия учётных данных |

### Создание пользователя: `creation_statements`

Пример шаблона:

```sql
CREATE ROLE "{{name}}"
WITH LOGIN
PASSWORD '{{password}}'
VALID UNTIL '{{expiration}}';

GRANT app_readonly TO "{{name}}";
```

### Продление пользователя: `renew_statements`

Выполняется при продлении Lease. Обновляет срок действия учётной записи в PostgreSQL.

Пример:

```sql
ALTER ROLE "{{name}}"
VALID UNTIL '{{expiration}}';
```

### Удаление пользователя: `revocation_statements`

Выполняется при отзыве Lease или истечении срока действия учётных данных.

Пример:

```sql
REVOKE app_readonly FROM "{{name}}";

DROP ROLE IF EXISTS "{{name}}";
```

При использовании групповых ролей отзыв членства перед удалением пользователя позволяет корректно очистить его полномочия.

---

## 5. Создание и настройка Dynamic Role

После подготовки SQL-шаблонов необходимо зарегистрировать роль в Vault.

Пример создания роли `app-readonly`:

```bash
vault write database/roles/app-readonly \
    db_name="postgres" \
    creation_statements=@readonly.sql \
    renew_statements=@renew.sql \
    revocation_statements=@revoke.sql \
    default_ttl="1h" \
    max_ttl="8h"
```

Для создания пользователя с правами чтения и записи можно зарегистрировать отдельную роль:

```bash
vault write database/roles/app-readwrite \
    db_name="postgres" \
    creation_statements=@readwrite.sql \
    revocation_statements=@revoke-readwrite.sql \
    default_ttl="30m" \
    max_ttl="4h"
```

### Получение учётных данных

```bash
vault read database/creds/app-readonly
```

В ответ Vault возвращает:
- `username` — имя созданного пользователя;
- `password` — сгенерированный пароль;
- `lease_id` — идентификатор Lease;
- `lease_duration` — время действия учётных данных;
- `lease_renewable` — возможность продления.

### Продление Lease

```bash
vault lease renew <lease_id>
```

### Принудительный отзыв учётных данных

```bash
vault lease revoke <lease_id>
```

При отзыве Vault выполняет настроенный SQL-шаблон `revocation_statements`.

---

## 6. Статические роли

В отличие от динамических ролей, статические роли управляют уже существующими пользователями PostgreSQL.

Для настройки используются:
- `username` — имя существующего пользователя PostgreSQL;
- `rotation_period` — период автоматической смены пароля;
- `rotation_statements` — SQL-команды, выполняемые при ротации пароля.

**Пример создания Static Role:**

```bash
vault write database/static-roles/app-monitoring \
    db_name="postgres" \
    username="monitoring" \
    rotation_period="24h"
```

Получение учётных данных:

```bash
vault read database/static-creds/app-monitoring
```

Vault возвращает актуальный пароль существующего пользователя. При ротации пароль меняется непосредственно в PostgreSQL.

**Ключевое отличие:** Dynamic Roles создают и удаляют пользователей, Static Roles сохраняют существующую учётную запись и управляют её паролем.

---

## 7. Основные компоненты управления

| Компонент | Назначение |
|---|---|
| `Database Config` | Настройка подключения Vault к PostgreSQL |
| `Dynamic Roles` | Создание временных пользователей |
| `Static Roles` | Управление существующими пользователями |
| `creation_statements` | SQL-шаблон создания пользователя |
| `renew_statements` | Продление срока действия пользователя |
| `revocation_statements` | Отзыв и удаление пользователя |
| `default_ttl` | Время действия учётных данных по умолчанию |
| `max_ttl` | Максимальное время действия Lease |
| `rotation_period` | Период ротации пароля статического пользователя |
