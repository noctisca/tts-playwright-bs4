import requests
import time


class VoicevoxClient:
    # VOICEVOXの設定
    BASE_URL = "http://127.0.0.1:50021"
    LONG_TEXT_THRESHOLD = 562  # 長いテキストと判断する文字数の閾値

    # 話者の設定
    HOST_SPEAKER_ID = "9"  # ホストの声色用のVOICEVOX話者ID
    GUEST_SPEAKER_ID = "52" # "13"  # ゲストの声色用のVOICEVOX話者ID

    def __init__(self, base_url=None):
        self.base_url = base_url or self.BASE_URL

    def create_audio_query(self, segment) -> dict | None:
        """VOICEVOXのaudio_query APIを呼び出してクエリデータを取得します"""
        speaker_id = self._get_speaker_id(segment)
        query_url = f"{self.base_url}/audio_query?speaker={speaker_id}"
        text = segment.text

        response = requests.post(query_url, params={"text": text})

        if response.status_code == 200:
            return response.json()
        else:
            print(f"Failed to generate audio query for text: {text}")
            return None

    def synthesize_audio(self, query_data: dict, segment) -> bytes | None:
        """VOICEVOXのsynthesis APIを呼び出して音声データを生成します"""
        speaker_id = self._get_speaker_id(segment)
        synthesis_url = f"{self.base_url}/synthesis?speaker={speaker_id}"
        text = segment.text

        if len(text) >= self.LONG_TEXT_THRESHOLD:
            print(
                f"****** Long text detected ({len(text)} chars). Waiting 1 second... ******"
            )
            time.sleep(1)

        response = requests.post(
            synthesis_url, headers={"Content-Type": "application/json"}, json=query_data
        )

        if response.status_code == 200:
            return response.content
        else:
            print(f"Failed to synthesize audio")
            return None

    @staticmethod
    def _get_speaker_id(segment) -> str:
        """SegmentからVOICEVOXのspeaker_idを取得します（内部用）"""
        return (
            VoicevoxClient.HOST_SPEAKER_ID
            if segment.is_host()
            else VoicevoxClient.GUEST_SPEAKER_ID
        )
