import os
from pydub import AudioSegment
import re
from voicevox_client import VoicevoxClient
from typing import List
from transcript_models import Transcript, Chapter, Segment


class AudioSynthesizer:
    # 出力ディレクトリの設定
    BASE_DIR = "voicevox"
    PODCAST_DIR = f"{BASE_DIR}/lex-fridman-podcast"

    def __init__(self, episode_name: str):
        self.episode_name = episode_name
        self.voicevox = VoicevoxClient()

    def _get_chapter_dir(self, chapter_no: str) -> str:
        """チャプターの音声ファイルを格納するディレクトリのパスを返します"""
        return f"{self.BASE_DIR}/{self.episode_name}/chapter-{chapter_no}"

    def _get_segment_path(self, chapter_no: str, segment_idx: int) -> str:
        """個別の音声セグメントファイルのパスを返します"""
        chapter_dir = self._get_chapter_dir(chapter_no)
        return f"{chapter_dir}/{self.episode_name}_{chapter_no}_{segment_idx}.wav"

    def _get_combined_output_path(self, chapter: Chapter) -> str:
        """結合後の音声ファイルの出力パスを返します"""
        output_dir = f"{self.PODCAST_DIR}/{self.episode_name}"
        return (
            f"{output_dir}/{self.episode_name}-chapter-{chapter.no}-{chapter.title}.wav"
        )

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
        self, segments: List[Segment], chapter_no: str, prev_speaker: str
    ) -> str:
        """チャプター内の各セグメントを処理し、最後のspeakerを返します"""
        for idx, segment in enumerate(segments):
            speaker = self._get_speaker_for_segment(segment, prev_speaker)
            segment.speaker = speaker  # 話者情報を更新
            wav_output_path = self._get_segment_path(chapter_no, idx)

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
        chapter_dir = self._get_chapter_dir(chapter.no)
        os.makedirs(chapter_dir, exist_ok=True)

        prev_speaker = self._process_segments(
            chapter.segments, chapter.no, prev_speaker
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

        output_path = self._get_combined_output_path(chapter)
        os.makedirs(os.path.dirname(output_path), exist_ok=True)

        combined_audio.export(output_path, format="wav")
        print(f"Saved combined audio for chapter {chapter.no}: {output_path}")
