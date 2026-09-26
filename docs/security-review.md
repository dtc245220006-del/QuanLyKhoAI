# Security Review Report

| Hạng mục | Xử lý |
|---|---|
| Authentication | JWT |
| Authorization | kiểm tra role ở backend |
| Admin account | JWT + username admin |
| Password | PBKDF2-SHA256 |
| SQL Injection | parameterized query trong SQL Tool |
| Secrets | `.env`, không commit API key |
| Gemini key | lấy từ env |
| Input validation | Pydantic + kiểm tra nghiệp vụ |
| Information leakage | không chủ động trả stack trace cho UI |
| AI mutation | AI không trực tiếp ghi kho |
