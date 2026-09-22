from sqlalchemy import Column, Integer, String
from database import Base


# =========================================================
# TÀI KHOẢN
# =========================================================

class User(Base):
    __tablename__ = "users"

    id = Column(
        Integer,
        primary_key=True,
        index=True
    )

    username = Column(
        String(50),
        unique=True,
        nullable=False,
        index=True
    )

    password = Column(
        String(255),
        nullable=False
    )

    full_name = Column(
        String(100),
        nullable=False
    )

    role = Column(
        String(20),
        nullable=False
    )


# =========================================================
# NHÓM HÀNG
# =========================================================

class NhomHang(Base):
    __tablename__ = "nhom_hang"

    id = Column(
        Integer,
        primary_key=True,
        index=True
    )

    ten_nhom = Column(
        String(100),
        unique=True,
        nullable=False,
        index=True
    )

    mo_ta = Column(
        String(255),
        nullable=True
    )



# =========================================================
# HÀNG HÓA
# =========================================================

class HangHoa(Base):
    __tablename__ = "hang_hoa"

    id = Column(
        Integer,
        primary_key=True,
        index=True
    )

    ma_nhom = Column(
        Integer,
        nullable=False,
        index=True
    )

    ten_hang = Column(
        String(150),
        nullable=False,
        index=True
    )

    don_vi_tinh = Column(
        String(50),
        nullable=False
    )

    ma_barcode = Column(
        String(100),
        unique=True,
        nullable=True
    )

    gia_nhap = Column(
        Integer,
        nullable=False,
        default=0
    )

    gia_ban = Column(
        Integer,
        nullable=False,
        default=0
    )

    ton_toi_thieu = Column(
        Integer,
        nullable=False,
        default=0
    )
    # =========================================================
# NHÀ CUNG CẤP
# =========================================================

class NhaCungCap(Base):
    __tablename__ = "nha_cung_cap"

    id = Column(
        Integer,
        primary_key=True,
        index=True
    )

    ten_ncc = Column(
        String(150),
        nullable=False,
        index=True
    )

    so_dien_thoai = Column(
        String(20),
        nullable=True
    )

    email = Column(
        String(100),
        nullable=True
    )

    dia_chi = Column(
        String(255),
        nullable=True
    )
    # =========================================================
# PHIẾU NHẬP
# =========================================================

class PhieuNhap(Base):
    __tablename__ = "phieu_nhap"

    id = Column(
        Integer,
        primary_key=True,
        index=True
    )

    ma_ncc = Column(
        Integer,
        nullable=False,
        index=True
    )

    ma_tai_khoan = Column(
        Integer,
        nullable=False,
        index=True
    )

    ngay_nhap = Column(
        String(30),
        nullable=False
    )

    tong_tien = Column(
        Integer,
        nullable=False,
        default=0
    )

    trang_thai = Column(
        String(30),
        nullable=False,
        default="Nhap"
    )


# =========================================================
# CHI TIẾT PHIẾU NHẬP
# =========================================================

class ChiTietPhieuNhap(Base):
    __tablename__ = "chi_tiet_phieu_nhap"

    id = Column(
        Integer,
        primary_key=True,
        index=True
    )

    ma_phieu_nhap = Column(
        Integer,
        nullable=False,
        index=True
    )

    ma_hang = Column(
        Integer,
        nullable=False,
        index=True
    )

    so_luong = Column(
        Integer,
        nullable=False
    )

    don_gia = Column(
        Integer,
        nullable=False
    )

    thanh_tien = Column(
        Integer,
        nullable=False
    )
    # =========================================================
# TỒN KHO
# =========================================================

class TonKho(Base):
    __tablename__ = "ton_kho"

    id = Column(
        Integer,
        primary_key=True,
        index=True
    )

    ma_hang = Column(
        Integer,
        unique=True,
        nullable=False,
        index=True
    )

    so_luong = Column(
        Integer,
        nullable=False,
        default=0
    )

    ngay_cap_nhat = Column(
        String(30),
        nullable=False
    )


# =========================================================
# LỊCH SỬ KHO
# =========================================================

class LichSuKho(Base):
    __tablename__ = "lich_su_kho"

    id = Column(
        Integer,
        primary_key=True,
        index=True
    )

    ma_hang = Column(
        Integer,
        nullable=False,
        index=True
    )

    ma_tai_khoan = Column(
        Integer,
        nullable=False,
        index=True
    )

    loai_giao_dich = Column(
        String(30),
        nullable=False
    )

    so_luong = Column(
        Integer,
        nullable=False
    )

    thoi_gian = Column(
        String(30),
        nullable=False
    )

    ghi_chu = Column(
        String(255),
        nullable=True
    )
    # =========================================================
# PHIẾU XUẤT
# =========================================================

class PhieuXuat(Base):
    __tablename__ = "phieu_xuat"

    id = Column(
        Integer,
        primary_key=True,
        index=True
    )

    ma_tai_khoan = Column(
        Integer,
        nullable=False,
        index=True
    )

    ngay_xuat = Column(
        String(30),
        nullable=False
    )

    ly_do = Column(
        String(255),
        nullable=True
    )

    trang_thai = Column(
        String(30),
        nullable=False,
        default="Nhap"
    )


# =========================================================
# CHI TIẾT PHIẾU XUẤT
# =========================================================

class ChiTietPhieuXuat(Base):
    __tablename__ = "chi_tiet_phieu_xuat"

    id = Column(
        Integer,
        primary_key=True,
        index=True
    )

    ma_phieu_xuat = Column(
        Integer,
        nullable=False,
        index=True
    )

    ma_hang = Column(
        Integer,
        nullable=False,
        index=True
    )

    so_luong = Column(
        Integer,
        nullable=False
    )
    # =========================================================
# ĐỀ XUẤT AI
# =========================================================

class DeXuatAI(Base):
    __tablename__ = "de_xuat_ai"

    id = Column(
        Integer,
        primary_key=True,
        index=True
    )

    ma_tai_khoan = Column(
        Integer,
        nullable=False,
        index=True
    )

    ngay_tao = Column(
        String(30),
        nullable=False
    )

    noi_dung = Column(
        String(5000),
        nullable=True
    )

    trang_thai = Column(
        String(30),
        nullable=False,
        default="ChoDuyet"
    )

    ly_do = Column(
        String(1000),
        nullable=True
    )


# =========================================================
# CHI TIẾT ĐỀ XUẤT AI
# =========================================================

class ChiTietDeXuatAI(Base):
    __tablename__ = "chi_tiet_de_xuat_ai"

    id = Column(
        Integer,
        primary_key=True,
        index=True
    )

    ma_de_xuat = Column(
        Integer,
        nullable=False,
        index=True
    )

    ma_hang = Column(
        Integer,
        nullable=False,
        index=True
    )

    so_luong_de_xuat = Column(
        Integer,
        nullable=False
    )

    ly_do = Column(
        String(500),
        nullable=True
    )