import json
from dataclasses import asdict
from pathlib import Path
from src.data_models.transcript_models import Transcript, Chapter, Segment, Role
from typing import List
import os


def transcript_from_dict(data: List[dict], episode_name: str) -> Transcript:
    """JSONから読み込んだ辞書データからTranscriptオブジェクトを生成します"""
    chapters = []
    for chapter_data in data:
        segments = [
            Segment(
                speaker=segment["speaker"],
                role=Role(segment["role"]),
                text=segment["text"],
            )
            for segment in chapter_data["segments"]
        ]
        chapter = Chapter(
            no=chapter_data["no"],
            title=chapter_data.get("title", ""),
            segments=segments,
        )
        chapters.append(chapter)
    return Transcript(chapters=chapters, episode_name=episode_name)


def transcript_to_dict(transcript: Transcript) -> List[dict]:
    """Transcriptオブジェクトを辞書形式に変換します"""
    return [asdict(chapter) for chapter in transcript.chapters]


def transcript_load_from_json(file_path: str | Path) -> Transcript:
    """JSONファイルからTranscriptオブジェクトを読み込みます"""
    episode_name = Path(file_path).stem
    with open(file_path, "r", encoding="utf-8") as f:
        data = json.load(f)
        return transcript_from_dict(data, episode_name)


def transcript_save_to_json(transcript: Transcript, file_path: str | Path) -> None:
    """Transcriptオブジェクトをファイルに保存します"""
    os.makedirs(os.path.dirname(file_path), exist_ok=True)
    with open(file_path, "w", encoding="utf-8") as f:
        json.dump(transcript_to_dict(transcript), f, ensure_ascii=False, indent=2)
