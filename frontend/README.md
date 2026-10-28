# QuanLyKhoAI — Frontend

Giao diện React + Vite của hệ thống quản lý kho tích hợp AI; **không phải ứng dụng hoạt động độc lập**. Phải chạy backend FastAPI và MySQL trước khi dùng các màn hình chính.

## Cài đặt và chạy

Từ thư mục gốc repository, trên PowerShell:

```powershell
cd frontend
npm ci
npm run dev
```

Mở http://localhost:5173. Yêu cầu Node.js/npm tương thích với `package.json` hiện có (Vite 8). Backend phải chạy tại **http://127.0.0.1:8000** vì `src/api.js` đang đặt `baseURL` cố định ở đó. Nếu chạy backend ở host/port khác, cần sửa `src/api.js` và CORS trong `backend/main.py` cho khớp.

Lệnh kiểm tra giao diện:

```powershell
npm run lint
npm run build
```

Các lệnh này phải được **thực thi và xem output** trước khi tuyên bố build/lint thành công. Không có bằng chứng kiểm thử E2E tự động đầy đủ chỉ từ các lệnh trên.

## Các trang

- `/` — đăng nhập; `/dashboard` — bảng điều khiển.
- `/tai-khoan`, `/nhom-hang`, `/hang-hoa`, `/nha-cung-cap`.
- `/phieu-nhap`, `/phieu-xuat`, `/ton-kho`, `/lich-su-kho`.
- `/bao-cao`, `/ai`, `/multi-agent`.

`src/api.js` tự đính kèm JWT từ `localStorage` vào request Axios. `App.jsx` chặn điều hướng theo token và kiểm tra username `admin` cho trang tài khoản; **đây chỉ là kiểm soát UI**, không thay thế kiểm tra role/JWT ở backend. Không coi việc ẩn menu là bằng chứng API an toàn.

## Quy trình demo gợi ý

1. Mở backend `/docs`; xác nhận MySQL và Gemini đã được cấu hình riêng trong `backend/.env`.
2. Đăng nhập bằng tài khoản thử nghiệm do nhóm kiểm soát; không dùng mật khẩu mặc định khi kết nối ra mạng.
3. Tạo/xem hàng hóa, kiểm tra tồn; lập phiếu nháp; xác nhận để thấy biến động tồn/lịch sử.
4. Xem AI phân tích, đề xuất và quy trình duyệt → tạo phiếu nhập nháp → xác nhận.
5. Đặt một câu hỏi ở màn hình Multi-Agent và giải thích nguồn dữ liệu, Critic/retry.

## Tài liệu chính

Xem [README dự án](../README.md), [Deployment](../docs/deployment.md), [Security Review](../docs/security-review.md), [Test Report](../docs/test-report.md).
