"""AI 陪伴助手 PWA - TTS 服务端语音合成"""
import asyncio
import os
import tempfile


class TTSService:
    def __init__(self, config: dict):
        self.config = config
        self.engine = config["voice"]["tts_engine"]
        self.voice_name = config["voice"]["voice_name"]
        self.rate = config["voice"]["rate"]

    async def synthesize(self, text: str) -> str | None:
        """合成语音，返回音频文件路径"""
        if self.engine == "edge_tts":
            return await self._edge_tts(text)
        return None

    async def _edge_tts(self, text: str) -> str:
        import edge_tts
        communicate = edge_tts.Communicate(text, self.voice_name, rate=self.rate)
        tmp_path = os.path.join(tempfile.gettempdir(), f"tts_{id(text)}.mp3")
        await communicate.save(tmp_path)
        return tmp_path
