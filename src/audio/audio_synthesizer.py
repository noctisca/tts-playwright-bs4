import os
from pydub import AudioSegment
import re
from .voicevox_client import VoicevoxClient
from .file_manager import AudioFileManager
from typing import List
from src.data_models.transcript_models import Transcript, Chapter, Segment
from google.cloud import texttospeech  # Google TTS import


class AudioSynthesizer:

    def __init__(self, episode_name: str, podcast_name: str):
        self.episode_name = episode_name
        self.podcast_name = podcast_name
        self.voicevox = VoicevoxClient()
        self.file_manager = AudioFileManager(episode_name, podcast_name)
        # Google TTS Client (assuming GOOGLE_APPLICATION_CREDENTIALS env var is set)
        try:
            self.google_tts_client = texttospeech.TextToSpeechClient()
        except Exception as e:
            print(f"Failed to initialize Google TTS client: {e}")
            print("Please ensure GOOGLE_APPLICATION_CREDENTIALS environment variable is set correctly.")
            self.google_tts_client = None

    def _synthesize_segment(self, segment: Segment, wav_output_path: str) -> None:
        """1つのセグメントの音声を合成してファイルに保存します"""
        query_data = self.voicevox.create_audio_query(segment)
        if query_data is None:
            raise RuntimeError(
                f"VOICEVOXのaudio_query APIが失敗しました。テキスト: {segment.text[:100]}..."
            )

        audio_content = self.voicevox.synthesize_audio(query_data, segment)
        if audio_content is not None:
            with open(wav_output_path, "wb") as wav_file:
                wav_file.write(audio_content)
            print(f"Generated audio: {wav_output_path}")
        else:
            raise RuntimeError(
                f"VOICEVOXのsynthesis APIが失敗しました。テキスト: {segment.text[:100]}..."
            )

    def _synthesize_segment_google(self, segment: Segment, wav_output_path: str) -> None:
        """1つのセグメントの音声をGoogle TTSで合成してファイルに保存します"""
        if not self.google_tts_client:
            raise RuntimeError("Google TTS client is not initialized.")

        synthesis_input = texttospeech.SynthesisInput(text=segment.text)

        # Select voice based on role
        if segment.is_host():
            voice_name = "ja-JP-Standard-B"  # Host voice
        else:
            voice_name = "ja-JP-Standard-D"  # Guest voice

        voice = texttospeech.VoiceSelectionParams(
            language_code="ja-JP", name=voice_name
        )

        audio_config = texttospeech.AudioConfig(
            audio_encoding=texttospeech.AudioEncoding.LINEAR16  # WAV format
        )

        try:
            response = self.google_tts_client.synthesize_speech(
                input=synthesis_input, voice=voice, audio_config=audio_config
            )

            with open(wav_output_path, "wb") as out:
                out.write(response.audio_content)
            print(f"Generated Google TTS audio: {wav_output_path}")

        except Exception as e:
            raise RuntimeError(
                f"Google TTS synthesis API failed. Text: {segment.text[:100]}... Error: {e}"
            )

    def _process_segments(self, chapter: Chapter) -> None:
        """チャプター内の各セグメントを処理します"""
        for idx, segment in enumerate(chapter.segments):
            wav_output_path = self.file_manager.get_segment_path(chapter.no, idx)

            # ファイルが既に存在する場合はスキップ
            if os.path.exists(wav_output_path):
                print(f"Skipping existing file: {wav_output_path}")
                continue

            self._synthesize_segment_google(segment, wav_output_path)

    def _process_chapter(self, chapter: Chapter) -> None:
        """チャプターを処理します"""
        chapter_dir = self.file_manager.get_chapter_dir(chapter.no)
        os.makedirs(chapter_dir, exist_ok=True)

        self._process_segments(chapter)
        self.file_manager.concatenate_chapter_audio(chapter, chapter_dir)

    def synthesize_from_transcript(self, transcript: Transcript) -> None:
        """Transcriptオブジェクトから音声を合成します"""
        for chapter in transcript.chapters:
            self._process_chapter(chapter)
