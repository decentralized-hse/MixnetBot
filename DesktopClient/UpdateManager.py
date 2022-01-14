import json
import random
import sys
import time

import requests

from Protocol.UpdateRequest import UpdateReq
from utils.coding import base64_str_to_public_key, unpack_obj, pack_k, pack_obj, unpack_str, unpack_pub_k

sys.path.append('../')
from Protocol.FieldType import Field
from multiple_encryption import multiple_encrypt, get_pub_keys


class UpdateManager:
    def __init__(self):
        def get_updates(self):
            try:
                server = random.choice(self.conn_manager.get_online_servers())
            except RuntimeError:  # all offline
                return [], []
            upd_request = get_update_request_message()
            try:
                response = requests.get(url=f"{server.addr}/messages", data=pack_obj(upd_request, server.pub_k))
                return self.parse_updates(response)
            except requests.exceptions.RequestException:
                return [], []

        def parse_updates(self, response):
            try:
                d = unpack_obj(data=response.text, sk=keys.private_key)
            except:
                return [], []
                # raise Exception(response.text)
            senders = set()
            messages = []
            for m in d["messages"]:
                encrypted = json.loads(m)
                unp = unpack_obj(encrypted[Field.body], keys.private_key)
                sender_pub_k = unpack_pub_k(unp[Field.sender_pub_k])
                # TODO Если упало с ошибкой, то сообщение - подделка
                mes = unpack_str(unp[Field.body], keys.private_key, sender_pub_k)
                self.mail_repo.add_message(unp[Field.sender_pub_k], mes, unp[Field.timestamp],
                                           unp[Field.uid])
                senders.add(unp[Field.sender_pub_k])
                messages.append(unp[Field.body])
            return list(senders), messages

        def get_update_request_message():
            return {UpdateReq.sender_public_key: pack_k(keys.public_key),
                    UpdateReq.last_message_time: mail_repo.get_last_message_time(),
                    UpdateReq.all_message_hash: mail_repo.get_all_messages_hash()}