from bs4 import BeautifulSoup

class HTMLParser:
    def __init__(self, html_content):
        self.soup = BeautifulSoup(html_content, 'html.parser')

    def extract_entry_content(self):
        """ `div.entry-content` を抽出 """
        return self.soup.find('div', class_='entry-content')

    def extract_additional_content(self):
        """ 追加のHTML解析ロジックをここに追加できる """
        # 例: 他の要素を抽出する処理をここに書く
        return self.soup.find_all('p')  # 例: すべての <p> タグを抽出
