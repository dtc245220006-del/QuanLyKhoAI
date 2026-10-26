from unittest.mock import Mock, patch

from multi_agent.agents.agent_message import AgentMessage
from multi_agent.agents.analyst_agent import AnalystAgent
from multi_agent.agents.critic_agent import CriticAgent
from multi_agent.agents.reasoning_agent import ReasoningAgent
from multi_agent.agents.response_agent import ResponseAgent
from multi_agent.agents.orchestrator_agent import OrchestratorAgent


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
    with patch("multi_agent.agents.analyst_agent.generate_json", side_effect=RuntimeError()):
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
    with patch("multi_agent.agents.reasoning_agent.generate_json", side_effect=RuntimeError()):
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
    with patch("multi_agent.agents.response_agent.generate_text", side_effect=RuntimeError()):
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


def test_12_analyst_normalizes_restock_question_to_low_stock():
    with patch(
        "multi_agent.agents.analyst_agent.generate_json",
        return_value={
            "intent": "inventory_search",
            "only_low_stock": False,
            "item_name": None,
            "group_name": None,
            "max_results": 10,
            "keywords": [],
        },
    ):
        result = AnalystAgent().process(AgentMessage(
            task_id="TASK-012",
            from_agent="orchestrator",
            to_agent="analyst_agent",
            message_type="analyze_request",
            payload={"question": "Hãy cho biết các mặt hàng cần nhập bổ sung."},
        ))

    assert result.status == "success"
    assert result.payload["only_low_stock"] is True
    assert result.payload["intent"] == "low_stock"


def test_13_analyst_normalizes_descending_sort():
    with patch(
        "multi_agent.agents.analyst_agent.generate_json",
        return_value={
            "intent": "inventory_search",
            "only_low_stock": False,
            "item_name": None,
            "group_name": None,
            "max_results": 10,
            "keywords": [],
        },
    ):
        result = AnalystAgent().process(AgentMessage(
            task_id="TASK-013",
            from_agent="orchestrator",
            to_agent="analyst_agent",
            message_type="analyze_request",
            payload={"question": "Hãy liệt kê tồn kho từ cao xuống thấp."},
        ))

    assert result.payload["sort_order"] == "desc"


def test_14_critic_rejects_sufficient_stock_for_restock_question():
    result = CriticAgent().process(AgentMessage(
        task_id="TASK-014",
        from_agent="reasoning_agent",
        to_agent="critic_agent",
        message_type="critic_request",
        payload={
            "question": "Hãy cho biết các mặt hàng cần nhập bổ sung.",
            "rows": [
                {"ma_hang": 1, "ten_hang": "Màn hình", "so_luong_ton": 0, "ton_toi_thieu": 10},
                {"ma_hang": 2, "ten_hang": "Chuột", "so_luong_ton": 15, "ton_toi_thieu": 10},
            ],
            "reasoning": {
                "answer": "Cần nhập màn hình và chuột.",
                "claims": [
                    {"ma_hang": 1, "ten_hang": "Màn hình", "so_luong_ton": 0},
                    {"ma_hang": 2, "ten_hang": "Chuột", "so_luong_ton": 15},
                ],
            },
        },
    ))

    assert result.payload["status"] == "REJECT"


def test_15_critic_rejects_wrong_stock_sort_order():
    rows = [
        {"ma_hang": 1, "ten_hang": "Màn hình", "so_luong_ton": 0, "ton_toi_thieu": 10},
        {"ma_hang": 2, "ten_hang": "Ram", "so_luong_ton": 4, "ton_toi_thieu": 5},
        {"ma_hang": 3, "ten_hang": "Chuột", "so_luong_ton": 15, "ton_toi_thieu": 10},
        {"ma_hang": 4, "ten_hang": "Laptop", "so_luong_ton": 50, "ton_toi_thieu": 10},
    ]
    result = CriticAgent().process(AgentMessage(
        task_id="TASK-015",
        from_agent="reasoning_agent",
        to_agent="critic_agent",
        message_type="critic_request",
        payload={
            "question": "Hãy liệt kê tồn kho từ cao xuống thấp.",
            "rows": rows,
            "reasoning": {
                "answer": "Màn hình, Ram, Chuột, Laptop.",
                "claims": [
                    {"ma_hang": r["ma_hang"], "ten_hang": r["ten_hang"], "so_luong_ton": r["so_luong_ton"]}
                    for r in rows
                ],
            },
        },
    ))

    assert result.payload["status"] == "REJECT"


def test_16_sql_tool_parameterizes_item_and_filters_low_stock(monkeypatch):
    from multi_agent.tools import sql_tool

    class FakeCursor:
        def __init__(self):
            self.sql = ""
            self.params = None

        def __enter__(self):
            return self

        def __exit__(self, exc_type, exc_value, traceback):
            return False

        def execute(self, sql, params):
            self.sql = sql
            self.params = params

        def fetchall(self):
            return [{"ma_hang": 1, "ten_hang": "Chuột", "so_luong_ton": 2}]

    class FakeConnection:
        def __init__(self):
            self.fake_cursor = FakeCursor()
            self.closed = False

        def cursor(self):
            return self.fake_cursor

        def close(self):
            self.closed = True

    connection = FakeConnection()
    monkeypatch.setattr(sql_tool, "get_connection", lambda: connection)

    rows = sql_tool.search_inventory({
        "item_name": "Chuột",
        "only_low_stock": True,
        "max_results": 10,
        "sort_order": "DESC",
    })

    assert "h.ten_hang LIKE %s" in connection.fake_cursor.sql
    assert "t.so_luong < h.ton_toi_thieu" in connection.fake_cursor.sql
    assert "ORDER BY t.so_luong DESC LIMIT %s" in connection.fake_cursor.sql
    assert connection.fake_cursor.params == ["%Chuột%", 10]
    assert rows[0]["ten_hang"] == "Chuột"
    assert connection.closed is True


def test_17_rag_agent_returns_knowledge_documents():
    from multi_agent.agents.rag_agent import RAGAgent

    documents = [{"text": "Chỉ cập nhật tồn kho khi phiếu nhập được xác nhận."}]
    with patch(
        "multi_agent.agents.rag_agent.search_knowledge",
        return_value=documents,
    ):
        result = RAGAgent().process(AgentMessage(
            task_id="TASK-017",
            from_agent="orchestrator",
            to_agent="rag_agent",
            message_type="rag_request",
            payload={"question": "Khi nào cập nhật tồn kho?"},
        ))

    assert result.status == "success"
    assert result.payload["documents"] == documents
