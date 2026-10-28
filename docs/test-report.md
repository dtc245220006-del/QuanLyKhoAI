# Test Report — QuanLyKhoAI

> Phân biệt **test được định nghĩa trong repo**, **kết quả chạy thủ công đã ghi nhận** và **phạm vi chưa kiểm thử**. Không suy diễn rằng mọi chức năng đều đã PASS.

## Lần audit 28/10/2026

Baseline được yêu cầu đã được đối chiếu trong source: **52 case** = 20 Agent + 15 API authorization cũ + 10 anonymous-route + 7 MySQL integration (`IT-001`…`IT-007`). Audit bổ sung `IT-008`…`IT-012` (duplicate line, xóa phiếu đã xác nhận, hàng tham chiếu, concurrent confirm, identity JWT), nên tổng hiện tại là **57 automated tests**.

### Kết quả regression Windows đã xác minh

- Unit/API/Agent: **45/45 PASS**.
- `test_it_011_concurrent_receipt_confirmation_updates_stock_once`: **1 PASS**.
- MySQL integration: **12/12 PASS**.
- Tổng: **57/57 PASS**, không failed/skipped/errors được báo cáo.
- `npm run lint`: exit 0; còn 10 warning `react(set-state-in-effect)` đã biết.
- `npm run build`: exit 0. `git diff --check`: exit 0.

IT-011 dùng hai Session worker và Session độc lập sau khi worker hoàn tất. Session độc lập xác minh schema/user test trước khi đọc và giữ assertion: `[200, 400]`, tồn `14`, phiếu `DaNhap`, đúng một lịch sử `Nhap`, số lượng lịch sử `4`. Đây là bằng chứng cho luồng xác nhận đồng thời với fixture tồn ban đầu `10` và lượng nhập `4`; không suy rộng thành kiểm thử mọi mẫu cạnh tranh nhiều hàng.

## 1. Bộ tự động đang có trong mã nguồn

| Bộ kiểm thử | Vị trí | Số test đã ghi nhận | Phương pháp |
|---|---|---:|---|
| Multi-Agent, Single-Agent, SQL Tool | `multi_agent/multi_agent/tests/` | 20 | pytest, mock; kiểm tra orchestration, Critic, SQL Tool, RAG và baseline |
| Phân quyền đề xuất AI/API | `backend/tests/test_de_xuat_ai_authorization.py` | 15 | FastAPI TestClient, fake session/dependency override |
| Route authentication | `backend/tests/test_route_authentication.py` | 10 | FastAPI TestClient, request không token phải trả 401 |
| Nhập, xuất, tồn, rollback và AI | `backend/tests/test_mysql_inventory_integration.py` | 12 | **MySQL thật** trên schema test riêng, Gemini được mock |
| **Tổng hiện tại** | | **57** | 45 Unit/API + 12 MySQL Integration |

`backend/tests/conftest.py` cung cấp cờ `--run-mysql-integration`. **Không** chạy integration test với tài khoản/database ứng dụng.

Báo cáo môn học còn trình bày **77 test case chức năng** theo bảng thủ công/hộp đen. Đây là **bộ test khác**, không được mô tả thành `118 automated tests` hay ngầm định đã được chạy bởi pytest.

## 2. Cách chạy thực tế trên Windows PowerShell

Từ thư mục gốc repository sau khi đã cài `backend/.venv`:

**45 Unit/API/Agent tests:**

```powershell
cd multi_agent
$env:PYTHONPATH = (Get-Location).Path
& "..\backend\.venv\Scripts\python.exe" -X utf8 -m pytest --pyargs multi_agent.tests ..\backend\tests\test_de_xuat_ai_authorization.py ..\backend\tests\test_route_authentication.py --import-mode=importlib -q
```

**12 MySQL integration tests:** khi Terminal vẫn đứng ở `multi_agent`:

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
| Unit/API/Agent | **45** | **0** | Windows regression output: 45/45 PASS |
| MySQL Integration | **12** | **0** | Windows regression output: IT-011 riêng PASS, sau đó 12/12 PASS trên `quanlykho_test` / `qlk_test_user` |
| Tổng | **57** | **0** | Kết quả Windows thực tế; không phải CI, E2E frontend hay Gemini thật |

Không thay thế bằng kết quả `collected` hay giả định máy khác cũng sẽ PASS. Các test dùng mock **không kiểm tra việc gọi Gemini thật**, hiệu năng ChromaDB thực tế hoặc frontend E2E.

### Tình huống lỗi đã được phát hiện và xử lý

Trong lần chạy integration đầu tiên: **5 passed, 1 failed** tại `test_it_005_receipt_failure_rolls_back_without_partial_stock_update`. Test cố tình tạo lỗi lúc ghi `LichSuKho` và phát hiện SQLAlchemy Session vẫn còn transaction sau exception. Nhóm bổ sung rollback + flush trong `backend/phieu_nhap.py`, giữ assertion không đổi, sau đó xác nhận **6/6 PASS**. Đây là minh chứng AI-assisted testing → phân tích lỗi → sửa code → kiểm thử hồi quy.

**Phần chưa kiểm chứng:** IT-011 đã chạy hai transaction cạnh tranh cho một mặt hàng; concurrency nhiều mặt hàng, Gemini thật và E2E frontend vẫn chưa được kiểm chứng. Không được suy rộng 57 PASS thành production readiness.

## 4. Phạm vi test case

- **AI Agent (20):** message, Analyst, SQL Tool query builder và parameterized query, RAG mock, Reasoning/Critic/Response, orchestration/retry, Single-Agent.
- **API authorization (15):** token thiếu/sai, role không hợp lệ, duyệt/từ chối proposal, trạng thái đề xuất, tạo phiếu nháp từ đề xuất đã duyệt, chống giả mạo `ma_tai_khoan`.
- **Route authentication (10):** tất cả router nghiệp vụ từ chối request không có Bearer token.
- **MySQL (12):** phiếu nhập/xuất nháp; nhập/xuất vượt tồn; rollback nhập/xuất; AI mock không sửa tồn; duplicate line; xóa phiếu đã xác nhận; hàng được tham chiếu; xác nhận đồng thời; identity token.

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

1. Test role matrix đầy đủ (401/403) cho từng endpoint và role.
2. Test concurrency nhập/xuất thực tế, kiểm tra tồn và trạng thái không lệch.
3. Test các luồng login/demo frontend end-to-end.
4. Test lỗi Gemini thật có kiểm soát, timeout/rate limit và thông tin lỗi không chứa secrets.
5. Test concurrency nhập/xuất, stock race conditions và kiểm tra các ràng buộc DB vật lý.

**Quy tắc báo cáo:** phải lưu output pytest, môi trường, ngày chạy và minh chứng riêng; không sửa assertion/giảm expected result để làm đẹp số PASS.
