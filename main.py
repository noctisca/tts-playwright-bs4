import sys
import asyncio
from scraper import WebScraper
from parser import HTMLParser
from utils import save_to_file

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
        save_to_file(entry_content)
        print(f"Content from {url} has been saved to output/output.txt")
    else:
        print(f"Could not find content with class 'entry-content' on {url}.")

if __name__ == '__main__':
    if len(sys.argv) < 2:
        print("Usage: python script.py <URL>")
    else:
        asyncio.run(main(sys.argv[1]))
