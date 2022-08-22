from typing import Optional, Union
import argparse
import asyncio
import json
import jsonpickle as jp
import sys

from Server.ConnectionManager import ConnectionManager, MixerConnection, ClientConnection
from Server.Cryptographer import Cryptographer, BoxAdapter
from Server.DTOs.Message import RedirectMessageDto, FinalMessageDto
from Server.DTOs.SecretMessage import SecretMessageDto
from Server.Types import MixerName

sys.path.append('..')
import websockets
from launcher import PORTS
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
            await websocket.send(jp.encode(GreetingDto(name=SERVER_NAME, pub_k=crypt.pub_k)))
            raw = await websocket.recv()
            greet_result = jp.decode(raw)
            if greet_result.accepted:
                connection = connection_manager.register_mixer(websocket, mixer_name, greet_result.pub_k)
                try:
                    await handle_existing_connection(connection)
                finally:
                    connection_manager.unregister(connection)
    except ConnectionRefusedError:
        print(f"{xport} rejection", mixer_name)


async def establish_connections_with_mixers():
    ip_by_name = await get_mixers()
    establishing_tasks = set()
    connected = connection_manager.conn_by_mixer_name
    # print(f"{xport} cons: {[c for c in connection_manager.connection_by_mixer_name]}")

    for mixer_name in ip_by_name:
        if SERVER_NAME == mixer_name or mixer_name in connected:
            continue
        task = asyncio.create_task(establish_conn(mixer_name, ip=ip_by_name[mixer_name]))
        establishing_tasks.add(task)
        task.add_done_callback(establishing_tasks.discard)
        print(f"{xport} try connect to {mixer_name, ip_by_name[mixer_name]}")


async def handle_existing_connection(connection: Union[MixerConnection, ClientConnection]):
    async for raw_message in connection.websocket:
        message = jp.decode(raw_message)
        if type(message) is SecretMessageDto:
            print("received secret message", message)
            await handle_secret_message(message, connection)


async def handle_secret_message(message: SecretMessageDto, connection: Union[MixerConnection, ClientConnection]):
    decrypted: str = BoxAdapter.decrypt(connection.box, message.body)
    dto = jp.decode(decrypted)
    print(f"{xport} decyphered. {dto}")
    if type(dto) is RedirectMessageDto:
        mixer_conn = connection_manager.get_ws_mixer_by_name(dto.to)
        websocket = mixer_conn.websocket
        encrypted = BoxAdapter.encrypt(mixer_conn.box, dto.body)
        await websocket.send(jp.encode(SecretMessageDto(body=encrypted)))
    if type(dto) is FinalMessageDto:
        print(f"{xport} FINAL. {dto}")


async def handler(websocket):
    raw = await websocket.recv()
    greeting = jp.decode(raw)
    if type(greeting) is GreetingDto:
        await websocket.send(jp.encode(GreetingResultDto(accepted=True, pub_k=crypt.pub_k)))
        connection = connection_manager.register_mixer(
            websocket, greeting.name, greeting.pub_k)
    elif type(greeting) is ClientGreetingDto:
        await websocket.send(jp.encode(GreetingResultDto(accepted=True, pub_k=crypt.pub_k)))
        connection = connection_manager.register_client(greeting.pub_name,
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


async def main():
    task_bg = asyncio.create_task(background_update())
    task_serv = asyncio.create_task(run_server())
    await task_bg
    await task_serv


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("--xport", dest="xport", default=5000, type=int)
    args = parser.parse_args()
    xport = args.xport
    crypt = Cryptographer()
    SERVER_NAME = str(xport)
    connection_manager = ConnectionManager(crypt)
    asyncio.run(main())
