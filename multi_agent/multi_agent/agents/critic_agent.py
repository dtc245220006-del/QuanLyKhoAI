from .agent_message import AgentMessage
from .base_agent import BaseAgent


class CriticAgent(BaseAgent):
    def __init__(self):
        super().__init__("critic_agent")

    def process(self, message: AgentMessage) -> AgentMessage:
        reasoning = message.payload.get("reasoning", {})
        rows = message.payload.get("rows", [])
        by_id = {r.get("ma_hang"): r for r in rows}
        errors = []

        for claim in reasoning.get("claims", []):
            item_id = claim.get("ma_hang")
            source = by_id.get(item_id)
            if source is None:
                errors.append(f"Mặt hàng {item_id} không có trong dữ liệu truy xuất")
                continue
            if claim.get("so_luong_ton") != source.get("so_luong_ton"):
                errors.append(f"Số lượng tồn của mã {item_id} không khớp dữ liệu DB")
            if claim.get("ten_hang") and claim.get("ten_hang") != source.get("ten_hang"):
                errors.append(f"Tên hàng của mã {item_id} không khớp dữ liệu DB")

        approved = not errors and isinstance(reasoning.get("answer"), str) and bool(reasoning.get("answer", "").strip())
        result = {
            "status": "APPROVED" if approved else "REJECT",
            "errors": errors,
            "checked_claims": len(reasoning.get("claims", [])),
        }
        return self.message(message.task_id, "orchestrator", "critic_result", result)
