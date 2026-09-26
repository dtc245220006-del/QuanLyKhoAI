---
name: product-retrieval
description: Truy xuất dữ liệu có cấu trúc cho AI từ database của QuanLyKhoAI.
---

# Product/Inventory Retrieval Skill — QuanLyKhoAI

## Quy tắc
- Trong project này, "product" được hiểu theo dữ liệu HangHoa/TonKho nếu module AI cần truy xuất.
- Dùng parameterized query.
- Không lấy toàn bộ database khi không cần.
- Không gửi secrets cho Gemini.
- Nếu không có kết quả, trả empty result thay vì tự bịa.
