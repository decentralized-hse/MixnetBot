import jsonpickle as jp
import pydantic as pydantic
import json
from nacl.utils import EncryptedMessage


class SecretMessageDto(pydantic.BaseModel):
    body: EncryptedMessage
