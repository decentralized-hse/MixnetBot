from nacl.public import PrivateKey, PublicKey, Box
from nacl.utils import EncryptedMessage


class Cryptographer:
    def __init__(self):
        self.priv_k = PrivateKey.generate()
        self.pub_k = self.priv_k.public_key

    def get_box(self, interlocutor_pub_k: PublicKey):
        return Box(self.priv_k, interlocutor_pub_k)


class BoxAdapter:
    @staticmethod
    def encrypt(box: Box, message: str) -> EncryptedMessage:
        return box.encrypt(message.encode())

    @staticmethod
    def decrypt(box: Box, message: EncryptedMessage) -> str:
        return box.decrypt(message).decode()


# ac = Cryptographer()
# bc = Cryptographer()
#
# ms = bytes(ac.pub_k)
#
# print(ms)
# bms = PublicKey(ms)
#
# bobox = Box(bc.priv_k, bms)
# abox = Box(ac.priv_k, PublicKey(bytes(bc.pub_k)))
#
# enc = bobox.encrypt("hi".encode())
# print(enc)
# print(type(enc))
#
# print(abox.decrypt(enc).decode())
