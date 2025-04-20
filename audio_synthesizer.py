import os
import json
from pydub import AudioSegment
import re
from voicevox_client import VoicevoxClient


class AudioSynthesizer:
    # 出力ディレクトリの設定
    BASE_DIR = "voicevox"
    PODCAST_DIR = f"{BASE_DIR}/lex-fridman-podcast"

    def __init__(self, episode_name):
        self.episode_name = episode_name
        self.voicevox = VoicevoxClient()

    def synthesize_from_json(self, json_file):
        with open(json_file, "r", encoding="utf-8") as f:
            data = json.load(f)

        prev_speaker = VoicevoxClient.HOST_NAME
        for chapter in data:
            chapter_no = chapter["no"]
            segments = chapter["segments"]
            chapter_dir = f"{self.BASE_DIR}/{self.episode_name}/chapter-{chapter_no}"
            os.makedirs(chapter_dir, exist_ok=True)

            for idx, segment in enumerate(segments):
                speaker = segment["speaker"]
                text = segment["text"]
                if speaker == "":
                    speaker = prev_speaker

                wav_output_path = (
                    f"{chapter_dir}/{self.episode_name}_{chapter_no}_{idx}.wav"
                )

                # ファイルが既に存在する場合はスキップ
                if os.path.exists(wav_output_path):
                    print(f"Skipping existing file: {wav_output_path}")
                    prev_speaker = speaker
                    continue

                speaker_id = self.voicevox.get_speaker_id(speaker)
                query_data = self.voicevox.create_audio_query(text, speaker_id)
                if query_data is None:
                    raise RuntimeError(
                        f"VOICEVOXのaudio_query APIが失敗しました。テキスト: {text[:100]}..."
                    )

                audio_content = self.voicevox.synthesize_audio(query_data, speaker_id)
                if audio_content is not None:
                    with open(wav_output_path, "wb") as wav_file:
                        wav_file.write(audio_content)
                    print(f"Generated audio: {wav_output_path}")
                else:
                    raise RuntimeError(
                        f"VOICEVOXのsynthesis APIが失敗しました。テキスト: {text[:100]}..."
                    )

                prev_speaker = speaker

            self.concatenate_chapter_audio(chapter, chapter_dir)

    def concatenate_chapter_audio(self, chapter, chapter_dir):
        def extract_idx(filename):
            match = re.search(
                rf"{self.episode_name}_{chapter['no']}_(\d+)\.wav$", filename
            )
            return int(match.group(1)) if match else -1

        wav_files = [
            os.path.join(chapter_dir, file)
            for file in sorted(os.listdir(chapter_dir), key=extract_idx)
            if file.startswith(f"{self.episode_name}_{chapter['no']}_")
            and file.endswith(".wav")
        ]
        combined_audio = AudioSegment.empty()
        for wav_file in wav_files:
            combined_audio += AudioSegment.from_wav(wav_file)
        output_dir = f"{self.PODCAST_DIR}/{self.episode_name}"
        os.makedirs(output_dir, exist_ok=True)
        chapter_title = chapter["title"]
        chapter_no = chapter["no"]
        output_path = (
            f"{output_dir}/{self.episode_name}-chapter-{chapter_no}-{chapter_title}.wav"
        )
        combined_audio.export(output_path, format="wav")
        print(f"Saved combined audio for chapter {chapter_no}: {output_path}")
