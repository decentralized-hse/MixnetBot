import json
import sys
import uuid

import requests
from datetime import datetime
from nacl.public import SealedBox, Box

from FlaskBots.Network import get_all_servers
from utils.coding import base64_str_to_public_key, bytes_to_b64, unpack_pub_k, pack_obj, pack_k, pack_str

sys.path.append('../')
from Protocol.FieldType import Field



def multiple_encrypt(message_from_user: str, route: list, conn_manager, uid, key_manager):
    node_pub_keys = get_pub_keys(route[:-1], conn_manager)
    receiver_pub_k = route[-1]
    packed_receiver_pub_k = pack_k(receiver_pub_k)
    node_pub_keys[route[-1]] = route[-1]
    sending_time = datetime.utcnow().isoformat()
    rev = list(reversed(route))  # сначала получатель, потом конечный миксер, ..., 1-й миксер
    cypher_count = 0
    obj = {Field.body: pack_str(message_from_user, key_manager.sk, receiver_pub_k),
           Field.to: None,
           Field.timestamp: sending_time,
           Field.uid: uid,
           Field.name: key_manager.nick,
           Field.sender_pub_k: pack_k(key_manager.pk),
           Field.cypher_count: cypher_count
           }
    # print("ROUTE", route)
    first_wrapped = True
    for node in rev:
        cypher_count += 1
        obj = pack_obj(obj, pub_k=node_pub_keys[node])
        obj = {
            Field.body: obj,
            Field.to: f"{node}/message" if not first_wrapped else None,
            Field.to_pub_k: packed_receiver_pub_k if first_wrapped else None,
            Field.cypher_count: cypher_count
        }
        if first_wrapped: obj[Field.timestamp] = sending_time
        first_wrapped = False
    # print(obj)
    return obj


def get_pub_keys(mixers, conn_manager):
    res = {}
    for m in mixers:
        res[m] = conn_manager.get_server_pub_k(m)
    return res
