import argparse
import asyncio
import json
import jsonpickle as jp
import sys

from Server.DTOs.Message import RedirectMessageDto, FinalMessageDto
from Server.DTOs.SecretMessage import SecretMessageDto

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


async def establish_connections_with_mixers(connections):
    ip_by_name = await get_mixers()
    for mixer_name in ip_by_name:
        if name == mixer_name:
            continue
        try:
            print(f"{xport} try connect to {mixer_name}")
            async with websockets.connect(ip_by_name[mixer_name],
                                          ping_interval=2) as websocket:
                # TODO only not connected.  TODO fix blocking connection atempt
                await websocket.send(jp.encode(GreetingDto(name=name)))
                raw = await websocket.recv()
                greet_result = jp.decode(raw)
                if greet_result.accepted:
                    connections[mixer_name] = websocket
        except ConnectionRefusedError:
            print(f"{xport} refused", mixer_name)
    print(f"{xport} Established", connections)
    if connections:
        print(list(connections.values())[0], "*****")
    # return connections


async def send_acceptance(websocket, greeting: GreetingDto):
    # print(f"{xport} found greet request", websocket.request_headers)

    connections[greeting.name] = websocket
    await websocket.send(jp.encode(GreetingResultDto(accepted=True)))


async def handle_message(websocket, event: SecretMessageDto):
    mdto = jp.decode(event.body)
    # decrypted
    if type(mdto) is FinalMessageDto:
        print("FINAL")
        return  # save to db
    if type(mdto) is RedirectMessageDto:
        print("####")
        print(f"I am {xport}", mdto.to, connections)
        ws = connections.get(mdto.to)
        if not ws:
            raise KeyError(f"Couldn't find {mdto.to} in {list(connections.keys())}")
        await ws.send(mdto.body)
        print("resent")
        return
    raise RuntimeError(f"Couldn't resend a message {mdto}")


async def router(websocket):
    message = await websocket.recv()
    event = jp.decode(message)
    if type(event) is GreetingDto:
        # print(f"{xport} GDto {websocket.response_headers['Host']}")
        await send_acceptance(websocket, event)
        print(f"{xport} Now cons:", connections)
    if type(event) is SecretMessageDto:
        print("received secret message", event)
        await handle_message(websocket, event)
    #     if "join" in event:
    #         # Second player joins an existing game.
    #         await join(websocket, event["join"])
    #     elif "watch" in event:
    #         # Spectator watches an existing game.
    #         await watch(websocket, event["watch"])
    #     else:
    #         # First player starts a new game.
    #         await start(websocket)
    # async for message in websocket:
    #     print("received form client" + message)
    #     await websocket.send("Hi from server")


async def main(xport):
    await establish_connections_with_mixers(connections)  # TODO explicit return connections

    async with websockets.serve(router, "localhost", xport):
        await asyncio.Future()  # run forever


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("--xport", dest="xport", default=5000, type=int)
    args = parser.parse_args()
    xport = args.xport
    name = str(xport)
    connections = {}
    asyncio.run(main(xport))
