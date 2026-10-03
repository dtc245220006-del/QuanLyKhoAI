from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field

from auth import get_current_user
from models import User
from .agents.orchestrator_agent import OrchestratorAgent
from .single_agent import SingleAgent

router = APIRouter(prefix="/multi-agent", tags=["Multi-Agent AI"])

_orchestrator = OrchestratorAgent(max_retries=2)
_single_agent = SingleAgent()


class AdvisorRequest(BaseModel):
    question: str = Field(min_length=1, max_length=1000)


def _check_role(current_user: User):
    if current_user.role not in {"QuanLy", "ThuKho", "KeToan"}:
        raise HTTPException(
            status_code=403,
            detail="Vai trò không được phép sử dụng AI Advisor",
        )


@router.post("/advisor")
def advisor(data: AdvisorRequest, current_user: User = Depends(get_current_user)):
    _check_role(current_user)
    return _orchestrator.run(data.question.strip())


@router.post("/single-agent/advisor")
def single_agent_advisor(
    data: AdvisorRequest,
    current_user: User = Depends(get_current_user),
):
    _check_role(current_user)
    return _single_agent.run(data.question.strip())
