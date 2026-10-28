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


## Cập nhật kiểm thử và đối chiếu (28/10/2026)

- Module này có **20 unit/Agent tests**; repo toàn bộ có **35 Unit/API/Agent + 6 MySQL integration = 41 automated tests** từng được nhóm xác nhận PASS khi chạy trên máy local.
- Lệnh chạy đúng với package lồng `multi_agent/multi_agent` nằm tại [README chính](../../README.md) và [Test Report](../../docs/test-report.md); không dùng `pytest multi_agent/multi_agent/tests` từ root nếu gây import nhầm.
- Các `SKILL.md` dưới `../../.agents/skills/` là tài liệu hỗ trợ phát triển, **không phải** 7 Agent runtime được liệt kê phía trên.
- AI chỉ phân tích dữ liệu kho; không tự xác nhận phiếu hoặc thay đổi tồn. Các rủi ro auth/rollback chưa kiểm thử đầy đủ được liệt kê tại [Security Review](../../docs/security-review.md).
