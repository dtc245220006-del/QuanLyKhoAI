---
name: testing
description: Xây dựng và thực thi kiểm thử cho QuanLyKhoAI theo requirements và ERD thực tế.
---

# Testing Skill — QuanLyKhoAI

## Quy trình
Requirements → Test Scenario → Test Case → Automated Test → Execution → Result → Defect.

## Phạm vi
- Đăng nhập/đăng xuất
- Phân quyền theo vai trò
- CRUD nhóm hàng/hàng hóa/NCC
- Phiếu nhập/xuất
- Cập nhật tồn kho
- Lịch sử kho
- Báo cáo
- AI phân tích tồn kho
- Tạo/duyệt/từ chối đề xuất AI
- Kiểm tra AI không trực tiếp mutate dữ liệu kho

## Quy tắc
- Không sửa test chỉ để làm test pass.
- Test phải trace về requirement.
- Phải có negative cases và authorization cases.
- Tạo `docs/test-plan.md` và `docs/test-report.md`.
