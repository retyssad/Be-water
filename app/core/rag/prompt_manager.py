# -*- coding: utf-8 -*-
"""Prompt 管理器（报告 4.5.2 / 9.3）"""
from app.core.base_module import BaseModule

SYSTEM_TEMPLATE = """你是一位资深水利工程技术专家，擅长解答水利工程领域的技术问题。
请严格遵循以下规则：
1. 回答必须基于提供的水利行业规范文档和工程案例
2. 引用规范时必须标注具体的标准编号（如SL 319-2018）
3. 涉及计算时必须展示计算过程和依据
4. 使用专业术语时请确保准确性，必要时给出解释
5. 如果不确定答案，请明确说明"该问题超出当前知识库范围"
6. 回答语言：中文，风格：专业、严谨、条理清晰

当前对话上下文：{history_summary}
参考文档：
{retrieved_docs}

用户问题：{question}
请回答："""

FEW_SHOT_EXAMPLES = [
    {
        "role": "user",
        "content": "混凝土重力坝的温控措施有哪些？",
    },
    {
        "role": "assistant",
        "content": "根据《混凝土重力坝设计规范》SL 319-2018，主要温控措施包括："
                   "1）优化混凝土配合比，采用低热水泥；"
                   "2）控制浇筑温度，夏季≤28℃，冬季≥5℃；"
                   "3）通水冷却，一期冷却水温≤12℃；"
                   "4）表面保温，拆模后及时覆盖保温材料。"
    },
]


class PromptManager(BaseModule):
    """提示词工程中枢：结构化管理系统/少样本/思维链提示词"""

    def __init__(self):
        super().__init__(module_id="PromptManager")
        self._system_template = SYSTEM_TEMPLATE
        self._few_shot_examples = FEW_SHOT_EXAMPLES
        self._domain = "water_conservancy"

    def initialize(self) -> bool:
        self.set_status("idle")
        self._logger.info("PromptManager initialized (domain=%s)", self._domain)
        return True

    def shutdown(self) -> None:
        self.set_status("idle")

    # ---- 核心方法 ----
    def build_prompt(self, question: str, context: list, history: list) -> str:
        """构建完整提示词：系统模板 + few-shot + 上下文 + 问题"""
        history_summary = self._summarize_history(history)
        retrieved_docs = self._format_docs(context)

        prompt = self._system_template.format(
            history_summary=history_summary,
            retrieved_docs=retrieved_docs,
            question=question,
        )

        # 追加 few-shot 示例
        prompt += "\n\n=== 参考示例 ===\n"
        for ex in self._few_shot_examples:
            prompt += f"\n{ex['role']}: {ex['content']}\n"

        return prompt

    def add_few_shot(self, examples: list) -> None:
        self._few_shot_examples.extend(examples)

    def optimize_prompt(self, prompt: str) -> str:
        """提示词优化：去除冗余、确保结构完整"""
        lines = [l for l in prompt.split("\n") if l.strip()]
        return "\n".join(lines)

    # ---- 内部 ----
    @staticmethod
    def _summarize_history(history: list, max_chars: int = 2000) -> str:
        """对话历史摘要"""
        texts = [f"{m.get('role', '')}: {m.get('content', '')}" for m in history[-10:]]
        summary = "\n".join(texts)
        if len(summary) > max_chars:
            summary = summary[:max_chars] + "..."
        return summary or "无历史对话"

    @staticmethod
    def _format_docs(docs: list) -> str:
        """格式化检索文档"""
        parts = []
        for doc in docs[:5]:
            source = doc.get("source", doc.get("doc_type", "未知"))
            title = doc.get("title", "")
            content = doc.get("content", "")[:300]
            parts.append(f"[来源: {source}] {title}\n{content}")
        return "\n\n".join(parts) if parts else "无相关参考文档"
