import os
import json
from urllib.parse import urlparse

def save_to_file(content, filename="output/noname.json"):
    """ 取得したコンテンツをファイルに保存 """
    os.makedirs(os.path.dirname(filename), exist_ok=True)  # 保存先のディレクトリを作成
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(content, f, ensure_ascii=False, indent=2)

def generate_filename_from_url(url):
    parsed_url = urlparse(url)
    path_parts = parsed_url.path.strip('/').split('-')

    if path_parts[-1] == "transcript":
        # Remove the "-transcript" part if it exists
        filename = '-'.join(path_parts[:-1])
    else:
        # Use the full path as the filename if "-transcript" is not present
        filename = '-'.join(path_parts) if path_parts else "noname"

    return filename  # 拡張子はここで付けない
