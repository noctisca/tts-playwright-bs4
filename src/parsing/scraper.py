from playwright.async_api import async_playwright
import asyncio

class WebScraper:
    def __init__(self, url):
        self.url = url
        self.page_content = None

    async def fetch_content(self):
        """ Playwrightを使って翻訳ページからHTMLを取得 """
        print("ページ取得を開始しています...")
        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=True)
            page = await browser.new_page()
            await page.goto(self.url)

            # 初期のテキストが読み込まれるのを待機
            await page.wait_for_selector('.entry-content', timeout=10000)

            # 最下部までスクロールして翻訳を促す
            # await page.evaluate("() => window.scrollTo(0, document.body.scrollHeight)")

            # ゆっくりスクロール（翻訳がすべての要素にかかるように）
            scroll_height = await page.evaluate("document.body.scrollHeight")
            current_position = 0
            scroll_step = 100
            delay_ms = 100
            progress_counter = 0

            while current_position < scroll_height:
                await page.evaluate(f"window.scrollTo(0, {current_position})")
                current_position += scroll_step
                await asyncio.sleep(delay_ms / 1000)

                # 1秒ごとに進捗を表示
                progress_counter += delay_ms
                if progress_counter >= 1000:
                    progress_percent = min(100, int((current_position / scroll_height) * 100))
                    print(f"...処理中です ({progress_percent}%)")
                    progress_counter = 0

            print("ページ取得処理完了")
            await asyncio.sleep(1.5)
            await page.wait_for_timeout(3000)  # 翻訳が実行されるまで少し待つ

            # .entry-content のHTMLを取得
            # await page.wait_for_selector('.entry-content', timeout=10000)
            # self.page_content = await page.inner_html('.entry-content')
            self.page_content = await page.content()

            await browser.close()

    def get_content(self):
        """ 取得したHTMLを返す """
        return self.page_content

