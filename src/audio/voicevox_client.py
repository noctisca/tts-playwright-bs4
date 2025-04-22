import requests
import time

class VoicevoxClient:
    # VOICEVOXの設定
    BASE_URL = "http://127.0.0.1:50021"
    LONG_TEXT_THRESHOLD = 562  # 長いテキストと判断する文字数の閾値

    # 話者の設定
    HOST_SPEAKER_ID = "9"  # ホスト（レックス）の声色用のVOICEVOX話者ID
    GUEST_SPEAKER_ID = "13"  # ゲストの声色用のVOICEVOX話者ID
    HOST_NAME = "レックス・フリードマン"

    def __init__(self, base_url=None):
        self.base_url = base_url or self.BASE_URL

    def create_audio_query(self, text: str, speaker_id: str):
        """VOICEVOXのaudio_query APIを呼び出してクエリデータを取得します"""
        query_url = f"{self.base_url}/audio_query?speaker={speaker_id}"

        # 長いテキストの場合は待機時間を入れる
        if len(text) >= self.LONG_TEXT_THRESHOLD:
            print(
                f"****** Long text detected ({len(text)} chars). Waiting 1 second... ******"
            )
            time.sleep(1)

        response = requests.post(query_url, params={"text": text})

        if response.status_code == 200:
            return response.json()
        else:
            print(f"Failed to generate audio query for text: {text}")
            return None

    def synthesize_audio(self, query_data: dict, speaker_id: str) -> bytes | None:
        """VOICEVOXのsynthesis APIを呼び出して音声データを生成します"""
        synthesis_url = f"{self.base_url}/synthesis?speaker={speaker_id}"

        response = requests.post(
            synthesis_url, headers={"Content-Type": "application/json"}, json=query_data
        )

        if response.status_code == 200:
            return response.content
        else:
            print(f"Failed to synthesize audio")
            return None

    @staticmethod
    def get_speaker_id(speaker_name: str) -> str:
        """話者名からVOICEVOXのspeaker_idを取得します"""
        return (
            VoicevoxClient.HOST_SPEAKER_ID
            if speaker_name == VoicevoxClient.HOST_NAME
            else VoicevoxClient.GUEST_SPEAKER_ID
        )
