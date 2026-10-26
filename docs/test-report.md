# Test Report

## Automated tests

Module AI có hai nhóm automated tests tại `multi_agent/multi_agent/tests/`:

- 17 Test Case trong `test_multi_agent.py`, bao gồm AgentMessage, Analyst, SQL Tool, RAG Agent, Reasoning, Critic, Response và Orchestrator/retry.
- 2 Test Case cho Single-Agent baseline trong `test_single_agent.py`.
- 1 Test Case SQL Tool độc lập trong `test_sql_tool.py`.

Tổng cộng: **20 Test Case tự động được định nghĩa trong module AI**. Đây là số lượng test case được định nghĩa trong mã nguồn; trạng thái pass/fail phải được cập nhật sau khi chạy pytest trên môi trường triển khai.

## Phạm vi kiểm thử tự động

Các nhóm kiểm tra hiện có gồm:

1. Định dạng message có đủ thông tin task và payload.
2. Analyst xử lý fallback khi Gemini lỗi, từ chối câu hỏi rỗng, nhận diện câu hỏi nhập bổ sung và sắp xếp giảm dần.
3. SQL Tool dùng tham số cho dữ liệu đầu vào, lọc hàng dưới mức tồn tối thiểu và áp dụng thứ tự sắp xếp được cho phép.
4. RAG Agent trả kết quả knowledge từ Vector Search Tool (được mock trong unit test).
5. Reasoning tạo claim từ dữ liệu DB khi Gemini lỗi.
6. Critic duyệt claim khớp dữ liệu, từ chối số lượng sai, mặt hàng không tồn tại, mặt hàng đủ tồn nhưng bị đưa vào danh sách cần nhập, và claim sai thứ tự giảm dần.
7. Response Agent dùng nội dung fallback khi Gemini lỗi.
8. Orchestrator dừng khi được duyệt, retry khi bị từ chối và trả trạng thái reject khi hết số lần retry.
9. Single-Agent dùng một lần gọi LLM trong baseline và từ chối claim chứa mã hàng không tồn tại.

Lưu ý: các unit test cho SQL Tool/RAG sử dụng mock, do đó **không thay thế** kiểm thử tích hợp cần kết nối MySQL thật và kiểm thử runtime của ChromaDB/SentenceTransformer.

## Chạy automated tests

Từ thư mục gốc repository, kích hoạt đúng virtual environment rồi chạy:

    python -m pytest multi_agent/multi_agent/tests -q

Kết quả mong đợi về số lượng: 20 tests collected. Chỉ ghi nhận "19 passed" nếu output thực tế của pytest xác nhận tất cả đều pass. Nếu có lỗi, lưu lại traceback và sửa nguyên nhân trước khi cập nhật báo cáo.

## Benchmark Single-Agent vs Multi-Agent

Benchmark sử dụng cùng bộ 10 câu hỏi, cùng database MySQL và cùng model Gemini. Các chỉ số gồm:

- Accuracy theo Test Oracle dựa trên claim đối chiếu với dữ liệu SQL và các điều kiện của câu hỏi.
- Response time trung bình.
- Số lần gọi LLM trung bình và tổng số lần gọi LLM.

Lệnh chạy từ thư mục gốc:

    cd multi_agent
    python -m multi_agent.benchmark

Kết quả được xuất ra:

    multi_agent/multi_agent_benchmark.json

### Kết quả benchmark đã ghi nhận

| Tiêu chí | Single-Agent | Multi-Agent |
|---|---:|---:|
| Accuracy theo Test Oracle | 100.0% (10/10) | 100.0% (10/10) |
| Thời gian trung bình | 2732.84 ms | 1488.47 ms |
| LLM calls trung bình/câu | 1 | 3 |
| Tổng LLM calls | 10 | 30 |

Đây là kết quả của một lần chạy cụ thể, không phải cam kết hiệu năng cho mọi lần chạy. Thời gian có thể chịu ảnh hưởng bởi việc khởi tạo model embedding, cache, mạng và độ trễ Gemini API. Accuracy ở đây là data-grounded accuracy của Test Oracle, không phải đánh giá tuyệt đối toàn bộ chất lượng câu trả lời tự nhiên. Nên chạy lại benchmark sau thay đổi code và lưu file JSON mới trước khi chốt báo cáo.

## Giới hạn

Bộ automated tests hiện tập trung vào module AI/Multi-Agent; chưa chứng minh toàn bộ frontend, backend nghiệp vụ kho, phân quyền API, giao dịch MySQL và các yêu cầu phi chức năng đã được kiểm thử đầy đủ. Các nội dung cần kiểm thử runtime riêng được liệt kê trong báo cáo và checklist kiểm thử của dự án.
