# Single-Agent vs Multi-Agent Comparison

## Phương pháp

Dùng cùng một bộ 10 câu hỏi kho, cùng database MySQL và cùng model Gemini.

Ba tiêu chí được đo:
- **Accuracy:** tỷ lệ câu hỏi vượt qua Test Oracle dựa trên claim so với dữ liệu SQL và điều kiện của câu hỏi.
- **Response time:** thời gian xử lý, tính bằng ms.
- **LLM calls:** số lần gọi Gemini.

## Kiến trúc

### Single-Agent

Question → SQL Tool + Vector Search Tool → Gemini → Answer

### Multi-Agent

Question → Orchestrator → Analyst → Database/SQL + RAG/Vector → Reasoning → Critic → Retry (tối đa 2 lần) → Response

## Bảng kết quả đã ghi nhận

| Test set | Single-Agent Accuracy | Multi-Agent Accuracy | Single-Agent Time (ms) | Multi-Agent Time (ms) | Single-Agent LLM calls/câu | Multi-Agent LLM calls/câu |
|---|---:|---:|---:|---:|---:|---:|
| Bộ 10 câu hỏi | 100.0% (10/10) | 100.0% (10/10) | 2732.84 | 1488.47 | 1 | 3 |

Tổng số LLM calls trong lần chạy đó là 10 với Single-Agent và 30 với Multi-Agent.

## Phân tích

Trong lần chạy đã ghi nhận, cả hai kiến trúc đều đạt 10/10 câu vượt qua Test Oracle. Multi-Agent có thời gian trung bình 1488.47 ms và Single-Agent 2732.84 ms; tuy nhiên đây là thời gian đo trong một lần chạy, không đủ để khẳng định Multi-Agent luôn nhanh hơn trong mọi điều kiện. Thời gian có thể thay đổi theo việc khởi tạo embedding model, cache, độ trễ mạng và Gemini API. Multi-Agent sử dụng 3 lần gọi LLM/câu, so với 1 lần/câu của Single-Agent.

Accuracy ở đây là **data-grounded accuracy theo Test Oracle**, không đồng nghĩa với đánh giá toàn diện hoặc tuyệt đối về chất lượng câu trả lời tự nhiên. Kết quả benchmark cũng không thay thế kiểm thử tích hợp và kiểm thử nghiệp vụ toàn hệ thống.

## Chạy lại benchmark

Từ thư mục gốc repository:

    cd multi_agent
    python -m multi_agent.benchmark

Kết quả từng câu và phần tổng hợp được lưu tại:

    multi_agent/multi_agent_benchmark.json

Sau khi sửa code, cần chạy lại benchmark và dùng số liệu trong file JSON mới nhất. Không tự điền hoặc ước lượng kết quả.
