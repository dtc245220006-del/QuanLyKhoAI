# Ngữ cảnh dự án QuanLyKhoAI

## Vai trò
- Quản lý
- Thủ kho
- Kế toán

## Thực thể database
User
NhomHang
HangHoa
NhaCungCap
PhieuNhap
ChiTietPhieuNhap
TonKho
LichSuKho
PhieuXuat
ChiTietPhieuXuat
DeXuatAI
ChiTietDeXuatAI

## Luồng AI
TonKho + HangHoa
→ GeminiAIService
→ DeXuatAI + ChiTietDeXuatAI
→ Quản lý duyệt/từ chối
→ nếu duyệt → Thủ kho tạo phiếu nhập nháp
→ xác nhận phiếu nhập
→ tăng TonKho + LichSuKho

AI không trực tiếp mutate dữ liệu kho.
