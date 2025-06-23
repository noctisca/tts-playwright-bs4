# English Transcript to Japanese Audio Converter

Automates English transcript conversion to Japanese audio with distinct voices for each speaker.

Currently focused on [Lex Fridman Podcast](https://lexfridman.com/podcast).

## How It Works

Extracts English transcripts from URLs and generates Japanese audio using Text-to-Speech.

## Requirements
* Python 3.12.10

## Tech Stack
- Python
- Playwright
- BeautifulSoup4
- Google Text-to-Speech


## Setup

1.  **Clone:**
    ```bash
    git clone https://github.com/noctisca/tts-playwright-bs4.git
    cd tts-playwright-bs4
    ```
2.  **Install dependencies:**
    ```bash
    pip install -r requirements.txt
    ```
3.  **Install Playwright browsers:**
    ```bash
    playwright install
    ```
4. **Set up Google Cloud credentials:**

    This tool uses Google Text-to-Speech, which requires Google Cloud credentials.

    Follow the official Google Cloud documentation to set up a service account and download its JSON key file.

    Then, set the `GOOGLE_APPLICATION_CREDENTIALS` environment variable to the path of your JSON key file.
    ```bash
    export GOOGLE_APPLICATION_CREDENTIALS="/path/to/your/keyfile.json"
    ```
    (Replace `/path/to/your/keyfile.json` with the actual path to your downloaded key file.)

## Usage

```bash
python main.py <URL_TO_TRANSCRIPT>
```
Output files will be generated in a directory structure under `output/`.

Example:
```
python main.py https://lexfridman.com/sundar-pichai-transcript
```
For the example command above, files will be saved to `output/lex-fridman-podcast/sundar-pichai/`.

## Future Work
- Explore alternative TTS models for natural Japanese voices.
- Expand compatibility to other transcript sources.
- Improve mobile audio management (e.g., metadata embedding for better app playback).
