# CRM-CC: стартовый каркас

## Что внутри
- `backend/` — FastAPI: /health, заготовки dialer'а (mock/ami), SSE-поток событий
- `frontend/` — React+Vite каркас: health-индикатор, SSE-подписка, кнопка старта мок-обзвона
- `docker-compose.yml` — dev-контур (db, redis, backend, frontend)

## Запуск локально (вне docker)
- backend: `pip install -r backend/requirements.txt && uvicorn app.main:app --reload --port 8001` (из каталога backend/)
- frontend: `cd frontend && npm i && npm run dev`

## Запуск через Portainer
1. Запушьте репозиторий в git.
2. Stacks -> Add stack -> Repository -> ветка main.
3. Environment variables — по образцу `.env.example` (TELEFONY=mock, BILLING_MODE=mock).
4. Deploy. Фронт: http://<хост>:81, API: http://<хост>:8001/health

## Проверка
- `/health` возвращает {"status":"ok", "telefony":"mock", ...}
- Кнопка «Старт обзвона» на фронте — в логе на странице появляются события:
  op_ring -> op_up -> dialing_subscriber -> call_connected -> call_finished -> campaign_done

## Следующие шаги
- Alembic + модели БД (Campaign, Contact, Call)
- Реализация AmiTelefony (panoramisk)
- shadcn/ui, TanStack Table/Query на фронте
