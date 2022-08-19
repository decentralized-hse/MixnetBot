from nacl.public import PrivateKey, PublicKey, Box


class Cryptographer:
    def __init__(self):
        self.priv_k = PrivateKey.generate()
        self.pub_k = self.priv_k.public_key

    def get_box(self, interlocutor_pub_k: PublicKey):
        return Box(self.priv_k, interlocutor_pub_k)


ac = Cryptographer()
bc = Cryptographer()

ms = bytes(ac.pub_k)

print(ms)
bms = PublicKey(ms)

bobox = Box(bc.priv_k, bms)
abox = Box(ac.priv_k, PublicKey(bytes(bc.pub_k)))

enc = bobox.encrypt("hi".encode())

print(abox.decrypt(enc).decode())
