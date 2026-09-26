# Multi-Agent AI — QuanLyKhoAI

## Mục tiêu
Triển khai Multi-Agent cho tư vấn/phân tích kho dựa trên dữ liệu của hệ thống Quản lý Kho.

## Workflow
User → Orchestrator → Analyst → Database Agent → SQL Tool/MySQL
→ RAG Agent → Vector Search/ChromaDB → Reasoning → Critic
→ Reject/Retry hoặc Approved → Response.

## Agent
1. Orchestrator Agent
2. Analyst Agent
3. Database Agent
4. RAG Agent
5. Reasoning Agent
6. Critic Agent
7. Response Agent

## API
`POST /multi-agent/advisor`

```json
{"question":"Hàng nào đang dưới mức tồn tối thiểu?"}
```

## Logging
`multi_agent/multi_agent/logs/agent_execution.log`

## Benchmark
`benchmark.py` có hàm `run_single_agent()` để so sánh với workflow Multi-Agent. Không điền số liệu giả vào báo cáo.
