from .agent_message import AgentMessage
from .base_agent import BaseAgent
from ..tools.vector_search_tool import search_knowledge


class RAGAgent(BaseAgent):
    def __init__(self):
        super().__init__("rag_agent")

    def process(self, message: AgentMessage) -> AgentMessage:
        question = message.payload.get("question", "")
        try:
            docs = search_knowledge(question, top_k=4)
        except Exception as exc:
            return self.message(
                message.task_id,
                "reasoning_agent",
                "knowledge_result",
                {"documents": [], "warning": str(exc)},
                "success",
            )
        return self.message(message.task_id, "reasoning_agent", "knowledge_result", {"documents": docs})
