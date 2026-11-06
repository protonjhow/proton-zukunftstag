import os
from collections import deque
from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

from secretmsgs.bus import Bus, NatsBus
from secretmsgs.eve import load_wordlist, peek

ROOT = Path(__file__).parent.parent
WEB = ROOT / "web"


def create_eve_app(bus: Bus, words: frozenset[str]) -> FastAPI:
    """Eve only ever sees what crosses the bus. She has no Vault access."""
    history: deque[dict] = deque(maxlen=50)
    sockets: set[WebSocket] = set()

    async def on_bus(payload: bytes) -> None:
        sighting = peek(payload, words).to_json()
        history.append(sighting)
        for ws in list(sockets):
            try:
                await ws.send_json({"type": "sighting", **sighting})
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
        return FileResponse(WEB / "eve.html")

    @app.websocket("/ws")
    async def ws(websocket: WebSocket):
        await websocket.accept()
        await websocket.send_json({"type": "history", "sightings": list(history)})
        sockets.add(websocket)
        try:
            while True:
                await websocket.receive_text()
        except WebSocketDisconnect:
            pass
        finally:
            sockets.discard(websocket)

    return app


app = create_eve_app(
    NatsBus(os.environ.get("NATS_URL", "nats://localhost:4222")),
    load_wordlist(os.environ.get("EVE_WORDLIST", str(ROOT / "wordlists" / "en.txt"))),
)
