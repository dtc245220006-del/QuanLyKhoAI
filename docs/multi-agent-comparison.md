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

Kết quả thực nghiệm trên bộ 10 câu hỏi, cùng dữ liệu MySQL và cùng model Gemini.

| Test set | Single-Agent Accuracy | Multi-Agent Accuracy | Single-Agent Time (ms) | Multi-Agent Time (ms) | Single-Agent LLM calls | Multi-Agent LLM calls |
|---|---:|---:|---:|---:|---:|---:|
| Bộ 10 câu hỏi | 100.0% | 100.0% | 2732.84 | 1488.47 | 1 | 3 |

## Phân tích kết quả

- Cả hai kiến trúc đều đạt 10/10 câu hỏi vượt qua Test Oracle, tương ứng Accuracy 100.0%.
- Thời gian xử lý trung bình ghi nhận trong lần chạy này là 2732.84 ms đối với Single-Agent và 1488.47 ms đối với Multi-Agent.
- Multi-Agent sử dụng trung bình 3 lần gọi LLM cho mỗi câu hỏi, trong khi Single-Agent sử dụng 1 lần gọi/câu.
- Tổng số lần gọi LLM trong bộ 10 câu là 10 lần với Single-Agent và 30 lần với Multi-Agent.
- Chênh lệch thời gian trung bình giữa hai kiến trúc là 1244.37 ms trong lần chạy benchmark này.

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

Lấy các giá trị summary từ hai nhóm single_agent và multi_agent để cập nhật bảng kết quả.

Lưu ý: Accuracy trong benchmark này là data-grounded accuracy theo Test Oracle, tức là các claim được đối chiếu với dữ liệu SQL thực tế và các điều kiện của câu hỏi. Kết quả không thay thế cho việc đánh giá toàn diện chất lượng câu trả lời tự nhiên.
