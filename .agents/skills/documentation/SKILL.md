---
name: documentation
description: Đồng bộ README, báo cáo, kiến trúc, ERD, skill, demo và bằng chứng kiểm thử với source code QuanLyKhoAI.
---

# Documentation Skill — QuanLyKhoAI

## Nguồn kiểm chứng

1. Đọc `docs/project-context.md`, `docs/repository-alignment.md`.
2. Kiểm chứng chức năng bằng `backend/*.py`, `backend/models.py`, `frontend/src/App.jsx`, `frontend/src/pages/`, `multi_agent/multi_agent/`.
3. Kiểm chứng CSDL qua `database/quan_ly_kho_mysql.sql` và `docs/erd.md`. Phân biệt logical FK với FK vật lý.
4. Kiểm chứng test bằng `backend/tests/`, `multi_agent/multi_agent/tests/` và output thật `pytest`. Không dùng một câu trong báo cáo thay cho bằng chứng chạy.
5. Kiểm tra tất cả đường dẫn Markdown, lệnh PowerShell và liên kết trong README.

## Các điều phải nhất quán

- Tên thực thể: `User`, `NhomHang`, `HangHoa`, `NhaCungCap`, `PhieuNhap`, `ChiTietPhieuNhap`, `TonKho`, `LichSuKho`, `PhieuXuat`, `ChiTietPhieuXuat`, `DeXuatAI`, `ChiTietDeXuatAI`.
- Role: `QuanLy`, `ThuKho`, `KeToan`.
- Stack: React/Vite, FastAPI, SQLAlchemy/PyMySQL, MySQL, Gemini, ChromaDB/SentenceTransformer.
- Sơ đồ: 7 Agent trong Multi-Agent, phân biệt baseline Single-Agent.
- Luồng: AI đề xuất → Quản lý duyệt → Thủ kho tạo phiếu **nháp** → khi xác nhận mới cập nhật tồn/lịch sử.
- Schema triển khai: 12 bảng trong `quan_ly_kho`; `quanlykho_test` chỉ là test DB. Nếu ảnh thiết kế có `BAO_CAO_AI`, không tuyên bố đó là bảng đã triển khai.
- Kiểm thử: báo cáo **77 functional cases**, repo **41 automated tests** (20 Agent, 15 API, 6 MySQL). Kết quả PASS chỉ là lần chạy nhóm đã ghi nhận và cần chạy lại sau sửa code.
- Benchmark 10 câu: chỉ là một lượt đo; không khẳng định AI tuyệt đối chính xác hay Multi-Agent luôn nhanh hơn.

## Quy trình cập nhật

1. Lập bảng `Claim | Nguồn tài liệu | Source code | Đã test? | Kết luận`.
2. Gắn nhãn **implemented**, **design only**, **needs verification**, **known defect**. Không sửa yêu cầu hoặc bịa implementation để làm tài liệu khớp.
3. Chỉnh đúng file source tài liệu: `README.md`, `docs/*`, `.agents/skills/*`, frontend README. Nếu cần sửa code, chuyển qua implementation + testing skill.
4. Cập nhật ví dụ API, lệnh cài đặt, đường dẫn và nhóm test; không chép password, API key, token.
5. Rà lại các thông tin thuyết trình: bìa có giảng viên hướng dẫn **Nguyễn Đình Dũng**; 7 chương được tóm tắt; hình ERD, Sequence, Activity và test case phải được ghi là hình gốc nếu lấy từ báo cáo.
6. Kiểm tra diff, link và chính tả trước khi commit.

## Output

Danh sách file sửa, bảng đối chiếu trước/sau, minh chứng tương ứng, điểm **chưa thể xác minh**, và hành động tiếp theo. Không tự tuyên bố báo cáo/code/slide đã đồng nhất 100% nếu còn lỗ hổng bảo mật hoặc mục thiết kế chưa triển khai.
