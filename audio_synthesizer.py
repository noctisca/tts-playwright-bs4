import os
import json
import requests
from pydub import AudioSegment
import re

class AudioSynthesizer:
    def __init__(self, base_filename):
        self.base_filename = base_filename

    def synthesize_from_json(self, json_file):
        with open(json_file, 'r', encoding='utf-8') as f:
            data = json.load(f)

        prev_speaker = 'レックス・フリードマン'  # デフォルト
        for chapter in data:
            chapter_no = chapter['no']
            segments = chapter['segments']
            chapter_dir = f"voicebox/{self.base_filename}/chapter-{chapter_no}"
            os.makedirs(chapter_dir, exist_ok=True)

            for idx, segment in enumerate(segments):
                speaker = segment['speaker']
                text = segment['text']
                if speaker == "":
                    speaker = prev_speaker
                speaker_id = '9' if speaker == 'レックス・フリードマン' else '13'
                wav_output_path = f"{chapter_dir}/{self.base_filename}_{chapter_no}_{idx}.wav"
                query_url = f"http://127.0.0.1:50021/audio_query?speaker={speaker_id}"
                query_response = requests.post(query_url, params={"text": text})
                if query_response.status_code == 200:
                    query_data = query_response.json()
                else:
                    print(f"Failed to generate audio query for text: {text}")
                    continue
                synthesis_url = f"http://127.0.0.1:50021/synthesis?speaker={speaker_id}"
                synthesis_response = requests.post(synthesis_url, headers={"Content-Type": "application/json"}, json=query_data)
                if synthesis_response.status_code == 200:
                    with open(wav_output_path, 'wb') as wav_file:
                        wav_file.write(synthesis_response.content)
                    print(f"Generated audio: {wav_output_path}")
                else:
                    print(f"Failed to synthesize audio for text: {text}")
                prev_speaker = speaker
            self.concatenate_chapter_audio(chapter, chapter_dir)

    def concatenate_chapter_audio(self, chapter, chapter_dir):
        def extract_idx(filename):
            match = re.search(rf"{self.base_filename}_{chapter['no']}_(\d+)\.wav$", filename)
            return int(match.group(1)) if match else -1
        wav_files = [
            os.path.join(chapter_dir, file)
            for file in sorted(os.listdir(chapter_dir), key=extract_idx)
            if file.startswith(f"{self.base_filename}_{chapter['no']}_") and file.endswith('.wav')
        ]
        combined_audio = AudioSegment.empty()
        for wav_file in wav_files:
            combined_audio += AudioSegment.from_wav(wav_file)
        output_dir = f"lex-fridman-podcast/{self.base_filename}"
        os.makedirs(output_dir, exist_ok=True)
        chapter_title = chapter['title']
        chapter_no = chapter['no']
        output_path = f"{output_dir}/{self.base_filename}-chapter-{chapter_no}-{chapter_title}.wav"
        combined_audio.export(output_path, format="wav")
        print(f"Saved combined audio for chapter {chapter_no}: {output_path}")
