# ЛР 2. Docker Compose

```bash
docker compose up -d --build
```

| Сервис | Контейнер | Что делает |
|--------|-----------|------------|
| `db` | `notes-db` | PostgreSQL 17, данные в volume `pg-data`, healthcheck `pg_isready` |
| `init-db` | `notes-init-db` | init: после `db` healthy создаёт таблицу через `psql` (`entrypoint`) и завершается |
| `app` | `notes-app` | приложение из ЛР 1 на PostgreSQL, образ `notes-app:2.0` собирается из `Dockerfile`, порт `8000`, стартует после успешного `init-db` |

Переменные лежат в `.env`, все сервисы в одной сети `notes-net`.

```
$ docker compose ps -a --format 'table {{.Name}}\t{{.Status}}\t{{.Ports}}'
NAME            STATUS                            PORTS
notes-app       Up 6 seconds (health: starting)   0.0.0.0:8000->8000/tcp, [::]:8000->8000/tcp
notes-db        Up 12 seconds (healthy)           5432/tcp
notes-init-db   Exited (0) 6 seconds ago
$ docker compose logs init-db
notes-init-db  | CREATE TABLE
$ curl -s localhost:8000/
{"host":"d45e4e0d7e1a","notes":[{"id":1,"text":"hello compose"}]}
```

## Ответы на вопросы

**Можно ли ограничивать ресурсы?** Да, через `deploy.resources` (работает в обычном `docker compose up`, Docker выставляет cgroups контейнера):

```yaml
deploy:
  resources:
    limits:
      cpus: "0.5"
      memory: 256M
```

Также есть ключи `mem_limit`, `cpus`, `pids_limit`.

**Как запустить только определённый сервис?** `docker compose up -d db` запускает сервис и его `depends_on`; `docker compose up -d --no-deps app` запускает без зависимостей; `docker compose run --rm init-db` выполняет разовый запуск.
