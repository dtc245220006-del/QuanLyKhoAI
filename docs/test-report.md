# Test Report — QuanLyKhoAI

> Phân biệt **test được định nghĩa trong repo**, **kết quả chạy thủ công đã ghi nhận** và **phạm vi chưa kiểm thử**. Không suy diễn rằng mọi chức năng đều đã PASS.

## 1. Bộ tự động đang có trong mã nguồn

| Bộ kiểm thử | Vị trí | Số test đã ghi nhận | Phương pháp |
|---|---|---:|---|
| Multi-Agent, Single-Agent, SQL Tool | `multi_agent/multi_agent/tests/` | 20 | pytest, mock; kiểm tra orchestration, Critic, SQL Tool, RAG và baseline |
| Phân quyền đề xuất AI/API | `backend/tests/test_de_xuat_ai_authorization.py` | 15 | FastAPI TestClient, fake session/dependency override |
| Nhập, xuất, tồn, rollback và AI | `backend/tests/test_mysql_inventory_integration.py` | 6 | **MySQL thật** trên schema test riêng, Gemini được mock |
| **Tổng** | | **41** | 35 Unit/API + 6 MySQL Integration |

`backend/tests/conftest.py` cung cấp cờ `--run-mysql-integration`. **Không** chạy integration test với tài khoản/database ứng dụng.

Báo cáo môn học còn trình bày **77 test case chức năng** theo bảng thủ công/hộp đen. Đây là **bộ test khác**, không được mô tả thành `118 automated tests` hay ngầm định đã được chạy bởi pytest.

## 2. Cách chạy thực tế trên Windows PowerShell

Từ thư mục gốc repository sau khi đã cài `backend/.venv`:

**35 Unit/API/Agent tests:**

```powershell
cd multi_agent
$env:PYTHONPATH = (Get-Location).Path
& "..\backend\.venv\Scripts\python.exe" -X utf8 -m pytest --pyargs multi_agent.tests ..\backend\tests\test_de_xuat_ai_authorization.py --import-mode=importlib -q
```

**6 MySQL integration tests:** khi Terminal vẫn đứng ở `multi_agent`:

```powershell
& "..\backend\.venv\Scripts\python.exe" -X utf8 -m pytest ..\backend\tests\test_mysql_inventory_integration.py --run-mysql-integration -s -q
```

- Yêu cầu local schema `quanlykho_test`, user `qlk_test_user` (chỉ quyền SELECT/INSERT/UPDATE/DELETE đối với test schema).
- `getpass` hỏi mật khẩu tương tác. **Dừng nếu Terminal cảnh báo có thể echo mật khẩu**. Không ghi mật khẩu trong lệnh, file, ảnh hay log.
- Test kiểm tra `SELECT DATABASE(), CURRENT_USER()` trước khi ghi/xóa, tạo fixture riêng và dọn các bản ghi do test tạo.
- Không dùng `backend.database`, `backend.main`, `.env` của ứng dụng trong test tích hợp để tránh kết nối nhầm schema.

## 3. Kết quả đã được nhóm ghi nhận trên máy chạy dự án

| Nhóm | Passed | Failed | Ghi chú |
|---|---:|---:|---|
| Unit/API/Agent | **35** | **0** | Đã thấy log pytest `35 passed, 1 warning` |
| MySQL Integration | **6** | **0** | Nhóm xác nhận đã chạy lại và PASS sau khi sửa rollback nhập kho |
| Tổng | **41** | **0** | Ghi nhận một phiên thử nghiệm local, **chưa được chạy lại ở GitHub Actions** |

Không thay thế bằng kết quả `collected` hay giả định máy khác cũng sẽ PASS. Các test dùng mock **không kiểm tra việc gọi Gemini thật**, hiệu năng ChromaDB thực tế hoặc frontend E2E.

### Tình huống lỗi đã được phát hiện và xử lý

Trong lần chạy integration đầu tiên: **5 passed, 1 failed** tại `test_it_005_receipt_failure_rolls_back_without_partial_stock_update`. Test cố tình tạo lỗi lúc ghi `LichSuKho` và phát hiện SQLAlchemy Session vẫn còn transaction sau exception. Nhóm bổ sung rollback + flush trong `backend/phieu_nhap.py`, giữ assertion không đổi, sau đó xác nhận **6/6 PASS**. Đây là minh chứng AI-assisted testing → phân tích lỗi → sửa code → kiểm thử hồi quy.

**Phần chưa kiểm chứng:** `xac_nhan_phieu_xuat` chưa có integration test inject lỗi giữa transaction; code chưa có rollback handler tương tự. Không được tuyên bố đã giải quyết rủi ro này.

## 4. Phạm vi test case

- **AI Agent (20):** message, Analyst, SQL Tool query builder và parameterized query, RAG mock, Reasoning/Critic/Response, orchestration/retry, Single-Agent.
- **API authorization (15):** token thiếu/sai, role không hợp lệ, duyệt/từ chối proposal, trạng thái đề xuất, tạo phiếu nháp từ đề xuất đã duyệt, chống giả mạo `ma_tai_khoan`.
- **MySQL (6):** phiếu nhập nháp giữ nguyên tồn; xác nhận nhập tăng tồn một lần; phiếu xuất nháp giữ nguyên tồn; xuất quá tồn bị từ chối; nhập lỗi rollback; AI (mock) không tự sửa tồn.

Không đánh đồng những lời mô tả về bảo mật/hệ thống trong báo cáo với kết quả kiểm thử thực tế. Xem [Security Review](security-review.md).

## 5. Benchmark Single-Agent và Multi-Agent

Một lượt benchmark đã ghi nhận với cùng 10 câu hỏi, Test Oracle đối chiếu dữ liệu MySQL:

| Chỉ số | Single-Agent | Multi-Agent |
|---|---:|---:|
| Data-grounded accuracy | 10/10 | 10/10 |
| Thời gian TB | 2732,84 ms | 1488,47 ms |
| LLM calls TB/câu | 1 | 3 |
| Tổng LLM calls | 10 | 30 |

Tham chiếu `multi_agent/multi_agent_benchmark.json`, [benchmark-guide](benchmark-guide.md), [multi-agent-comparison](multi-agent-comparison.md). Kết quả một lượt không chứng minh Multi-Agent luôn nhanh hơn hoặc mọi câu trả lời đều đúng tuyệt đối.

## 6. Việc còn thiếu trước khi gọi là kiểm thử toàn diện

1. Test JWT/role **tất cả** endpoint kho, đặc biệt `/phieu-nhap`, `/phieu-xuat`, `/ai`, `/de-xuat-ai` chưa bảo vệ đầy đủ.
2. Test forced-failure rollback phiếu xuất, kiểm tra trạng thái/tồn/lịch sử không commit dở.
3. Test frontend build, lint, các luồng login/demo end-to-end.
4. Test lỗi Gemini thật có kiểm soát, timeout/rate limit và thông tin lỗi không chứa secrets.
5. Test concurrency nhập/xuất, stock race conditions và kiểm tra các ràng buộc DB vật lý.

**Quy tắc báo cáo:** phải lưu output pytest, môi trường, ngày chạy và minh chứng riêng; không sửa assertion/giảm expected result để làm đẹp số PASS.
