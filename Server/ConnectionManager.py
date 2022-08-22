from nacl.public import PublicKey, Box
from typing import NamedTuple, Optional, Union, Dict
from abc import ABC, abstractmethod
import jsonpickle as jp
from websockets.legacy.protocol import WebSocketCommonProtocol

from Server.Cryptographer import Cryptographer
from Server.DTOs.Greeting import GreetingResultDto
from Server.Types import MixerName, ClientPubName


class MixerConnection(NamedTuple):
    name: str
    websocket: WebSocketCommonProtocol
    box: Box


class ClientConnection(NamedTuple):
    pub_name: str  # ~public_key в удобном формате, которым люди будут обмениваться
    websocket: WebSocketCommonProtocol
    box: Box


class ConnectionManager:
    def __init__(self, crypt: Cryptographer):
        self.conn_by_mixer_name: Dict[str, MixerConnection] = dict()
        self.conn_by_client_pub_name: Dict[str, ClientConnection] = dict()
        self.crypt = crypt

    def register_mixer(self, websocket, name: MixerName, pub_k: PublicKey):
        created = MixerConnection(name, websocket, self.crypt.get_box(interlocutor_pub_k=pub_k))
        self.conn_by_mixer_name[name] = created
        return created

    def register_client(self, pub_name: str, websocket, client_pub_k: PublicKey):
        created = ClientConnection(pub_name, websocket, self.crypt.get_box(interlocutor_pub_k=client_pub_k))
        self.conn_by_client_pub_name[pub_name] = created
        # TODO send ack?
        return created

    def get_ws_mixer_by_name(self, name: MixerName) -> MixerConnection:
        return self.conn_by_mixer_name[name]

    #
    def unregister(self, connection: Union[MixerConnection, ClientConnection]):
        if type(connection) is MixerConnection:
            del self.conn_by_mixer_name[connection.name]
            return
        if type(connection) is ClientConnection:
            del self.conn_by_client_pub_name[connection.pub_name]
            return  # TODO set not dict?
        raise KeyError()
