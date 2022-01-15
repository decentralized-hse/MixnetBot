import argparse
import json
from threading import Thread

import requests
from flask import Flask
from flask import request

from DesktopClient.multiple_encryption import get_pub_keys
from FlaskBots.BackroundMessageQueue import MessageQueue, MessageTask
from FlaskBots.ConnectionManager import ConnectionManager
from FlaskBots.Network import get_all_servers
from FlaskBots.db.DB import DB
from Protocol.FieldType import Field
from Protocol.UpdateRequest import UpdateReq
from utils.coding import pack_k, unpack_obj, pack_obj, unpack_pub_k
from Domain import PUBLIC_KEY, PRIVATE_KEY, get_json_dict, get_updates_for_user

app = Flask(__name__)
db = DB()
connection_manager = ConnectionManager(is_server=True).start()
message_queue = MessageQueue(connection_manager)

print("PUBLIC KEY", PUBLIC_KEY.__bytes__())

import logging

log = logging.getLogger('werkzeug')
log.setLevel(logging.ERROR)


@app.route("/public-key", methods=['GET'])
def get_public_key():
    body = request.get_json()
    # print(PUBLIC_KEY)
    response = {
        "public_key": pack_k(PUBLIC_KEY),
        "private_key": pack_k(PRIVATE_KEY),
        "encoding": "base64"}
    # print(response)
    return response


@app.route("/message", methods=['POST'])
def message():
    message = get_json_dict(request)  # расшифрованное своим приватным ключом
    print("MES:", message)
    if message.get(Field.is_junk):
        return "OK", 200
    if message[Field.cypher_count] == 1:
        if message.get(Field.type) == "broadcast":
            db.mail_repo.add_message(recv_pub_k=message[Field.to_pub_k], message=json.dumps(message),
                                     timestamp=message[Field.timestamp])
            print("saved", json.dumps(message))
        else:
            send_broadcast(message)
        return "OK", 200
    send_to_next_node(message)
    return "OK", 200


def send_to_next_node(message):
    message_queue.append_message(MessageTask(url=message[Field.to], data=message[Field.body]))


def send_broadcast(message):
    message[Field.type] = "broadcast"
    for mixer in connection_manager.get_online_servers():
        encrypted = pack_obj(message, mixer.pub_k)  # Зашифровали для получателя
        message_queue.append_message(MessageTask(url=mixer.addr + "/message", data=encrypted))
    print("sent broadcast", message)


@app.route("/messages", methods=['GET'])
def get_all_messages():
    update_request = get_json_dict(request)
    print("GETTING UPDATES", update_request)
    updates = get_updates_for_user(update_request, db)
    client_pub_k = update_request[UpdateReq.sender_public_key]
    return pack_obj(updates, pub_k=unpack_pub_k(client_pub_k))
    # return pack_obj({"messages": [r.text for r in db.mail_repo.get_messages_by_recv_pub_k(pub_k)]},
    #                 pub_k=unpack_pub_k(pub_k))


@app.route("/user", methods=['POST'])
def register_new_user():
    message_obj = get_json_dict(request)
    pub_k = message_obj[Field.sender_public_key]
    nickname = message_obj[Field.sender_nickname]
    success = db.user_repo.add_user(pub_k, nickname)
    if success:
        for server in get_all_servers():
            message_queue.append_message(MessageTask(url=server + "/user", data=message_obj))
    return "OK", 200


@app.route("/new-node-notification", methods=['POST'])
def add_new():
    print("ADD NEW NOTIFICATION--------------------------------------------------------")
    connection_manager.update_connection_list(request.json["servers"])
    print("ALL CONNECTIONS", connection_manager.connections.keys())
    return "OK", 200


xport = None
if __name__ == '__main__':
    q_thread = Thread(target=message_queue.send_mixed, daemon=True)
    q_thread.start()

    parser = argparse.ArgumentParser()
    parser.add_argument("--xport", dest="xport", default=5000, type=int)
    args = parser.parse_args()
    db.connect(args.xport)
    xport = args.xport
    response = requests.get(url="http://127.0.0.1:5000/register", json={"port": xport})
    app.run(port=args.xport, debug=True)
