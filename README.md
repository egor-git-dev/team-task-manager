# Team Task Manager

Fullstack pet-проект для управления командной работой: пользователи, команды, задачи, комментарии, оценки выполненных задач, встречи и техническая админка.

## Стек

- FastAPI
- SQLAlchemy async
- Alembic
- PostgreSQL
- Pydantic
- JWT auth
- pytest
- sqladmin
- React + TypeScript + Vite
- Docker Compose

## Быстрый запуск

```bash
git clone https://github.com/egor-git-dev/team-task-manager.git
cd team-task-manager
cp .env.example .env
docker compose up --build
```

В другом терминале примените миграции:

```bash
docker compose exec api alembic upgrade head
```

Swagger доступен по адресу:

```text
http://127.0.0.1:8000/docs
```

Админ-панель доступна по адресу:

```text
http://127.0.0.1:8000/admin
```

## Переменные окружения

Перед запуском проверьте значения в `.env`.

Минимальный набор переменных:

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

По умолчанию в `.env` используется `POSTGRES_SERVER=localhost` — это удобно для локального запуска backend с PostgreSQL из Docker.

При запуске через Docker Compose значение для контейнера API переопределяется на `postgres`, потому что внутри Docker-сети база доступна по имени сервиса `postgres`.

## Архитектура backend

Backend разделён на слои:

- `api` — роутеры и зависимости FastAPI;
- `services` — бизнес-логика и проверки прав;
- `crud` — работа с базой данных;
- `models` — SQLAlchemy-модели;
- `schemas` — Pydantic-схемы;
- `core` — настройки, безопасность и общая конфигурация.

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

## Тесты

Для тестов нужен `TEST_DATABASE_URL` в `.env` и отдельная тестовая база PostgreSQL.

Пример:

```env
TEST_DATABASE_URL=postgresql+asyncpg://postgres:postgres@localhost:5432/team_task_manager_test
```

Если в `.env` используется нестандартный внешний порт PostgreSQL, например `POSTGRES_PORT=5433`, то в `TEST_DATABASE_URL` нужно указать этот же порт:

```env
TEST_DATABASE_URL=postgresql+asyncpg://postgres:postgres@localhost:5433/team_task_manager_test
```

Создать тестовую БД можно командой:

```bash
docker compose exec postgres psql -U postgres -c "CREATE DATABASE team_task_manager_test;"
```

Установите backend-зависимости локально, включая dev-зависимости:

```bash
python3.12 -m venv .venv
source .venv/bin/activate
pip install -e ".[dev]"
```

Запуск тестов:

```bash
pytest -q
```

## Покрытие тестами

Последний локальный запуск тестов показал общее покрытие:

```text
TOTAL: 1232 statements, 64 missed, 95% coverage
```

Основные API-роуты, схемы, модели и service-слой покрыты тестами на 90–100%.  

Для просмотра отчёта покрытия:

```bash
pytest --cov=app --cov-report=term-missing
```

## Роли

- `user` — обычный участник команды.
- `manager` — управляет задачами и встречами.
- `admin` — управляет командой: создание команды, код приглашения, роли, удаление участников.
- `is_superuser` — технический доступ в `/admin`, не бизнес-роль.

## Назначение администратора

После регистрации пользователя роль можно выдать через БД.

Зайти в PostgreSQL:

```bash
docker compose exec postgres psql -U postgres -d team_task_manager
```

Сделать пользователя одновременно бизнес-админом и superuser:

```sql
UPDATE users
SET role = 'admin',
    is_superuser = true
WHERE email = 'user@example.com';
```

`role = 'admin'` используется в бизнес-логике команд, а `is_superuser = true` нужен только для доступа к технической админке.

## Возможности

- регистрация и авторизация пользователей через JWT;
- команды и вступление по invite-коду;
- роли user / manager / admin;
- создание и назначение задач;
- комментарии к задачам;
- оценки выполненных задач;
- вывод средней оценки пользователя;
- встречи между участниками команды;
- отображение задач и встреч в календаре;
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
9. Пользователь видит свои оценки и средний балл.
10. Пользователь просматривает свои задачи и встречи в календаре.

## Админка

Доступ в `/admin` разрешён только пользователям с `is_superuser = true`.

Админка используется для технического управления существующими данными. Основные бизнес-сценарии необходимо проверять через API или frontend.
