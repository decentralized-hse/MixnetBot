import datetime
import sys
import uuid

import requests

from DesktopClient.KeyManager import KeyManager
from DesktopClient.UpdateManager import UpdateManager
from FlaskBots.ConnectionManager import ConnectionManager
from db.MailRepository import User, Repo, MessageDirection
from utils.coding import unpack_pub_k

sys.path.append('../')
from Protocol.FieldType import Field
from multiple_encryption import multiple_encrypt


class MixnetClient:
    def __init__(self):
        self.repo = Repo()
        self.key_manager = KeyManager()
        self.key_manager.try_generate_and_save_keys(nickname="User")
        self.conn_manager = ConnectionManager(is_server=False).start()
        self.update_manager = UpdateManager(self.conn_manager, self.key_manager, self.repo).start()

    def send(self, receiver_pub_k, message: str):
        route = self.build_route(unpack_pub_k(receiver_pub_k))
        uid = uuid.uuid4().int
        onion_encrypted = multiple_encrypt(message, route, self.conn_manager, uid, self.key_manager)
        first_node = onion_encrypted[Field.to]
        data = onion_encrypted[Field.body]
        requests.post(url=first_node, data=data)
        self.mail_repo.add_message(receiver_pub_k, message,
                                   datetime.datetime.utcnow(),
                                   uid, direction=MessageDirection.outgoing)

    def build_route(self, recv_pub_k):
        return [s.addr for s in self.conn_manager.get_online_servers()] + [recv_pub_k]

    def add_user(self, name, pub_k):
        success = self.user_repo.add_user(name, pub_k)
        return success

    def get_chat_list(self):
        return self.user_repo.get_all_users()

    def get_chat(self, user: User):
        return self.mail_repo.get_chat(user.pub_k)

    @property
    def mail_repo(self): return self.repo.mail

    @property
    def user_repo(self): return self.repo.user

