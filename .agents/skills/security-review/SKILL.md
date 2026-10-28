---
name: security-review
description: Kiểm tra JWT, phân quyền API, bí mật, IDOR và tính nguyên tử transaction của QuanLyKhoAI; báo cáo rủi ro có bằng chứng code và test.
---

# Security Review Skill — QuanLyKhoAI

## Đọc trước

`docs/project-context.md`, `docs/requirements.md`, `docs/security-review.md`, `backend/main.py`, `backend/auth.py`, `backend/tai_khoan.py`, `backend/de_xuat_ai.py`, `backend/phieu_nhap.py`, `backend/phieu_xuat.py`, `backend/ai_controller.py`, `frontend/src/App.jsx`.

## Checklist theo repo thật

1. **Default admin:** `backend/main.py` có tự seed `admin` bằng password cố định không? Nếu còn, gắn **CRITICAL**, không public dịch vụ.
2. **JWT + role:** với mọi GET/POST/PUT/DELETE trong router kho, AI, đề xuất, tài khoản, kiểm tra dependency `get_current_user` / `require_roles` **ở backend**; không lấy việc UI ẩn menu làm minh chứng.
3. **Identity:** tài khoản tạo giao dịch phải lấy từ token ở các luồng nhạy cảm; chống client spoof `ma_tai_khoan` và kiểm tra IDOR/BOLA.
4. **Password/JWT:** hash mật khẩu, secret đủ mạnh, expiry token, không trả thông tin nhạy cảm từ lỗi.
5. **Database:** SQL Tool dùng parameterized SQL; kiểm tra mọi dynamic query khác. Không fallback tài khoản MySQL `root` khi triển khai.
6. **Transaction:** test nhập và xuất lỗi giữa giao dịch; bắt buộc rollback cả tồn, lịch sử, trạng thái nếu có exception; test cùng `quanlykho_test` riêng.
7. **Gemini/RAG:** không gửi API key/token vào prompt; xử lý timeout/error, không trả `str(e)` chưa lọc ra client; giới hạn dữ liệu dùng làm context; AI không trực tiếp sửa `TonKho`.
8. **Frontend:** XSS, JWT lưu localStorage, phân quyền UI chỉ là UX; thử gọi API trực tiếp.
9. **Secrets/Git:** rà `.env`, file JSON, log, history và screenshots; không cam kết bí mật an toàn nếu chưa kiểm tra lịch sử.
10. **Dependency/runtime:** review package versions, CORS và việc `main.py` tự `create_all` / seed admin khi import.

## Kiểm thử và mức độ chắc chắn

- Dùng `backend/tests/test_de_xuat_ai_authorization.py` (15 tests) để xác nhận những route proposal đã được bao phủ.
- Dùng `backend/tests/test_mysql_inventory_integration.py` (6 tests) chỉ trên `quanlykho_test` với `qlk_test_user`, theo [testing skill](../testing/SKILL.md).
- Không đánh đồng **41 tests đã PASS tại máy nhóm** với việc đã kiểm thử toàn bộ security.
- Nếu không chạy được môi trường, báo `NOT RUN`, tuyệt đối không đoán kết quả.

## Output

Ghi vào `docs/security-review.md`: `Finding | Severity | Source path/function | Observed behavior | Risk | Recommended fix | Regression test | Status`. Phân loại CRITICAL/HIGH/MEDIUM/LOW, phân biệt đã sửa và chưa sửa. Nếu sửa code nghiệp vụ hoặc auth, bổ sung test fail→fix→pass; không chỉ sửa tài liệu để đóng rủi ro.
