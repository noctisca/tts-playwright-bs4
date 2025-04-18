import os
from urllib.parse import urlparse

def save_to_file(content, filename="output/noname.json"):
    """ 取得したコンテンツをファイルに保存 """
    os.makedirs(os.path.dirname(filename), exist_ok=True)  # 保存先のディレクトリを作成
    with open(filename, 'w', encoding='utf-8') as f:
        f.write(str(content))

def generate_filename_from_url(url, output_dir="output"):
    parsed_url = urlparse(url)
    path_parts = parsed_url.path.strip('/').split('-')

    if path_parts[-1] == "transcript":
        # Remove the "-transcript" part if it exists
        filename_prefix = '-'.join(path_parts[:-1])
    else:
        # Use the full path as the filename if "-transcript" is not present
        filename_prefix = '-'.join(path_parts) if path_parts else "noname"

    return f"{output_dir}/{filename_prefix}.json"
