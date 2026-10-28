---
name: release-readiness
description: Rà soát tính nhất quán code, README, skill, báo cáo, slide, kiểm thử và bảo mật trước khi demo hoặc bàn giao QuanLyKhoAI.
---

# Release Readiness Skill — QuanLyKhoAI

## Nhiệm vụ

Giúp nhóm chốt tài liệu **mà không thay đổi yêu cầu hoặc tuyên bố sai về kết quả thực nghiệm**. Đọc:
- `docs/project-context.md`, `docs/repository-alignment.md`, `README.md`.
- `docs/requirements.md`, `docs/architecture.md`, `docs/erd.md`, `docs/database-design.md`.
- `docs/test-report.md`, `docs/security-review.md`, `docs/deployment.md`.
- `backend/main.py`, `backend/auth.py`, các route kho, `backend/de_xuat_ai.py`, `multi_agent/multi_agent/router.py`, `frontend/src/App.jsx`.

## Checklist bắt buộc

1. **Giới hạn phạm vi:** một kho, `QuanLy/ThuKho/KeToan`. Không tự bổ sung module chưa tồn tại.
2. **Dữ liệu:** schema ứng dụng `quan_ly_kho`, 12 bảng; schema test `quanlykho_test` riêng. `BAO_CAO_AI` trong bản vẽ (nếu có) là thiết kế dự kiến khi không có trong SQL thực tế.
3. **Luồng:** AI phân tích/gợi ý; Quản lý duyệt; Thủ kho tạo phiếu nháp; tồn chỉ đổi khi xác nhận. Xem implementation để xác minh từng API.
4. **Chứng cứ test:** 20 Agent + 15 API + 6 MySQL = 41 automated tests trong repo; 77 test case chức năng thuộc báo cáo, là nhóm khác. Test PASS local không tương đương CI/E2E.
5. **Benchmark:** 10 câu hỏi, 1 lượt đo được ghi nhận; không khẳng định luôn nhanh hơn.
6. **Bảo mật:** rà admin mặc định, JWT/role cho từng endpoint, IDOR, secrets, rollback xuất kho, lỗi Gemini. Không gắn nhãn production-ready khi còn lỗ hổng.
7. **Giới hạn thực thi:** nếu không chạy được Python, MySQL, Node, Gemini, báo rõ `NOT RUN`, không đoán.
8. **Hồ sơ thuyết trình:** báo cáo và Canva/PowerPoint chứa hình gốc; không biến ảnh thiết kế thành bằng chứng API runtime.
9. **Giữ an toàn repo:** kiểm tra diff, không chỉnh secrets, không force-push, không reset dữ liệu.

## Chạy kiểm thử được ghi nhận trên Windows

Từ root repo, sau khi đã cài `backend/.venv`:

```powershell
cd multi_agent
$env:PYTHONPATH = (Get-Location).Path
& "..\backend\.venv\Scripts\python.exe" -X utf8 -m pytest --pyargs multi_agent.tests ..\backend\tests\test_de_xuat_ai_authorization.py --import-mode=importlib -q
& "..\backend\.venv\Scripts\python.exe" -X utf8 -m pytest ..\backend\tests\test_mysql_inventory_integration.py --run-mysql-integration -s -q
```

Lệnh thứ hai cần schema/user test chính xác, nhập mật khẩu bằng `getpass` qua Terminal không echo; **không tự chạy nếu thiếu xác nhận an toàn dữ liệu test**.

## Output cuối

Báo cáo dạng bảng: `Item | Expected | Found | Evidence path | Status (PASS/GAP/NOT RUN) | Owner/action`; liệt kê tất cả file thay đổi và kết quả test thực tế. Không tự đóng GAP chỉ bằng việc sửa văn bản.
