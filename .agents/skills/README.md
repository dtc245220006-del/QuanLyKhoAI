# AI-Augmented SDLC Skills — QuanLyKhoAI

Các file `SKILL.md` dưới đây hướng dẫn **công cụ AI hỗ trợ phát triển/kiểm tra dự án**, không phải các Agent runtime của web và **không tự động chạy test** chỉ vì có mặt trong repository.

## Bắt đầu ở đâu

1. Đọc [ngữ cảnh dự án](../../docs/project-context.md), [requirements](../../docs/requirements.md), [architecture](../../docs/architecture.md), [database design](../../docs/database-design.md) và [đối chiếu source–báo cáo](../../docs/repository-alignment.md).
2. Đọc file thực tế trước khi nhận xét/tạo code. Không thay project kho thành ví dụ Product/Category/Laptop; dùng `User`, `NhomHang`, `HangHoa`, `TonKho` và các entity hiện có.
3. Với nhiệm vụ tác động đến dữ liệu: xác định rõ **schema ứng dụng `quan_ly_kho`** và **schema test `quanlykho_test`**, tuyệt đối không tự chọn fallback DB.
4. Mỗi task phải báo kết quả cụ thể: file đã đọc/sửa, kiểm thử thực sự chạy được, vấn đề chưa giải quyết, thao tác cần con người xác nhận. Không tuyên bố PASS nếu chưa thấy output.

## Danh mục

| Skill | Mục đích |
|---|---|
| [requirements-analysis](requirements-analysis/SKILL.md) | FR/NFR, user story, acceptance criteria |
| [architecture-design](architecture-design/SKILL.md) | Kiến trúc React–FastAPI–MySQL và ranh giới AI |
| [database-design](database-design/SKILL.md) | ERD logic và schema MySQL 12 bảng |
| [implementation](implementation/SKILL.md) | Thực thi nghiệp vụ giữ nguyên yêu cầu |
| [code-review](code-review/SKILL.md) | Đánh giá correctness, security và technical debt |
| [security-review](security-review/SKILL.md) | JWT, role, secrets, IDOR và transaction |
| [testing](testing/SKILL.md) | 45 Unit/API + 12 MySQL Integration, mock và test oracle |
| [documentation](documentation/SKILL.md) | Đồng nhất docs, README, báo cáo, bằng chứng |
| [context-builder](context-builder/SKILL.md) | Context kho dựa trên dữ liệu thật |
| [product-retrieval](product-retrieval/SKILL.md) | Truy xuất `HangHoa`/`TonKho` qua SQL an toàn |
| [question-analysis](question-analysis/SKILL.md) | Phân tích intent câu hỏi tư vấn kho |
| [rag-prompt](rag-prompt/SKILL.md) | Grounding, giới hạn hallucination |
| [release-readiness](release-readiness/SKILL.md) | Kiểm tra chéo code–docs–demo–test trước khi nộp |

## Thứ tự dùng gợi ý

`requirements-analysis → architecture-design → database-design → implementation → code-review/security-review → testing → documentation → release-readiness`.

Với module AI, lồng thêm `question-analysis → product-retrieval/context-builder → rag-prompt`. Đây là **workflow làm việc**, không phải mô tả tuyến gọi runtime của 7 Agent; tuyến runtime đọc [multi-agent-architecture](../../docs/multi-agent-architecture.md).

### Quy tắc bất biến

- AI không trực tiếp xác nhận phiếu, ghi tồn hoặc duyệt đề xuất.
- Không đưa mật khẩu, API key, JWT, URL MySQL chứa mật khẩu vào Git/prompt/log/screenshot.
- Không xóa assertion khi test lỗi; cần phân tích và sửa source có kiểm thử hồi quy.
- Không tự gộp 77 test case của báo cáo thành 57 automated test của repository.
- Nếu cần sửa security/business logic, tạo test trước; không sửa code chỉ để khớp một sơ đồ chưa xác minh.

Xem thêm [Test Report](../../docs/test-report.md) và [Security Review](../../docs/security-review.md).
