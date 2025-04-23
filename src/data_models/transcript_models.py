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
    BASE_DIR = "voicevox"

    def get_chapter_dir(self, episode_name: str) -> str:
        return os.path.join(self.BASE_DIR, episode_name, f"chapter-{self.no}")

    def get_segment_path(self, episode_name: str, segment_idx: int) -> str:
        chapter_dir = self.get_chapter_dir(episode_name)
        return os.path.join(chapter_dir, f"{episode_name}_{self.no}_{segment_idx}.wav")

    def get_combined_output_path(self, episode_name: str) -> str:
        output_dir = os.path.join(self.BASE_DIR, "lex-fridman-podcast", episode_name)
        return os.path.join(
            output_dir, f"{episode_name}-chapter-{self.no}-{self.title}.wav"
        )


@dataclass
class Transcript:
    chapters: List[Chapter]
    episode_name: str
