# Agent Execution Logs

Log runtime được ghi tại:
`multi_agent/multi_agent/logs/agent_execution.log`

Mỗi record chứa:
- time
- task_id
- from_agent
- to_agent
- message_type
- status

Retry record có thêm `attempt` và `errors`.
