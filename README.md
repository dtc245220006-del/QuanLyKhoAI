# QuanLyKhoAI

Hệ thống quản lý kho tích hợp AI.

## Stack
- Frontend: React + Vite
- Backend: FastAPI + SQLAlchemy
- Database: MySQL
- AI: Gemini API
- Vector DB: ChromaDB
- Embedding: SentenceTransformer

## Chức năng
- Đăng nhập và phân quyền
- Nhóm hàng, hàng hóa, nhà cung cấp
- Phiếu nhập/xuất
- Tồn kho và lịch sử kho
- Thống kê/báo cáo
- AI phân tích tồn kho
- Đề xuất nhập hàng bằng AI
- Multi-Agent AI

## Multi-Agent
Orchestrator → Analyst → Database/SQL → RAG/Vector → Reasoning → Critic → Retry → Response.

## Cấu trúc
```text
.agents/skills/      AI-Augmented SDLC skills
docs/                requirements, architecture, ERD, testing, review
backend/             FastAPI + MySQL
frontend/            React
multi_agent/         Multi-Agent implementation
database/            MySQL schema
```

## Secrets
Không commit `backend/.env` hoặc API key.

## Bộ bổ sung
Xem `APPLY_PATCH.md` để áp dụng các phần MySQL, Multi-Agent, UI và tài liệu.
