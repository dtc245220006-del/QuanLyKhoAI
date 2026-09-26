# Acceptance Criteria

## AC-001 Đăng nhập
Given tài khoản hợp lệ
When nhập đúng username/password
Then nhận JWT và vào dashboard.

## AC-002 Phân quyền tài khoản
Given user không phải admin
When gọi API quản lý tài khoản
Then backend trả 403.

## AC-003 Nhập kho
Given phiếu nhập ở trạng thái Nhap
When xác nhận
Then TonKho tăng và LichSuKho có giao dịch Nhap.

## AC-004 Xuất kho
Given tồn kho đủ số lượng
When xác nhận phiếu xuất
Then TonKho giảm và LichSuKho có giao dịch Xuat.

## AC-005 AI phân tích
Given TonKho và HangHoa có dữ liệu
When gọi phân tích
Then AI trả phân tích dựa trên dữ liệu được truy xuất và không tự thay đổi kho.

## AC-006 Đề xuất AI
Given tồn kho dưới mức tối thiểu
When Quản lý tạo đề xuất
Then DeXuatAI và ChiTietDeXuatAI được tạo ở trạng thái ChoDuyet.

## AC-007 Multi-Agent
Given câu hỏi về kho
When gửi tới `/multi-agent/advisor`
Then workflow phải có Analyst, Database, RAG, Reasoning, Critic và Response dưới sự điều phối của Orchestrator.

## AC-008 Retry
Given Critic trả REJECT
When còn lượt retry
Then Orchestrator chạy lại Reasoning/verification và ghi log retry.
