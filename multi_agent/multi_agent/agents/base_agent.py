from abc import ABC, abstractmethod
from typing import Any

from .agent_message import AgentMessage


class BaseAgent(ABC):
    def __init__(self, name: str):
        self.name = name

    def message(self, task_id: str, to_agent: str, message_type: str, payload: Any, status: str = "success", error: str | None = None) -> AgentMessage:
        return AgentMessage(
            task_id=task_id,
            from_agent=self.name,
            to_agent=to_agent,
            message_type=message_type,
            payload=payload,
            status=status,
            error=error,
        )

    @abstractmethod
    def process(self, message: AgentMessage) -> AgentMessage:
        raise NotImplementedError
