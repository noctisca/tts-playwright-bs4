import json
from pathlib import Path
from src.data_models.transcript_models import Transcript, Chapter, Segment, Role
from typing import List
import os


def transcript_from_dict(data: List[dict], episode_name: str) -> Transcript:
    """JSONから読み込んだ辞書データからTranscriptオブジェクトを生成します"""
    chapters = []
    for chapter_data in data:
        segments = []
        for segment in chapter_data["segments"]:
            # role を取得。存在すれば Role Enum に変換、なければ None
            role_value = segment.get("role")  # .get() でキー存在チェック、なければ None
            segment_role = (
                Role(role_value) if role_value else None
            )  # 値があれば Enum 化、なければ None

            segments.append(
                Segment(
                    speaker=segment["speaker"],
                    text=segment["text"],
                    role=segment_role,  # 取得/変換した role を設定 (None の場合もある)
                )
            )

        chapter = Chapter(
            no=chapter_data["no"],
            title=chapter_data.get("title", ""),
            segments=segments,
        )
        chapters.append(chapter)
    return Transcript(chapters=chapters, episode_name=episode_name)


def transcript_to_dict(transcript: Transcript) -> List[dict]:
    """TranscriptオブジェクトをJSONシリアライズ可能な辞書形式に変換します"""
    output_chapters = []
    for chapter in transcript.chapters:
        output_segments = []
        for segment in chapter.segments:
            output_segments.append(
                {
                    "speaker": segment.speaker,
                    "text": segment.text,
                    # Role Enum をその値 (文字列) に変換。None の場合は None のまま。
                    "role": segment.role.value if segment.role else None,
                }
            )
        output_chapters.append(
            {"no": chapter.no, "title": chapter.title, "segments": output_segments}
        )
    return output_chapters


def transcript_load_from_json(file_path: str | Path) -> Transcript:
    """JSONファイルからTranscriptオブジェクトを読み込みます"""
    episode_name = Path(file_path).stem
    with open(file_path, "r", encoding="utf-8") as f:
        data = json.load(f)
        return transcript_from_dict(data, episode_name)
