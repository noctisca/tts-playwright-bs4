import sys
import asyncio
import os
from scraper import WebScraper
from parser import HTMLParser
from utils import save_to_file, generate_filename_from_url
from audio_synthesizer import AudioSynthesizer

async def main(url):
    episode_name = generate_filename_from_url(url)
    json_file_path = f"output/{episode_name}.json"  # JSONファイルのパスを生成

    # JSONファイルがなければスクレイピング→保存
    if not os.path.exists(json_file_path):
        translate_url = f"https://translate.google.com/translate?sl=auto&tl=ja&hl=ja&u={url}"

        # スクレイピング処理
        scraper = WebScraper(translate_url)
        await scraper.fetch_content()

        # HTMLパース処理
        parser = HTMLParser(scraper.get_content())
        entry_content = parser.extract_conversation_structure()

        # コンテンツが抽出できたら保存
        if entry_content:
            save_to_file(entry_content, json_file_path)
            print(f"Content from {url} has been saved to {json_file_path}")
        else:
            print(f"Could not find content with class 'entry-content' on {url}.")
            return
    else:
        print(f"既存のJSONファイルが見つかりました: {json_file_path}")

    synthesizer = AudioSynthesizer(episode_name)
    synthesizer.synthesize_from_json(json_file_path)

if __name__ == '__main__':
    if len(sys.argv) < 2:
        print("Usage: python script.py <URL>")
    else:
        asyncio.run(main(sys.argv[1]))
