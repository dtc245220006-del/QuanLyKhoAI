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

## Single-Agent baseline

Repository có baseline Single-Agent để phục vụ yêu cầu so sánh kiến trúc:

Question → SQL Tool + Vector Search Tool → Gemini → Answer

API:
- POST /multi-agent/advisor — Multi-Agent
- POST /multi-agent/single-agent/advisor — Single-Agent

## Benchmark

Từ thư mục gốc:

    cd multi_agent
    python -m multi_agent.benchmark

Kết quả:
multi_agent/multi_agent_benchmark.json

Tài liệu:
- docs/benchmark-guide.md
- docs/multi-agent-comparison.md
- docs/test-plan.md
- docs/test-report.md

## Cấu trúc

.agents/skills/      AI-Augmented SDLC skills
docs/                requirements, architecture, ERD, testing, benchmark
backend/              FastAPI + MySQL
frontend/             React
multi_agent/         Multi-Agent + Single-Agent benchmark
database/             MySQL schema

## Secrets

Không commit backend/.env hoặc API key.
