import json
import re

from .agent_message import AgentMessage
from .base_agent import BaseAgent
from ..services.gemini_service import generate_json


class AnalystAgent(BaseAgent):
    def __init__(self):
        super().__init__("analyst_agent")

    def process(self, message: AgentMessage) -> AgentMessage:
        question = str(message.payload.get("question", "")).strip()
        if not question:
            return self.message(message.task_id, "orchestrator", "error", {}, "error", "Câu hỏi không được để trống")

        prompt = f"""
Bạn là Analyst Agent của hệ thống quản lý kho.
Chuyển câu hỏi tiếng Việt thành JSON thuần.
Các trường có thể dùng:
- intent: inventory_search | low_stock | warehouse_summary | item_search
- item_name: tên hàng nếu người dùng nêu
- group_name: tên nhóm hàng nếu có
- only_low_stock: true/false
- max_results: số lượng tối đa, mặc định 10
- keywords: danh sách từ khóa
Không tự tạo tên hàng, nhóm hàng hoặc số lượng.
Câu hỏi: {question}
"""

        try:
            data = generate_json(prompt)
        except Exception:
            # Fallback để demo vẫn hoạt động khi Gemini tạm thời lỗi.
            low_stock = any(x in question.lower() for x in ["thiếu", "sắp hết", "dưới mức", "tồn thấp"])
            intent = "low_stock" if low_stock else ("warehouse_summary" if "tổng quan" in question.lower() else "inventory_search")
            data = {
                "intent": intent,
                "item_name": None,
                "group_name": None,
                "only_low_stock": low_stock,
                "max_results": 10,
                "keywords": re.findall(r"\w+", question.lower())[:10],
            }

        data.setdefault("intent", "inventory_search")
        data.setdefault("item_name", None)
        data.setdefault("group_name", None)
        data.setdefault("only_low_stock", False)
        data.setdefault("max_results", 10)
        data.setdefault("keywords", [])

        return self.message(message.task_id, "database_agent", "structured_requirements", data)
