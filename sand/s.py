import asyncio
import websockets


async def echo(websocket):
    async for message in websocket:
        print("received form client" + message)
        await websocket.send("Hi from server")


async def main():
    async with websockets.serve(echo, "localhost", 5000):
        await asyncio.Future()  # run forever


asyncio.run(main())
