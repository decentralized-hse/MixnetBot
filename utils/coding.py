import base64
import json
import hashlib

from nacl.public import PublicKey, SealedBox, PrivateKey, Box


def pack_k(key: PublicKey) -> str:
    s = base64.b64encode(key.__bytes__())
    s = str(s)
    return s


def unpack_pub_k(s: str) -> PublicKey:
    bytes_s = base64.b64decode(s[2:-1])
    return PublicKey(bytes_s)


def unpack_priv_k(s: str) -> PrivateKey:
    bytes_s = base64.b64decode(s[2:-1])
    return PrivateKey(bytes_s)


def pack_obj(obj, pub_k: PublicKey) -> str:
    box = SealedBox(pub_k)
    data = json.dumps(obj).encode()
    b = box.encrypt(data)
    return str(base64.b64encode(b))


def unpack_obj(data: str, sk: PrivateKey) -> dict:
    b = base64.b64decode(data[2:-1])
    box = SealedBox(sk)
    r_str = box.decrypt(b).decode()
    return json.loads(r_str)


def get_hash_of_uids(uids):
    s = "".join(map(str, sorted(uids)))
    hash_object = hashlib.sha256(s.encode())
    return hash_object.hexdigest()


def pack_str(s: str, priv_k: PrivateKey, pub_k: PublicKey) -> str:
    box = Box(priv_k, pub_k)
    data = json.dumps(s).encode()
    b = box.encrypt(data)
    return str(base64.b64encode(b))


def unpack_str(data: str, sk: PrivateKey, pk) -> str:
    b = base64.b64decode(data[2:-1])
    box = Box(sk, pk)
    r_str = box.decrypt(b).decode()
    return json.loads(r_str)
