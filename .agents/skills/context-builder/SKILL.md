---
name: context-builder
description: Xây context cho AI từ kết quả HangHoa/TonKho thực tế, có nguồn và giới hạn độ dài; không tự thay đổi dữ liệu kho.
---

# Context Builder Skill — QuanLyKhoAI

## Input

Đọc `docs/project-context.md`, `backend/gemini_service.py` và `multi_agent/multi_agent/services/vector_service.py`. Dữ liệu cấu trúc bắt buộc lấy từ truy vấn thực tế: `ma_hang`, `ten_hang`, `so_luong_ton`, `ton_toi_thieu`; có thể bổ sung `ten_nhom`, giá nếu nguồn cung cấp.

## Thực hiện

1. Giữ nguyên id, tên, giá và số lượng của hàng hóa trong nguồn.
2. Lọc đúng tập dữ liệu phù hợp câu hỏi; giữ giới hạn bản ghi và chỉ chứa trường cần thiết.
3. Gắn nguồn: **SQL live data** cho tồn kho; **RAG policy/knowledge** cho quy tắc giải thích. Không coi các câu văn trong ChromaDB là số tồn kho thật.
4. Nếu không có dữ liệu, trả trạng thái `empty` cùng câu thông báo, không tự bịa dữ liệu.
5. Không đưa mật khẩu DB, API key, JWT, thông tin cá nhân không cần thiết vào context.
6. Không cập nhật `TonKho`, `LichSuKho`, trạng thái phiếu hoặc đề xuất trong bước dựng context.

## Output / test oracle

Xuất `{question, sql_rows, knowledge_chunks, constraints, source_labels}` hoặc cấu trúc tương đương đang dùng trong code; các field phải tồn tại trong output thực tế, không tự hứa format mới đã được triển khai. Đối chiếu sample context với SQL và test Agent tương ứng. Nếu Gemini bị lỗi, fallback phải bảo toàn số liệu nguồn và ghi rõ giới hạn.
