import argparse
import asyncio
import json
import jsonpickle as jp
import sys

from Server.DTOs.Message import RedirectMessageDto, FinalMessageDto
from Server.DTOs.SecretMessage import SecretMessageDto
from Server.Types import MixerName

sys.path.append('..')
import websockets
from sand import PORTS
from Server.DTOs.Greeting import GreetingDto, GreetingResultDto


async def get_mixers():
    return {str(x): f"ws://localhost:{x}" for x in PORTS}
    # return [
    #     "ws://localhost:8001",
    #     "ws://localhost:8002"
    # ]


async def establish_conn(mixer_name: MixerName, ip: str):
    try:
        async with websockets.connect(ip) as websocket:
            # TODO only not connected.  TODO fix blocking connection atempt
            await websocket.send(jp.encode(GreetingDto(name=SERVER_NAME)))
            raw = await websocket.recv()
            greet_result = jp.decode(raw)
            if greet_result.accepted:
                socket_by_name[mixer_name] = websocket
                try:
                    await handle_existing_connection(websocket)
                finally:
                    await unregister(mixer_name)
    except ConnectionRefusedError:
        print(f"{xport} rejection", mixer_name)


async def establish_connections_with_mixers():
    ip_by_name = await get_mixers()
    establishing_tasks = set()
    for mixer_name in ip_by_name:
        if SERVER_NAME == mixer_name:
            continue
        task = asyncio.create_task(establish_conn(mixer_name, ip=ip_by_name[mixer_name]))
        establishing_tasks.add(task)
        task.add_done_callback(establishing_tasks.discard)
        print(f"{xport} try connect to {mixer_name, ip_by_name[mixer_name]}")
    # print(f"{xport} Established", socket_by_name)


# async def handle_message2(websocket, event: SecretMessageDto):
#     mdto = jp.decode(event.body)
#     # decrypted
#     if type(mdto) is FinalMessageDto:
#         print("FINAL")
#         return  # save to db
#     if type(mdto) is RedirectMessageDto:
#         print("####")
#         print(f"I am {xport}", mdto.to, socket_by_name)
#         ws = socket_by_name.get(mdto.to)
#         if not ws:
#             raise KeyError(f"Couldn't find {mdto.to} in {list(socket_by_name.keys())}")
#         await ws.send(mdto.body)
#         print("resent")
#         return
#     raise RuntimeError(f"Couldn't resend a message {mdto}")


async def register(websocket) -> MixerName:
    raw = await websocket.recv()
    greeting = jp.decode(raw)
    if type(greeting) is not GreetingDto:
        raise ConnectionRefusedError("Wrong Greeting message")
    socket_by_name[greeting.name] = websocket
    await websocket.send(jp.encode(GreetingResultDto(accepted=True)))
    return greeting.name


async def unregister(mixer_name: MixerName):  # TODO delete async?
    print(f"unregister {mixer_name}")
    del socket_by_name[mixer_name]


async def handle_existing_connection(websocket):
    print(f"{xport} connections: {list(socket_by_name.keys())}")
    async for raw_message in websocket:
        message = jp.decode(raw_message)
        if type(message) is SecretMessageDto:
            print("received secret message", message)


async def handler(websocket):
    print(f"{xport} HANDLER")
    mixer_name = await register(websocket)
    try:
        print(f"{xport} registered {mixer_name}")
        await handle_existing_connection(websocket)
    finally:
        await unregister(mixer_name)


async def background_update():
    while True:
        await establish_connections_with_mixers()
        await asyncio.sleep(1)


async def run_server():
    async with websockets.serve(handler, "localhost", xport):
        await asyncio.Future()  # run forever


async def main(xport):
    # task = asyncio.create_task(establish_connections_with_mixers())
    # await task  # не должен блокировать # TODO explicitly return connections
    # async with websockets.serve(handler, "localhost", xport):
    #     await task
    #     await asyncio.Future()  # run forever
    print("!")
    task_bg = asyncio.create_task(background_update())
    task_serv = asyncio.create_task(run_server())
    await task_bg
    print("?")
    await task_serv


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("--xport", dest="xport", default=5000, type=int)
    args = parser.parse_args()
    xport = args.xport
    SERVER_NAME = str(xport)
    socket_by_name = {}
    asyncio.run(main(xport))
