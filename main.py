import sys
import asyncio
import os
from src.parsing.scraper import WebScraper
from src.parsing.parser import HTMLParser
from src.utils.utils import extract_episode_name_from_url
from src.audio.audio_synthesizer import AudioSynthesizer
from src.data_models.transcript_models import Transcript
from src.parsing.preprocess import preprocess_data
import json  # jsonモジュールを追加

async def get_raw_data(url: str, episode_name: str) -> str | None:
    """
    URLから生データを取得し、ファイルに保存する。
    既存ファイルがあればそれを読み込む。
    """
    raw_data_file_path = os.path.join("output", f"{episode_name}.json")

    if os.path.exists(raw_data_file_path):
        print(f"既存のJSONファイルが見つかりました: {raw_data_file_path}")
        return raw_data_file_path
    else:
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
            # スクレイピング結果を元のJSONファイルに保存
            transcript = Transcript.from_dict(transcript_data, episode_name)
            transcript.save_to_json(raw_data_file_path)
            print(f"Content from {url} has been saved to {raw_data_file_path}")
            return raw_data_file_path
        else:
            print(f"Could not find content with class 'entry-content' on {url}.")
            return None

def preprocess_and_load_transcript(raw_data_file_path: str, episode_name: str) -> Transcript | None:
    """
    生データファイルからデータを読み込み、前処理を行い、Transcriptオブジェクトを生成する。
    前処理済みファイルがあればそれを読み込む。
    """
    preprocessed_json_file_path = os.path.join(
        "output", f"{episode_name}_preprocessed.json"
    )

    # 前処理済みファイルが存在するか確認
    if os.path.exists(preprocessed_json_file_path):
        print(f"既存の前処理済みファイルが見つかりました: {preprocessed_json_file_path}")
        # 既存ファイルからTranscriptを読み込む
        transcript = Transcript.load_from_json(preprocessed_json_file_path)
        return transcript
    else:
        # 前処理の呼び出し
        print(f"前処理を開始します: {raw_data_file_path}")
        preprocessed_data = preprocess_data(raw_data_file_path)
        if preprocessed_data is None:
            print("前処理に失敗しました。処理を中断します。")
            return None
        print("前処理が完了しました。")

        # 前処理結果を一時ファイルに保存
        try:
            with open(preprocessed_json_file_path, "w", encoding="utf-8") as f:
                json.dump(preprocessed_data, f, indent=2)
            print(f"前処理結果を保存しました: {preprocessed_json_file_path}")
        except Exception as e:
            print(f"前処理結果の保存に失敗しました: {e}")
            return None

        # 前処理結果の一時ファイルからTranscriptを読み込む
        transcript = Transcript.load_from_json(preprocessed_json_file_path)
        return transcript


def synthesize_episode_audio(transcript: Transcript, episode_name: str) -> None:
    """
    Transcriptオブジェクトから音声合成を実行する。
    """
    # 前処理後のtranscriptオブジェクトを後続処理に渡す
    synthesizer = AudioSynthesizer(episode_name)
    synthesizer.synthesize_from_transcript(transcript)


async def main(url: str) -> None:
    episode_name = extract_episode_name_from_url(url)

    # 1. scraping (or load file)
    raw_data_file_path = await get_raw_data(url, episode_name)
    if raw_data_file_path is None:
        return

    # 2. preprocess (or load file)
    transcript = preprocess_and_load_transcript(raw_data_file_path, episode_name)
    if transcript is None:
        return

    # 3. synthesize
    synthesize_episode_audio(transcript, episode_name)


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("使用方法: python main.py <URL>")
        sys.exit(1)
    try:
        asyncio.run(main(sys.argv[1]))
    except Exception as e:
        print(f"エラーが発生しました: {e}")
        sys.exit(1)
