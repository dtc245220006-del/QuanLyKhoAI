# Single-Agent vs Multi-Agent Comparison

## Phương pháp

Dùng cùng một bộ 10 câu hỏi kho, cùng database MySQL và cùng model Gemini.

Đo 3 tiêu chí bắt buộc:
- Accuracy: tỷ lệ câu trả lời vượt qua Test Oracle dựa trên dữ liệu SQL.
- Response time: thời gian từ request tới response, tính bằng ms.
- LLM calls: số lần gọi Gemini.

## Kiến trúc

### Single-Agent

Question → SQL Tool + Vector Search Tool → Gemini → Answer

### Multi-Agent

Question → Orchestrator → Analyst → Database/SQL + RAG/Vector → Reasoning → Critic → Retry → Response

## Bảng kết quả

| Test set | Single-Agent Accuracy | Multi-Agent Accuracy | Single-Agent Time | Multi-Agent Time | Single-Agent LLM calls | Multi-Agent LLM calls |
|---|---:|---:|---:|---:|---:|---:|
| Bộ 10 câu hỏi | Chưa đo | Chưa đo | Chưa đo | Chưa đo | Chưa đo | Chưa đo |

## Cách cập nhật

Chạy:

    cd multi_agent
    python -m multi_agent.benchmark

Sau khi chạy, file multi_agent_benchmark.json chứa:
- kết quả của từng câu hỏi;
- oracle_reason;
- Accuracy;
- Response time;
- LLM calls;
- số lần retry.

Lấy các giá trị summary từ hai nhóm single_agent và multi_agent để điền bảng trên.

Không điền số liệu giả.
