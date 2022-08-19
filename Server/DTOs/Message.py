import base64

import jsonpickle as jp
import pydantic as pydantic
import json
from typing import Union

from Server.Types import MixerName


class RedirectMessageDto(pydantic.BaseModel):
    body: str
    to: MixerName = ""


class FinalMessageDto(pydantic.BaseModel):
    body: str  # зашифрованное
    recv_pub_k: str = ""


if __name__ == '__main__':
    rm = RedirectMessageDto(body="Hi!")
    print(jp.encode(rm))
    print("######")
    print(dict(rm))
    print('******')
    rm2 = RedirectMessageDto(body=base64.b64encode(jp.encode(rm).encode()))
    # rm3 = RedirectMessageDto(body=str(dict(rm2)))
    print(rm2)
    print('OLD:')
    rm20 = RedirectMessageDto(body=jp.encode(rm))
    print(rm20)

    # print(jp.encode(rm))
