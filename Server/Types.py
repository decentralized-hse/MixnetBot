from enum import Enum, auto

MixerName = str


class Participant(Enum):
    MIXER = auto()
    CLIENT = auto()
