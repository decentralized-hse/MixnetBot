import jsonpickle as jp
import pydantic as pydantic
import json


class GreetingDto(pydantic.BaseModel):
    name: str = ""  # name of sender


class GreetingResultDto(pydantic.BaseModel):
    accepted: bool = False


g = GreetingResultDto()
# print(type(GreetingDto.parse_raw(g.json())))

# j = jp.encode(g)
# print(j)
# print(jp.encode(GreetingDto(name=j)))
# gr = jp.decode(j)
# print(isinstance(gr, GreetingResultDto))
