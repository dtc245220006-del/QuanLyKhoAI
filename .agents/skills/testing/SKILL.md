---
name: testing
description: Kiểm thử hệ thống Quản lý Kho tích hợp AI bằng cách phân tích requirements, xây dựng test scenario, sinh test case, chuyển test case thành automated tests trong code, thực thi test, phân tích failure và kiểm tra requirements coverage.
---

# Testing Skill - QuanLyKhoAI

## 1. Mục tiêu

Skill này được sử dụng để:

1. Phân tích requirements và acceptance criteria.
2. Xây dựng Test Scenario.
3. Xây dựng Test Case.
4. Chuyển Test Case thành Automated Test trong source code.
5. Chạy automated tests.
6. Thu thập kết quả thực tế.
7. Phân tích test failure.
8. Xác định defect.
9. Kiểm tra requirements coverage.
10. Sử dụng AI để hỗ trợ sinh test và phân tích kết quả.
11. Human verification đối với các kết quả quan trọng.

Không sửa test chỉ để làm test pass.

---

## 2. Input

Đọc trước khi kiểm thử:

- docs/requirements.md
- docs/user-stories.md
- docs/acceptance-criteria.md
- docs/architecture.md
- docs/database-design.md

Sau đó đọc source code thực tế:

### Backend

- backend/main.py
- backend/auth.py
- backend/models.py
- backend/*.py

### Frontend

- frontend/src/App.jsx
- frontend/src/components/*
- frontend/src/pages/*

Không được giả định chức năng chưa tồn tại.

---

## 3. Quy trình kiểm thử

Requirements
↓
Test Scenario
↓
Test Case
↓
Automated Test
↓
Execution
↓
Result
↓
AI Analysis
↓
Human Verification
↓
Defect Report

---

# 4. Phân loại Test

## 4.1 Functional Test

Kiểm thử:

- Đăng nhập
- Đăng xuất
- Quản lý tài khoản
- Nhóm hàng
- Hàng hóa
- Nhà cung cấp
- Nhập kho
- Xuất kho
- Tồn kho
- Lịch sử kho
- Báo cáo

---

## 4.2 Authorization Test

Kiểm thử 3 role:

- QuanLy
- ThuKho
- KeToan

Kiểm tra:

- endpoint có yêu cầu đăng nhập không;
- role có được phép truy cập không;
- role không có quyền có bị từ chối không;
- không được chỉ dựa vào việc ẩn menu ở frontend.

---

## 4.3 Negative Test

Luôn sinh test cho:

- dữ liệu rỗng;
- dữ liệu sai kiểu;
- số lượng = 0;
- số lượng âm;
- giá trị âm;
- username trùng;
- barcode trùng;
- mã không tồn tại;
- token không hợp lệ;
- token hết hạn;
- truy cập sai role.

---

## 4.4 Boundary Test

Ưu tiên:

- 0;
- 1;
- giá trị tối thiểu;
- giá trị tối đa;
- chuỗi quá dài;
- số lượng lớn;
- danh sách rỗng;
- một phần tử;
- nhiều phần tử.

---

# 5. Automated Test trong code

Mỗi Test Case quan trọng phải được chuyển thành Automated Test.

Backend ưu tiên sử dụng:

- pytest
- FastAPI TestClient
- mock
- fixture

Không gọi Gemini API thật trong Unit Test nếu không cần thiết.

---

# 6. Unit Test

Kiểm thử từng module hoặc function độc lập.

Ví dụ:

- xác thực username/password;
- kiểm tra dữ liệu đầu vào;
- kiểm tra quyền;
- tính tổng tiền;
- tính số lượng tồn;
- kiểm tra điều kiện xuất kho;
- xử lý dữ liệu AI.

Unit Test phải độc lập và dễ lặp lại.

---

# 7. Integration Test

Kiểm thử luồng hoàn chỉnh:

Login
→ Access Token
→ API
→ Database
→ Response

Ví dụ:

Tạo phiếu nhập
→ thêm chi tiết
→ xác nhận
→ cập nhật tồn kho
→ ghi lịch sử kho.

Ví dụ:

Tạo phiếu xuất
→ kiểm tra tồn
→ xác nhận
→ giảm tồn
→ ghi lịch sử.

---

# 8. Database Oracle

Khi kiểm thử nghiệp vụ kho, expected result phải được đối chiếu với database.

Ví dụ:

Tồn trước = 80
Nhập = 20
Xuất = 10

Expected:

80 + 20 - 10 = 90

Automated Test phải kiểm tra giá trị thực tế trong database.

Không chỉ kiểm tra HTTP status = 200.

---

# 9. AI-Assisted Testing

AI được sử dụng ở 4 bước:

## 9.1 Test Generation

AI đọc requirements và sinh:

- positive cases;
- negative cases;
- edge cases;
- security cases;
- AI-specific cases.

## 9.2 Test Code Generation

AI chuyển Test Case thành:

- pytest;
- integration test;
- API test;
- frontend test nếu có framework phù hợp.

## 9.3 Test Analysis

AI đọc:

- expected result;
- actual result;
- HTTP status;
- response body;
- exception;
- database state;
- logs.

AI xác định:

- PASS;
- FAIL;
- suspected defect;
- possible root cause.

## 9.4 Coverage Analysis

AI đối chiếu:

Requirement
→ Test Case
→ Test Code
→ Test Result

Requirement không có test phải được đánh dấu.

---

# 10. Kiểm thử chức năng AI

Phải kiểm thử tối thiểu:

### AI-01
Gemini phân tích tồn kho có dữ liệu.

Expected:

- nhận được response;
- response dựa trên dữ liệu được cung cấp;
- không crash.

### AI-02
Không có dữ liệu tồn kho.

Expected:

- thông báo không có dữ liệu;
- không bịa dữ liệu;
- không crash.

### AI-03
Gemini API lỗi / timeout / 503.

Expected:

- hệ thống xử lý lỗi;
- không làm crash backend;
- không làm hỏng dữ liệu kho.

### AI-04
AI tạo đề xuất nhập hàng.

Expected:

- tạo DeXuatAI;
- trạng thái ban đầu = ChoDuyet;
- có chi tiết mặt hàng;
- có số lượng đề xuất.

### AI-05
AI không tự thay đổi tồn kho.

Before:

stock = X

Run AI analysis / create proposal.

After:

stock = X

Nếu stock thay đổi trước khi phiếu nhập được xác nhận → FAIL.

### AI-06
Đề xuất AI phải qua phê duyệt.

ChoDuyet
→ DaDuyet
hoặc
→ TuChoi

Không cho AI tự chuyển trạng thái mà không qua nghiệp vụ được phép.

### AI-07
Chỉ đề xuất đã duyệt mới được tạo phiếu nhập từ AI.

### AI-08
Phiếu nhập được tạo từ đề xuất AI phải là phiếu nháp.

Tồn kho chưa được tăng cho đến khi xác nhận phiếu.

---

# 11. AI Hallucination Test

AI không được tạo dữ liệu không tồn tại trong database.

Ví dụ:

Database:

Chuột X
stock = 80
minimum = 100

Nếu AI trả về:

Laptop Dell XYZ
stock = 300

nhưng DB không có dữ liệu đó:

FAIL.

Automated test phải đối chiếu output với database hoặc dữ liệu input đã cấp cho AI.

---

# 12. Security Test

Kiểm tra:

- SQL Injection;
- XSS;
- broken authentication;
- broken authorization;
- token giả;
- truy cập endpoint không có token;
- truy cập endpoint bằng role sai;
- secret/API key bị trả về response;
- thông tin lỗi chứa stack trace nhạy cảm.

---

# 13. Quy tắc viết Test Code

Mỗi test phải có:

- Test ID;
- mục tiêu;
- precondition;
- input;
- action;
- expected result;
- assertion.

Tên test phải thể hiện rõ hành vi.

Ví dụ:

test_login_with_valid_credentials()

test_login_with_invalid_password()

test_export_quantity_greater_than_stock()

test_ai_analysis_does_not_modify_stock()

test_only_manager_can_approve_ai_proposal()

---

# 14. Fixture

Sử dụng fixture để tạo:

- test database;
- test user;
- admin;
- thủ kho;
- kế toán;
- nhóm hàng;
- hàng hóa;
- nhà cung cấp;
- tồn kho mẫu.

Không dùng dữ liệu production cho automated test.

---

# 15. Mock AI

Trong Unit Test:

Không phụ thuộc trực tiếp Gemini.

Mock:

GeminiAIService
↓
Fake response

Ví dụ:

{
  "analysis": "Hàng dưới mức tồn tối thiểu",
  "recommendation": 20
}

Integration Test có thể sử dụng AI thật nếu cần kiểm tra integration, nhưng phải ghi rõ:

- model;
- thời gian;
- response;
- lỗi;
- chi phí hoặc giới hạn API nếu có.

---

# 16. Không sửa test để PASS

Nếu implementation FAIL:

1. Giữ nguyên Test Case.
2. Giữ nguyên assertion.
3. Ghi nhận actual result.
4. Tìm nguyên nhân.
5. Xác định defect.
6. Sửa source code nếu được giao nhiệm vụ sửa lỗi.
7. Chạy lại test.

Không được:

- xóa assertion;
- giảm yêu cầu;
- đổi expected result cho phù hợp implementation;
- bỏ test failing.

---

# 17. Test Result

Mỗi lần chạy phải ghi:

- tổng số test;
- passed;
- failed;
- skipped;
- errors;
- thời gian chạy.

Ví dụ:

PASS: 42
FAIL: 3
SKIP: 1

---

# 18. Defect Classification

Phân loại:

### Functional Defect
Chức năng sai.

### Authorization Defect
Sai quyền truy cập.

### Data Integrity Defect
Sai dữ liệu hoặc sai tồn kho.

### AI Defect
AI trả kết quả sai, không phù hợp dữ liệu hoặc hallucination.

### Integration Defect
Các module kết hợp không đúng.

### Security Defect
Có vấn đề bảo mật.

---

# 19. Output

Skill phải tạo/cập nhật:

docs/test-plan.md
docs/test-report.md

và automated tests trong source code.

Sau mỗi lần test phải báo cáo:

1. Test Case đã chạy.
2. Test Code tương ứng.
3. Test Result.
4. Failed tests.
5. Defect.
6. Requirement bị ảnh hưởng.
7. AI đã phát hiện gì.
8. Human đã xác minh gì.
9. Files đã thay đổi.

---

# 20. Final Verification

Trước khi kết thúc:

- tất cả requirements quan trọng phải có test;
- các nghiệp vụ ảnh hưởng tồn kho phải có integration test;
- các role phải có authorization test;
- chức năng AI phải có positive + negative test;
- AI phải được kiểm tra không tự thay đổi dữ liệu;
- lỗi Gemini phải được kiểm thử;
- test failure phải được phân tích;
- không được che giấu test failure;
- phải có human verification.