# Аутентификация приложения через AppRole

## 1. Первым делом включим AppRole

```bash
$ vault auth enable approle
```
## 2. Создадим политику для приложения

```bash
$ vault policy write app-read

# Разрешим чтение секретов из пространства secret/data/app/
path "secret/data/app/*" {
  capabilities = ["read"]
}
```
## 3. Создадим роль для приложения

```bash
$ vault write auth/approle/role/app \
    token_policies="app-read" \ # Политика доступа приложения
    token_ttl="1h" \ # Начальное время жизни токена
    token_max_ttl="4h" \ # Максимальное время жизни токена
    secret_id_ttl="24h" \ # Время действия Secret ID
    secret_id_num_uses=1 # Secret ID можно использовать один раз
```
## 4. Получаем RoleID

Параметр RoleID нам пригодится для выполнения авторизации в хранилище.
```bash
$ vault read auth/approle/role/app/role-id
```
## 5. Генерируем SecretID

```bash
$ vault write -f auth/approle/role/app/secret-id
```
## 6. Передаём приложению начальный SecretID

| Способ | Принцип работы|
|---|---|
| Переменные окружения | Secret ID передаётся при запуске приложения |
| Защищённый файл | Secret ID записывается в файл с ограниченными правами |
| Docker Secrets | Секрет передаётся контейнеру через механизм Docker |
| Kubernetes Secret | Secret ID передаётся Pod через Kubernetes |
| Response Wrapping | Приложение получает одноразовый wrapping token и раскрывает его |
| Внешняя система управления секретами | Учётные данные выдаются через доверенную инфраструктуру |