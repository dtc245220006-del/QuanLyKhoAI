from pydantic import BaseModel
from typing import Any, Optional


class AgentMessage(BaseModel):
    task_id: str
    from_agent: str
    to_agent: str
    message_type: str
    payload: Any
    status: str = "success"
    error: Optional[str] = None