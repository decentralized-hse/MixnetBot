import random
import json
import requests
import time
from Protocol.FieldType import Field


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
        self.buffer_size = 0
        self.connection_manager = connection_manager

    def fill_by_junk(self):
        servers = self.connection_manager.get_all_servers()
        if len(self.messages) < self.buffer_size:
            for i in range(self.buffer_size - len(self.messages)):
                junk_mes = {Field.to: None,
                            Field.body: "J" * random.randrange(0, 100)}
                receiver = servers[random.randrange(0, len(servers))] + "/message"
                self.append_message(MessageTask(url=receiver, data=junk_mes))

    def send_mixed(self):
        while True:
            time.sleep(self.send_interval)
            # self.fill_by_junk()
            random.shuffle(self.messages)
            for message in self.messages:
                message.send()
            self.messages.clear()

    def append_message(self, mes: MessageTask):
        self.messages.append(mes)
