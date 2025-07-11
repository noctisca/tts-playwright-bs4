import os
from pydub import AudioSegment
import re
from src.data_models.transcript_models import Chapter


class AudioFileManager:
    """音声ファイルの結合・管理を担当するクラス"""

    def __init__(self, episode_name: str, podcast_name: str):
        self.episode_name = episode_name
        self.podcast_name = podcast_name

    def get_chapter_dir(self, chapter_no: str) -> str:
        """チャプターの音声ファイルを格納するディレクトリのパスを返す"""
        return os.path.join("output", "audio", self.episode_name, f"chapter-{chapter_no}")

    def get_segment_path(self, chapter_no: str, segment_idx: int) -> str:
        """個別の音声セグメントファイルのパスを返す"""
        chapter_dir = self.get_chapter_dir(chapter_no)
        return os.path.join(
            chapter_dir, f"{self.episode_name}_{chapter_no}_{segment_idx}.wav"
        )

    def get_combined_output_path(self, chapter_no: str, chapter_title: str) -> str:
        """結合後の音声ファイルの出力パスを返す"""
        output_dir = os.path.join("output", "lex-fridman-podcast", self.episode_name)
        return os.path.join(
            output_dir, f"{self.episode_name}-chapter-{chapter_no}-{chapter_title}.wav"
        )

    def concatenate_chapter_audio(self, chapter: Chapter, chapter_dir: str) -> None:
        """チャプター内の音声ファイルを結合します"""

        # Check if combined file already exists
        output_path = self.get_combined_output_path(chapter.no, chapter.title)
        if os.path.exists(output_path):
            print(f"Skipping concatenation, combined file already exists: {output_path}")
            return

        def extract_idx(filename: str) -> int:
            match = re.search(
                rf"{self.episode_name}_{chapter.no}_(\d+)\.wav$", filename
            )
            return int(match.group(1)) if match else -1

        wav_files = [
            os.path.join(chapter_dir, file)
            for file in sorted(os.listdir(chapter_dir), key=extract_idx)
            if file.startswith(f"{self.episode_name}_{chapter.no}_")
            and file.endswith(".wav")
        ]

        # If no segment files found, skip concatenation (avoid creating empty file)
        if not wav_files:
            print(f"No segment files found in {chapter_dir}, skipping concatenation for chapter {chapter.no}.")
            return

        combined_audio = AudioSegment.empty()
        for wav_file in wav_files:
            combined_audio += AudioSegment.from_wav(wav_file)

        os.makedirs(os.path.dirname(output_path), exist_ok=True)

        combined_audio.export(output_path, format="wav")
        print(f"Saved combined audio for chapter {chapter.no}: {output_path}")
