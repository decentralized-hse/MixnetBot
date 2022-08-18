import jsonpickle as jp
import pydantic as pydantic
import json


class SecretMessageDto(pydantic.BaseModel):
    body: str
