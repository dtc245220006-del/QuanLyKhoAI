# Code Review — 28/10/2026

**Phạm vi:** backend FastAPI, Multi-Agent SQL tool, React frontend, schema SQL và test hiện có. Audit tĩnh được thực hiện sau khi pull `ce4a5ff`; regression Windows đã xác minh 45/45 Unit/API/Agent, IT-011 riêng PASS và 12/12 MySQL integration PASS (57/57). Không đánh đồng review tĩnh với pentest hoặc production readiness.

| Mức | Phát hiện | Bằng chứng trước sửa | Trạng thái |
|---|---|---|---|
| CRITICAL | Seed `admin/123456` khi import | `backend/main.py` | **Đã sửa:** bỏ seed và `create_all` lúc import. |
| HIGH | API kho, báo cáo và AI không yêu cầu JWT | router chỉ có `Depends(get_db)` | **Đã sửa:** router nghiệp vụ yêu cầu JWT; thao tác sửa dữ liệu kiểm tra role ở backend. |
| HIGH | Client có thể giả `ma_tai_khoan` khi tạo phiếu/đề xuất | payload/query request | **Đã sửa:** dùng `current_user.id` từ JWT; frontend không còn gửi trường này. |
| HIGH | Xuất kho có thể để Session ở trạng thái dở khi lỗi | thiếu rollback/flush | **Đã sửa:** rollback decorator, `flush()` trước commit và test injected-failure. |
| HIGH | Cạnh tranh xác nhận phiếu có thể làm sai tồn | đọc trạng thái/tồn không lock | **Đã sửa và regression PASS:** khoá hàng phiếu và dòng tồn bằng `FOR UPDATE`; IT-011 xác nhận `[200, 400]`, tồn `14`, `DaNhap` và đúng một lịch sử nhập trên Session độc lập. |
| HIGH | Dòng phiếu xuất trùng mã có thể vượt tồn | kiểm tra từng dòng thay vì tổng theo hàng | **Đã sửa:** từ chối mã hàng trùng trước khi tạo phiếu. |
| HIGH | Xóa phiếu nhập đã xác nhận hoặc hàng tham chiếu | có thể làm lệch audit trail hoặc dựa vào DB error | **Đã sửa:** chặn với 400 trước thao tác delete. |
| MEDIUM | Fallback MySQL `root`, URL ghép chuỗi | `database.py`, SQL Tool | **Đã sửa:** bắt buộc `DB_USER`, dùng `URL.create`, SQL Tool không fallback root. |
| MEDIUM | Trả exception Gemini cho client | `detail=str(e)` | **Đã sửa:** trả lỗi 502 tổng quát, giữ exception làm nguyên nhân nội bộ. |
| MEDIUM | UI quản trị phụ thuộc username `admin` | App/Layout/TaiKhoan/AI | **Đã sửa:** UI dựa role `QuanLy`; backend vẫn là nguồn quyết định quyền. |

## Rủi ro còn lại

- JWT đang nằm trong `localStorage`; XSS vẫn có thể đánh cắp token. Cần CSP, rà XSS/E2E và cân nhắc cookie `HttpOnly` trước khi public.
- Chưa có rate limit/login throttling, audit log bất biến, refresh-token/revocation hay CORS production allow-list.
- ORM không khai báo `ForeignKey` dù script MySQL có FK; migration schema cần được thiết kế/backup riêng, không được tự chạy trên `quan_ly_kho`.
- Regression Windows 57/57 PASS không thay thế Gemini thật, frontend E2E hay toàn bộ authorization matrix bằng pytest trên môi trường hoạt động.

## Quy tắc dữ liệu AI

Gemini chỉ phân tích/đề xuất. Đề xuất được lọc theo đúng `ma_hang` trong context tồn kho; AI không ghi `TonKho` hay `LichSuKho`. Tồn chỉ đổi trong xác nhận phiếu nhập/xuất có transaction.
