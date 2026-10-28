# QuanLyKhoAI — Hệ thống quản lý kho tích hợp AI

Đồ án môn **Ứng dụng Trí tuệ nhân tạo**, Khoa Công nghệ Thông tin, Trường Đại học Công nghệ Thông tin và Truyền thông (ICTU).

- **Giảng viên hướng dẫn:** Nguyễn Đình Dũng
- **Nhóm thực hiện:** Trương Khánh Duy, Hà Quang Vinh, Mã Hoàng Lai (ATTT-K23A)
- **Phạm vi:** một kho; ba vai trò `QuanLy`, `ThuKho`, `KeToan`.
- **Báo cáo & slide:** mô tả yêu cầu và thiết kế; mã nguồn trong repo này là căn cứ để xác minh tính năng *đã triển khai*.

> **Trạng thái:** Dự án học tập/demo, **chưa được đánh giá an toàn để triển khai công khai**. Xem [các vấn đề bảo mật cần xử lý](docs/security-review.md) và [bảng đối chiếu tài liệu–mã nguồn](docs/repository-alignment.md).

## 1. Chức năng và quy tắc nghiệp vụ

- Đăng nhập JWT; màn hình theo ba vai trò.
- Quản lý tài khoản, nhóm hàng, hàng hóa, nhà cung cấp.
- Tạo/xem/xác nhận phiếu nhập và xuất; theo dõi tồn kho, lịch sử biến động và báo cáo.
- Gemini phân tích tồn kho và tạo đề xuất nhập hàng.
- Quản lý duyệt/từ chối đề xuất; Thủ kho tạo **phiếu nhập nháp** từ đề xuất đã duyệt.
- Multi-Agent Advisor và Single-Agent baseline để so sánh.

**Ràng buộc quan trọng:** AI chỉ phân tích/đề xuất, **không tự tăng hoặc giảm `TonKho`**. Phiếu nháp không thay đổi tồn; xác nhận phiếu mới cập nhật tồn và lịch sử. Quy tắc dự kiến này không thay thế việc kiểm tra các API và transaction trên môi trường thật.

## 2. Công nghệ và cấu trúc

| Thành phần | Triển khai |
|---|---|
| Frontend | React, Vite, Axios |
| Backend | FastAPI, SQLAlchemy, Pydantic |
| Database | MySQL, PyMySQL |
| AI | Gemini API (`google-genai`) |
| Multi-Agent | Orchestrator, Analyst, Database, RAG, Reasoning, Critic, Response |
| RAG | ChromaDB + SentenceTransformer |
| Test | pytest, FastAPI TestClient, mock, MySQL test schema |

```text
backend/                API, models, Gemini, nghiệp vụ kho, tests/
frontend/               React UI
multi_agent/multi_agent/ Multi-Agent, Single-Agent, SQL/RAG tools, tests/
database/               quan_ly_kho_mysql.sql; quanlykho_test.sql
docs/                   requirements, architecture, kiểm thử, bảo mật, benchmark
.agents/skills/         hướng dẫn cho AI hỗ trợ SDLC (không phải module runtime)
scripts/                tiện ích migration lịch sử
```

Kiến trúc: **React → FastAPI → MySQL**; AI Advisor sử dụng SQL Tool và RAG/ChromaDB, Gemini tổng hợp kết quả; luồng Multi-Agent có Critic và retry tối đa hai lần theo cấu hình router. Xem [architecture](docs/architecture.md) và [Multi-Agent](docs/multi-agent-architecture.md).

## 3. Cài đặt và chạy trên Windows (PowerShell)

Cần có MySQL Server, Python phù hợp với `backend/requirements.txt`, Node.js/npm tương thích với `frontend/package.json` và kết nối Internet nếu gọi Gemini thật.

**Bước 1 — Database.** Mở MySQL Workbench và chạy **chỉ trên MySQL local/dành cho demo** file `database/quan_ly_kho_mysql.sql`. Script này khởi tạo schema ứng dụng `quan_ly_kho`; không chạy trên schema có dữ liệu cần giữ nếu chưa kiểm tra nội dung SQL.

**Bước 2 — Backend** (từ thư mục gốc repo):

```powershell
Copy-Item .\backend\.env.example .\backend\.env
cd backend
py -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\python.exe .\bootstrap_admin.py
.\.venv\Scripts\python.exe -m uvicorn main:app --reload
```

**Trước khi chạy:** sửa `backend/.env` cho đúng MySQL local; đặt `JWT_SECRET_KEY` ngẫu nhiên, dài và `GEMINI_API_KEY` hợp lệ. Không commit `.env`; không đưa mật khẩu hoặc API key vào báo cáo, log hay ảnh Terminal. API docs: http://127.0.0.1:8000/docs.

**Cảnh báo bảo mật hiện tại:** `backend/main.py` không tự tạo schema hoặc seed tài khoản. Các API nghiệp vụ yêu cầu JWT ở backend, còn quyền tạo/xác nhận phiếu và thao tác AI được kiểm tra theo role. Frontend tự xóa phiên và về login khi API trả 401 ngoài login; 403 giữ phiên để hiển thị lỗi quyền. Đây không thay thế review production: token hiện vẫn ở `localStorage`, chưa có rate limit, E2E hay pentest. Xem [Security Review](docs/security-review.md).

**Bước 3 — Frontend** (mở Terminal khác, từ thư mục gốc):

```powershell
cd frontend
npm ci
npm run dev
```

Mở http://localhost:5173. `frontend/src/api.js` đang trỏ cố định tới `http://127.0.0.1:8000` nên phải chạy backend trên cổng 8000. Hướng dẫn UI: [frontend/README.md](frontend/README.md).

## 4. API chính

- `POST /auth/login`, `GET /auth/me` — xác thực JWT.
- `/phieu-nhap`, `/phieu-xuat`, `/ton-kho` — nghiệp vụ kho (trạng thái xác thực endpoint: xem mục bảo mật).
- `GET /ai/phan-tich-ton-kho`, `/de-xuat-ai` — phân tích và đề xuất AI.
- `PUT /de-xuat-ai/{id}/duyet`, `.../tu-choi` — chỉ `QuanLy` theo JWT.
- `POST /de-xuat-ai/{id}/tao-phieu-nhap` — chỉ `ThuKho` theo JWT; tạo phiếu **nháp**.
- `POST /multi-agent/advisor` — Multi-Agent.
- `POST /multi-agent/single-agent/advisor` — Single-Agent baseline.

Hai API Advisor yêu cầu Bearer token và body JSON `{"question":"Hàng nào đang dưới mức tồn tối thiểu?"}`.

## 5. Kiểm thử — lệnh đã dùng trên máy Windows

**A. Bộ Unit/API/Agent (45 bài kiểm thử được định nghĩa)**, chạy từ **thư mục gốc**:

```powershell
cd multi_agent
$env:PYTHONPATH = (Get-Location).Path
& "..\backend\.venv\Scripts\python.exe" -X utf8 -m pytest --pyargs multi_agent.tests ..\backend\tests\test_de_xuat_ai_authorization.py ..\backend\tests\test_route_authentication.py --import-mode=importlib -q
```

Cách gọi trên giải quyết trường hợp package `multi_agent/multi_agent` bị nhầm với thư mục ngoài khi chạy pytest từ root.

**B. Bộ tích hợp MySQL thật (12 bài kiểm thử được định nghĩa)** — Terminal vẫn ở `multi_agent`:

```powershell
& "..\backend\.venv\Scripts\python.exe" -X utf8 -m pytest ..\backend\tests\test_mysql_inventory_integration.py --run-mysql-integration -s -q
```

- Dùng **chỉ** schema `quanlykho_test` và tài khoản `qlk_test_user` (`database/quanlykho_test.sql`); script hỏi mật khẩu bằng `getpass`.
- **Không nhập mật khẩu nếu Terminal cảnh báo rằng ký tự sẽ hiển thị**. Dùng PowerShell thông thường và không chụp thông tin bí mật.
- Test tạo/xóa dữ liệu mẫu của chính nó. Không chạy trên `quan_ly_kho`, không thay tên schema/user để vượt guard.

**Kết quả regression Windows (28/10/2026):** **45/45** Unit/API/Agent PASS, `IT-011` chạy riêng PASS, **12/12** MySQL integration PASS, tổng **57/57** automated tests PASS. `npm run lint` exit 0 với 10 warning React cũ; `npm run build` và `git diff --check` exit 0. 77 test case trong báo cáo là bộ chức năng/manual riêng, không cộng gộp với 57 automated tests. Chi tiết: [test-report](docs/test-report.md).

## 6. Benchmark Single-Agent và Multi-Agent

Chạy tại thư mục `multi_agent`:

```powershell
python -m multi_agent.benchmark
```

Kết quả ghi tại `multi_agent/multi_agent_benchmark.json`. Báo cáo đã ghi nhận một lượt đo 10 câu hỏi với Test Oracle 10/10 ở cả hai kiến trúc; Single-Agent trung bình 2732,84 ms / 1 LLM call mỗi câu; Multi-Agent 1488,47 ms / 3 LLM calls mỗi câu. **Không suy ra Multi-Agent luôn nhanh hơn** từ một lượt đo. Xem [benchmark guide](docs/benchmark-guide.md) và [comparison](docs/multi-agent-comparison.md).

## 7. AI Skills và quy trình phát triển

`.agents/skills/` là bộ hướng dẫn cho AI hỗ trợ yêu cầu, kiến trúc, triển khai, kiểm thử, bảo mật và viết tài liệu — **không phải công cụ tự động được phần mềm chạy khi người dùng mở web**. Danh mục, cách dùng và giới hạn có tại [Skills README](.agents/skills/README.md).

## 8. Tài liệu và giới hạn cần lưu ý

- [Requirements](docs/requirements.md) · [ERD logic](docs/erd.md) · [Database design](docs/database-design.md).
- [Deployment](docs/deployment.md) · [Test plan](docs/test-plan.md) · [Test report](docs/test-report.md).
- [Security review](docs/security-review.md) · [Đối chiếu báo cáo/source](docs/repository-alignment.md).
- Database đã khai báo **12 bảng** trong SQL; sơ đồ thiết kế có thể nêu thành phần dự kiến chưa tồn tại vật lý (ví dụ `BAO_CAO_AI`). Không trình bày các phần dự kiến như đã chạy.
- Chưa có bằng chứng E2E/frontend CI cho mọi chức năng, test Gemini thật liên tục, kiểm thử concurrency thực tế và rà bảo mật toàn diện.

**Nguyên tắc:** trước khi demo, kiểm tra trên máy nhóm, dùng dữ liệu thử, chỉ báo kết quả đã thực sự quan sát và không chia sẻ secrets.
