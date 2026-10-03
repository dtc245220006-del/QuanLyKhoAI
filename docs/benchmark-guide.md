# Benchmark Single-Agent vs Multi-Agent

## Mục tiêu

Đánh giá hai kiến trúc trên cùng một bộ 10 câu hỏi, cùng dữ liệu MySQL và cùng model Gemini.

Ba tiêu chí bắt buộc:
1. Accuracy — tỷ lệ câu trả lời vượt qua Test Oracle dựa trên dữ liệu SQL.
2. Response time — thời gian xử lý một câu hỏi, tính bằng ms.
3. LLM calls — số lần gọi Gemini.

## Chạy benchmark

Từ thư mục gốc:

    cd multi_agent
    python -m multi_agent.benchmark

Kết quả được in ra terminal và lưu tại:

    multi_agent/multi_agent_benchmark.json

## Bộ 10 câu hỏi

1. Hàng nào đang dưới mức tồn tối thiểu?
2. Cho tôi xem tồn kho hiện tại.
3. Có những mặt hàng nào trong kho?
4. Mặt hàng nào có số lượng tồn cao nhất?
5. Có mặt hàng nào đang có nguy cơ thiếu hàng không?
6. Hãy cho biết các mặt hàng cần nhập bổ sung.
7. Mặt hàng nào có số lượng tồn thấp nhất?
8. Hãy liệt kê tồn kho từ cao xuống thấp.
9. Hãy giải thích tình trạng tồn kho hiện tại của kho.
10. Mặt hàng nào cần kiểm tra để nhập bổ sung?

## Test Oracle

Oracle đối chiếu các claim của câu trả lời với dữ liệu SQL thực tế tại thời điểm chạy.

- Mã hàng phải tồn tại trong kết quả SQL.
- Tên hàng và số lượng tồn phải khớp SQL.
- Câu hỏi về thiếu hàng/nhập bổ sung phải có claim thỏa tồn < mức tối thiểu.
- Câu hỏi "cao nhất" phải có claim chứa mức tồn cao nhất.
- Câu hỏi "thấp nhất" phải có claim chứa mức tồn thấp nhất.
- Câu hỏi sắp xếp cao xuống thấp phải có thứ tự claim giảm dần.

Oracle này đo data-grounded accuracy. Người kiểm thử vẫn nên đọc lại câu trả lời để xác nhận ý nghĩa nghiệp vụ.

## LLM calls

Bộ đếm được đặt tại Gemini Service. Mỗi lần gọi generate_text hoặc generate_json làm tăng bộ đếm trong đúng một lượt benchmark.

## Không điền số giả

Chỉ lấy số Accuracy, Response time và LLM calls từ file multi_agent_benchmark.json sau khi chạy thực nghiệm trên máy triển khai.
