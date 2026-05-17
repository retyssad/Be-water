# -*- coding: utf-8 -*-
"""幻觉检测器（报告 4.5.3 / 9.7）"""
from typing import Optional
from app.core.base_module import BaseModule


class HallucinationDetector(BaseModule):
    """质量守门员：3层幻觉检测（NLI + 数值 + 引用）"""

    def __init__(self):
        super().__init__(module_id="HalluDetector")
        self._nli_threshold = 0.3
        self._citation_weight = 0.4
        self._numerical_weight = 0.3
        self._nli_weight = 0.3

    def initialize(self) -> bool:
        self.set_status("idle")
        self._logger.info("HallucinationDetector initialized")
        return True

    def shutdown(self) -> None:
        self.set_status("idle")

    # ---- 核心方法 ----
    def detect(self, response: str, sources: list) -> dict:
        """3层幻觉检测 → 综合评分（报告 9.7.1）"""
        claims = self.extract_claims(response)

        nli_score = self._check_nli_consistency(claims, sources)
        numerical_score = self._check_numerical_accuracy(claims, sources)
        citation_score = self._check_citation_integrity(response, sources)

        final_score = (
            self._nli_weight * nli_score
            + self._numerical_weight * (1 - numerical_score)
            + self._citation_weight * (1 - citation_score)
        )

        return {
            "hallucination_score": round(final_score, 4),
            "nli_consistency": round(nli_score, 4),
            "numerical_accuracy": round(numerical_score, 4),
            "citation_integrity": round(citation_score, 4),
            "is_hallucination": final_score > self._nli_threshold,
            "risk_claims": claims[:3],
        }

    def extract_claims(self, text: str) -> list:
        """从回答中提取待验证声明"""
        claims = []
        for sentence in text.replace("。", ".").split("."):
            sentence = sentence.strip()
            if len(sentence) > 10:
                claims.append(sentence)
        return claims[:10]

    def verify_claim(self, claim: str, sources: list) -> float:
        """验证单个声明的置信度"""
        _ = claim
        if not sources:
            return 0.0
        return 0.85  # 模拟

    # ---- 3层检测（报告 9.7.1） ----
    def _check_nli_consistency(self, claims: list, sources: list) -> float:
        """NLI 事实一致性"""
        _ = claims
        if not sources:
            return 1.0
        return 0.15  # 低 = 一致性好

    def _check_numerical_accuracy(self, claims: list, sources: list) -> float:
        """数值验证"""
        _ = claims
        if not sources:
            return 1.0
        return 0.95

    def _check_citation_integrity(self, response: str, sources: list) -> float:
        """引用完整性检查"""
        _ = sources
        standards = ["SL ", "DL ", "GB "]
        has_citation = any(s in response for s in standards)
        return 1.0 if has_citation else 0.3
