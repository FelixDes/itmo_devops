# ЛР 1. Dockerfile

Приложение: `main.py`, минимальный сервис заметок на FastAPI (`GET /`, `POST /notes`, `GET /healthz`), данные в SQLite в `/data` (volume).

```bash
docker build -f bad.Dockerfile -t notes-app:1.0-bad .
docker build -f good.Dockerfile -t notes-app:1.0-good .
docker run -d --name notes -p 8000:8000 -v notes-data:/data notes-app:1.0-good
```

## Плохие практики в bad.Dockerfile

| # | Плохо | Почему | Исправлено в good.Dockerfile |
|---|-------|--------|------------------------------|
| 1 | `FROM python:latest` | сборка невоспроизводима (сейчас это 3.15, приложение писалось под 3.13), полный образ с компиляторами | `python:3.13-slim-trixie` |
| 2 | `apt-get update` отдельным `RUN`, лишние `vim gcc build-essential`, нет очистки | закэшированный индекс устаревает, +67 МБ мусора и поверхность атаки | системные пакеты не ставятся |
| 3 | `ADD . /app` до `pip install`, нет `.dockerignore` | любая правка кода сбрасывает кэш слоя зависимостей, в образ попадает лишнее | сначала `requirements.txt`, потом `main.py`; `good.Dockerfile.dockerignore` |
| 4 | `pip install fastapi uvicorn` | версии не закреплены, кэш pip в слое | `requirements.txt` с версиями, `--no-cache-dir`, multi-stage с venv |
| 5 | нет `USER` | процесс работает от root | пользователь `app` (uid 10001) |
| 6 | shell-форма `CMD` | PID 1 это `/bin/sh`, SIGTERM не доходит до uvicorn, `docker stop` ждёт 10 с и убивает SIGKILL | exec-форма `CMD [...]` |
| 7 | нет `HEALTHCHECK` | Docker не знает, живо ли приложение | `HEALTHCHECK` на `/healthz` |

| | bad | good |
|-|-----|------|
| размер образа | 1.23 ГБ | 145 МБ |
| пересборка после правки `main.py` | 7 с (`pip install` заново) | 2 с (всё из кэша) |
| `docker stop` | 10.1 с, exit 137 | 0.3 с, exit 0 |

## Плохие практики использования контейнера

1. Запуск без volume (`docker run -p 8000:8000 notes-app:1.0-good`). База окажется в записываемом слое и пропадёт при `docker rm` или обновлении образа.
2. Правка работающего контейнера через `docker exec` (`pip install`, `sed` по коду). Изменений нет в git и Dockerfile, они теряются при пересоздании, экземпляры одного образа начинают отличаться.

## Когда не стоит использовать контейнеры

1. Нужна сильная изоляция (недоверенный код разных клиентов): ядро общее с хостом, уязвимость ядра даёт выход из контейнера. Нужны VM или gVisor/Kata/Firecracker.
2. Нужно своё ядро или прямая работа с железом: драйверы и модули ядра, GUI-приложения, real-time, Windows-приложения на Linux. Контейнер тут только добавляет `--privileged` и проброс устройств.
