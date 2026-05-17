# -*- coding: utf-8 -*-
"""语音 API（报告 8.1 / 5.3.6-5.3.8）"""
from flask import jsonify, request
from app.api.v1 import api_bp
from app.utils.audio import AudioData
from app.core.voice_assistant import VoiceAssistant

_assistant = VoiceAssistant()
_assistant.initialize()


@api_bp.route("/voice/recognize", methods=["POST"])
def recognize_voice():
    """语音识别（8.1.2）"""
    data = request.get_json(silent=True) or {}
    if "audio_data" not in data:
        return jsonify({"error_code": "P001", "message": "缺少音频数据"}), 400

    audio = AudioData.from_base64(
        data["audio_data"],
        sample_rate=data.get("sample_rate", 16000),
        bit_depth=data.get("bit_depth", 16),
        channels=data.get("channels", 1),
    )
    result = _assistant.asr.recognize_voice(audio)

    if result.get("error_code"):
        return jsonify({
            "error_code": result["error_code"],
            "message": result.get("message", "识别失败"),
        }), 400 if result["error_code"] == "A001" else 500

    return jsonify({
        "status": "success",
        "text": result.get("corrected", ""),
        "raw_text": result.get("raw", ""),
        "confidence": result.get("confidence", 0),
    })


@api_bp.route("/voice/synthesize", methods=["POST"])
def synthesize_voice():
    """语音合成（8.1.4）"""
    data = request.get_json(silent=True) or {}
    text = data.get("text", "").strip()

    if not text:
        return jsonify({"error_code": "P001", "message": "缺少文本"}), 400
    if len(text) > 500:
        return jsonify({"error_code": "T002", "message": "文本过长，最多500字"}), 400

    audio = _assistant.tts.synthesize_speech(text)
    return jsonify({
        "status": "success",
        "audio_data": audio.to_base64(),
        "duration": round(audio.duration, 2),
        "sample_rate": audio.sample_rate,
    })


@api_bp.route("/voice/process", methods=["POST"])
def process_voice():
    """完整语音问答流程（8.1.1 → 8.1.5）"""
    data = request.get_json(silent=True) or {}

    # 8.1.1 接收音频数据
    if "audio_data" not in data:
        return jsonify({"error_code": "P001", "message": "缺少音频数据"}), 400

    audio = AudioData.from_base64(
        data["audio_data"],
        sample_rate=data.get("sample_rate", 16000),
        bit_depth=data.get("bit_depth", 16),
        channels=data.get("channels", 1),
    )

    # 完整流水线: VCL → ASR → LLM → TTS → VRL
    result = _assistant.process_voice_question(
        audio_data=audio,
        session_id=data.get("session_id"),
        user_id=data.get("user_id", "anonymous"),
    )

    if result.get("error_code"):
        return jsonify(result), 400 if result["error_code"] in ("A001", "P001") else 500

    # 8.1.5 返回完整响应
    return jsonify({
        "status": "success",
        "session_id": result["session_id"],
        "question": result["question"],
        "asr_confidence": result["asr_confidence"],
        "answer": result["answer"],
        "sources": [s.get("title", "") for s in result.get("sources", [])],
        "domain": result.get("domain", "通用"),
        "term_match_rate": result.get("term_match_rate", 0),
        "hallucination_score": result.get("hallucination_score", 0),
        "audio_data": result.get("audio"),
        "audio_duration": result.get("audio_duration", 0),
        "timeline": result.get("timeline", {}),
    })


@api_bp.route("/voice/status", methods=["GET"])
def voice_status():
    """获取语音系统各模块状态"""
    return jsonify(_assistant.get_status())
