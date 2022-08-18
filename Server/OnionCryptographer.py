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
        inner = jp.encode(inner)
        return SecretMessageDto(body=inner)
        # print(inner)


# r = OnionCryptographer().encrypt("ab", ["m1", "m2", "m3"])
# pprint.pprint(r)
# print(jp.decode(r).to)
