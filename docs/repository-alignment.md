# Đối chiếu mã nguồn ↔ README ↔ báo cáo/slide — QuanLyKhoAI

Bảng này giúp nhóm trình bày **đúng những gì đã triển khai**, không tự điền bằng suy đoán. Căn cứ code là GitHub `main` ở thời điểm rà soát 28/10/2026; báo cáo/slide là tài liệu môn học nhóm đã hoàn thiện **ngoài repository**. Số trang Word/PDF có thể thay đổi sau khi chỉnh layout.

## Theo 7 chương báo cáo

| Chương | Nội dung quan trọng | Mã nguồn / tài liệu đối chiếu | Trạng thái và lưu ý |
|---|---|---|---|
| I — Tổng quan | Lý do, mục tiêu, phạm vi một kho, 3 vai trò | `README.md`, `docs/project-context.md` | Đúng `QuanLy`, `ThuKho`, `KeToan`; không tự thêm vai trò |
| II — Kế hoạch | Agile/Scrum, sprint, phân công, DOD | Báo cáo môn học | Thông tin quản trị dự án, không phải tính năng runtime; chưa có artefact lịch sprint đầy đủ trong repo |
| III — Yêu cầu | FR/NFR, chức năng kho và AI | `docs/requirements.md`, `docs/user-stories.md`, `docs/acceptance-criteria.md` | Requirement là **mong đợi**, cần kiểm tra từng yêu cầu với implementation |
| IV — Use Case | Tài khoản, nhập/xuất, tồn, đề xuất AI | `backend/*.py`, `frontend/src/pages/` | Một số API nghiệp vụ **chưa bảo vệ JWT/role** như mô tả lý tưởng; xem security review |
| V — Phân tích/thiết kế | Use Case, Activity, Sequence, quy trình | Hình gốc trong báo cáo; routes và logic Python | Sơ đồ là thiết kế/đặc tả; không coi tất cả luồng trong hình đã có automated test |
| VI — Kiến trúc/CSDL/UI | React–FastAPI–MySQL, 7 Agent, ERD, màn hình | `docs/architecture.md`, `docs/erd.md`, `backend/models.py`, `database/quan_ly_kho_mysql.sql`, `frontend/src/` | **12 bảng hiện diện trong schema SQL**. Bảng `BAO_CAO_AI` nếu có trong bản thiết kế là **dự kiến**, không có trong file SQL |
| VII — Kiểm thử | Functional test, AI-assisted testing, test case, benchmark | `docs/test-report.md`, `backend/tests/`, `multi_agent/multi_agent/tests/`, `multi_agent/multi_agent_benchmark.json` | Báo cáo có **77 functional test case** (được trình bày riêng); repo có **41 automated tests** (20 Agent + 15 API + 6 MySQL) đã được nhóm ghi nhận PASS local; không đánh đồng hai bộ |

## Sơ đồ và AI — các ràng buộc cần nói nhất quán

1. Có **bảy agent** trong Multi-Agent: Orchestrator, Analyst, Database, RAG, Reasoning, Critic, Response. Công cụ đi kèm: SQL Tool (MySQL), vector search (ChromaDB + SentenceTransformer), Gemini service. Single-Agent là baseline để so sánh.
2. **Không nói AI tự nhập hàng hoặc tự cập nhật tồn kho.** AI trả phân tích/đề xuất → Quản lý phê duyệt → Thủ kho tạo phiếu nhập nháp → xác nhận phiếu → nghiệp vụ mới tăng tồn và ghi lịch sử.
3. MySQL ứng dụng: `quan_ly_kho`. MySQL integration test: `quanlykho_test` với `qlk_test_user`. Test không kết nối database ứng dụng.
4. Schema SQL và ORM có một số `logical FK` là cột `Integer` thay vì constraint `FOREIGN KEY` vật lý. Diễn giải ERD quan hệ logic, không khẳng định mọi FK đã enforce tại DB.
5. Backend và multi-agent có Gemini service riêng: `backend/gemini_service.py` đặt model mặc định trong code, `multi_agent/.../gemini_service.py` cho phép `GEMINI_MODEL` qua env; các benchmark phải ghi rõ model/config thực tế.
6. Kết quả một lần benchmark 10/10 theo **Test Oracle**, không chứng minh không hallucinate trong mọi câu hỏi hoặc Multi-Agent luôn nhanh hơn Single-Agent.

## Những khoảng cách chưa được đóng

- **Bảo mật:** JWT/role thiếu ở một số routes; POST tạo đề xuất AI nhận `ma_tai_khoan` từ request; admin default yếu. Không nên tuyên bố hoàn thiện bảo mật.
- **Transaction:** rollback nhập đã có test tái hiện; rollback giữa transaction **xuất kho** chưa có test inject lỗi.
- **Test:** 35 + 6 PASS là output ghi nhận thủ công, không có GitHub Actions CI trong repo ở thời điểm rà soát; thiếu E2E frontend và test Gemini thật.
- **Tài liệu:** hình gốc và DOCX/PDF/Canva slide chưa được lưu trong repository. Chỉ đối chiếu được nội dung code/dữ liệu và các tệp `docs/`, không xác nhận mã nguồn nào cũng tái tạo hoàn toàn hình/bảng trong báo cáo.
- **Khởi tạo:** `backend/main.py` gọi `create_all` và tạo admin khi import, cần cô lập trước khi thử nghiệm/migration.
- **Secrets:** file `.env`, token và API key tuyệt đối không đưa vào Git. Nếu từng lộ, cần đổi/thu hồi.

## Checklist trước khi thuyết trình hoặc phát hành

- [ ] Bản GitHub, README, sơ đồ, demo dùng đúng tên vai trò và schema.
- [ ] Thực thi các lệnh theo [README](../README.md), lưu output thật, không dùng số PASS giả định.
- [ ] Không public port/backend với admin mặc định hoặc routes chưa bảo vệ.
- [ ] Kiểm tra `npm run build` và `npm run lint` trên máy demo.
- [ ] Demo được 1 luồng nhập, 1 luồng xuất, 1 luồng AI phê duyệt.
- [ ] Giải thích rõ **77 test case trình bày trong báo cáo** khác **41 test tự động trong repo**.
- [ ] Mọi ảnh, slide và số liệu benchmark có nguồn/điều kiện đo, không che giấu phần chưa kiểm tra.
