# Deployment / Run Guide

## Backend
```powershell
cd backend
python -m venv .venv
.venv\\Scripts\\activate
pip install -r requirements.txt
uvicorn main:app --reload
```

## Database
Chạy `database/quan_ly_kho_mysql.sql`, sau đó cấu hình `backend/.env`.

## Frontend
```powershell
cd frontend
npm install
npm run dev
```

## Multi-Agent endpoint
`POST http://127.0.0.1:8000/multi-agent/advisor`

Câu hỏi mẫu:
`Hàng nào đang dưới mức tồn tối thiểu?`
