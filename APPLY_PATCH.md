# Bộ bổ sung cho QuanLyKhoAI

Bộ này được dựng theo source hiện có trên repo `dtc245220006-del/QuanLyKhoAI` và 2 tài liệu bài thực hành mà bạn đã cung cấp.

## Có gì trong bộ này

### Backend / MySQL
- `backend/database.py`: chuyển connection SQLAlchemy sang MySQL qua `.env`.
- `backend/auth.py`: JWT secret đọc từ environment.
- `backend/tai_khoan.py`: kiểm tra quyền admin bằng JWT ở backend.
- `backend/main.py`: tích hợp router Multi-Agent.
- `backend/requirements.txt`
- `backend/.env.example`

### Multi-Agent
- 7 Agent: Orchestrator, Analyst, Database, RAG, Reasoning, Critic, Response.
- Structured message.
- SQL Tool cho bảng kho trên MySQL.
- Vector Search Tool + ChromaDB + SentenceTransformer.
- Critic + retry tối đa 2 lần.
- Logging workflow.
- API `POST /multi-agent/advisor`.
- 12 automated tests.
- Benchmark helper cho Single-Agent.

### Frontend
- `MultiAgent.jsx` + CSS.
- `App.jsx` route `/multi-agent`.
- `Layout.jsx` thêm menu Multi-Agent và sửa điều kiện admin.

### Database / docs
- `database/quan_ly_kho_mysql.sql`.
- Hướng dẫn migration PostgreSQL → MySQL.
- Requirements, architecture, database design, test plan/report, code review, security review, deployment và Multi-Agent architecture/comparison.

## Cách áp dụng
1. Giải nén bộ này vào thư mục gốc `QuanLyKhoAI` và cho phép overwrite các file được trùng tên.
2. Tạo `backend/.env` từ `backend/.env.example`.
3. Chạy `database/quan_ly_kho_mysql.sql` trên MySQL.
4. Nếu cần giữ dữ liệu cũ từ PostgreSQL, dùng `scripts/migrate_pg_to_mysql.py` trước khi demo.
5. `cd backend` → kích hoạt venv → `pip install -r requirements.txt`.
6. `uvicorn main:app --reload`.
7. `cd frontend` → `npm install` → `npm run dev`.
8. Đăng nhập rồi mở `/multi-agent`.

## Quan trọng
- Không commit `backend/.env`.
- Không chép API key thật vào GitHub.
- Bộ này không tự chạy migration DB và không thể xác nhận kết nối MySQL/Gemini của máy bạn từ đây.
- Trước khi demo cần chạy test và kiểm tra 1 vòng end-to-end trên máy local.
