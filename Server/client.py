import asyncio
from typing import Dict

import websockets
import jsonpickle as jp
from nacl.public import PublicKey, Box

from Server.Client.OnionCryptographer import OnionCryptographer
from Server.ConnectionManager import MixerConnection
from Server.DTOs.Greeting import ClientGreetingDto, GreetingResultDto
from Server.Types import MixerName
from Server.server import get_mixers


class Client:
    def __init__(self):
        self.onion_crypt = OnionCryptographer()
        self.conn_manager = ClientConnectionManager(self.onion_crypt)

    async def run(self):
        task_bg = asyncio.create_task(self.background_update())
        await task_bg
        # Do smth OR run a task

    async def background_update(self):
        while True:
            await self.establish_connections_with_mixers()
            await asyncio.sleep(1)

    async def establish_connections_with_mixers(self):
        """Try to connect as many mixers as possible. Every second."""
        ip_by_name = await get_mixers()  # TODO request to tracker
        establishing_tasks = set()
        for mixer_name in ip_by_name:
            if mixer_name in self.conn_manager.conn_by_mixer_name:
                continue
            task = asyncio.create_task(self.establish_conn(mixer_name, ip=ip_by_name[mixer_name]))
            establishing_tasks.add(task)
            task.add_done_callback(establishing_tasks.discard)

    async def establish_conn(self, mixer: str, ip: str):
        """Try to connect with Mixer and handle this connection if succeed"""
        try:
            async with websockets.connect(ip) as websocket:
                # TODO only not connected.  TODO fix blocking connection atempt
                await websocket.send(
                    jp.encode(ClientGreetingDto(pub_name=self.onion_crypt.pub_name, pub_k=self.onion_crypt.pub_k)))
                raw = await websocket.recv()
                greet_result = jp.decode(raw)
                if type(greet_result) is not GreetingResultDto:
                    raise TypeError("Wrong greeting type")
                if greet_result.accepted:
                    connection = self.conn_manager.register_mixer(websocket, mixer, greet_result.pub_k)
                    try:
                        await self.handle_existing_connection(connection)
                    finally:
                        self.conn_manager.unregister(mixer)
        except ConnectionRefusedError:
            print(f"Client rejection", mixer)

    async def handle_existing_connection(self, connection: MixerConnection):
        async for raw_message in connection.websocket:
            message = jp.decode(raw_message)
            print(f'Client recieved {type(message)} from {connection.name}')
            # if type(message) is SecretMessageDto:
            #     print("received secret message", message)
            #     await handle_secret_message(message, connection)


class ClientConnectionManager:
    """ Keeps list of connections"""

    def __init__(self, crypt: OnionCryptographer):
        self.conn_by_mixer_name: Dict[str:MixerConnection] = dict()
        self.crypt: OnionCryptographer = crypt

    def register_mixer(self, websocket, name: MixerName, pub_k: PublicKey):
        created = MixerConnection(name, websocket, self.crypt.get_box(interlocutor_pub_k=pub_k))
        self.conn_by_mixer_name[name] = created
        return created

    def unregister(self, mixer: str):
        if mixer in self.conn_by_mixer_name:
            del self.conn_by_mixer_name[mixer]
        else:
            raise KeyError()


async def main():
    client = Client()
    await client.run()

    # try:
    #     async with websockets.connect("ws://localhost:8001") as websocket:
    #         await websocket.send(jp.encode(ClientGreetingDto()))
    #         cryptographer = OnionCryptographer()
    #         dto: SecretMessageDto = cryptographer.encrypt("Hi", ["8002", "8001"])
    #         await websocket.send(jp.encode(dto))
    #
    #         # msg = await websocket.recv()
    #         # print(msg)
    # except ConnectionRefusedError:
    #     print("refused")


if __name__ == '__main__':
    asyncio.run(main())
