from unittest.mock import patch

from multi_agent.multi_agent.single_agent import SingleAgent


def test_single_agent_uses_one_llm_call():
    rows = [{"ma_hang": 1, "ten_hang": "Chuột", "so_luong_ton": 5}]

    with patch(
        "multi_agent.multi_agent.single_agent.search_inventory",
        return_value=rows,
    ), patch(
        "multi_agent.multi_agent.single_agent.search_knowledge",
        return_value=[],
    ), patch(
        "multi_agent.multi_agent.single_agent.generate_json",
        return_value={
            "answer": "Chuột đang tồn 5.",
            "claims": [
                {
                    "ma_hang": 1,
                    "ten_hang": "Chuột",
                    "so_luong_ton": 5,
                }
            ],
            "recommendation": "",
        },
    ), patch(
        "multi_agent.multi_agent.single_agent.get_metrics",
        return_value={"llm_calls": 1},
    ):
        result = SingleAgent().run("Tồn kho của chuột là bao nhiêu?")

    assert result["status"] == "APPROVED"
    assert result["accuracy_check"]["valid"] is True
    assert result["claims"][0]["so_luong_ton"] == 5
    assert result["llm_calls"] == 1


def test_single_agent_rejects_unknown_claim():
    rows = [{"ma_hang": 1, "ten_hang": "Chuột", "so_luong_ton": 5}]

    with patch(
        "multi_agent.multi_agent.single_agent.search_inventory",
        return_value=rows,
    ), patch(
        "multi_agent.multi_agent.single_agent.search_knowledge",
        return_value=[],
    ), patch(
        "multi_agent.multi_agent.single_agent.generate_json",
        return_value={
            "answer": "Có sản phẩm X.",
            "claims": [
                {
                    "ma_hang": 999,
                    "ten_hang": "X",
                    "so_luong_ton": 3,
                }
            ],
            "recommendation": "",
        },
    ), patch(
        "multi_agent.multi_agent.single_agent.get_metrics",
        return_value={"llm_calls": 1},
    ):
        result = SingleAgent().run("Có sản phẩm nào?")

    assert result["status"] == "REJECTED"
    assert result["accuracy_check"]["valid"] is False
