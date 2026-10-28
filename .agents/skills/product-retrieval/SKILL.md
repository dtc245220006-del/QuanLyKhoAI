---
name: product-retrieval
description: Truy xuất dữ liệu HangHoa/NhomHang/TonKho thực tế từ MySQL để trả lời câu hỏi kho; ưu tiên SQL parameterized và dữ liệu kiểm chứng được.
---

# Product / Inventory Retrieval Skill — QuanLyKhoAI

## Input

Đọc `docs/project-context.md`, `docs/database-design.md` và `multi_agent/multi_agent/tools/sql_tool.py`. Input là intent **đã được chuẩn hóa**; các trường hiện được SQL Tool hỗ trợ:
`item_name` (tên hàng), `group_name` (tên nhóm), `only_low_stock` (boolean), `max_results` (1–50), `sort_order` (`asc` / `desc`).

## Quy trình

1. Kiểm tra tên hàng/nhóm từ đúng câu hỏi; không tự thêm điều kiện hoặc bịa mã hàng.
2. Gọi SQL Tool kết nối MySQL `quan_ly_kho` qua tham số bind, không nối text người dùng vào câu lệnh; `ASC/DESC` phải whitelist.
3. Giới hạn số hàng; không truy xuất toàn database nếu không cần.
4. Mỗi hàng kết quả dùng đúng các field `ma_hang`, `ten_hang`, `ten_nhom`, `so_luong_ton`, `ton_toi_thieu`, `gia_nhap`, `gia_ban`, `ngay_cap_nhat` nếu chúng thực sự được trả về.
5. Nếu không có kết quả, trả `[]` và giải thích không tìm thấy; không dùng tài liệu RAG để chế số tồn thực tế.
6. Không thực hiện INSERT/UPDATE/DELETE; Gemini và AI Agent chỉ được đọc.

## Output / oracle

Trả dữ liệu có cấu trúc (rows + filters đã dùng + trạng thái empty/error) cho Agent tiếp theo; giữ số lượng và giá chính xác. Kiểm chứng với kết quả SQL và các test `multi_agent/multi_agent/tests/test_sql_tool.py`; không báo PASS nếu chưa chạy pytest.

**An toàn:** `multi_agent/multi_agent/tools/sql_tool.py` mặc định đọc `backend/.env`; không gọi SQL Tool thật trong test chỉ dành cho `quanlykho_test` nếu không cô lập kết nối.
