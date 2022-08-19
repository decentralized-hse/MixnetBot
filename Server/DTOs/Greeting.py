import jsonpickle as jp
import pydantic as pydantic
import json
from nacl.public import PrivateKey, PublicKey, Box


class GreetingDto(pydantic.BaseModel):
    name: str = ""  # name of sender
    pub_k: PublicKey

    class Config:
        arbitrary_types_allowed = True


class ClientGreetingDto(pydantic.BaseModel):
    pub_k: str = ""  # pub_k of sender


class GreetingResultDto(pydantic.BaseModel):
    accepted: bool = False
    pub_k: PublicKey

    class Config:
        arbitrary_types_allowed = True

# sk = PrivateKey.generate()
# g = GreetingDto(pub_k=sk.public_key)
# print(g.pub_k)
# r = jp.decode(jp.encode(g))
# print(type(r.pub_k))
# print(type(GreetingDto.parse_raw(g.json())))

# j = jp.encode(g)
# print(j)
# print(jp.encode(GreetingDto(name=j)))
# gr = jp.decode(j)
# print(isinstance(gr, GreetingResultDto))
