from dataclasses import dataclass
from enum import Enum
from typing import List


class Role(Enum):
    HOST = "host"
    GUEST = "guest"


@dataclass
class Segment:
    speaker: str
    role: Role
    text: str

    def is_host(self) -> bool:
        return self.role == Role.HOST


@dataclass
class Chapter:
    no: str
    title: str
    segments: List[Segment]


@dataclass
class Transcript:
    chapters: List[Chapter]
    episode_name: str
