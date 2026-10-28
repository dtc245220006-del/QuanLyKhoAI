# Test Plan — QuanLyKhoAI

## Mục tiêu

Kiểm thử yêu cầu quan trọng của hệ thống kho (một kho; ba vai trò `QuanLy`, `ThuKho`, `KeToan`) và AI. Phân biệt rõ **test được viết**, **test đã chạy** và **test còn thiếu**.

## Mức kiểm thử và nguồn

| Mức | Mã nguồn | Mục tiêu |
|---|---|---|
| Unit/Agent | `multi_agent/multi_agent/tests/` (20 tests) | Analyst, SQL Tool, RAG mock, Reasoning, Critic, Orchestrator/retry, Single-Agent |
| API/Auth | `backend/tests/test_de_xuat_ai_authorization.py` (15 tests) | JWT/role cho proposal, trạng thái duyệt và phiếu nháp |
| Route authentication | `backend/tests/test_route_authentication.py` (10 tests) | Mọi router nghiệp vụ từ chối request không có Bearer token |
| MySQL Integration | `backend/tests/test_mysql_inventory_integration.py` (12 tests) | Nhập/xuất, duplicate line, rollback, concurrent confirm, ID token và AI mock |
| Manual/functional | 77 test case trình bày trong báo cáo | Đăng nhập, CRUD kho, chức năng AI, bảng quyết định |
| Benchmark | `multi_agent/multi_agent/benchmark.py` | Cùng 10 câu hỏi, Test Oracle, thời gian và LLM calls |

`20 + 15 + 10 + 12 = 57` automated test được định nghĩa. Regression Windows 28/10/2026 đã chạy lại toàn bộ: 45/45 Unit/API/Agent, IT-011 riêng PASS và 12/12 MySQL integration, tổng 57/57 PASS. 77 functional test case trong báo cáo là một bộ khác.

## Cách chạy

Dùng lệnh đầy đủ trong [README](../README.md) hoặc [Testing Skill](../.agents/skills/testing/SKILL.md). Chạy Unit/API từ **thư mục `multi_agent`** với `PYTHONPATH` và `--import-mode=importlib` để tránh import sai package lồng nhau.

Bộ MySQL yêu cầu opt-in `--run-mysql-integration -s`, prompt mật khẩu kín, schema `quanlykho_test` và user `qlk_test_user`. Không dùng dữ liệu thực, không chạy trên database `quan_ly_kho`.

## Test oracle quan trọng

- Phiếu nháp **không** thay đổi `TonKho`.
- Xác nhận phiếu nhập tăng đúng một lần; xác nhận lại bị từ chối.
- Phiếu xuất quá tồn bị từ chối, không có tồn âm.
- Nếu phát sinh lỗi khi ghi `LichSuKho` hoặc update, transaction phải rollback; trạng thái phiếu, tồn kho và lịch sử không commit dở.
- Chỉ `QuanLy` được duyệt/từ chối đề xuất; chỉ `ThuKho` tạo phiếu nhập nháp từ đề xuất đã duyệt.
- AI analysis/đề xuất không trực tiếp làm biến động tồn kho.
- AI không bịa mã hàng/giá/tồn khi dữ liệu đầu vào không có; Test Oracle đối chiếu SQL, không chỉ đọc câu văn.

## Exit criteria đề xuất cho demo/bàn giao

1. Chạy lại toàn bộ test liên quan sau khi sửa code và lưu output.
2. Không còn lỗi **CRITICAL/HIGH** chưa được thừa nhận/xử lý trước khi mở hệ thống ra mạng.
3. Kiểm tra backend/DB trên máy demo; `npm run lint` và `npm run build` nếu có thể.
4. Có minh chứng live cho phiếu nhập, xuất, tồn kho, duyệt đề xuất AI và hỏi Multi-Agent.
5. Các test còn thiếu phải ghi `NOT COVERED`, không cho PASS bằng giả định.

## Gap cần bổ sung

- Test role matrix đầy đủ (401/403) cho từng endpoint kho/AI.
- Test concurrency/double confirmation thực tế khi có nhiều người cùng thao tác.
- Kiểm tra migration/constraints MySQL, E2E frontend, lỗi Gemini thật có giới hạn, thông tin exception.
- Test cache, ChromaDB/embedding và đo nhiều lượt benchmark nếu muốn kết luận hiệu năng.

Tham khảo [Test Report](test-report.md), [Security Review](security-review.md) và [Requirements Traceability](requirements-traceability.md).
