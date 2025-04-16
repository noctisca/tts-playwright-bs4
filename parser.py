from bs4 import BeautifulSoup

class HTMLParser:
    def __init__(self, html_content):
        self.soup = BeautifulSoup(html_content, 'html.parser')

    def extract_conversation_structure(self):
        content_div = self.soup.find('div', class_='entry-content')
        if not content_div:
            return []

        results = []
        current_chapter = None
        chapter_no = -1
        processing = False  # ★ スクリプト開始フラグ

        for elem in content_div.find_all(True):  # recursive=True
            if elem.name == 'h2' and elem.has_attr('id') and elem['id'].startswith('chapter'):
                processing = True  # ★ ここからスクリプト開始
                chapter_no += 1
                chapter_title = elem.get_text(strip=True)
                current_chapter = {
                    "no": chapter_no,
                    "title": chapter_title,
                    "segments": []
                }
                results.append(current_chapter)

            elif processing and elem.name == 'div' and 'ts-segment' in elem.get('class', []):
                if current_chapter is None:
                    continue

                speaker_elem = elem.find('span', class_='ts-name')
                text_elem = elem.find('span', class_='ts-text')

                speaker = speaker_elem.get_text(strip=True) if speaker_elem else ""
                text = text_elem.get_text(strip=True) if text_elem else ""

                segment = {
                    "speaker": speaker,
                    "text": text
                }
                current_chapter["segments"].append(segment)

        return results
