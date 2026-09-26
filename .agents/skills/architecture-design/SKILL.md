---
name: architecture-design
description: Thiết kế kiến trúc cho hệ thống Quản lý Kho tích hợp AI dựa trên requirements đã được duyệt.
---

# Architecture Design Skill — QuanLyKhoAI

## Project context
React → FastAPI → Database.
Các nhóm chức năng: xác thực, quản lý dữ liệu kho, nhập/xuất, tồn kho, báo cáo và AI.

## Quy tắc
- Đọc requirements và `docs/project-context.md`.
- Không tự đổi stack.
- Giữ ranh giới frontend/backend/database/AI.
- AI chỉ phân tích và đề xuất; không trực tiếp mutate dữ liệu kho.
- Phải mô tả luồng AI và quyền của Quản lý/Thủ kho.
- Phải có traceability từ requirement → component.
- Không dùng kiến trúc chatbot sản phẩm làm ví dụ thay thế cho hệ thống kho.

## Outputs
- docs/architecture.md
- docs/architecture-decisions.md
