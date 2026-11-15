"""Слой телефонии: один интерфейс, две реализации (mock / AMI).

События уходят в asyncio.Queue, из которой SSE-эндпоинт отдаёт их фронтенду.
"""
import asyncio
import json
import random
from typing import AsyncGenerator

from app.config import settings

# имена событий — контракт фронтенда, менять только вместе с фронтом
DIALER_EVENTS = (
    "op_ring", "op_up", "dialing_subscriber",
    "call_connected", "call_finished", "campaign_done", "error",
)


class BaseTelefony:
    def __init__(self) -> None:
        self.queues: dict[str, asyncio.Queue] = {}

    def subscribe(self, ext: str) -> asyncio.Queue:
        self.queues.setdefault(ext, asyncio.Queue())
        return self.queues[ext]

    async def emit(self, ext: str, event: str, **payload) -> None:
        q = self.queues.get(ext)
        if q:
            await q.put({"event": event, **payload})

    async def start_campaign(self, ext: str, campaign_id: int) -> None:
        raise NotImplementedError

    async def stop(self, ext: str) -> None:
        raise NotImplementedError


class MockTelefony(BaseTelefony):
    """Проигрывает сценарий звонка таймерами — без Asterisk."""

    def __init__(self) -> None:
        super().__init__()
        self.running: dict[str, bool] = {}

    async def start_campaign(self, ext: str, campaign_id: int) -> None:
        self.running[ext] = True
        for i in range(5):  # мок-кампания: 5 контактов
            if not self.running.get(ext):
                return
            await self.emit(ext, "op_ring", call_id=i, contact=i)
            await asyncio.sleep(2)
            await self.emit(ext, "op_up", call_id=i)
            await asyncio.sleep(1)
            await self.emit(ext, "dialing_subscriber", call_id=i)
            await asyncio.sleep(random.uniform(3, 8))
            roll = random.random()
            if roll < 0.3:
                await self.emit(ext, "call_finished", call_id=i, result="NOANSWER")
            elif roll < 0.4:
                await self.emit(ext, "call_finished", call_id=i, result="BUSY")
            else:
                await self.emit(ext, "call_connected", call_id=i,
                                phone="+7917000000%d" % i, name="Абонент %d" % i)
                await asyncio.sleep(random.uniform(5, 15))
                await self.emit(ext, "call_finished", call_id=i, result="ANSWERED")
            await asyncio.sleep(3)  # wrapup
        await self.emit(ext, "campaign_done", total=5)

    async def stop(self, ext: str) -> None:
        self.running[ext] = False


class AmiTelefony(BaseTelefony):
    """Заготовка под реальную Asterisk (panoramisk). Заполним при подключении."""

    async def start_campaign(self, ext: str, campaign_id: int) -> None:
        # TODO: panoramisk Originate + обработка Newstate/DialBegin/DialStatus
        await self.emit(ext, "error",
                        detail="AMI не подключен: telefony=ami, реализация ещё не написана")

    async def stop(self, ext: str) -> None:
        pass


def get_telefony() -> BaseTelefony:
    if settings.telefony == "ami":
        return AmiTelefony()
    return MockTelefony()


telefony = get_telefony()


async def sse_stream(ext: str) -> AsyncGenerator[str, None]:
    q = telefony.subscribe(ext)
    while True:
        data = await q.get()
        yield f"data: {json.dumps(data, ensure_ascii=False)}\n\n"
