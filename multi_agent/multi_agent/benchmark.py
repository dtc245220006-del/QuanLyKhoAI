import json
import time

from .agents.analyst_agent import AnalystAgent
from .agents.database_agent import DatabaseAgent
from .agents.rag_agent import RAGAgent
from .agents.response_agent import ResponseAgent
from .agents.agent_message import AgentMessage
from .services.gemini_service import generate_text, reset_metrics, get_metrics


def run_single_agent(question: str):
    reset_metrics()
    started = time.perf_counter()
    analyst = AnalystAgent()
    analyst_msg = analyst.process(AgentMessage(
        task_id="SINGLE-001", from_agent="user", to_agent="analyst_agent",
        message_type="user_question", payload={"question": question}
    ))
    db = DatabaseAgent().process(analyst_msg)
    rag = RAGAgent().process(AgentMessage(
        task_id="SINGLE-001", from_agent="user", to_agent="rag_agent",
        message_type="rag_request", payload={"question": question}
    ))
    prompt = f"""
Bạn là Single-Agent tư vấn kho. Trả lời câu hỏi chỉ từ dữ liệu DB và Knowledge Base.
Câu hỏi: {question}
DB: {json.dumps(db.payload.get('rows', []), ensure_ascii=False)}
Knowledge: {json.dumps(rag.payload.get('documents', []), ensure_ascii=False)}
Không bịa số liệu.
"""
    answer = generate_text(prompt)
    elapsed_ms = (time.perf_counter() - started) * 1000
    return {"answer": answer, "time_ms": round(elapsed_ms, 2), **get_metrics()}
