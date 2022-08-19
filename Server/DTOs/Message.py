import jsonpickle as jp
import pydantic as pydantic
import json

from Server.Types import MixerName


class RedirectMessageDto(pydantic.BaseModel):
    body: str
    to: MixerName = ""


class FinalMessageDto(pydantic.BaseModel):
    body: str  # зашифрованное
    recv_pub_k: str = ""
