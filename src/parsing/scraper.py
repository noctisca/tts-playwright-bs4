from playwright.async_api import async_playwright

class WebScraper:
    def __init__(self, url):
        self.url = url
        self.page_content = None

    async def fetch_content(self):
        """ Playwrightを使って翻訳ページからHTMLを取得 """
        print("Playwrightによるページ取得を開始しています（この処理には数分かかる場合があります）...")
        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=True)
            page = await browser.new_page()
            await page.goto(self.url)

            # 初期のテキストが読み込まれるのを待機
            await page.wait_for_selector('.entry-content', timeout=10000)

            # 最下部までスクロールして翻訳を促す
            # await page.evaluate("() => window.scrollTo(0, document.body.scrollHeight)")

            # ゆっくりスクロール（翻訳がすべての要素にかかるように）
            await page.evaluate("""
                async () => {
                    const delay = ms => new Promise(res => setTimeout(res, ms));
                    const scrollStep = 100;
                    const delayMs = 100;

                    let currentPosition = 0;
                    const scrollHeight = document.body.scrollHeight;

                    while (currentPosition < scrollHeight) {
                        window.scrollTo(0, currentPosition);
                        currentPosition += scrollStep;
                        await delay(delayMs);
                    }

                    await delay(1500);
                }
            """)
            await page.wait_for_timeout(3000)  # 翻訳が実行されるまで少し待つ

            # .entry-content のHTMLを取得
            # await page.wait_for_selector('.entry-content', timeout=10000)
            # self.page_content = await page.inner_html('.entry-content')
            self.page_content = await page.content()

            await browser.close()

    def get_content(self):
        """ 取得したHTMLを返す """
        return self.page_content

