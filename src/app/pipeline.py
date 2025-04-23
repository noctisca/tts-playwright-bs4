import os
import json
import asyncio
from src.parsing.scraper import WebScraper
from src.parsing.parser import HTMLParser
from src.utils.utils import extract_episode_name_from_url, save_json
from src.audio.audio_synthesizer import AudioSynthesizer
from src.data_models.transcript_utils import (
    transcript_from_dict,
    transcript_load_from_json,
)
from src.parsing.preprocess import preprocess_data


async def get_raw_data(url: str, episode_name: str) -> str | None:
    """
    URLから生データを取得し、ファイルに保存する。
    既存ファイルがあればそれを読み込む。
    """
    raw_data_file_path = os.path.join("output", f"{episode_name}.json")

    if os.path.exists(raw_data_file_path):
        print(f"既存のJSONファイルが見つかりました: {raw_data_file_path}")
        return raw_data_file_path

    translate_url = (
        f"https://translate.google.com/translate?sl=auto&tl=ja&hl=ja&u={url}"
    )

    scraper = WebScraper(translate_url)
    await scraper.fetch_content()

    parser = HTMLParser(scraper.get_content())
    transcript_data = parser.extract_conversation_structure()

    if not transcript_data:
        print(f"Could not find content with class 'entry-content' on {url}.")
        return None

    try:
        save_json(transcript_data, raw_data_file_path)
    except Exception as e:
        print(f"ファイル保存に失敗しました: {raw_data_file_path} ({e})")
        raise

    print(f"Content from {url} has been saved to {raw_data_file_path}")
    return raw_data_file_path


def preprocess_and_save(raw_data_file_path: str, episode_name: str) -> str | None:
    """
    生データファイルからデータを読み込み、前処理を行い、前処理済みデータをファイルに保存する。
    保存したファイルパスを返す。
    """
    preprocessed_json_file_path = os.path.join(
        "output", f"{episode_name}_preprocessed.json"
    )

    if os.path.exists(preprocessed_json_file_path):
        print(
            f"既存の前処理済みファイルが見つかりました: {preprocessed_json_file_path}"
        )
        return preprocessed_json_file_path

    print(f"前処理を開始します: {raw_data_file_path}")
    preprocessed_data = preprocess_data(raw_data_file_path)

    if preprocessed_data is None:
        print("前処理に失敗しました。処理を中断します。")
        return None

    print("前処理が完了しました。")

    try:
        save_json(preprocessed_data, preprocessed_json_file_path)
    except Exception as e:
        print(f"前処理結果の保存に失敗しました: {e}")
        raise

    print(f"前処理結果を保存しました: {preprocessed_json_file_path}")
    return preprocessed_json_file_path


def load_transcript(preprocessed_json_file_path: str) -> Transcript:
    """
    前処理済みファイルからTranscriptモデルをロードする
    """
    return transcript_load_from_json(preprocessed_json_file_path)


def synthesize_episode_audio(transcript: Transcript, episode_name: str) -> None:
    """
    Transcriptオブジェクトから音声合成を実行する。
    """
    synthesizer = AudioSynthesizer(episode_name)
    synthesizer.synthesize_from_transcript(transcript)


async def run_pipeline(url: str) -> None:
    episode_name = extract_episode_name_from_url(url)

    # 1. scraping (or load file)
    raw_data_file_path = await get_raw_data(url, episode_name)
    if raw_data_file_path is None:
        return

    # 2. preprocess and save
    preprocessed_json_file_path = preprocess_and_save(raw_data_file_path, episode_name)
    if preprocessed_json_file_path is None:
        return

    # 3. load transcript
    transcript = load_transcript(preprocessed_json_file_path)

    # 4. synthesize
    synthesize_episode_audio(transcript, episode_name)
