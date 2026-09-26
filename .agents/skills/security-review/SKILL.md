---
name: security-review
description: Kiểm tra bảo mật hệ thống Quản lý Kho tích hợp AI.
---

# Security Review Skill — QuanLyKhoAI

## Checklist
- Authentication
- Authorization theo role
- SQL Injection
- XSS
- CSRF phù hợp kiến trúc API
- Password storage
- Secrets và `.env`
- Gemini API key
- Input validation
- Dependency vulnerabilities
- Information leakage
- IDOR/BOLA đối với endpoint tài khoản, phiếu và đề xuất
- Không cho AI trực tiếp ghi dữ liệu kho
Output: `docs/security-review.md`.
