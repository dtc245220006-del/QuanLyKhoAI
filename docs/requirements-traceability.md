# Requirements Traceability Matrix

| Requirement | Implementation / Artifact | Test |
|---|---|---|
| FR-001 Đăng nhập | `backend/auth.py`, Login.jsx | Manual / API login |
| FR-002 Phân quyền | `auth.py`, `tai_khoan.py` | TC authorization |
| FR-006 Phiếu nhập | `phieu_nhap.py` | Inventory tests |
| FR-007 Phiếu xuất | `phieu_xuat.py` | Inventory tests |
| FR-008 Tồn kho | `ton_kho.py` | Import/export tests |
| FR-011 AI phân tích | `ai_controller.py`, `gemini_service.py` | AI analysis test |
| FR-012-014 Đề xuất AI | `de_xuat_ai.py` | Proposal tests |
| FR-015 Multi-Agent | `multi_agent/multi_agent/` | MA-01..MA-10 |
| FR-016 Retry + logging | `orchestrator_agent.py`, `message_bus.py` | MA-08..MA-10 |
