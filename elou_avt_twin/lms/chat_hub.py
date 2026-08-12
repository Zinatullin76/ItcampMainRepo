"""
lms/chat_hub.py
================
Тонкий хаб для многооператорского чата практики. Держит набор подключённых
WebSocket-клиентов `/ws/chat` и рассылает сообщения, опубликованные через REST
`POST /lms/chat/send`. Вызов `broadcast()` безопасен из любого потока
(в т.ч. из sync-обработчика FastAPI, выполняющегося в threadpool).
"""

from __future__ import annotations

import asyncio
import logging
from typing import Any, Dict, Optional, Set

logger = logging.getLogger("elou_avt.lms")

_clients: Set[Any] = set()
_loop: Optional[asyncio.AbstractEventLoop] = None


def register(websocket: Any) -> None:
    global _loop
    try:
        _loop = asyncio.get_event_loop()
    except RuntimeError:
        _loop = None
    _clients.add(websocket)


def unregister(websocket: Any) -> None:
    _clients.discard(websocket)


def broadcast(payload: Dict[str, Any]) -> None:
    if not _clients:
        return
    loop = _loop
    if loop is None or loop.is_closed():
        return
    asyncio.run_coroutine_threadsafe(_send_all(payload), loop)


async def _send_all(payload: Dict[str, Any]) -> None:
    dead = []
    for ws in list(_clients):
        try:
            await ws.send_json(payload)
        except Exception:
            dead.append(ws)
    for ws in dead:
        _clients.discard(ws)
