#import pygame
#
# class AudioPlayer:
#     def __init__(self):
#         pygame.mixer.init()
#         self.current_audio = None
#         self.is_playing = False
#         self.volume = 0.7
#
#!/usr/bin/env python3
"""
Ultra-Simplified Audio Listen Engine for Word & Sentence Memorizer
极简版音频引擎 - 仅实现核心的TTS播放功能
"""

import asyncio
import io
import threading
import time
import logging
from typing import Callable

# 第三方库导入
import pygame
import edge_tts

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class TTSEngine:
    """文本转语音引擎，使用edge-tts"""

    def __init__(self):
        # 使用一个常见的英文语音作为默认值
        self.default_voice = 'en-US-AriaNeural'

    async def text_to_audio_async(self, text: str) -> bytes:
        """异步将文本转换为音频数据"""
        communicate = edge_tts.Communicate(text=text, voice=self.default_voice)
        audio_data = b""
        async for chunk in communicate.stream():
            if chunk["type"] == "audio":
                audio_data += chunk["data"]
        return audio_data

    def text_to_audio(self, text: str) -> bytes:
        """同步将文本转换为音频数据"""
        try:
            loop = asyncio.get_event_loop()
        except RuntimeError:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
        
        return loop.run_until_complete(self.text_to_audio_async(text))


class AudioPlayer:
    """简化的音频播放器"""

    def __init__(self):
        pygame.mixer.init()
        self.is_playing = False
        # 设置一个固定的默认音量 (0.0 到 1.0之间)
        pygame.mixer.music.set_volume(0.7)

    def play_audio_data(self, audio_data: bytes, callback: Callable = None) -> bool:
        """直接播放音频数据"""
        try:
            self.stop_audio()
            audio_stream = io.BytesIO(audio_data)
            pygame.mixer.music.load(audio_stream)
            pygame.mixer.music.play()
            self.is_playing = True
            logger.info("开始播放音频...")

            if callback:
                def monitor_playback():
                    while pygame.mixer.music.get_busy():
                        time.sleep(0.1)
                    self.is_playing = False
                    callback()
                
                threading.Thread(target=monitor_playback, daemon=True).start()
            
            return True
        except Exception as e:
            logger.error(f"播放音频数据失败: {e}")
            self.is_playing = False
            return False

    def stop_audio(self):
        """停止音频播放"""
        if self.is_playing:
            pygame.mixer.music.stop()
            self.is_playing = False


class ListenEngine:
    """极简的听写引擎，只负责播放"""

    def __init__(self):
        self.tts_engine = TTSEngine()
        self.player = AudioPlayer()
        self.current_text = ""
        self.playback_callback = None

    def play_text(self, text: str, callback: Callable = None) -> bool:
        """将文本转换为语音并播放"""
        self.current_text = text
        self.playback_callback = callback
        
        try:
            audio_data = self.tts_engine.text_to_audio(text)
            return self.player.play_audio_data(audio_data, callback)
        except Exception as e:
            logger.error(f"播放文本 '{text[:30]}...' 失败: {e}")
            return False


# 全局听写引擎实例
_listen_engine = None

def get_listen_engine() -> ListenEngine:
    """获取全局唯一的听写引擎实例"""
    global _listen_engine
    if _listen_engine is None:
        _listen_engine = ListenEngine()
    return _listen_engine

