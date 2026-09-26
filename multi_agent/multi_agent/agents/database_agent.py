from .agent_message import AgentMessage
from .base_agent import BaseAgent
from ..tools.sql_tool import search_inventory


class DatabaseAgent(BaseAgent):
    def __init__(self):
        super().__init__("database_agent")

    def process(self, message: AgentMessage) -> AgentMessage:
        try:
            rows = search_inventory(message.payload)
            return self.message(message.task_id, "rag_agent", "database_result", {"rows": rows})
        except Exception as exc:
            return self.message(message.task_id, "orchestrator", "error", {}, "error", str(exc))
