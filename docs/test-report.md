# Test Report

## Automated tests

Project có bộ unit tests Multi-Agent tại multi_agent/multi_agent/tests/.

Phạm vi hiện tại:
- 11 Test Case cho workflow Multi-Agent.
- 2 Test Case cho Single-Agent baseline.

Tổng: 13 Test Case tự động trong phạm vi module AI.

## 10 test case bắt buộc của Multi-Agent

1. Analyst parse/fallback intent
2. SQL Tool parameterized query
3. SQL Tool lọc hàng
4. RAG trả knowledge
5. Reasoning tạo answer/claims
6. Critic APPROVED khi claim đúng
7. Critic REJECT khi claim sai
8. Orchestrator retry khi reject
9. Orchestrator stop khi approved
10. Orchestrator trả lỗi khi vượt giới hạn retry

## Single-Agent tests

- Single-Agent dùng một lần gọi LLM.
- Single-Agent từ chối claim không tồn tại trong dữ liệu SQL.

## Benchmark

Bộ benchmark so sánh Single-Agent và Multi-Agent dùng 10 câu hỏi chung và đo:
- Accuracy theo Test Oracle dữ liệu SQL.
- Response time.
- LLM calls.

Chạy:

    cd multi_agent
    python -m multi_agent.benchmark

Kết quả được ghi vào multi_agent/multi_agent_benchmark.json.

## Kết quả

Số liệu runtime phải được ghi sau khi chạy thực nghiệm trên máy triển khai. Không điền kết quả giả.
