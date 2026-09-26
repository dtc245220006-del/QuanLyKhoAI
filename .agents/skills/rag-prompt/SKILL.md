---
name: rag-prompt
description: Xây prompt grounded cho Gemini trong hệ thống Quản lý Kho.
---

# RAG Prompt Skill — QuanLyKhoAI

## Quy tắc
- Chỉ sử dụng context được cung cấp.
- Không bịa hàng hóa, tồn kho, giá hoặc đề xuất.
- Nếu dữ liệu không đủ, phải nói rõ không đủ dữ liệu.
- Không để API key xuất hiện trong prompt/log/output.
