import logging
import os
from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from starlette.concurrency import run_in_threadpool

from secretmsgs.bus import Bus, NatsBus
from secretmsgs.envelope import VpnUnavailable, Wrapper, open_, seal

WEB = Path(__file__).parent.parent / "web"
log = logging.getLogger("chat")


def clean_name(name: str | None) -> str:
    return (name or "").strip()[:20] or "Guest"


def create_chat_app(bus: Bus, wrapper: Wrapper | None) -> FastAPI:
    sockets: set[WebSocket] = set()

    async def on_bus(payload: bytes) -> None:
        try:
            msg = await run_in_threadpool(open_, payload, wrapper)
        except Exception as e:
            log.warning("skipping unreadable message: %s", e)
            return
        out = {"type": "message", "from": msg.sender, "text": msg.text, "vpn": msg.vpn}
        for ws in list(sockets):
            try:
                await ws.send_json(out)
            except Exception:
                sockets.discard(ws)

    bus.subscribe(on_bus)

    @asynccontextmanager
    async def lifespan(app):
        await bus.start()
        yield
        await bus.stop()

    app = FastAPI(lifespan=lifespan)
    app.mount("/static", StaticFiles(directory=WEB), name="static")

    @app.get("/")
    async def index():
        return FileResponse(WEB / "chat.html")

    @app.websocket("/ws")
    async def ws(websocket: WebSocket, me: str | None = None):
        name = clean_name(me)
        await websocket.accept()
        sockets.add(websocket)
        try:
            while True:
                data = await websocket.receive_json()
                text = str(data.get("text", ""))
                if not text.strip():
                    continue
                try:
                    payload = await run_in_threadpool(seal, name, text, bool(data.get("vpn")), wrapper)
                except VpnUnavailable as e:
                    log.warning("vpn unavailable: %s", e)
                    await websocket.send_json({"type": "error", "reason": "vpn", "id": data.get("id")})
                    continue
                await bus.publish(payload)
        except WebSocketDisconnect:
            pass
        finally:
            sockets.discard(websocket)

    return app


def _from_env() -> FastAPI:
    wrapper = None
    if os.environ.get("ZT_VAULT_ADDR") and os.environ.get("ZT_VAULT_TOKEN"):
        from secretmsgs.vault import VaultTransit

        wrapper = VaultTransit(os.environ["ZT_VAULT_ADDR"], os.environ["ZT_VAULT_TOKEN"])
    return create_chat_app(NatsBus(os.environ.get("NATS_URL", "nats://localhost:4222")), wrapper)


app = _from_env()
