from fastapi import FastAPI, WebSocket
import asyncio
import numpy as np
import math
from datetime import datetime

app = FastAPI()

@app.websocket("/ws/ticks")
async def send_ticks(websocket: WebSocket):
    await websocket.accept()
    price = 100.0
    while True:
        price *= math.exp(np.random.normal(0, 0.01))
        await websocket.send_json({
            "time": str(datetime.now().strftime("%M:%S")),
            "price": round(price, 2)
        })
        await asyncio.sleep(1)