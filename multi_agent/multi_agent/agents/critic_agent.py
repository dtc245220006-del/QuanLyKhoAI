from .agent_message import AgentMessage
from .base_agent import BaseAgent


class CriticAgent(BaseAgent):
    def __init__(self):
        super().__init__("critic_agent")

    def process(self, message: AgentMessage) -> AgentMessage:
        reasoning = message.payload.get("reasoning", {})
        rows = message.payload.get("rows", [])
        question = str(message.payload.get("question", "")).lower().strip()
        by_id = {r.get("ma_hang"): r for r in rows}
        claims = reasoning.get("claims", [])
        errors = []

        if rows and not claims:
            errors.append("Không có claim để đối chiếu với dữ liệu DB.")

        for claim in claims:
            item_id = claim.get("ma_hang")
            source = by_id.get(item_id)
            if source is None:
                errors.append(f"Mặt hàng {item_id} không có trong dữ liệu truy xuất")
                continue

            if claim.get("so_luong_ton") != source.get("so_luong_ton"):
                errors.append(f"Số lượng tồn của mã {item_id} không khớp dữ liệu DB")

            if claim.get("ten_hang") and claim.get("ten_hang") != source.get("ten_hang"):
                errors.append(f"Tên hàng của mã {item_id} không khớp dữ liệu DB")

        if question:
            if any(k in question for k in (
                "dưới mức tồn",
                "tồn thấp",
                "sắp hết",
                "thiếu hàng",
                "thiếu",
                "cần nhập",
                "nhập bổ sung",
                "nguy cơ thiếu",
                "cần kiểm tra để nhập",
            )):
                wrong = [
                    claim for claim in claims
                    if by_id.get(claim.get("ma_hang"), {}).get("so_luong_ton")
                    >= by_id.get(claim.get("ma_hang"), {}).get("ton_toi_thieu")
                ]
                if wrong:
                    errors.append("Câu trả lời chứa mặt hàng không thuộc nhóm dưới mức tồn tối thiểu.")

            if "cao nhất" in question and rows:
                max_stock = max(r.get("so_luong_ton") for r in rows)
                if not any(c.get("so_luong_ton") == max_stock for c in claims):
                    errors.append("Câu trả lời chưa nêu mặt hàng có tồn kho cao nhất.")

            if "thấp nhất" in question and rows:
                min_stock = min(r.get("so_luong_ton") for r in rows)
                if not any(c.get("so_luong_ton") == min_stock for c in claims):
                    errors.append("Câu trả lời chưa nêu mặt hàng có tồn kho thấp nhất.")

            if "cao xuống thấp" in question:
                values = [c.get("so_luong_ton") for c in claims]
                if values != sorted(values, reverse=True):
                    errors.append("Câu trả lời chưa sắp xếp tồn kho theo thứ tự giảm dần.")

        answer = reasoning.get("answer")
        approved = (
            not errors
            and isinstance(answer, str)
            and bool(answer.strip())
        )

        result = {
            "status": "APPROVED" if approved else "REJECT",
            "errors": errors,
            "checked_claims": len(claims),
        }
        return self.message(
            message.task_id,
            "orchestrator",
            "critic_result",
            result,
        )
