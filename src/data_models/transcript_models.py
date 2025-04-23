from dataclasses import dataclass, asdict
from typing import List
import json
from pathlib import Path
import os
from enum import Enum

class Role(Enum):
    HOST = 'host'
    GUEST = 'guest'

@dataclass
class Segment:
    """会話の一つのセグメントを表現するクラス"""

    speaker: str
    role: Role
    text: str

@dataclass
class Chapter:
    """チャプターを表現するクラス"""

    no: str
    title: str
    segments: List[Segment]
    BASE_DIR = "voicevox"

    def get_chapter_dir(self, episode_name: str) -> str:
        """チャプターの音声ファイルを格納するディレクトリのパスを返します"""
        return os.path.join(self.BASE_DIR, episode_name, f"chapter-{self.no}")

    def get_segment_path(self, episode_name: str, segment_idx: int) -> str:
        """個別の音声セグメントファイルのパスを返します"""
        chapter_dir = self.get_chapter_dir(episode_name)
        return os.path.join(chapter_dir, f"{episode_name}_{self.no}_{segment_idx}.wav")

    def get_combined_output_path(self, episode_name: str) -> str:
        """結合後の音声ファイルの出力パスを返します"""
        output_dir = os.path.join(self.BASE_DIR, "lex-fridman-podcast", episode_name)
        return os.path.join(output_dir, f"{episode_name}-chapter-{self.no}-{self.title}.wav")


@dataclass
class Transcript:
    """ポッドキャストの書き起こし全体を表現するクラス"""

    chapters: List[Chapter]
    episode_name: str

    @classmethod
    def from_dict(cls, data: List[dict], episode_name: str) -> "Transcript":
        """JSONから読み込んだ辞書データからTranscriptオブジェクトを生成します"""
        chapters = []
        for chapter_data in data:
            segments = [
                Segment(speaker=segment["speaker"], role=segment['role'], text=segment["text"])
                for segment in chapter_data["segments"]
            ]
            chapter = Chapter(
                no=chapter_data["no"],
                title=chapter_data.get("title", ""),  # titleが無い場合は空文字を使用
                segments=segments,
            )
            chapters.append(chapter)
        return cls(chapters=chapters, episode_name=episode_name)

    def to_dict(self) -> List[dict]:
        """Transcriptオブジェクトを辞書形式に変換します"""
        return [asdict(chapter) for chapter in self.chapters]

    @classmethod
    def load_from_json(cls, file_path: str | Path) -> "Transcript":
        """JSONファイルからTranscriptオブジェクトを読み込みます"""
        episode_name = Path(file_path).stem
        with open(file_path, "r", encoding="utf-8") as f:
            data = json.load(f)
            return cls.from_dict(data, episode_name)

    def save_to_json(self, file_path: str | Path) -> None:
        """Transcriptオブジェクトをファイルに保存します"""
        os.makedirs(os.path.dirname(file_path), exist_ok=True)
        with open(file_path, "w", encoding="utf-8") as f:
            json.dump(self.to_dict(), f, ensure_ascii=False, indent=2)
