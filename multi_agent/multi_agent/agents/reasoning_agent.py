import json

from .agent_message import AgentMessage
from .base_agent import BaseAgent
from ..services.gemini_service import generate_json


class ReasoningAgent(BaseAgent):
    def __init__(self):
        super().__init__("reasoning_agent")

    def process(self, message: AgentMessage) -> AgentMessage:
        data = message.payload
        question = data.get("question", "")
        rows = data.get("rows", [])
        documents = data.get("documents", [])

        prompt = f"""
Bạn là Reasoning Agent của hệ thống quản lý kho.
Chỉ sử dụng dữ liệu DB và Knowledge Base bên dưới.
Không được bịa số lượng tồn, tên hàng hoặc giá trị không có trong dữ liệu.
Trả JSON thuần gồm:
{{
  "answer": "...",
  "claims": [
    {{"ma_hang": 1, "so_luong_ton": 10, "ten_hang": "..."}}
  ],
  "recommendation": "..."
}}
Câu hỏi: {question}
DB:
{json.dumps(rows, ensure_ascii=False, indent=2)}
Knowledge Base:
{json.dumps(documents, ensure_ascii=False, indent=2)}
"""
        try:
            result = generate_json(prompt)
        except Exception:
            result = {
                "answer": self._fallback_answer(rows),
                "claims": [
                    {"ma_hang": r.get("ma_hang"), "so_luong_ton": r.get("so_luong_ton"), "ten_hang": r.get("ten_hang")}
                    for r in rows
                ],
                "recommendation": "Ưu tiên kiểm tra các mặt hàng có tồn thấp so với mức tối thiểu.",
            }

        return self.message(message.task_id, "critic_agent", "reasoning_result", result)

    @staticmethod
    def _fallback_answer(rows):
        if not rows:
            return "Không tìm thấy dữ liệu tồn kho phù hợp."
        names = [f"{r.get('ten_hang')} (tồn {r.get('so_luong_ton')})" for r in rows[:5]]
        return "Dữ liệu tồn kho phù hợp: " + ", ".join(names) + "."
