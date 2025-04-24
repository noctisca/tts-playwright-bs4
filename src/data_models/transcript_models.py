from dataclasses import dataclass, field  # field をインポート (デフォルト値のため)
from enum import Enum
from typing import List, Optional  # Optional をインポート


class Role(Enum):
    HOST = "host"
    GUEST = "guest"


@dataclass
class Segment:
    speaker: str
    text: str
    role: Optional[Role] = None

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
    podcast_name: str = "lex-fridman-podcast"
