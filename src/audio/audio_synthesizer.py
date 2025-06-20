import os
from pydub import AudioSegment
import re
from collections import Counter
from .voicevox_client import VoicevoxClient
from .file_manager import AudioFileManager
from typing import List, Dict
from src.data_models.transcript_models import Transcript, Chapter, Segment, Role
from google.cloud import texttospeech  # Google TTS import
from src.constants import HOST_SPEAKER_NAMES  # 定数をインポート


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
            print(
                "Please ensure GOOGLE_APPLICATION_CREDENTIALS environment variable is set correctly."
            )
            self.google_tts_client = None

        # 話者と音声のマッピングを保持する辞書
        self.speaker_voice_map: Dict[str, str] = {}
        # 利用可能なGoogle TTS音声リスト
        self.google_host_voice = "ja-JP-Standard-B"
        self.google_guest_voices = [
            "ja-JP-Standard-D",
            "ja-JP-Standard-C",
        ]
        # マッピングにない話者や、ゲスト音声リストが不足した場合のデフォルト
        self.google_default_voice = "ja-JP-Standard-A"  # デフォルトは A にしてみる

    def _build_speaker_voice_map(self, transcript: Transcript) -> None:
        """Transcriptから話者の登場頻度を計算し、音声マッピングを構築する"""
        speaker_counts = Counter()
        guest_speakers = set()  # 重複なしのゲスト話者リスト

        # 全セグメントを走査して話者と登場回数をカウント
        for chapter in transcript.chapters:
            for segment in chapter.segments:
                # preprocess.py で Role が割り当てられている前提
                if segment.speaker and segment.role == Role.GUEST:
                    speaker_counts[segment.speaker] += 1
                    guest_speakers.add(segment.speaker)

        # 登場頻度順にゲスト話者をソート
        sorted_guest_speakers = [
            speaker
            for speaker, count in speaker_counts.most_common()
            if speaker
            in guest_speakers  # Counterにはホストも含まれる可能性があるのでフィルタ
        ]

        # --- ゲスト数のチェック ---
        if len(sorted_guest_speakers) > len(self.google_guest_voices):
            print(
                f"注意: 検出されたゲスト話者数 ({len(sorted_guest_speakers)}) が、"
                f"利用可能なゲスト音声数 ({len(self.google_guest_voices)}) を超えています。"
                f" ゲスト話者リスト: {sorted_guest_speakers}"
                f" 余分なゲストにはリストの最後の音声が割り当てられます。"
            )
        # -------------------------

        voice_map: Dict[str, str] = {}
        # ホストの割り当て
        voice_map[self.host_speaker] = self.google_host_voice

        # ゲストの割り当て (登場頻度順)
        for i, speaker in enumerate(sorted_guest_speakers):
            # ゲストの数がリストの長さを超えた場合、リストの最後の音声を割り当てる
            voice_map[speaker] = self.google_guest_voices[i] if i < len(self.google_guest_voices) else self.google_guest_voices[-1]

        self.speaker_voice_map = voice_map
        print("--- Speaker-Voice Map ---")
        for speaker, voice in self.speaker_voice_map.items():
            print(f"- {speaker}: {voice}")
        print("-------------------------")

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

    def _synthesize_segment_google(
        self, segment: Segment, wav_output_path: str
    ) -> None:
        """1つのセグメントの音声をGoogle TTSで合成してファイルに保存します"""
        if not self.google_tts_client:
            raise RuntimeError("Google TTS client is not initialized.")

        synthesis_input = texttospeech.SynthesisInput(text=segment.text)

        voice_name = self.speaker_voice_map.get(
            segment.speaker, self.google_default_voice
        )

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

        self._build_speaker_voice_map(transcript)

        for chapter in transcript.chapters:
            self._process_chapter(chapter)
