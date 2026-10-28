# Deployment / Run Guide — QuanLyKhoAI

> Dành cho **demo local Windows**, chưa phải hướng dẫn triển khai production. Đọc [Security Review](security-review.md) trước khi đưa ra mạng.

## 1. MySQL local

- Khởi động MySQL Server trên `localhost:3306`.
- Kiểm tra file `database/quan_ly_kho_mysql.sql` rồi chạy bằng MySQL Workbench để có schema **`quan_ly_kho`**. Không chạy lại bừa bãi trên database có dữ liệu cần giữ.
- Tạo tài khoản DB ít quyền thích hợp cho ứng dụng thay vì dùng `root` trong môi trường chia sẻ.

## 2. Backend FastAPI

Tại **root repository** trên PowerShell:

```powershell
Copy-Item .\backend\.env.example .\backend\.env
cd backend
py -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\python.exe -m uvicorn main:app --reload
```

Trước khi khởi động, sửa `backend/.env` với `DB_HOST`, `DB_PORT`, `DB_USER`, `DB_PASSWORD`, `DB_NAME=quan_ly_kho`, `JWT_SECRET_KEY`, `GEMINI_API_KEY`. Không commit `.env`; dùng JWT secret đủ mạnh. Backend API: http://127.0.0.1:8000/docs.

`backend/main.py` không tạo schema hay seed tài khoản khi import. Khởi tạo schema bằng script SQL đã review, sau đó tạo tài khoản Quản lý một lần bằng lệnh sau; mật khẩu được nhập kín và không có mặc định:

```powershell
.\.venv\Scripts\python.exe .\bootstrap_admin.py
```

## 3. Frontend React/Vite

Mở Terminal khác từ root repository:

```powershell
cd frontend
npm ci
npm run dev
```

Truy cập http://localhost:5173. Code `frontend/src/api.js` trỏ cố định `http://127.0.0.1:8000`, nên backend phải đúng địa chỉ; CORS ở `backend/main.py` cho phép `localhost:5173` và `127.0.0.1:5173`.

Regression Windows 28/10/2026: `npm run lint` exit 0 với 10 warning React đã biết; `npm run build` exit 0. Kiểm tra lại trên máy demo sau khi đổi môi trường hoặc dependency.

## 4. AI và Multi-Agent

- Model Gemini cho phân tích/đề xuất cần `GEMINI_API_KEY`.
- Multi-Agent router:
  - `POST /multi-agent/advisor`
  - `POST /multi-agent/single-agent/advisor`
- Body JSON `{"question":"Hàng nào đang dưới mức tồn tối thiểu?"}`; hai route yêu cầu Bearer JWT.
- SQL Tool đọc MySQL `quan_ly_kho`; Vector Service dùng ChromaDB và SentenceTransformer. Lần đầu tạo embedding có thể chậm và cần tài nguyên.

## 5. Chạy tests

Tham khảo [README](../README.md) và [Test Report](test-report.md) để có lệnh chính xác: 45 Unit/API/Agent và 12 MySQL integration; **không** chạy integration trên DB ứng dụng.

## 6. Demo và các giới hạn

1. Đăng nhập trên máy cô lập.
2. Mở hàng hóa, nhập nháp → xác nhận → kiểm tra tồn và lịch sử.
3. Xuất nháp → xác nhận → kiểm tra tồn; thử trường hợp xuất vượt tồn.
4. Quản lý duyệt đề xuất AI → Thủ kho tạo phiếu nhập nháp; AI không tự tăng tồn.
5. Chạy Multi-Agent và giải thích Analyst/SQL/RAG/Critic/retry.

Đây là checklist demo, **không bảo đảm mỗi bước đã được test E2E**. Rủi ro token storage, rate limit, concurrency thực tế và E2E còn được ghi ở [Security Review](security-review.md).
