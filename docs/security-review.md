# Security Review — Final regression review, 28/10/2026

Phạm vi: diff chưa commit, router FastAPI, frontend React, SQL Tool, bootstrap script và test source. Regression Windows đã xác minh **45/45 Unit/API/Agent**, **IT-011 PASS** và **12/12 MySQL integration PASS** (tổng **57/57**). Đây vẫn không phải pentest, frontend E2E hay chứng nhận production-ready.

| Finding | Severity | Evidence / behavior | Regression test | Status |
|---|---|---|---|---|
| Tài khoản mặc định cố định | CRITICAL | `main.py` không còn seed `admin/123456` hoặc `create_all` lúc import; `bootstrap_admin.py` hỏi mật khẩu ẩn, từ chối username đã tồn tại và không xóa/ghi đè dữ liệu. | Static review; toàn bộ regression PASS, bootstrap chưa chạy interactive riêng | Code fixed; interactive bootstrap remains manual |
| Anonymous access tới API kho/AI | HIGH | Router nghiệp vụ dùng `get_current_user`; thao tác nhạy cảm dùng `require_roles`. | `test_route_authentication.py` 10 parameter cases | **PASS**; chỉ chứng minh anonymous GET, chưa là full role matrix |
| Client spoof `ma_tai_khoan` | HIGH | Phiếu nhập/xuất và đề xuất dùng `current_user.id`; frontend không gửi field này. | `test_it_012_*` và proposal API test cũ | **PASS** |
| Partial transaction nhập/xuất | HIGH | Confirm dùng rollback decorator, `flush`, `FOR UPDATE`; xuất có test injected failure. | `test_it_005`, `test_it_006` | **PASS** |
| Xác nhận đồng thời | HIGH | Khóa phiếu/tồn bằng `FOR UPDATE`; test hai session độc lập kiểm tra chỉ một confirm thành công. | `test_it_011_*` | **PASS**; Session độc lập xác nhận tồn `14`, `DaNhap`, một lịch sử nhập |
| Xuất nhiều dòng trùng mã / tồn âm | HIGH | Backend từ chối mặt hàng trùng trong một phiếu trước khi tạo phiếu. | `test_it_008_*` | **PASS** |
| Xóa phiếu/hàng có tham chiếu | HIGH | Không xóa `DaNhap`; không xóa hàng có chi tiết phiếu, đề xuất, tồn hoặc lịch sử. | `test_it_009_*`, `test_it_010_*` | **PASS** |
| Xóa nhóm hàng / nhà cung cấp có tham chiếu | MEDIUM | Hai endpoint vẫn gọi `delete/commit` trực tiếp; ràng buộc FK phải bảo vệ dữ liệu nhưng API có thể trả lỗi DB thay vì 400 có chủ đích. | Chưa có dedicated test | Open |
| MySQL root fallback / password URL | MEDIUM | `DB_USER` bắt buộc; SQLAlchemy dùng `URL.create`; SQL Tool không fallback root. | Static review | Code fixed, runtime unverified |
| Leaked Gemini exception | MEDIUM | AI endpoints trả 502 chung, chaining exception nội bộ. | Chưa có dedicated API test | Needs coverage |
| JWT trong `localStorage` | MEDIUM | `frontend/src/api.js` đọc Bearer token từ localStorage; 401 ngoài login xóa phiên và chuyển về login, 403 giữ phiên để UI hiển thị lỗi quyền. | Không có E2E/XSS test | Open: localStorage vẫn có rủi ro XSS |

## Kiểm tra script bootstrap

`backend/bootstrap_admin.py` chỉ tạo một `QuanLy` mới sau khi người vận hành nhập username, tên và hai lần mật khẩu. Mật khẩu được hash PBKDF2-SHA256; trùng username sẽ dừng trước `add/commit`; mọi exception rollback transaction. Script không có mật khẩu mặc định, `DELETE`, `DROP`, `TRUNCATE` hoặc update tài khoản có sẵn. Đây là kết luận từ code review; không chạy interactive bootstrap trên database có dữ liệu trong regression.

## Điều kiện trước khi public

1. Bổ sung full 401/403 role matrix, test Gemini failure và concurrency nhiều hàng theo transaction thực.
2. Giảm rủi ro token storage/XSS, thêm rate limit, audit log và CORS production allow-list.
3. Không commit `.env`, API key, password, DB dump có dữ liệu hoặc file runtime.
