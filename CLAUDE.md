# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Development Commands

**Running the application:**
```bash
python main.py <URL_TO_TRANSCRIPT>
```

**Installing dependencies:**
```bash
pip install -r requirements.txt
playwright install
```

**Setting up Google Cloud credentials:**
```bash
export GOOGLE_APPLICATION_CREDENTIALS="/path/to/your/keyfile.json"
```

## Architecture Overview

This is a Python application that converts English podcast transcripts to Japanese audio using text-to-speech synthesis. The pipeline processes Lex Fridman podcast transcripts through multiple stages.

### Core Pipeline (src/app/pipeline.py)
The main processing flow:
1. **Web Scraping**: Uses Playwright to fetch transcript content via Google Translate
2. **HTML Parsing**: Extracts conversation structure from translated content
3. **Preprocessing**: Clean and structure data into transcript format
4. **Audio Synthesis**: Generate Japanese audio with distinct voices per speaker

### Data Models (src/data_models/)
- `Transcript`: Contains chapters, episode name, and podcast name
- `Chapter`: Groups segments by topic with title and number
- `Segment`: Individual speaker utterances with role (host/guest)
- `Role`: Enum for HOST/GUEST speaker classification

### Audio Processing (src/audio/)
- `AudioSynthesizer`: Main audio generation controller
- VoiceVox client integration for Japanese TTS
- File management for organized audio output structure

### Web Scraping (src/parsing/)
- `WebScraper`: Playwright-based content fetching with translation (runs with headless=False for debugging)
- `HTMLParser`: BeautifulSoup-based transcript extraction
- Preprocessing utilities for data cleaning

### Key Constants
- Host speaker names defined in `src/constants.py` as Japanese names
- Episode names extracted from URL patterns
- Output organized under `output/` directory structure

### Output Structure
```
output/
├── data/           # Raw and preprocessed JSON files
├── audio/          # Generated audio files by episode/chapter
└── lex-fridman-podcast/  # Final organized audio output
```

The application is designed to handle incremental processing, skipping already-processed files and resuming from any pipeline stage.

## Git Commit Guidelines

This repository follows [Conventional Commits](https://www.conventionalcommits.org/) specification. Use these prefixes:
- `feat:` for new features
- `fix:` for bug fixes
- `docs:` for documentation changes
- `chore:` for maintenance tasks
- `refactor:` for code refactoring
- `style:` for formatting and style changes
