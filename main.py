import sys
import asyncio
import os
from scraper import WebScraper
from parser import HTMLParser
from utils import extract_episode_name_from_url
from audio_synthesizer import AudioSynthesizer
from transcript_models import Transcript


async def main(url: str) -> None:
    episode_name = extract_episode_name_from_url(url)
    json_file_path = f"output/{episode_name}.json"

    if not os.path.exists(json_file_path):
        translate_url = (
            f"https://translate.google.com/translate?sl=auto&tl=ja&hl=ja&u={url}"
        )

        # スクレイピング処理
        scraper = WebScraper(translate_url)
        await scraper.fetch_content()

        # HTMLパース処理
        parser = HTMLParser(scraper.get_content())
        transcript_data = parser.extract_conversation_structure()

        # コンテンツが抽出できたら保存
        if transcript_data:
            transcript = Transcript.from_dict(transcript_data)
            os.makedirs(os.path.dirname(json_file_path), exist_ok=True)
            transcript.save_to_json(json_file_path)
            print(f"Content from {url} has been saved to {json_file_path}")
        else:
            print(f"Could not find content with class 'entry-content' on {url}.")
            return
    else:
        print(f"既存のJSONファイルが見つかりました: {json_file_path}")
        transcript = Transcript.load_from_json(json_file_path)

    synthesizer = AudioSynthesizer(episode_name)
    synthesizer.synthesize_from_transcript(transcript)


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("使用方法: python main.py <URL>")
        sys.exit(1)
    try:
        asyncio.run(main(sys.argv[1]))
    except Exception as e:
        print(f"エラーが発生しました: {e}")
        sys.exit(1)
