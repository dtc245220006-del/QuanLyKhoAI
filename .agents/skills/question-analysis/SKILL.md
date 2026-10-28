---
name: question-analysis
description: Chuyển câu hỏi về hàng hóa/tồn kho thành intent có cấu trúc cho SQL Tool và RAG, bảo toàn điều kiện mà người dùng thực sự yêu cầu.
---

# Question Analysis Skill — QuanLyKhoAI

## Trước khi phân tích

Đọc `docs/project-context.md`, `multi_agent/multi_agent/agents/analyst_agent.py`, `multi_agent/multi_agent/tools/sql_tool.py`. Không thêm thực thể hoặc tham số mà code không hỗ trợ.

## Checklist

1. Xác định yêu cầu: xem tồn, tìm tên hàng, lọc nhóm, hàng dưới `ton_toi_thieu`, cao nhất/thấp nhất, sắp xếp, cần nhập bổ sung.
2. Giữ nguyên `item_name` và `group_name`; không suy diễn hãng, giá, số lượng hoặc mã hàng.
3. Tạo intent tương ứng các key SQL Tool đang nhận: `item_name`, `group_name`, `only_low_stock`, `max_results`, `sort_order`. Không bịa thêm filter chưa có trong query builder.
4. Giới hạn `max_results` 1–50; sắp xếp `asc/desc` theo câu hỏi; nếu mơ hồ ưu tiên default code.
5. Câu hỏi không liên quan kho hoặc thiếu thông tin quan trọng → yêu cầu làm rõ hay trả trạng thái không hỗ trợ; không ngụy tạo kết quả.
6. Dữ liệu RAG chỉ cung cấp chính sách/giải thích; số tồn phải truy xuất SQL.
7. Ghi đủ thông tin nguồn/intent để Critic so với SQL. Không coi đầu ra LLM là dữ liệu xác thực.

## Output

Intent có cấu trúc và phần giải thích ngắn về điều kiện đã nhận diện. Unit test analyst ở `multi_agent/multi_agent/tests/test_multi_agent.py` là nguồn kiểm chứng; khi sửa prompt phải chạy lại test, không điều chỉnh assertion để hợp thức hóa hallucination.
