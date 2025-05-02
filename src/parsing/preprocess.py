import json
import os
from src.data_models.transcript_utils import transcript_from_dict, transcript_to_dict
from src.data_models.transcript_models import Transcript, Role
from src.constants import HOST_SPEAKER_NAMES
from typing import Dict, List, Any


def preprocess_data(file_path: str) -> List[Dict[str, Any]] | None:
    """
    スクレイピング後のJSONデータを読み込み、前処理を行う.

    Args:
        file_path: 前処理対象のJSONファイルのパス.

    Returns:
        前処理後のデータ (チャプターのリスト形式). エラーが発生した場合は None.
    """
    if not os.path.exists(file_path):
        print(f"エラー: ファイルが見つかりません - {file_path}")
        return None

    try:
        with open(file_path, "r", encoding="utf-8") as f:
            data = json.load(f)
        print(f"データを読み込みました: {file_path}")

        # データモデル化
        transcript = transcript_from_dict(
            data, os.path.splitext(os.path.basename(file_path))[0]
        )

        # 1. Speaker の決定
        last_speaker = ""
        for chapter in transcript.chapters:
            for segment in chapter.segments:
                if segment.speaker == "":
                    if last_speaker == "":
                        raise ValueError(
                            f"エラー: Chapter '{chapter.no}', Segment starting with "
                            f"'{segment.text[:50]}...' で話者が見つからず、"
                            f"前の話者情報もありません。データを確認してください。"
                        )
                    segment.speaker = last_speaker
                last_speaker = segment.speaker

        # 2. Role の決定
        for chapter in transcript.chapters:
            for segment in chapter.segments:
                if segment.speaker in HOST_SPEAKER_NAMES:
                    segment.role = Role.HOST
                elif segment.speaker != "":
                    segment.role = Role.GUEST
                else:
                    raise ValueError(
                        f"エラー: Chapter '{chapter.no}', Segment starting with "
                        f"'{segment.text[:50]}...' で話者が空です。"
                        f"Speaker決定処理に問題がある可能性があります。"
                    )

        # dictに戻して返す (Role Enum のシリアライズに注意)
        return transcript_to_dict(transcript)

    except json.JSONDecodeError:
        print(f"エラー: JSONファイルの読み込みに失敗しました - {file_path}")
        return None
    except ValueError as ve:  # 追加したValueErrorをキャッチ
        print(ve)  # エラーメッセージを表示
        return None
    except Exception as e:
        print(f"予期せぬエラーが発生しました: {e}")
        # 必要であればここで詳細なエラーログを出力
        # import traceback
        # traceback.print_exc()
        return None
