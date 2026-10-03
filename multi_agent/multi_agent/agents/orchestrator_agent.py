import time
import uuid

from .agent_message import AgentMessage
from .analyst_agent import AnalystAgent
from .database_agent import DatabaseAgent
from .rag_agent import RAGAgent
from .reasoning_agent import ReasoningAgent
from .critic_agent import CriticAgent
from .response_agent import ResponseAgent
from ..services.message_bus import MessageBus
from ..services.gemini_service import get_metrics, reset_metrics


class OrchestratorAgent:
    def __init__(self, max_retries: int = 2):
        self.name = "orchestrator_agent"
        self.max_retries = max_retries
        self.analyst = AnalystAgent()
        self.database = DatabaseAgent()
        self.rag = RAGAgent()
        self.reasoning = ReasoningAgent()
        self.critic = CriticAgent()
        self.response = ResponseAgent()
        self.bus = MessageBus()

    def run(self, question: str) -> dict:
        task_id = f"TASK-{uuid.uuid4().hex[:8].upper()}"
        started = time.perf_counter()
        reset_metrics()

        self.bus.emit(AgentMessage(
            task_id=task_id,
            from_agent="user",
            to_agent=self.name,
            message_type="user_question",
            payload={"question": question},
        ))

        analyst_msg = self.analyst.process(AgentMessage(
            task_id=task_id,
            from_agent=self.name,
            to_agent="analyst_agent",
            message_type="analyze_request",
            payload={"question": question},
        ))
        self.bus.emit(analyst_msg)
        if analyst_msg.status == "error":
            return self._error(task_id, analyst_msg.error, started)

        db_msg = self.database.process(analyst_msg)
        self.bus.emit(db_msg)
        if db_msg.status == "error":
            return self._error(task_id, db_msg.error, started)

        rag_msg = self.rag.process(AgentMessage(
            task_id=task_id,
            from_agent=self.name,
            to_agent="rag_agent",
            message_type="rag_request",
            payload={"question": question},
        ))
        self.bus.emit(rag_msg)

        rows = db_msg.payload.get("rows", [])
        documents = rag_msg.payload.get("documents", [])
        critique = None
        reasoning_result = None

        for retry in range(self.max_retries + 1):
            reasoning_msg = self.reasoning.process(AgentMessage(
                task_id=task_id,
                from_agent=self.name,
                to_agent="reasoning_agent",
                message_type="reasoning_request",
                payload={
                    "question": question,
                    "rows": rows,
                    "documents": documents,
                    "previous_errors": critique.get("errors", []) if critique else [],
                },
            ))
            self.bus.emit(reasoning_msg)
            if reasoning_msg.status == "error":
                return self._error(task_id, reasoning_msg.error, started)
            reasoning_result = reasoning_msg.payload

            critic_msg = self.critic.process(AgentMessage(
                task_id=task_id,
                from_agent="reasoning_agent",
                to_agent="critic_agent",
                message_type="critic_request",
                payload={"reasoning": reasoning_result, "rows": rows},
            ))
            self.bus.emit(critic_msg)
            if critic_msg.status == "error":
                return self._error(task_id, critic_msg.error, started)
            critique = critic_msg.payload

            if critique.get("status") == "APPROVED":
                final_msg = self.response.process(AgentMessage(
                    task_id=task_id,
                    from_agent="critic_agent",
                    to_agent="response_agent",
                    message_type="approved_result",
                    payload={"question": question, "reasoning": reasoning_result},
                ))
                self.bus.emit(final_msg)
                if final_msg.status == "error":
                    return self._error(task_id, final_msg.error, started)

                return {
                    "success": True,
                    "task_id": task_id,
                    "retry_count": retry,
                    "status": "APPROVED",
                    "answer": final_msg.payload["answer"],
                    "data": rows,
                    "knowledge": documents,
                    "critic": critique,
                    "time_ms": round((time.perf_counter() - started) * 1000, 2),
                    **get_metrics(),
                }

            if retry < self.max_retries:
                self.bus.log_retry(task_id, retry + 1, critique.get("errors", []))

        return {
            "success": False,
            "task_id": task_id,
            "retry_count": self.max_retries,
            "status": "REJECTED",
            "answer": "Kết quả chưa vượt qua bước kiểm chứng Critic Agent.",
            "data": rows,
            "knowledge": documents,
            "critic": critique or {},
            "time_ms": round((time.perf_counter() - started) * 1000, 2),
            **get_metrics(),
        }

    @staticmethod
    def _error(task_id: str, error: str | None, started: float):
        return {
            "success": False,
            "task_id": task_id,
            "status": "ERROR",
            "error": error or "Lỗi không xác định",
            "time_ms": round((time.perf_counter() - started) * 1000, 2),
            **get_metrics(),
        }
