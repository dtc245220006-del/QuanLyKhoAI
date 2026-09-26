from pathlib import Path
import json
import time

from .agents.orchestrator_agent import OrchestratorAgent


def run_questions(questions: list[str]):
    rows = []
    orchestrator = OrchestratorAgent(max_retries=2)
    for q in questions:
        started = time.perf_counter()
        result = orchestrator.run(q)
        elapsed_ms = (time.perf_counter() - started) * 1000
        rows.append({
            "question": q,
            "time_ms": round(elapsed_ms, 2),
            "status": result.get("status"),
            "retry_count": result.get("retry_count", 0),
        })
    return rows


if __name__ == "__main__":
    questions = [
        "Hàng nào đang dưới mức tồn tối thiểu?",
        "Cho tôi xem tồn kho hiện tại.",
        "Có những mặt hàng nào trong nhóm Máy tính & phụ kiện?",
    ]
    output = run_questions(questions)
    Path("multi_agent_benchmark.json").write_text(
        json.dumps(output, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    print(json.dumps(output, ensure_ascii=False, indent=2))
