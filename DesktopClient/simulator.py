# import datetime
# import json
# import time
#
# import requests
#
# from DesktopClient.Keys import get_keys_f
# from MixnetClient import send, get_update_request_message
#
# # # private_key = PrivateKey.generate()
# # # public_key = private_key.public_key
# #
# # private_key = PrivateKey(
# #     b'L\xcf\\\xb5\xb9RSly\x81\xae\xf7\x9b\xdc\xcao\xca\xb1],\xd0$\x03\xbd\xfc\xe6\xd7z\xa4\xdd\xcc\x85')
# # public_key = private_key.public_key
# # print(private_key)
# # print("-------------")
# # print(public_key)
# from Protocol.FieldType import Field
# from Protocol.UpdateRequest import UpdateReq
# from utils.coding import unpack_obj, pack_k, pack_obj, unpack_str
#
# recv_keys = get_keys_f()
# public_key = recv_keys.public_key
# private_key = recv_keys.private_key
# conn_manager = send(public_key, f"7Hello Mark")
# for i in range(1500):
#     mes = f"Y! {i}"
#     send(public_key, mes)
#     print("SENT", mes)
#     time.sleep(3)
# # #
# # server = get_all_servers()[1]
# # server_pub_k = get_pub_keys([server], conn_manager)[server]
# # keys = get_keys_f()
# # message = {UpdateReq.sender_public_key: pack_k(public_key),
# #            UpdateReq.last_message_time: datetime.datetime(1980, 1, 1).isoformat()}
# # response = requests.get(url=f"{server}/messages", data=pack_obj(message, server_pub_k))
# # #
# # # message = {"sender_public_key": pack_k(public_key)}
# # # response = requests.get(url=f"{server}/messages", data=pack_obj(message, server_pub_k))
# # print(response)
# # d = unpack_obj(data=response.text, sk=private_key)
# # for m in d["messages"]:
# #     encrypted = json.loads(m)
# #     print(encrypted)
# #     unp = unpack_obj(encrypted[Field.body], private_key)
# #     print("UNP")
# #     print(unp)
# #
# #     encrypted_body = unp[Field.body]
# #     print("ENC BODY")
# #     print(encrypted_body)
# #     print("REAL MES: ", unpack_str(unp[Field.body], keys.private_key, keys.public_key))
# #
# #     sender = unp[Field.sender_pub_k]
# #     print(sender)
# #     print(unp)
