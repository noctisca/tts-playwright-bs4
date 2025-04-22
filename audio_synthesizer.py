import os
from pydub import AudioSegment
import re
from voicevox_client import VoicevoxClient
from typing import List
from transcript_models import Transcript, Chapter, Segment


class AudioSynthesizer:

    def __init__(self, episode_name: str):
        self.episode_name = episode_name
        self.voicevox = VoicevoxClient()

    # _get_segment_path is removed as it's moved to Chapter class

    def _synthesize_segment(self, segment: Segment, wav_output_path: str) -> None:
        """1つのセグメントの音声を合成してファイルに保存します"""
        speaker_id = self.voicevox.get_speaker_id(segment.speaker)
        query_data = self.voicevox.create_audio_query(segment.text, speaker_id)
        if query_data is None:
            raise RuntimeError(
                f"VOICEVOXのaudio_query APIが失敗しました。テキスト: {segment.text[:100]}..."
            )

        audio_content = self.voicevox.synthesize_audio(query_data, speaker_id)
        if audio_content is not None:
            with open(wav_output_path, "wb") as wav_file:
                wav_file.write(audio_content)
            print(f"Generated audio: {wav_output_path}")
        else:
            raise RuntimeError(
                f"VOICEVOXのsynthesis APIが失敗しました。テキスト: {segment.text[:100]}..."
            )

    def _get_speaker_for_segment(self, segment: Segment, prev_speaker: str) -> str:
        """セグメントの話者を決定します。空の場合は前の話者を使用します"""
        return segment.speaker or prev_speaker

    def _process_segments(
        self, chapter: Chapter, prev_speaker: str
    ) -> str:
        """チャプター内の各セグメントを処理し、最後のspeakerを返します"""
        for idx, segment in enumerate(chapter.segments):
            speaker = self._get_speaker_for_segment(segment, prev_speaker)
            segment.speaker = speaker  # 話者情報を更新
            # Use the new method from Chapter class
            wav_output_path = chapter.get_segment_path(self.episode_name, idx)

            # ファイルが既に存在する場合はスキップ
            if os.path.exists(wav_output_path):
                print(f"Skipping existing file: {wav_output_path}")
                prev_speaker = speaker
                continue

            self._synthesize_segment(segment, wav_output_path)
            prev_speaker = speaker

        return prev_speaker

    def _process_chapter(self, chapter: Chapter, prev_speaker: str) -> str:
        """チャプターを処理し、最後のspeakerを返します"""
        chapter_dir = chapter.get_chapter_dir(self.episode_name)
        os.makedirs(chapter_dir, exist_ok=True)

        prev_speaker = self._process_segments(
            chapter, prev_speaker
        )
        self.concatenate_chapter_audio(chapter, chapter_dir)
        return prev_speaker

    def synthesize_from_transcript(self, transcript: Transcript) -> None:
        """Transcriptオブジェクトから音声を合成します"""
        prev_speaker = VoicevoxClient.HOST_NAME

        for chapter in transcript.chapters:
            prev_speaker = self._process_chapter(chapter, prev_speaker)

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
