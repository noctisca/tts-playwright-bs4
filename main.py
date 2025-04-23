import sys
import asyncio
from src.app.pipeline import run_pipeline

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("使用方法: python main.py <URL>")
        sys.exit(1)
    try:
        asyncio.run(run_pipeline(sys.argv[1]))
    except Exception as e:
        print(f"エラーが発生しました: {e}")
        sys.exit(1)
