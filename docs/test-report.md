# Test Report

## Automated tests
Project có bộ unit tests Multi-Agent tại `multi_agent/multi_agent/tests/`.

## 10 test case bắt buộc
1. Analyst parse intent
2. SQL Tool parameterized query
3. SQL Tool lọc hàng
4. RAG trả knowledge
5. Reasoning tạo answer/claims
6. Critic APPROVED khi claim đúng
7. Critic REJECT khi claim sai
8. Orchestrator retry khi reject
9. Orchestrator stop khi approved
10. Orchestrator trả lỗi giới hạn retry

## Kết quả
Các số liệu chạy thực tế phải được ghi sau khi chạy test trên máy triển khai. Tài liệu này không bịa kết quả runtime.
