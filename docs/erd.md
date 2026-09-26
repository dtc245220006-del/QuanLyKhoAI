# ERD — Hệ thống Quản lý Kho tích hợp AI

```mermaid
erDiagram
    USER ||--o{ PHIEU_NHAP : tao
    USER ||--o{ PHIEU_XUAT : tao
    USER ||--o{ LICH_SU_KHO : ghi_nhan
    USER ||--o{ DE_XUAT_AI : tao

    NHOM_HANG ||--o{ HANG_HOA : gom
    NHA_CUNG_CAP ||--o{ PHIEU_NHAP : cung_cap

    PHIEU_NHAP ||--o{ CHI_TIET_PHIEU_NHAP : co
    HANG_HOA ||--o{ CHI_TIET_PHIEU_NHAP : duoc_nhap

    HANG_HOA ||--|| TON_KHO : co_ton
    HANG_HOA ||--o{ LICH_SU_KHO : phat_sinh

    PHIEU_XUAT ||--o{ CHI_TIET_PHIEU_XUAT : co
    HANG_HOA ||--o{ CHI_TIET_PHIEU_XUAT : duoc_xuat

    DE_XUAT_AI ||--o{ CHI_TIET_DE_XUAT_AI : gom
    HANG_HOA ||--o{ CHI_TIET_DE_XUAT_AI : duoc_de_xuat
```

## User
| Trường | Ý nghĩa |
|---|---|
| id | Khóa chính |
| username | Tên đăng nhập, duy nhất |
| password | Mật khẩu đã mã hóa |
| full_name | Họ tên |
| role | QuanLy / ThuKho / KeToan |

## Ghi chú implementation
Trong code hiện tại, các quan hệ FK đang được lưu bằng các cột Integer như `ma_hang`, `ma_tai_khoan`, `ma_phieu_nhap`...; cần phân biệt "logical FK" với "ForeignKey constraint vật lý" khi viết báo cáo.
