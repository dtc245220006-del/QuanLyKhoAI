import json

from .agent_message import AgentMessage
from .base_agent import BaseAgent
from ..services.gemini_service import generate_text


class ResponseAgent(BaseAgent):
    def __init__(self):
        super().__init__("response_agent")

    def process(self, message: AgentMessage) -> AgentMessage:
        question = message.payload.get("question", "")
        reasoning = message.payload.get("reasoning", {})
        prompt = f"""
Bạn là Response Agent của hệ thống quản lý kho.
Viết câu trả lời ngắn gọn bằng tiếng Việt.
Chỉ dùng dữ liệu được cung cấp. Không thêm số liệu mới.
Câu hỏi: {question}
Kết quả suy luận:
{json.dumps(reasoning, ensure_ascii=False, indent=2)}
"""
        try:
            answer = generate_text(prompt)
        except Exception:
            answer = reasoning.get("answer", "Không có kết quả.")
        return self.message(message.task_id, "user", "final_response", {"answer": answer.strip()})
