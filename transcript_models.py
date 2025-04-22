from dataclasses import dataclass, asdict
from typing import List
import json
from pathlib import Path
import os


@dataclass
class Segment:
    """会話の一つのセグメントを表現するクラス"""

    speaker: str
    text: str

    @property
    def has_speaker(self) -> bool:
        """話者が指定されているかどうかを返します"""
        return bool(self.speaker)


@dataclass
class Chapter:
    """チャプターを表現するクラス"""

    no: str
    title: str
    segments: List[Segment]

    @property
    def segment_count(self) -> int:
        """セグメントの数を返します"""
        return len(self.segments)

    
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
                Segment(
                    speaker=segment["speaker"],
                    text=segment["text"]
                )
                for segment in chapter_data["segments"]
            ]
            chapter = Chapter(
                no=chapter_data["no"],
                title=chapter_data.get("title", ""),  # titleが無い場合は空文字を使用
                segments=segments
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
