import json
import os


def preprocess_data(file_path: str):
    """
    スクレイピング後のJSONデータを読み込み、前処理を行う.

    Args:
        file_path: 前処理対象のJSONファイルのパス.

    Returns:
        前処理後のデータ.
    """
    if not os.path.exists(file_path):
        print(f"エラー: ファイルが見つかりません - {file_path}")
        return None

    try:
        with open(file_path, "r", encoding="utf-8") as f:
            data = json.load(f)
        print(f"データを読み込みました: {file_path}")

        # 前処理ロジック
        if isinstance(data, list): # データがチャプターのリストであることを想定
            for chapter in data:
                last_speaker = None
                if isinstance(chapter.get("segments"), list): # 各チャプターがsegmentsリストを持つことを想定
                    for segment in chapter["segments"]:
                        # speakerが空文字列の場合、直前のspeakerをコピー
                        if segment.get("speaker") == "" and last_speaker is not None:
                            segment["speaker"] = last_speaker

                        # speakerに基づいてroleを設定
                        if segment.get("speaker") == "レックス・フリードマン":
                            segment["role"] = "host"
                        else:
                            segment["role"] = "guest"

                        # 現在のspeakerを次のセグメントのために保持
                        if segment.get("speaker") != "":
                            last_speaker = segment.get("speaker")

        return data
    except json.JSONDecodeError:
        print(f"エラー: JSONファイルの読み込みに失敗しました - {file_path}")
        return None
    except Exception as e:
        print(f"エラーが発生しました: {e}")
        return None
