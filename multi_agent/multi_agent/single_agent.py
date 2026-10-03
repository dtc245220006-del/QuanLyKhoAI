import json
import re
import time

from .tools.sql_tool import search_inventory
from .tools.vector_search_tool import search_knowledge
from .services.gemini_service import generate_json, get_metrics, reset_metrics


def build_intent(question: str) -> dict:
    text = question.lower().strip()

    low_stock = any(
        keyword in text
        for keyword in (
            "dưới mức tồn",
            "tồn thấp",
            "sắp hết",
            "thiếu hàng",
            "thiếu",
            "cần nhập",
            "nhập bổ sung",
            "nguy cơ thiếu",
        )
    )

    sort_order = "desc" if any(
        keyword in text
        for keyword in ("cao nhất", "nhiều nhất", "lớn nhất", "cao xuống thấp")
    ) else "asc"

    group_name = None
    group_match = re.search(
        r"(?:nhóm|nhóm hàng)\s+([^?.,]+)",
        question,
        flags=re.IGNORECASE,
    )
    if group_match:
        group_name = group_match.group(1).strip()

    return {
        "intent": "low_stock" if low_stock else "inventory_search",
        "item_name": None,
        "group_name": group_name,
        "only_low_stock": low_stock,
        "max_results": 50,
        "sort_by": "stock",
        "sort_order": sort_order,
    }


def validate_claims(rows: list[dict], claims: list[dict]) -> list[str]:
    by_id = {row.get("ma_hang"): row for row in rows}
    errors = []

    for claim in claims or []:
        item_id = claim.get("ma_hang")
        source = by_id.get(item_id)
        if source is None:
            errors.append(f"Mặt hàng {item_id} không có trong dữ liệu DB")
            continue

        if claim.get("so_luong_ton") != source.get("so_luong_ton"):
            errors.append(f"Số lượng tồn của mã {item_id} không khớp dữ liệu DB")

        if claim.get("ten_hang") and claim.get("ten_hang") != source.get("ten_hang"):
            errors.append(f"Tên hàng của mã {item_id} không khớp dữ liệu DB")

    if rows and not claims:
        errors.append("Câu trả lời không cung cấp claim để đối chiếu với dữ liệu DB")

    return errors


class SingleAgent:
    """Một Agent duy nhất, trực tiếp dùng SQL + RAG rồi gọi Gemini."""

    def __init__(self):
        self.name = "single_agent"

    def run(self, question: str) -> dict:
        question = question.strip()
        if not question:
            return {
                "success": False,
                "status": "ERROR",
                "answer": "Câu hỏi không được để trống.",
                "time_ms": 0,
                "llm_calls": 0,
                "data": [],
                "knowledge": [],
                "claims": [],
                "accuracy_check": {
                    "valid": False,
                    "errors": ["Câu hỏi không được để trống"],
                },
            }

        reset_metrics()
        started = time.perf_counter()

        intent = build_intent(question)
        rows = search_inventory(intent)

        try:
            documents = search_knowledge(question, top_k=4)
        except Exception as exc:
            documents = []
            rag_warning = str(exc)
        else:
            rag_warning = None

        prompt = f"""
Bạn là Single-Agent của hệ thống quản lý kho.
Bạn có thể sử dụng dữ liệu DB và Knowledge Base được cung cấp bên dưới.

QUY TẮC:
1. Chỉ sử dụng thông tin có trong DB hoặc Knowledge Base.
2. Không được bịa tên hàng, số lượng tồn, giá hoặc thông tin khác.
3. Nếu DB không có dữ liệu phù hợp, nói rõ không tìm thấy dữ liệu.
4. Trả JSON thuần theo đúng cấu trúc:
{{
  "answer": "câu trả lời tiếng Việt",
  "claims": [
    {{"ma_hang": 1, "ten_hang": "...", "so_luong_ton": 10}}
  ],
  "recommendation": "..."
}}

CÂU HỎI:
{question}

DB:
{json.dumps(rows, ensure_ascii=False, indent=2)}

KNOWLEDGE BASE:
{json.dumps(documents, ensure_ascii=False, indent=2)}
"""

        try:
            reasoning = generate_json(prompt)
        except Exception as exc:
            elapsed_ms = (time.perf_counter() - started) * 1000
            return {
                "success": False,
                "status": "ERROR",
                "answer": "Single-Agent không thể tạo câu trả lời.",
                "time_ms": round(elapsed_ms, 2),
                **get_metrics(),
                "data": rows,
                "knowledge": documents,
                "claims": [],
                "error": str(exc),
                "accuracy_check": {
                    "valid": False,
                    "errors": [str(exc)],
                },
            }

        claims = reasoning.get("claims", [])
        errors = validate_claims(rows, claims)
        elapsed_ms = (time.perf_counter() - started) * 1000

        return {
            "success": not errors,
            "status": "APPROVED" if not errors else "REJECTED",
            "answer": str(reasoning.get("answer", "")).strip(),
            "time_ms": round(elapsed_ms, 2),
            **get_metrics(),
            "data": rows,
            "knowledge": documents,
            "claims": claims,
            "critic": {
                "status": "APPROVED" if not errors else "REJECT",
                "errors": errors,
                "checked_claims": len(claims),
            },
            "accuracy_check": {
                "valid": not errors,
                "errors": errors,
            },
            "rag_warning": rag_warning,
        }
