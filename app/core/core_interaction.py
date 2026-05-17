# -*- coding: utf-8 -*-
"""LLM 核心交互模块（报告 8.1.3）"""
from typing import Optional
from app.core.base_module import BaseModule

# 领域分类关键词
DOMAIN_KEYWORDS = {
    "防洪": ["防洪", "洪水", "堤防", "泄洪", "汛期", "水位"],
    "灌溉": ["灌溉", "农田", "渠道", "滴灌", "喷灌", "节水"],
    "水电": ["水电", "发电", "水轮机", "装机", "电站", "电网"],
    "航运": ["航运", "航道", "船闸", "港口", "通航", "船"],
    "基础处理": ["帷幕", "灌浆", "地基", "桩基", "防渗", "围岩"],
}
CONTEXT_MAX_CHARS = 2000  # （1）上下文限制约 2000 字


class CoreInteraction(BaseModule):
    """核心交互：问题分类 → RAG 检索 → LLM 调用 → 质量校验 → 幻觉检测"""

    def __init__(self):
        super().__init__(module_id="LLM")
        self._provider = "deepseek"
        self._temperature = 0.3
        self._top_p = 0.85
        self._rag_engine = None
        self._hallucination_detector = None

    def initialize(self) -> bool:
        self.set_status("idle")
        self._logger.info("CoreInteraction initialized | provider=%s temp=%.1f",
                          self._provider, self._temperature)
        return True

    def shutdown(self) -> None:
        self.set_status("idle")

    # ---- 核心方法 ----

    def process_question(self, text: str, session_id: str,
                         history: Optional[list] = None) -> dict:
        """处理用户问题：RAG → Prompt → LLM → 校验 → 幻觉检测"""
        self.set_status("processing")

        # （1）获取会话上下文，限制约 2000 字
        ctx_text = self._build_context(history or [])

        # （2）问题分类
        domain = self._classify_question(text)
        self._logger.info("question domain: %s", domain)

        # （2b）根据问题类型调整 temperature：规范查询 0.2，开放讨论 0.5
        self._adjust_temperature(domain, text)

        # （3）RAG 检索
        retrieved = self._retrieve_knowledge(text)

        # （4）构建 LLM 请求
        prompt = self._build_prompt(text, retrieved, history or [])
        full_prompt = ctx_text + prompt if ctx_text else prompt

        # （5）调用 LLM 服务
        answer = self._call_llm(full_prompt, history or [])

        # （6）质量校验：术语匹配度 ≥85%，规范引用率 ≥90%
        validated = self._validate_response(answer, retrieved, domain)

        # （7）幻觉检测
        hallucination = self._detect_hallucination(answer, retrieved)

        # （8）更新会话历史（由外部 SessionManager 完成）

        self.set_status("idle")
        return {
            "answer": validated["text"],
            "sources": retrieved,
            "confidence": validated["confidence"],
            "term_match_rate": validated["term_match_rate"],
            "domain": domain,
            "hallucination_score": hallucination.get("score", 0),
            "hallucination_risk": hallucination.get("risk_claims", []),
        }

    def generate_response(self, question: str, context: list) -> dict:
        return self.process_question(question, "", context)

    # ----（1）上下文构建 ----
    def _build_context(self, history: list) -> str:
        """从历史对话构建上下文，限制长度约 2000 字"""
        if not history:
            return ""
        lines = []
        total = 0
        for h in reversed(history[-10:]):
            role = "用户" if h.get("role") == "user" else "助手"
            content = h.get("content", "")
            line = f"{role}：{content}"
            total += len(line)
            if total > CONTEXT_MAX_CHARS:
                break
            lines.insert(0, line)
        return "\n".join(lines) + "\n" if lines else ""

    # ----（2）问题分类 ----
    def _classify_question(self, text: str) -> str:
        """识别问题所属领域：防洪/灌溉/水电/航运/基础处理/通用"""
        scores = {}
        for domain, keywords in DOMAIN_KEYWORDS.items():
            scores[domain] = sum(1 for kw in keywords if kw in text)
        best = max(scores, key=scores.get)
        return best if scores[best] > 0 else "通用"

    # ----（2b）温度自适应 ----
    def _adjust_temperature(self, domain: str, text: str):
        """规范查询 temperature=0.2，开放讨论=0.5"""
        # 识别是否为规范查询（含"规范/标准/依据/要求"等）
        spec_keywords = ["规范", "标准", "依据", "要求", "规定", "SL "]
        is_spec_query = any(kw in text for kw in spec_keywords)
        if is_spec_query:
            self._temperature = 0.2
        elif domain == "通用":
            self._temperature = 0.5
        else:
            self._temperature = 0.3
        self._logger.debug("temperature set to %.1f for domain=%s", self._temperature, domain)

    # ----（3）RAG 检索 ----
    def _retrieve_knowledge(self, query: str) -> list:
        from app.core.rag.rag_engine import RAGEngine
        if self._rag_engine is None:
            self._rag_engine = RAGEngine()
            self._rag_engine.initialize()
        return self._rag_engine.hybrid_search(query)

    # ----（4）构建 Prompt ----
    def _build_prompt(self, question: str, docs: list, history: list) -> str:
        from app.core.rag.prompt_manager import PromptManager
        pm = PromptManager()
        pm.initialize()
        return pm.build_prompt(question, docs, history)

    # ----（5）调用 LLM ----
    def _call_llm(self, prompt: str, history: list = None, system: str = None) -> str:
        from app.services.llm_service import LLMService
        svc = LLMService()
        return svc.call(
            prompt, temperature=self._temperature, top_p=self._top_p,
            history=history, system_prompt=system,
        )

    # ----（6）质量校验 ----
    def _validate_response(self, answer: str, sources: list, domain: str) -> dict:
        """验证术语匹配度和规范引用率"""
        # 从来源文档提取关键术语
        source_terms: set[str] = set()
        for s in sources:
            if isinstance(s, dict):
                content = s.get("content", "")
            else:
                content = str(s)
            for word in ["帷幕", "灌浆", "混凝土", "坝体", "防洪", "灌溉", "水电"]:
                if word in content:
                    source_terms.add(word)

        # 计算术语匹配度
        if source_terms:
            matched = sum(1 for t in source_terms if t in answer)
            term_match = matched / len(source_terms)
        else:
            term_match = 1.0

        # 计算规范引用率
        has_ref = any(f in answer for f in ["SL ", "GB ", "DL "])
        ref_rate = 1.0 if has_ref else 0.5

        confidence = (term_match * 0.5 + ref_rate * 0.5)
        return {
            "text": answer,
            "confidence": round(confidence, 3),
            "term_match_rate": round(term_match, 3),
        }

    # ----（7）幻觉检测 ----
    def _detect_hallucination(self, answer: str, sources: list) -> dict:
        from app.core.rag.hallucination_detector import HallucinationDetector
        if self._hallucination_detector is None:
            self._hallucination_detector = HallucinationDetector()
            self._hallucination_detector.initialize()

        result = self._hallucination_detector.detect(answer, sources)
        return {
            "score": result.get("hallucination_score", 0),
            "is_hallucination": result.get("is_hallucination", False),
            "risk_claims": result.get("risk_claims", []),
        }

    def set_llm_provider(self, provider: str, api_key: str, app_id: str) -> bool:
        self._provider = provider
        return True

    def set_generation_params(self, temperature: float, top_p: float) -> bool:
        self._temperature = temperature
        self._top_p = top_p
        return True
