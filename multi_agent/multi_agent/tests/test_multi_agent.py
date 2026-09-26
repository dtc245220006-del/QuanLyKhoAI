from unittest.mock import Mock, patch

from multi_agent.multi_agent.multi_agent.agents.agent_message import AgentMessage
from multi_agent.multi_agent.multi_agent.agents.analyst_agent import AnalystAgent
from multi_agent.multi_agent.multi_agent.agents.critic_agent import CriticAgent
from multi_agent.multi_agent.multi_agent.agents.reasoning_agent import ReasoningAgent
from multi_agent.multi_agent.multi_agent.agents.response_agent import ResponseAgent
from multi_agent.multi_agent.multi_agent.agents.orchestrator_agent import OrchestratorAgent


def test_01_structured_message():
    msg = AgentMessage(
        task_id="TASK-001",
        from_agent="user",
        to_agent="analyst_agent",
        message_type="user_question",
        payload={"question": "Hàng nào tồn thấp?"},
    )
    assert msg.task_id == "TASK-001"
    assert msg.payload["question"] == "Hàng nào tồn thấp?"


def test_02_analyst_fallback_for_low_stock():
    agent = AnalystAgent()
    with patch("multi_agent.multi_agent.agents.analyst_agent.generate_json", side_effect=RuntimeError()):
        result = agent.process(AgentMessage(
            task_id="TASK-002",
            from_agent="orchestrator",
            to_agent="analyst_agent",
            message_type="analyze_request",
            payload={"question": "Hàng nào đang tồn thấp?"},
        ))
    assert result.status == "success"
    assert result.payload["only_low_stock"] is True


def test_03_analyst_rejects_empty_question():
    result = AnalystAgent().process(AgentMessage(
        task_id="TASK-003", from_agent="user", to_agent="analyst_agent",
        message_type="user_question", payload={"question": "   "}
    ))
    assert result.status == "error"


def test_04_critic_approves_matching_claim():
    result = CriticAgent().process(AgentMessage(
        task_id="TASK-004", from_agent="reasoning_agent", to_agent="critic_agent",
        message_type="critic_request",
        payload={
            "rows": [{"ma_hang": 1, "ten_hang": "Chuột Logitech", "so_luong_ton": 8}],
            "reasoning": {
                "answer": "Chuột Logitech đang tồn 8.",
                "claims": [{"ma_hang": 1, "ten_hang": "Chuột Logitech", "so_luong_ton": 8}],
            },
        },
    ))
    assert result.payload["status"] == "APPROVED"


def test_05_critic_rejects_wrong_quantity():
    result = CriticAgent().process(AgentMessage(
        task_id="TASK-005", from_agent="reasoning_agent", to_agent="critic_agent",
        message_type="critic_request",
        payload={
            "rows": [{"ma_hang": 1, "ten_hang": "Chuột Logitech", "so_luong_ton": 8}],
            "reasoning": {
                "answer": "Chuột Logitech đang tồn 80.",
                "claims": [{"ma_hang": 1, "ten_hang": "Chuột Logitech", "so_luong_ton": 80}],
            },
        },
    ))
    assert result.payload["status"] == "REJECT"


def test_06_critic_rejects_unknown_item():
    result = CriticAgent().process(AgentMessage(
        task_id="TASK-006", from_agent="reasoning_agent", to_agent="critic_agent",
        message_type="critic_request",
        payload={
            "rows": [],
            "reasoning": {
                "answer": "Có sản phẩm X.",
                "claims": [{"ma_hang": 999, "ten_hang": "X", "so_luong_ton": 3}],
            },
        },
    ))
    assert result.payload["status"] == "REJECT"


def test_07_reasoning_fallback_uses_database_data():
    with patch("multi_agent.multi_agent.agents.reasoning_agent.generate_json", side_effect=RuntimeError()):
        result = ReasoningAgent().process(AgentMessage(
            task_id="TASK-007", from_agent="rag_agent", to_agent="reasoning_agent",
            message_type="reasoning_request",
            payload={
                "question": "Cho tôi biết tồn kho.",
                "rows": [{"ma_hang": 1, "ten_hang": "Bàn phím", "so_luong_ton": 5}],
                "documents": [],
            },
        ))
    assert result.payload["claims"][0]["so_luong_ton"] == 5


def test_08_response_fallback():
    with patch("multi_agent.multi_agent.agents.response_agent.generate_text", side_effect=RuntimeError()):
        result = ResponseAgent().process(AgentMessage(
            task_id="TASK-008", from_agent="critic_agent", to_agent="response_agent",
            message_type="approved_result",
            payload={"question": "Tồn?", "reasoning": {"answer": "Tồn là 5."}},
        ))
    assert result.payload["answer"] == "Tồn là 5."


def test_09_orchestrator_stops_after_approval():
    orchestrator = OrchestratorAgent(max_retries=2)
    with patch.object(orchestrator.analyst, "process") as analyst, \
         patch.object(orchestrator.database, "process") as database, \
         patch.object(orchestrator.rag, "process") as rag, \
         patch.object(orchestrator.reasoning, "process") as reasoning, \
         patch.object(orchestrator.critic, "process") as critic, \
         patch.object(orchestrator.response, "process") as response:
        analyst.return_value = AgentMessage(task_id="T", from_agent="analyst_agent", to_agent="database_agent", message_type="structured_requirements", payload={"intent":"inventory_search"})
        database.return_value = AgentMessage(task_id="T", from_agent="database_agent", to_agent="rag_agent", message_type="database_result", payload={"rows": []})
        rag.return_value = AgentMessage(task_id="T", from_agent="rag_agent", to_agent="reasoning_agent", message_type="knowledge_result", payload={"documents": []})
        reasoning.return_value = AgentMessage(task_id="T", from_agent="reasoning_agent", to_agent="critic_agent", message_type="reasoning_result", payload={"answer":"ok", "claims":[]})
        critic.return_value = AgentMessage(task_id="T", from_agent="critic_agent", to_agent="orchestrator", message_type="critic_result", payload={"status":"APPROVED", "errors":[]})
        response.return_value = AgentMessage(task_id="T", from_agent="response_agent", to_agent="user", message_type="final_response", payload={"answer":"ok"})
        out = orchestrator.run("Tồn kho thế nào?")
    assert out["success"] is True
    assert out["retry_count"] == 0
    assert reasoning.call_count == 1


def test_10_orchestrator_retries_after_reject():
    orchestrator = OrchestratorAgent(max_retries=2)
    with patch.object(orchestrator.analyst, "process") as analyst, \
         patch.object(orchestrator.database, "process") as database, \
         patch.object(orchestrator.rag, "process") as rag, \
         patch.object(orchestrator.reasoning, "process") as reasoning, \
         patch.object(orchestrator.critic, "process") as critic, \
         patch.object(orchestrator.response, "process") as response:
        analyst.return_value = AgentMessage(task_id="T", from_agent="analyst_agent", to_agent="database_agent", message_type="structured_requirements", payload={"intent":"inventory_search"})
        database.return_value = AgentMessage(task_id="T", from_agent="database_agent", to_agent="rag_agent", message_type="database_result", payload={"rows": []})
        rag.return_value = AgentMessage(task_id="T", from_agent="rag_agent", to_agent="reasoning_agent", message_type="knowledge_result", payload={"documents": []})
        reasoning.side_effect = [
            AgentMessage(task_id="T", from_agent="reasoning_agent", to_agent="critic_agent", message_type="reasoning_result", payload={"answer":"bad", "claims":[{"ma_hang":1,"so_luong_ton":99,"ten_hang":"X"}]}),
            AgentMessage(task_id="T", from_agent="reasoning_agent", to_agent="critic_agent", message_type="reasoning_result", payload={"answer":"ok", "claims":[]}),
        ]
        critic.side_effect = [
            AgentMessage(task_id="T", from_agent="critic_agent", to_agent="orchestrator", message_type="critic_result", payload={"status":"REJECT", "errors":["wrong claim"]}),
            AgentMessage(task_id="T", from_agent="critic_agent", to_agent="orchestrator", message_type="critic_result", payload={"status":"APPROVED", "errors":[]}),
        ]
        response.return_value = AgentMessage(task_id="T", from_agent="response_agent", to_agent="user", message_type="final_response", payload={"answer":"ok"})
        out = orchestrator.run("Tồn kho thế nào?")
    assert out["success"] is True
    assert out["retry_count"] == 1
    assert reasoning.call_count == 2


def test_11_orchestrator_returns_rejected_after_retry_limit():
    orchestrator = OrchestratorAgent(max_retries=1)
    with patch.object(orchestrator.analyst, "process") as analyst, \
         patch.object(orchestrator.database, "process") as database, \
         patch.object(orchestrator.rag, "process") as rag, \
         patch.object(orchestrator.reasoning, "process") as reasoning, \
         patch.object(orchestrator.critic, "process") as critic:
        analyst.return_value = AgentMessage(task_id="T", from_agent="analyst_agent", to_agent="database_agent", message_type="structured_requirements", payload={"intent":"inventory_search"})
        database.return_value = AgentMessage(task_id="T", from_agent="database_agent", to_agent="rag_agent", message_type="database_result", payload={"rows": []})
        rag.return_value = AgentMessage(task_id="T", from_agent="rag_agent", to_agent="reasoning_agent", message_type="knowledge_result", payload={"documents": []})
        reasoning.return_value = AgentMessage(task_id="T", from_agent="reasoning_agent", to_agent="critic_agent", message_type="reasoning_result", payload={"answer":"bad", "claims":[{"ma_hang":1,"so_luong_ton":99,"ten_hang":"X"}]})
        critic.return_value = AgentMessage(task_id="T", from_agent="critic_agent", to_agent="orchestrator", message_type="critic_result", payload={"status":"REJECT", "errors":["wrong claim"]})
        out = orchestrator.run("Tồn kho thế nào?")
    assert out["success"] is False
    assert out["status"] == "REJECTED"
    assert out["retry_count"] == 1
