# Security Review — trạng thái mã nguồn hiện tại

**Phạm vi:** rà soát tĩnh các file trên nhánh `main` trước đợt cập nhật tài liệu (28/10/2026). Đây **không phải** chứng nhận an toàn hoặc pentest toàn diện; đánh giá dựa trên code nhìn thấy, không có xác minh exploit với production. Thứ tự ưu tiên dưới đây dành cho nhóm phát triển.

| Ưu tiên | Bằng chứng trong mã nguồn | Rủi ro / bước sửa |
|---|---|---|
| **CRITICAL** | `backend/main.py` gọi `create_default_users()` và hash mật khẩu cố định `123456` cho `admin` nếu chưa có | Người biết tên đăng nhập và mật khẩu mặc định có thể thử đăng nhập. **Không đưa app ra Internet** trước khi thay cơ chế seed admin bằng mật khẩu ngẫu nhiên lấy từ env/thiết lập thủ công và test đăng nhập đầu tiên |
| **HIGH** | `backend/phieu_nhap.py` và `backend/phieu_xuat.py` khai báo GET/POST/PUT/DELETE chỉ với `Depends(get_db)`, không có `get_current_user` / `require_roles` | Phân quyền hiển thị trên React **không bảo vệ API**. Cần thêm JWT/role ở router/dependency, suy ra người thực hiện từ JWT và viết test 401/403 cho từng endpoint |
| **HIGH** | `backend/de_xuat_ai.py` POST tạo đề xuất dùng `ma_tai_khoan` từ request và kiểm tra role của **tài khoản được chỉ định**, không xác thực người gọi. GET đề xuất cũng chưa có auth | Có nguy cơ giả danh người quản lý và rò dữ liệu. Cần xác thực JWT, dùng `current_user.id`, role server-side và test |
| **HIGH** | `backend/ai_controller.py` GET phân tích tồn kho không có JWT | Truy xuất dữ liệu kho qua AI endpoint; cần xác thực/role và giới hạn lượng dữ liệu/cost |
| **HIGH** | `backend/phieu_xuat.py` hàm `xac_nhan_phieu_xuat` trừ tồn/ghi lịch sử trước `commit()`, chưa có `except: db.rollback()` | Khi lỗi giữa transaction, Session có thể giữ thay đổi chưa commit; cần test injected failure tương tự `test_it_005` rồi sửa và chạy lại |
| **MEDIUM** | `backend/de_xuat_ai.py` trả `detail=f"Lỗi khi gọi Gemini: {str(e)}"` | Thông tin exception từ dịch vụ có thể lộ nội dung nội bộ; trả mã lỗi an toàn cho client, log nội bộ đã lọc secrets |
| **MEDIUM** | `frontend/src/App.jsx` dựa vào `localStorage` / username `admin`; `frontend/src/api.js` dùng Bearer token trong localStorage | Chỉ là điều hướng UI; cần xác thực ở backend và kiểm tra nguy cơ XSS/token storage |
| **MEDIUM** | `backend/database.py`, `multi_agent/.../sql_tool.py` có default `DB_USER=root` nếu thiếu cấu hình | Không dùng quyền root trong demo/public; dùng DB account ít quyền, bắt buộc cấu hình rõ thay vì fallback |
| **REVIEW** | `backend/main.py` chạy `Base.metadata.create_all(bind=engine)` ngay khi import module | Khởi tạo schema ngầm gây tác động ngoài ý muốn khi test/import; cân nhắc migration/startup riêng có guard |

## Điều đang được triển khai đúng

- `backend/auth.py` yêu cầu `JWT_SECRET_KEY` từ env và mã hóa mật khẩu bằng PBKDF2-SHA256.
- `backend/tai_khoan.py` có kiểm tra JWT và `admin` ở backend cho các endpoint quản lý tài khoản.
- Các endpoint duyệt/từ chối đề xuất và tạo phiếu nhập nháp từ đề xuất đã duyệt đã dùng `require_roles` ở backend.
- `multi_agent/multi_agent/router.py` yêu cầu JWT; `multi_agent/multi_agent/tools/sql_tool.py` dùng tham số truy vấn cho dữ liệu đầu vào và whitelist hướng sắp xếp.
- `backend/phieu_nhap.py` đã có rollback khi exception trong luồng xác nhận nhập; test `test_it_005` đã từng phát hiện lỗi này và nhóm xác nhận PASS sau sửa.

Những điểm trên **không suy ra toàn hệ thống đã đạt đầy đủ các yêu cầu bảo mật**.

## Kế hoạch sửa an toàn

1. **Đóng môi trường** (không public port 8000, không dùng dữ liệu thật), thay tài khoản `admin` mặc định.
2. Viết test 401 khi thiếu JWT, 403 khi sai role cho tất cả route kho, đề xuất AI và phân tích AI; giữ 3 role `QuanLy`, `ThuKho`, `KeToan`.
3. Áp dụng kiểm tra role ở backend, lấy `ma_tai_khoan` từ token thay vì tin dữ liệu client cho thao tác nghiệp vụ.
4. Thêm test rollback xuất kho, kiểm tra `TonKho`, `LichSuKho` và trạng thái phiếu trước/sau lỗi.
5. Chạy lại **35 test mock/API** và **6 test MySQL** cùng các test mới; lưu stdout thực, không tự nhận PASS nếu chưa chạy.
6. Kiểm tra secrets trong lịch sử Git trước khi phát hành bản demo; rotate nếu đã lộ, không chỉ xóa khỏi commit mới.

**Lý do chưa tự sửa các lỗi code trên trong nhánh tài liệu:** đây là thay đổi security/business có khả năng làm thay đổi luồng giao diện và hợp đồng API; phải có test regression ở máy người dùng trước khi đưa lên `main`. Xem [README](../README.md), [test-report](test-report.md).
