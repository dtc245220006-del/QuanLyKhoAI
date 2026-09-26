---
name: requirements-analysis
description: Phân tích yêu cầu cho hệ thống Quản lý Kho tích hợp AI và tạo yêu cầu có cấu trúc, user story, acceptance criteria và traceability.
---

# Requirements Analysis Skill — QuanLyKhoAI

## Project context
Hệ thống: Quản lý Kho tích hợp AI.
Stack hiện tại: React frontend, FastAPI backend, SQLAlchemy, cơ sở dữ liệu quan hệ, Gemini API.
Vai trò người dùng: Quản lý, Thủ kho, Kế toán.
Không được tự thay thế mô hình dữ liệu hoặc nghiệp vụ hiện có bằng ví dụ sản phẩm/laptop.

## Quy tắc
- Đọc `docs/project-context.md` trước.
- Phải giữ đúng các thực thể kho: User, NhomHang, HangHoa, NhaCungCap, PhieuNhap, ChiTietPhieuNhap, TonKho, LichSuKho, PhieuXuat, ChiTietPhieuXuat, DeXuatAI, ChiTietDeXuatAI.
- Không tự thêm nghiệp vụ chưa có.
- Phân biệt requirement thật, giả định và điểm chưa rõ.
- Mọi requirement phải có ID FR-/NFR-.
- User story phải gắn với vai trò thực tế.
- Acceptance criteria phải kiểm thử được.
- Phần AI phải phản ánh luồng: TonKho + HangHoa → GeminiAIService → DeXuatAI + ChiTietDeXuatAI → Quản lý duyệt/từ chối → nếu duyệt thì Thủ kho tạo phiếu nhập nháp → xác nhận phiếu nhập → cập nhật TonKho + LichSuKho.
- AI không được trực tiếp thay đổi dữ liệu kho.

## Outputs
- docs/requirements.md
- docs/user-stories.md
- docs/acceptance-criteria.md
- docs/requirements-issues.md
