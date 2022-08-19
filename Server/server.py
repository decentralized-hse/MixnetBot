from typing import Optional, Union
import argparse
import asyncio
import json
import jsonpickle as jp
import sys

from Server.ConnectionManager import ConnectionManager, MixerConnection, ClientConnection
from Server.DTOs.Message import RedirectMessageDto, FinalMessageDto
from Server.DTOs.SecretMessage import SecretMessageDto
from Server.Types import MixerName

sys.path.append('..')
import websockets
from sand import PORTS
from Server.DTOs.Greeting import GreetingDto, GreetingResultDto, ClientGreetingDto


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
                connection = connection_manager.register_mixer(websocket, mixer_name)
                try:
                    await handle_existing_connection(connection)
                finally:
                    connection_manager.unregister(connection)
    except ConnectionRefusedError:
        print(f"{xport} rejection", mixer_name)
    print("*******")


async def establish_connections_with_mixers():
    ip_by_name = await get_mixers()
    establishing_tasks = set()
    connected = connection_manager.socket_by_mixer_name
    print(f"{xport} cons: {[c for c in connection_manager.socket_by_mixer_name]}")

    for mixer_name in ip_by_name:
        if SERVER_NAME == mixer_name or mixer_name in connected:
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

async def handle_existing_connection(connection: Union[MixerConnection, ClientConnection]):
    async for raw_message in connection.websocket:
        message = jp.decode(raw_message)
        if type(message) is SecretMessageDto:
            print("received secret message", message)


async def handler(websocket):
    raw = await websocket.recv()
    greeting = jp.decode(raw)
    if type(greeting) is GreetingDto:
        await websocket.send(jp.encode(GreetingResultDto(accepted=True)))
        connection = connection_manager.register_mixer(
            websocket, greeting.name)
    elif type(greeting) is ClientGreetingDto:
        connection = await connection_manager.register_client(
            websocket, greeting.pub_k)
    else:
        raise TypeError("Wrong Greeting")
    try:
        await handle_existing_connection(connection)
    finally:
        connection_manager.unregister(connection)


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
    await task_serv


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("--xport", dest="xport", default=5000, type=int)
    args = parser.parse_args()
    xport = args.xport
    SERVER_NAME = str(xport)
    connection_manager = ConnectionManager()
    asyncio.run(main(xport))
