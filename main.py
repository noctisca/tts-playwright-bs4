import sys
import asyncio
import json
import os
import requests
from pydub import AudioSegment
from scraper import WebScraper
from parser import HTMLParser
from utils import save_to_file, generate_filename_from_url

async def main(url):
    translate_url = f"https://translate.google.com/translate?sl=auto&tl=ja&hl=ja&u={url}"

    # スクレイピング処理
    scraper = WebScraper(translate_url)
    await scraper.fetch_content()

    # HTMLパース処理
    parser = HTMLParser(scraper.get_content())
    entry_content = parser.extract_conversation_structure()

    # コンテンツが抽出できたら保存
    if entry_content:
        filename = generate_filename_from_url(url)
        json_file_path = f"output/{filename}.json"  # JSONファイルのパスを生成
        save_to_file(entry_content, json_file_path)
        print(f"Content from {url} has been saved to {json_file_path}")

        # 音声合成処理を呼び出し
        synthesize_audio_from_json(json_file_path, filename)

        # チャプター音声結合処理を呼び出し
        concatenate_chapter_audio(json_file_path, filename)
    else:
        print(f"Could not find content with class 'entry-content' on {url}.")

def synthesize_audio_from_json(json_file, base_filename):
    with open(json_file, 'r', encoding='utf-8') as f:
        data = json.load(f)

    for chapter in data:
        chapter_no = chapter['no']
        segments = chapter['segments']

        # Create a directory for the chapter
        chapter_dir = f"voicebox/{base_filename}/chapter-{chapter_no}"
        os.makedirs(chapter_dir, exist_ok=True)

        for idx, segment in enumerate(segments):
            speaker = segment['speaker']
            text = segment['text']

            # Determine speaker ID
            speaker_id = '9' if speaker == 'レックス・フリードマン' else '13'

            # Generate filenames
            wav_output_path = f"{chapter_dir}/segment-{idx}.wav"

            # Step 1: Generate audio query JSON
            query_url = f"http://127.0.0.1:50021/audio_query?speaker={speaker_id}"
            query_response = requests.post(query_url, params={"text": text})

            if query_response.status_code == 200:
                query_data = query_response.json()
            else:
                print(f"Failed to generate audio query for text: {text}")
                continue

            # Step 2: Synthesize audio from JSON
            synthesis_url = f"http://127.0.0.1:50021/synthesis?speaker={speaker_id}"
            synthesis_response = requests.post(synthesis_url, headers={"Content-Type": "application/json"}, json=query_data)

            if synthesis_response.status_code == 200:
                with open(wav_output_path, 'wb') as wav_file:
                    wav_file.write(synthesis_response.content)
                print(f"Generated audio: {wav_output_path}")
            else:
                print(f"Failed to synthesize audio for text: {text}")

def concatenate_chapter_audio(json_file, base_filename):
    with open(json_file, 'r', encoding='utf-8') as f:
        data = json.load(f)

    for chapter in data:
        chapter_no = chapter['no']
        chapter_title = chapter['title']

        # Path to the chapter directory
        chapter_dir = f"voicebox/{base_filename}/chapter-{chapter_no}"

        # Collect all WAV file paths in the chapter directory
        wav_files = [
            os.path.join(chapter_dir, file)
            for file in sorted(os.listdir(chapter_dir)) if file.endswith('.wav')
        ]

        # Combine WAV files
        combined_audio = AudioSegment.empty()
        for wav_file in wav_files:
            combined_audio += AudioSegment.from_wav(wav_file)

        # Save the combined audio
        output_dir = f"lex-fridman-podcast/{base_filename}"
        os.makedirs(output_dir, exist_ok=True)
        output_path = f"{output_dir}/{base_filename}-chapter-{chapter_no}-{chapter_title}.wav"

        combined_audio.export(output_path, format="wav")
        print(f"Saved combined audio for chapter {chapter_no}: {output_path}")

if __name__ == '__main__':
    if len(sys.argv) < 2:
        print("Usage: python script.py <URL>")
    else:
        asyncio.run(main(sys.argv[1]))
