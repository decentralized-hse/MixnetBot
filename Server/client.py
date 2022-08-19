import asyncio
import websockets
import jsonpickle as jp

from Server.DTOs.Greeting import ClientGreetingDto
from Server.DTOs.Message import RedirectMessageDto
from Server.DTOs.SecretMessage import SecretMessageDto
from Server.OnionCryptographer import OnionCryptographer


async def hello():
    try:
        async with websockets.connect("ws://localhost:8001") as websocket:
            await websocket.send(jp.encode(ClientGreetingDto()))
            cryptographer = OnionCryptographer()
            dto: SecretMessageDto = cryptographer.encrypt("Hi", ["8002", "8001"])
            await websocket.send(jp.encode(dto))

            # msg = await websocket.recv()
            # print(msg)
    except ConnectionRefusedError:
        print("refused")


asyncio.run(hello())
