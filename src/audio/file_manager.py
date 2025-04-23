import os
from pydub import AudioSegment
import re
from src.data_models.transcript_models import Chapter


class AudioFileManager:
    """音声ファイルの結合・管理を担当するクラス"""

    def __init__(self, episode_name: str):
        self.episode_name = episode_name

    def concatenate_chapter_audio(self, chapter: Chapter, chapter_dir: str) -> None:
        """チャプター内の音声ファイルを結合します"""

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
        combined_audio = AudioSegment.empty()
        for wav_file in wav_files:
            combined_audio += AudioSegment.from_wav(wav_file)

        output_path = chapter.get_combined_output_path(self.episode_name)
        os.makedirs(os.path.dirname(output_path), exist_ok=True)

        combined_audio.export(output_path, format="wav")
        print(f"Saved combined audio for chapter {chapter.no}: {output_path}")
