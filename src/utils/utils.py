import os
import json
from urllib.parse import urlparse


def save_json(data, filename):
    """データを指定パスにJSON形式で保存し、例外時はエラーを出力してNoneを返す"""
    try:
        os.makedirs(os.path.dirname(filename), exist_ok=True)
        with open(filename, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        return filename
    except Exception as e:
        print(f"ファイル保存に失敗しました: {filename} ({e})")
        return None


def extract_episode_name_from_url(url):
    parsed_url = urlparse(url)
    path_parts = parsed_url.path.strip("/").split("-")

    if path_parts[-1] == "transcript":
        # Remove the "-transcript" part if it exists
        filename = "-".join(path_parts[:-1])
    else:
        # Use the full path as the filename if "-transcript" is not present
        filename = "-".join(path_parts) if path_parts else "noname"

    return filename  # 拡張子はここで付けない
