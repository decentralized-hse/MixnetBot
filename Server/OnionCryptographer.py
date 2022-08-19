import base64
import json
import pprint
from typing import List

from Server.DTOs.Message import RedirectMessageDto, FinalMessageDto
import jsonpickle as jp

from Server.DTOs.SecretMessage import SecretMessageDto
from Server.Types import MixerName


class OnionCryptographer:
    def __init__(self):
        pass

    def encrypt(self, message: str, mixers: List[MixerName]) -> SecretMessageDto:
        inner = FinalMessageDto(body=message)
        # encrypt by recv_pub_k
        for mixer in mixers[:-1]:
            inner = RedirectMessageDto(body=jp.encode(inner), to=mixer)
            # inner = RedirectMessageDto(body=base64.b64encode(jp.encode(inner).encode()), to=mixer)
        inner = jp.encode(inner)
        return SecretMessageDto(body=inner)
        # print(inner)

    # def old_encrypt(self, message: str, mixers: List[MixerName]) -> SecretMessageDto:
    #     inner = FinalMessageDto(body=message)
    #     # encrypt by recv_pub_k
    #     for mixer in mixers[:-1]:
    #         inner = RedirectMessageDto(body=jp.encode(inner), to=mixer)
    #     inner = jp.encode(inner)
    #     return SecretMessageDto(body=inner)


# r = OnionCryptographer().encrypt("ab", ["m1", "m2", "m3"])
# pprint.pprint(r)
# print(jp.decode(r).to)
# 4306
# if __name__ == '__main__':
#     cryptographer = OnionCryptographer()
#     t = "Hi"
#     r = ["8002", "3"]
#     dto: SecretMessageDto = cryptographer.encrypt(t, r)
#     a = base64.b64decode(jp.decode(dto.body).body).decode()
#     print(a)
#     print(type(a))
