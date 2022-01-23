import random
import sys

sys.path.append('../')
import requests
import time
from Protocol.FieldType import Field
from utils.coding import pack_obj


class MessageTask:
    def __init__(self, url: str, data):
        self.url = url
        self.data = data

    def send(self):
        try:
            requests.post(url=self.url, data=self.data)
        except ConnectionError:
            pass
            # TODO add to queue again. But make an attempt only n times


class MessageQueue:
    def __init__(self, connection_manager):
        self.messages = list()
        self.send_interval = 1
        self.buffer_size = 5
        self.connection_manager = connection_manager

    def fill_by_junk(self):
        servers = self.connection_manager.get_online_servers()
        if len(self.messages) < self.buffer_size:
            for i in range(self.buffer_size - len(self.messages)):
                junk_mes = {Field.to: None,
                            Field.body: "J" * random.randrange(100, 300),
                            Field.is_junk: True,
                            Field.cypher_count: 1}
                s = servers[random.randrange(0, len(servers))]
                receiver = s.addr + "/message"
                encrypted = pack_obj(junk_mes, s.pub_k)
                self.append_message(MessageTask(url=receiver, data=encrypted))

    def send_mixed(self):
        while True:
            time.sleep(self.send_interval)
            try:
                self.fill_by_junk()
            except:
                pass
            random.shuffle(self.messages)
            for message in self.messages:
                message.send()
            self.messages.clear()

    def append_message(self, mes: MessageTask):
        self.messages.append(mes)
