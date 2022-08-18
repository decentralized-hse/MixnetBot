import asyncio
import websockets


async def hello():
    try:
        async with websockets.connect("ws://localhost:5000") as websocket:
            await websocket.send("Hello world! Im client ")

            msg = await websocket.recv()
            print(msg)
    except ConnectionRefusedError:
        print("refused")


asyncio.run(hello())
