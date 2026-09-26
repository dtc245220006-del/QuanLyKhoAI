# Multi-Agent AI — QuanLyKhoAI

Module này triển khai workflow Multi-Agent theo đề thực hành:

User → Orchestrator → Analyst → Database(SQL Tool) + RAG(Vector Search) → Reasoning → Critic → Retry → Response.

## Các Agent
- OrchestratorAgent
- AnalystAgent
- DatabaseAgent
- RAGAgent
- ReasoningAgent
- CriticAgent
- ResponseAgent

## Tool
- SQL Tool: PyMySQL truy vấn MySQL `quan_ly_kho`.
- Vector Search Tool: ChromaDB + SentenceTransformer.

## API
`POST /multi-agent/advisor`

Request:
```json
{"question":"Hàng nào đang dưới mức tồn tối thiểu?"}
```
