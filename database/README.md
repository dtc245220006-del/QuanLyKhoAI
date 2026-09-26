# Chuyển QuanLyKhoAI sang MySQL

1. Cài MySQL Server.
2. Chạy `quan_ly_kho_mysql.sql`.
3. Tạo `backend/.env` từ `.env.example`.
4. Điền `DB_USER`, `DB_PASSWORD`, `DB_NAME=quan_ly_kho`, `JWT_SECRET_KEY`, `GEMINI_API_KEY`.
5. Cài `backend/requirements.txt`.
6. Khởi động backend và kiểm tra `/docs`.

## Dữ liệu cũ từ PostgreSQL
Schema mới không tự chuyển dữ liệu cũ. Nếu cần giữ dữ liệu PostgreSQL hiện tại, hãy xuất dữ liệu từ PostgreSQL và nhập vào MySQL theo thứ tự bảng/khóa hoặc dùng script migration riêng. Không đưa mật khẩu/API key vào Git.
