from nacl.public import PrivateKey, SealedBox

from Protocol.UpdateRequest import UpdateReq
from Protocol.Updates import Update, UpdateType
from utils.coding import unpack_obj, get_hash_of_uids
from dateutil import parser

PRIVATE_KEY = PrivateKey.generate()
PUBLIC_KEY = PRIVATE_KEY.public_key


def get_json_dict(request) -> dict:
    data = request.get_data()
    return unpack_obj(data=data, sk=PRIVATE_KEY)


def get_updates_for_user(update_request: dict, db) -> dict:  # TODO проверять хэши
    # print("GETTING UPDATES", update_request[UpdateReq.last_message_time])
    pub_k = update_request[UpdateReq.sender_public_key]
    all_messages = db.mail_repo.get_messages_by_recv_pub_k_time_ASC(pub_k)
    if update_request[UpdateReq.last_message_time] is None:
        return Update(UpdateType.all_messages, get_texts(all_messages)).to_dict()
    if not all_messages:
        return Update(UpdateType.up_to_date, []).to_dict()
    client_last_message = parser.parse(update_request[UpdateReq.last_message_time])
    unseen_messages = list(filter(lambda r: r.timestamp > client_last_message, all_messages))
    # last_message = all_messages[-1] if all_messages else None
    return Update(UpdateType.new_messages, get_texts(unseen_messages)).to_dict()


def get_texts(messages):
    return [r.text for r in messages]
