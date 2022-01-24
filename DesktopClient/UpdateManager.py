import datetime
import json
import random
import sys
import time
from threading import Thread
from dateutil import parser
import requests

from DesktopClient.db.MailRepository import MessageDirection
from Protocol.UpdateRequest import UpdateReq
from utils.coding import unpack_obj, pack_k, pack_obj, unpack_str, unpack_pub_k

sys.path.append('../')
from Protocol.FieldType import Field



class UpdateManager:
    def __init__(self, conn_manager, key_manager, repo):
        self.conn_manager = conn_manager
        self.key_manager = key_manager
        self.repo = repo

    def start(self):
        thread = Thread(target=self.background_update, daemon=True)
        thread.start()
        return self

    def background_update(self):
        while True:
            self.get_updates()
            time.sleep(1)

    def get_updates(self, all_messages=False):
        try:
            server = random.choice(self.conn_manager.get_online_servers())
        except RuntimeError:
            # print("All offline", self.conn_manager.connections)
            return [], []
        upd_request = self.get_update_request_message(all_messages)
        try:
            response = requests.get(url=f"{server.addr}/messages", data=pack_obj(upd_request, server.pub_k))
            return self.parse_updates(response)
        except requests.exceptions.RequestException:
            return [], []

    def parse_updates(self, response):
        try:
            d = unpack_obj(data=response.text, sk=self.key_manager.sk)
        except:
            return [], []
        senders = set()
        messages = []
        for m in d["messages"]:
            encrypted = json.loads(m)
            unp = unpack_obj(encrypted[Field.body], self.key_manager.sk)
            sender_pub_k = unpack_pub_k(unp[Field.sender_pub_k])
            mes = unpack_str(unp[Field.body], self.key_manager.sk, sender_pub_k)
            ts = parser.parse(unp[Field.timestamp])
            self.repo.mail.add_message(unp[Field.sender_pub_k], mes, ts,
                                       unp[Field.uid], direction=MessageDirection.incoming)
            self.repo.user.add_user(name=unp[Field.name], pub_k=unp[Field.sender_pub_k])
            senders.add(unp[Field.sender_pub_k])
            messages.append(mes)
        return list(senders), messages

    def get_update_request_message(self, all_messages=False):
        res = {UpdateReq.sender_public_key: pack_k(self.key_manager.pk),
               UpdateReq.last_message_time: datetime.datetime(1975, 1,
                                                              1).isoformat() if all_messages else self.repo.mail.get_last_message_time()}
        return res
