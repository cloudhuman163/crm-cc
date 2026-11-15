import asyncio

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from redis import asyncio as aioredis
from sqlalchemy import text

from app.config import settings
from app.db import engine
from app.telefony import telefony, sse_stream

from .auth import router as auth_router
app.include_router(auth_router)

app = FastAPI(title="CRM-CC API", version="0.1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],   # dev; в бою — конкретный origin
    allow_methods=["*"],
    allow_headers=["*"],
)


class Health(BaseModel):
    status: str
    telefony: str
    billing_mode: str
    db: str
    redis: str


@app.get("/health", response_model=Health)
async def health():
    db_ok = redis_ok = "ok"
    try:
        async with engine.connect() as conn:
            await conn.execute(text("SELECT 1"))
    except Exception as e:
        db_ok = f"fail: {type(e).__name__}"
    try:
        r = aioredis.from_url(settings.redis_url)
        await r.ping()
    except Exception as e:
        redis_ok = f"fail: {type(e).__name__}"
    status = "ok" if db_ok == redis_ok == "ok" else "degraded"
    return Health(status=status, telefony=settings.telefony,
                  billing_mode=settings.billing_mode, db=db_ok, redis=redis_ok)


@app.post("/dialer/{campaign_id}/start")
async def dialer_start(campaign_id: int, ext: str = "101"):
    # в dev мок сам проигрывает сценарий; в stage/прод — реальный dialer
    asyncio.create_task(telefony.start_campaign(ext, campaign_id))
    return {"status": "started", "telefony": settings.telefony}


@app.post("/dialer/stop")
async def dialer_stop(ext: str = "101"):
    await telefony.stop(ext)
    return {"status": "stopped"}


@app.get("/dialer/events")
async def dialer_events(ext: str = "101"):
    return StreamingResponse(sse_stream(ext), media_type="text/event-stream",
                             headers={"Cache-Control": "no-cache",
                                      "X-Accel-Buffering": "no"})
