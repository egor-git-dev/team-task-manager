# Team Task Manager

Учебный fullstack-проект для управления командными задачами: пользователи, команды, задачи, комментарии, оценки, встречи, календарь и техническая админка.

## Стек

- FastAPI
- SQLAlchemy async
- Alembic
- PostgreSQL
- JWT auth
- pytest
- React + TypeScript + Vite
- Docker Compose

## Переменные окружения

Создайте `.env` из примера:

```bash
cp .env.example .env
```

Минимально нужно заполнить:

```env
POSTGRES_USER=postgres
POSTGRES_PASSWORD=postgres
POSTGRES_DB=team_task_manager
POSTGRES_PORT=5432
POSTGRES_SERVER=localhost

SECRET_KEY=change_me
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
```

Для запуска через Docker Compose `POSTGRES_SERVER=localhost` оставляем как есть: внутри контейнера API значение переопределяется на `postgres`.

## Архитектура backend

Backend разделён на слои:

- `api` — роутеры и зависимости FastAPI;
- `services` — бизнес-логика и проверки прав;
- `crud` — работа с базой данных;
- `models` — SQLAlchemy-модели;
- `schemas` — Pydantic-схемы;
- `core` — настройки, безопасность и общая конфигурация.

## Запуск backend через Docker

```bash
docker compose up --build
```

В другом терминале примените миграции:

```bash
docker compose exec api alembic upgrade head
```

Проверка:

```bash
curl http://127.0.0.1:8000/api/v1/health
```

Swagger:

```text
http://127.0.0.1:8000/docs
```

## Запуск frontend

Frontend запускается отдельно:

```bash
cd frontend
npm install
npm run dev
```

Откройте адрес, который покажет Vite. Обычно:

```text
http://127.0.0.1:5173/
```

Frontend проксирует `/api` на backend `http://127.0.0.1:8000`.

## Тесты

Для тестов нужен `TEST_DATABASE_URL` в `.env` и отдельная тестовая база PostgreSQL.

То есть для тестов один раз нужно создать БД вручную, например:

```bash
docker compose exec postgres psql -U postgres -c "CREATE DATABASE team_task_manager_test;"
```

Запуск:

```bash
pytest -q
```

## Роли

- `user` — обычный участник команды.
- `manager` — управляет задачами и встречами.
- `admin` — управляет командой: создание команды, код приглашения, роли, удаление участников.
- `is_superuser` — технический доступ в `/admin`, не бизнес-роль.

## Возможности

- регистрация и авторизация пользователей через JWT;
- команды и вступление по invite-коду;
- роли user / manager / admin;
- создание и назначение задач;
- комментарии к задачам;
- оценки выполненных задач;
- встречи между участниками команды;
- техническая админка для управления данными.

## Основные сценарии

1. Зарегистрировать пользователя.
2. Выдать нужную роль через админку или БД.
3. Admin создаёт команду и получает код приглашения.
4. Пользователи вступают в команду по коду.
5. Manager/Admin создаёт задачи и встречи, выбирая участников по email.
6. Исполнитель меняет статус задачи.
7. Участники обсуждают задачу в комментариях.
8. Manager/Admin оценивает выполненную задачу.

## Админка

Админ-панель доступна по адресу:

```text
http://127.0.0.1:8000/admin
```

Доступ разрешён только пользователям с `is_superuser = true`.

Админка используется для технического управления существующими данными. Основные бизнес-сценарии необходимо проверять через API или frontend.
