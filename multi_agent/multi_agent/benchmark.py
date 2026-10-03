import json
import statistics
import time
from pathlib import Path

from .agents.orchestrator_agent import OrchestratorAgent
from .single_agent import SingleAgent


QUESTIONS = [
    "Hàng nào đang dưới mức tồn tối thiểu?",
    "Cho tôi xem tồn kho hiện tại.",
    "Có những mặt hàng nào trong kho?",
    "Mặt hàng nào có số lượng tồn cao nhất?",
    "Có mặt hàng nào đang có nguy cơ thiếu hàng không?",
    "Hãy cho biết các mặt hàng cần nhập bổ sung.",
    "Mặt hàng nào có số lượng tồn thấp nhất?",
    "Hãy liệt kê tồn kho từ cao xuống thấp.",
    "Hãy giải thích tình trạng tồn kho hiện tại của kho.",
    "Mặt hàng nào cần kiểm tra để nhập bổ sung?",
]


def _validate_claims(result: dict) -> tuple[bool, str]:
    rows = result.get("data") or []
    claims = result.get("claims") or []
    by_id = {row.get("ma_hang"): row for row in rows}

    if result.get("status") != "APPROVED":
        return False, f"Status = {result.get('status')}"

    if rows and not claims:
        return False, "Có dữ liệu SQL nhưng không có claim để đối chiếu."

    for claim in claims:
        source = by_id.get(claim.get("ma_hang"))
        if source is None:
            return False, "Claim chứa mã hàng không tồn tại trong SQL."
        if claim.get("so_luong_ton") != source.get("so_luong_ton"):
            return False, "Claim có số lượng tồn không khớp SQL."
        if claim.get("ten_hang") and claim.get("ten_hang") != source.get("ten_hang"):
            return False, "Claim có tên hàng không khớp SQL."

    return True, "Claims khớp dữ liệu SQL."


def _apply_question_oracle(result: dict, question: str) -> tuple[int, str]:
    ok, reason = _validate_claims(result)
    if not ok:
        return 0, reason

    rows = result.get("data") or []
    claims = result.get("claims") or []
    if not rows:
        return 1, "Không có dữ liệu phù hợp và hệ thống trả về trạng thái rỗng."

    q = question.lower()
    by_id = {row.get("ma_hang"): row for row in rows}

    if any(k in q for k in (
        "dưới mức tồn",
        "tồn thấp",
        "cần nhập",
        "nhập bổ sung",
        "nguy cơ thiếu",
        "cần kiểm tra",
    )):
        wrong = [
            c for c in claims
            if by_id[c["ma_hang"]]["so_luong_ton"]
            >= by_id[c["ma_hang"]]["ton_toi_thieu"]
        ]
        if wrong:
            return 0, "Có claim không thuộc nhóm dưới mức tồn tối thiểu."
        return 1, "Tất cả claim đều thỏa tồn < mức tối thiểu."

    if "cao nhất" in q:
        max_stock = max(row["so_luong_ton"] for row in rows)
        if not any(c.get("so_luong_ton") == max_stock for c in claims):
            return 0, "Không có claim chứa mức tồn cao nhất."
        return 1, "Claim chứa mặt hàng có tồn cao nhất."

    if "thấp nhất" in q:
        min_stock = min(row["so_luong_ton"] for row in rows)
        if not any(c.get("so_luong_ton") == min_stock for c in claims):
            return 0, "Không có claim chứa mức tồn thấp nhất."
        return 1, "Claim chứa mặt hàng có tồn thấp nhất."

    if "cao xuống thấp" in q:
        values = [c.get("so_luong_ton") for c in claims]
        if values != sorted(values, reverse=True):
            return 0, "Thứ tự claim không giảm dần theo số lượng tồn."
        return 1, "Claims được sắp xếp giảm dần theo tồn kho."

    return 1, "Claims đã được đối chiếu với dữ liệu SQL."


def _score_single(result: dict, question: str) -> tuple[int, str]:
    return _apply_question_oracle(result, question)


def _score_multi(result: dict, question: str) -> tuple[int, str]:
    critic = result.get("critic") or {}
    if result.get("status") != "APPROVED":
        return 0, f"Workflow status = {result.get('status')}"
    if critic.get("status") != "APPROVED":
        return 0, "; ".join(critic.get("errors") or ["Critic chưa approve"])
    return _apply_question_oracle(result, question)


def _run_suite(agent, scorer, label: str):
    rows = []
    for index, question in enumerate(QUESTIONS, start=1):
        started = time.perf_counter()
        result = agent.run(question)
        elapsed_ms = round((time.perf_counter() - started) * 1000, 2)
        accuracy, oracle_reason = scorer(result, question)
        rows.append({
            "id": f"{label}-{index:02d}",
            "question": question,
            "accuracy": accuracy,
            "oracle_reason": oracle_reason,
            "time_ms": result.get("time_ms", elapsed_ms),
            "llm_calls": result.get("llm_calls", 0),
            "status": result.get("status"),
            "retry_count": result.get("retry_count", 0),
            "answer": result.get("answer", ""),
        })
    return rows


def _summary(rows):
    return {
        "accuracy_percent": round(
            sum(row["accuracy"] for row in rows) / len(rows) * 100,
            2,
        ),
        "avg_time_ms": round(
            statistics.mean(row["time_ms"] for row in rows),
            2,
        ),
        "avg_llm_calls": round(
            statistics.mean(row["llm_calls"] for row in rows),
            2,
        ),
        "total_llm_calls": sum(row["llm_calls"] for row in rows),
    }


def run():
    single_rows = _run_suite(SingleAgent(), _score_single, "SINGLE")
    multi_rows = _run_suite(
        OrchestratorAgent(max_retries=2),
        _score_multi,
        "MULTI",
    )

    result = {
        "question_count": len(QUESTIONS),
        "oracle": "Data-grounded claim validation against the live MySQL result set.",
        "single_agent": {
            "summary": _summary(single_rows),
            "results": single_rows,
        },
        "multi_agent": {
            "summary": _summary(multi_rows),
            "results": multi_rows,
        },
        "generated_at": time.strftime("%Y-%m-%dT%H:%M:%S"),
    }

    output = Path("multi_agent_benchmark.json")
    output.write_text(
        json.dumps(result, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return result


if __name__ == "__main__":
    run()
