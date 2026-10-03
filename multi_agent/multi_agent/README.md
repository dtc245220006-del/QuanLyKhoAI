# Multi-Agent AI — QuanLyKhoAI

## Mục tiêu

Triển khai hệ thống Multi-Agent cho tư vấn/phân tích kho dựa trên dữ liệu MySQL.

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

## Single-Agent baseline

Để có cơ sở so sánh, module có một baseline Single-Agent:

Question → SQL Tool + Vector Search Tool → Gemini → Answer

API:
- POST /multi-agent/advisor — Multi-Agent
- POST /multi-agent/single-agent/advisor — Single-Agent

## Benchmark

Chạy từ thư mục multi_agent:

    python -m multi_agent.benchmark

Benchmark dùng cùng bộ 10 câu hỏi cho cả hai kiến trúc và ghi:
- Accuracy
- Response time
- LLM calls
- oracle_reason
- retry_count

Kết quả:
multi_agent/multi_agent_benchmark.json

Tài liệu:
docs/benchmark-guide.md
docs/multi-agent-comparison.md

## Testing

Unit tests nằm tại:
multi_agent/multi_agent/tests/

Kết quả runtime phải được chạy và ghi nhận thực tế trước khi điền báo cáo.

## Logging

Runtime log:
multi_agent/multi_agent/logs/agent_execution.log

Mỗi record có task_id, agent nguồn/đích, message type, status; retry record có attempt và errors.
