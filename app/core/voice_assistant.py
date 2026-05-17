# -*- coding: utf-8 -*-
"""VoiceAssistant 编排器 — 串联 8.1.1~8.1.5 完整语音问答流程"""
from app.core.voice_capture import VoiceCapture
from app.core.speech_recognizer import SpeechRecognizer
from app.core.core_interaction import CoreInteraction
from app.core.speech_synthesizer import SpeechSynthesizer
from app.core.voice_response import VoiceResponse
from app.core.session_manager import SessionManager
from app.core.config_manager import ConfigManager
from app.core.error_handler import ErrorHandler
from app.utils.audio import AudioData
from app.utils.helpers import now_str


class VoiceAssistant:
    """系统主编排器：串联 8 大模块"""

    def __init__(self):
        self.vcl = VoiceCapture()          # 8.1.1 语音采集
        self.asr = SpeechRecognizer()       # 8.1.2 语音识别
        self.llm = CoreInteraction()        # 8.1.3 核心交互
        self.tts = SpeechSynthesizer()      # 8.1.4 语音合成
        self.vrl = VoiceResponse()          # 8.1.5 语音响应
        self.session = SessionManager()
        self.config = ConfigManager()
        self.error = ErrorHandler()

    def initialize(self) -> bool:
        for mod in [self.vcl, self.asr, self.llm, self.tts, self.vrl,
                    self.session, self.config, self.error]:
            if not mod.initialize():
                return False
        return True

    def shutdown(self):
        for mod in [self.vcl, self.asr, self.llm, self.tts, self.vrl,
                    self.session, self.config, self.error]:
            mod.shutdown()

    # ---- 完整语音问答流程（报告 8.1） ----

    def process_voice_question(self, audio_data: AudioData,
                               session_id: str = None,
                               user_id: str = "anonymous") -> dict:
        """完整处理一次语音问答，串联 8.1.1 → 8.1.5"""
        timeline = {}

        # ---- 8.1.1 语音采集预处理 ----
        audio = self.vcl.preprocess(audio_data)
        timeline["capture"] = "done"

        # ---- 8.1.2 语音识别 ----
        rec_result = self.asr.recognize_voice(audio)
        if rec_result.get("error_code"):
            return self.error.format_error_response(rec_result["error_code"],
                                                     {"detail": rec_result.get("message")})
        text = rec_result.get("corrected", "")
        confidence = rec_result.get("confidence", 0)
        timeline["asr"] = {"text": text, "confidence": confidence}

        # ---- 会话管理 ----
        if not session_id:
            session_id = self.session.create_session(user_id)
        ctx = self.session.get_session(session_id)
        if ctx is None:
            return self.error.format_error_response("S003")
        self.session.update_session(session_id, {
            "role": "user", "content": text, "timestamp": now_str()
        })

        # ---- 8.1.3 核心交互 ----
        answer_data = self.llm.process_question(text, session_id, ctx.history)
        timeline["llm"] = {
            "domain": answer_data.get("domain", "通用"),
            "confidence": answer_data.get("confidence"),
        }

        # ---- 更新会话 ----
        self.session.update_session(session_id, {
            "role": "assistant", "content": answer_data["answer"], "timestamp": now_str()
        })

        # ---- 8.1.4 语音合成 ----
        audio_out = self.tts.synthesize_speech(answer_data["answer"])
        timeline["tts"] = {"duration": round(audio_out.duration, 2)}

        # ---- 8.1.5 语音响应 ----
        self.vrl.play_audio(audio_out)
        timeline["vrl"] = self.vrl.get_playback_status()

        return {
            "session_id": session_id,
            "question": text,
            "asr_confidence": confidence,
            "answer": answer_data["answer"],
            "sources": answer_data.get("sources", []),
            "domain": answer_data.get("domain", "通用"),
            "term_match_rate": answer_data.get("term_match_rate", 0),
            "hallucination_score": answer_data.get("hallucination_score", 0),
            "audio": audio_out.to_base64(),
            "audio_duration": round(audio_out.duration, 2),
            "timeline": timeline,
        }

    def get_status(self) -> dict:
        return {
            "vcl": {"state": self.vcl.capture_state, "status": self.vcl.status},
            "asr": {"provider": self.asr.provider, "status": self.asr.status},
            "llm": {"status": self.llm.status},
            "tts": {"status": self.tts.status},
            "vrl": {"state": self.vrl.playback_state, "status": self.vrl.status},
            "session": {"status": self.session.status},
        }
