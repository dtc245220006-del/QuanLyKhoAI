# Database Design

Database thống nhất: MySQL `quan_ly_kho`.

Các bảng:
`users`, `nhom_hang`, `hang_hoa`, `nha_cung_cap`, `phieu_nhap`, `chi_tiet_phieu_nhap`, `ton_kho`, `lich_su_kho`, `phieu_xuat`, `chi_tiet_phieu_xuat`, `de_xuat_ai`, `chi_tiet_de_xuat_ai`.

ERD: xem `docs/erd.md`.

Nguyên tắc:
- PK duy nhất cho mỗi bảng.
- username và barcode có UNIQUE phù hợp.
- `ton_kho.ma_hang` UNIQUE.
- Chi tiết phiếu tham chiếu phiếu và hàng hóa.
- Đề xuất AI tham chiếu User và HangHoa.
- Dữ liệu chỉ được cập nhật qua transaction nghiệp vụ.
