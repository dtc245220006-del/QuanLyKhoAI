# Requirements — Hệ thống Quản lý Kho tích hợp AI

## Functional Requirements

| ID | Yêu cầu |
|---|---|
| FR-001 | Người dùng đăng nhập/đăng xuất bằng tài khoản hợp lệ. |
| FR-002 | Hệ thống phân quyền theo QuanLy, ThuKho, KeToan. |
| FR-003 | Quản lý nhóm hàng. |
| FR-004 | Quản lý hàng hóa. |
| FR-005 | Quản lý nhà cung cấp. |
| FR-006 | Lập và xác nhận phiếu nhập. |
| FR-007 | Lập và xác nhận phiếu xuất. |
| FR-008 | Cập nhật tồn kho sau giao dịch được xác nhận. |
| FR-009 | Ghi nhận lịch sử kho. |
| FR-010 | Xem thống kê và báo cáo. |
| FR-011 | AI phân tích tồn kho dựa trên dữ liệu HangHoa và TonKho. |
| FR-012 | Gemini tạo đề xuất nhập hàng. |
| FR-013 | Quản lý duyệt hoặc từ chối đề xuất AI. |
| FR-014 | Thủ kho tạo phiếu nhập nháp từ đề xuất đã duyệt. |
| FR-015 | Hệ thống cung cấp workflow Multi-Agent cho câu hỏi kho. |
| FR-016 | Multi-Agent ghi log từng bước phối hợp và hỗ trợ retry khi Critic từ chối. |

## Non-functional Requirements
- NFR-001: Không lưu API key trong source code.
- NFR-002: Mật khẩu người dùng phải được lưu dưới dạng hash.
- NFR-003: Endpoint quản trị tài khoản phải kiểm tra JWT và quyền admin ở backend.
- NFR-004: SQL Tool dùng parameterized query.
- NFR-005: AI không được trực tiếp sửa TonKho hoặc LichSuKho.
- NFR-006: Lỗi backend không trả stack trace cho người dùng cuối.
