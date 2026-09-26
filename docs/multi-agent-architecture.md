# Multi-Agent Architecture

## Agents
1. Orchestrator Agent — điều phối.
2. Analyst Agent — phân tích câu hỏi thành intent có cấu trúc.
3. Database Agent — gọi SQL Tool.
4. RAG Agent — gọi Vector Search Tool.
5. Reasoning Agent — tổng hợp và suy luận.
6. Critic Agent — kiểm chứng claim.
7. Response Agent — sinh phản hồi cuối.

## Workflow
```text
User
 ↓
Orchestrator
 ↓
Analyst
 ↓
Database Agent → SQL Tool → MySQL
 ↓
RAG Agent → Vector Search Tool → ChromaDB
 ↓
Reasoning
 ↓
Critic
 ├─ REJECT → Retry (tối đa 2)
 └─ APPROVED
       ↓
Response
```

## Message Protocol
```json
{
  "task_id": "TASK-001",
  "from_agent": "analyst_agent",
  "to_agent": "database_agent",
  "message_type": "structured_requirements",
  "payload": {},
  "status": "success",
  "error": null
}
```
