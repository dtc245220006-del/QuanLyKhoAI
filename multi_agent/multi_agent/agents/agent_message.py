from typing import Any

from pydantic import BaseModel


class AgentMessage(BaseModel):
    task_id: str
    from_agent: str
    to_agent: str
    message_type: str
    payload: Any
    status: str = "success"
    error: str | None = None
