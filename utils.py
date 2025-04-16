import os

def save_to_file(content, filename="output/output.txt"):
    """ 取得したコンテンツをファイルに保存 """
    os.makedirs(os.path.dirname(filename), exist_ok=True)  # 保存先のディレクトリを作成
    with open(filename, 'w', encoding='utf-8') as f:
        f.write(str(content))
