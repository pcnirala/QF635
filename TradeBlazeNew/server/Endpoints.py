import aiosqlite
import bcrypt
from fastapi import APIRouter, HTTPException, status
from fastapi import WebSocket, WebSocketDisconnect

from Dashboard import *
from TradingStrategy import *


class Endpoints:
    # using static vars because we need to access them from static methods
    _logger = logging.getLogger(__name__)

    _trading_strategy = TradingStrategy.get_instance()

    _dashboard = Dashboard()

    _ws_clients = set()

    _router = APIRouter()

    def __init__(self):
        raise NotImplementedError("Can't create object of util class")

    @classmethod
    def get_router(cls):
        return cls._router

    # Websocket endpoints
    @staticmethod
    @_router.websocket("/ws/livefeed")
    async def websocket_endpoint(websocket: WebSocket):
        await websocket.accept()
        Endpoints._ws_clients.add(websocket)
        Endpoints._logger.info(f"Created new websocket connection: {websocket}")
        Endpoints._logger.info(f"Websocket clients count: {len(Endpoints._ws_clients)}")
        try:
            await websocket.send_json(Endpoints._dashboard.get_last_dashboard_data())
            while True:
                data = await Endpoints._dashboard.get_realtime_dashboard_update()
                await websocket.send_json(data)
                await asyncio.sleep(0)  # because `while True`
        except WebSocketDisconnect:
            Endpoints._ws_clients.remove(websocket)
            Endpoints._logger.info(f"Removed websocket connection: {websocket}")
            Endpoints._logger.info(f"Websocket clients count: {len(Endpoints._ws_clients)}")

    # REST endpoints are here
    @staticmethod
    @_router.post("/api/reset-dashboard")
    async def reset_dashboard():
        Endpoints._logger.info("Resetting dashboard")
        Endpoints._dashboard.reset_dashboard_data()
        return {"status": "Reset Success"}

    @staticmethod
    @_router.post("/api/pause-trading-engine")
    async def pause_trading_engine():
        Endpoints._logger.info(f"Pausing trading engine: {Endpoints._trading_strategy}")
        Endpoints._trading_strategy.pause_trading_engine()
        return {"status": "Pause Success"}

    @staticmethod
    @_router.post("/api/resume-trading-engine")
    async def resume_trading_engine():
        Endpoints._logger.info(f"Resuming trading engine: {Endpoints._trading_strategy}")
        Endpoints._trading_strategy.resume_trading_engine()
        return {"status": "Resume Success"}

    @staticmethod
    @_router.post("/api/login")
    async def login(request: LoginRequest):
        Endpoints._logger.info(f"Login request for user: {request.username}")
        async with aiosqlite.connect("data/users.db") as db:
            cursor = await db.execute("SELECT hashed_password FROM users WHERE username = ?", (request.username,))
            row = await cursor.fetchone()
            await cursor.close()

            if row is None:
                raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")

            stored_hash = row[0]
            if not bcrypt.checkpw(request.password.encode(), stored_hash.encode()):
                raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")

            Endpoints._logger.info(f"Login success for user: {request.username}")
            return LoginResponse(status="Login Success",
                                 is_trading_engine_paused=Endpoints._trading_strategy.is_trading_engine_paused())
