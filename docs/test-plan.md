# Test Plan

## Phạm vi
Authentication, CRUD kho, nhập/xuất, tồn kho, báo cáo, AI, Multi-Agent.

## Test levels
1. Unit test: AgentMessage, SQL Tool query builder, Critic, Orchestrator với mock.
2. Integration test: FastAPI endpoint + MySQL trên máy chạy dự án.
3. Manual UI test: React frontend.
4. AI validation: cùng tập câu hỏi dùng cho Single-Agent và Multi-Agent.

## Exit criteria
- Không còn test case Critical/High chưa xử lý.
- Core API và UI chạy được.
- ≥ 10 Multi-Agent test cases.
- Có log workflow.
- Có bảng đo Single-Agent vs Multi-Agent.
