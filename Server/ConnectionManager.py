from typing import NamedTuple, Optional, Union
from abc import ABC, abstractmethod
import jsonpickle as jp
from websockets.legacy.protocol import WebSocketCommonProtocol

from Server.DTOs.Greeting import GreetingResultDto
from Server.Types import MixerName


class MixerConnection(NamedTuple):
    name: str
    websocket: WebSocketCommonProtocol


class ClientConnection(NamedTuple):
    pub_k: str
    websocket: WebSocketCommonProtocol


class ConnectionManager:
    def __init__(self):
        self.connection_by_mixer_name = dict()
        self.socket_by_client_pub_k = dict()

    def register_mixer(self, websocket, name: MixerName):
        created = MixerConnection(name, websocket)
        self.connection_by_mixer_name[name] = created
        return created

    def register_client(self, websocket, pub_k):
        created = ClientConnection(pub_k, websocket)
        self.socket_by_client_pub_k[pub_k] = created
        # TODO send ack?
        return created

    def get_ws_mixer_by_name(self, name: MixerName) -> WebSocketCommonProtocol:
        return self.connection_by_mixer_name[name].websocket

    #
    def unregister(self, connection: Union[MixerConnection, ClientConnection]):
        if type(connection) is MixerConnection:
            del self.connection_by_mixer_name[connection.name]
            return
        if type(connection) is ClientConnection:
            del self.socket_by_client_pub_k[connection.pub_k]
            return  # TODO set not dict?
        raise KeyError()
