# -*- coding: utf-8 -*-
"""术语库查询 API（报告 5.3.10）"""
from flask import jsonify, request
from app.api.v1 import api_bp

TERM_DB = {
    "帷幕灌浆": {
        "term": "帷幕灌浆",
        "pinyin": "weimu guanjiang",
        "definition": "在坝基或岸坡中钻孔，用压力灌注浆液形成防渗帷幕的工程措施。",
        "category": "基础处理",
        "source": "SL 570-2013",
    },
    "戗堤": {
        "term": "戗堤",
        "pinyin": "qiang di",
        "definition": "在河道中修筑的临时围堰，用于截流施工。",
        "category": "施工导流",
        "source": "SL 252-2017",
    },
}


@api_bp.route("/terminology/search", methods=["GET"])
def search_terminology():
    term = request.args.get("term", "")
    fuzzy = request.args.get("fuzzy", "false").lower() == "true"

    if not term:
        return jsonify({"error_code": "P001", "message": "缺少查询参数"}), 400

    if term in TERM_DB:
        return jsonify(TERM_DB[term])

    if fuzzy:
        for key, val in TERM_DB.items():
            if term in key or term in val.get("pinyin", ""):
                return jsonify(val)

    return jsonify({"error_code": "S001", "message": "术语未找到"}), 404
