import datetime
import time
from collections import namedtuple
from threading import Thread
import sys

sys.path.append('../')
import requests

from FlaskBots.Network import get_all_servers
from utils.coding import unpack_pub_k

ServerInfo = namedtuple('ServerInfo', ['addr', 'last_online_dt', 'pub_k'])


class ConnectionManager:
    def __init__(self, is_server):
        self.connections = {}  # TODO энергонезависимый кэш
        self.is_server = is_server
        for server in get_all_servers():
            self.connections[server] = ConnectionInfo(datetime.datetime(1980, 1, 1), None)

    def start(self):
        thread = Thread(target=self.ping_online_servers, daemon=True)
        thread.start()
        time.sleep(3)
        return self

    def ping_online_servers(self):
        while True:
            for mixer in self.connections.keys():
                try:
                    response = requests.get(f"{mixer}/public-key")
                    pub_k = unpack_pub_k(response.json()['public_key'])
                    self.connections[mixer] = ConnectionInfo(last_online_dt=datetime.datetime.now(),
                                                             pub_k=pub_k)
                    print("PING SUCCESS", mixer)
                    time.sleep(1)
                except requests.exceptions.RequestException:
                    pass  # TODO log

    def get_online_servers(self):
        res = [s for s in self.get_all_servers() if is_online(s.last_online_dt)]
        if not res:
            raise RuntimeError(f"All servers are offline: {self.get_all_servers()}")
        return res

    def get_server_pub_k(self, server):
        server_info = self.connections[server]
        if server_info.is_online():
            return server_info.pub_k
        else:
            raise Exception("Attempt to get pub_k of offline server")

    def get_all_servers(self):
        return [ServerInfo(addr, info.last_online_dt, info.pub_k)
                for addr, info in self.connections.items()]


def is_online(last_online_dt):
    now = datetime.datetime.now()
    delta = now - last_online_dt
    return delta.total_seconds() < 10


class ConnectionInfo:
    def __init__(self, last_online_dt, pub_k):
        self.last_online_dt = last_online_dt
        self.pub_k = pub_k

    def __str__(self):
        return f"{self.last_online_dt, self.is_online()}"

    def __repr__(self):
        return self.__str__()

    def is_online(self):
        return is_online(self.last_online_dt)
