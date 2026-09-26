from unittest.mock import patch, MagicMock

from multi_agent.multi_agent.tools.sql_tool import search_inventory


def test_12_sql_tool_uses_parameterized_query():
    cursor = MagicMock()
    cursor.__enter__.return_value = cursor
    cursor.fetchall.return_value = []
    conn = MagicMock()
    conn.cursor.return_value = cursor

    with patch("multi_agent.multi_agent.tools.sql_tool.get_connection", return_value=conn):
        search_inventory({"item_name": "Chuột", "max_results": 10})

    sql, params = cursor.execute.call_args.args
    assert "%s" in sql
    assert "Chuột" in params
