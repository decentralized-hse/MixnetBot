from enum import Enum, auto

MixerName = str

ClientPubName = str


class Participant(Enum):
    MIXER = auto()
    CLIENT = auto()
