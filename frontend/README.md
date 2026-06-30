# Фронтенд менеджера задач

React + TypeScript + Vite интерфейс для FastAPI backend.

## Запуск

Сначала должен быть запущен backend на `http://127.0.0.1:8000`.

```bash
npm install
npm run dev
```

Открыть приложение:

```text
http://127.0.0.1:5173/
```

## Проверки

```bash
npm run lint
npm run build
```

Vite проксирует запросы `/api` на backend, поэтому CORS для локальной разработки не нужен.
