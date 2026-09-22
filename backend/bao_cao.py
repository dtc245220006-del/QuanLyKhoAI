from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import func

from database import SessionLocal
from models import (
    PhieuNhap,
    PhieuXuat,
    ChiTietPhieuNhap,
    ChiTietPhieuXuat,
    TonKho,
    HangHoa
)

router = APIRouter(
    prefix="/bao-cao",
    tags=["Thống kê & Báo cáo"]
)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# =========================================================
# DASHBOARD TỔNG QUAN
# =========================================================

@router.get("/dashboard")
def dashboard(
    db: Session = Depends(get_db)
):
    tong_hang = db.query(HangHoa).count()
    tong_nhom = db.execute(
        func.count(func.distinct(HangHoa.ma_nhom))
    ).scalar() or 0

    tong_nhap = (
        db.query(func.coalesce(func.sum(ChiTietPhieuNhap.thanh_tien), 0))
        .join(
            PhieuNhap,
            ChiTietPhieuNhap.ma_phieu_nhap == PhieuNhap.id
        )
        .filter(PhieuNhap.trang_thai == "DaNhap")
        .scalar()
        or 0
    )

    tong_xuat = (
        db.query(func.coalesce(func.sum(ChiTietPhieuXuat.so_luong), 0))
        .join(
            PhieuXuat,
            ChiTietPhieuXuat.ma_phieu_xuat == PhieuXuat.id
        )
        .filter(PhieuXuat.trang_thai == "DaXuat")
        .scalar()
        or 0
    )

    tong_ton = (
        db.query(func.coalesce(func.sum(TonKho.so_luong), 0))
        .scalar()
        or 0
    )

    return {
        "tong_hang_hoa": tong_hang,
        "tong_nhom_hang": tong_nhom,
        "tong_tien_nhap": tong_nhap,
        "tong_so_luong_xuat": tong_xuat,
        "tong_so_luong_ton": tong_ton
    }


# =========================================================
# BÁO CÁO NHẬP
# =========================================================

@router.get("/nhap")
def bao_cao_nhap(
    db: Session = Depends(get_db)
):
    rows = (
        db.query(
            PhieuNhap.id.label("ma_phieu_nhap"),
            PhieuNhap.ngay_nhap,
            PhieuNhap.ma_ncc,
            PhieuNhap.ma_tai_khoan,
            PhieuNhap.tong_tien
        )
        .filter(PhieuNhap.trang_thai == "DaNhap")
        .order_by(PhieuNhap.id.desc())
        .all()
    )

    return [
        {
            "ma_phieu_nhap": row.ma_phieu_nhap,
            "ngay_nhap": row.ngay_nhap,
            "ma_ncc": row.ma_ncc,
            "ma_tai_khoan": row.ma_tai_khoan,
            "tong_tien": row.tong_tien
        }
        for row in rows
    ]


# =========================================================
# BÁO CÁO XUẤT
# =========================================================

@router.get("/xuat")
def bao_cao_xuat(
    db: Session = Depends(get_db)
):
    rows = (
        db.query(
            PhieuXuat.id.label("ma_phieu_xuat"),
            PhieuXuat.ngay_xuat,
            PhieuXuat.ma_tai_khoan,
            PhieuXuat.ly_do
        )
        .filter(PhieuXuat.trang_thai == "DaXuat")
        .order_by(PhieuXuat.id.desc())
        .all()
    )

    return [
        {
            "ma_phieu_xuat": row.ma_phieu_xuat,
            "ngay_xuat": row.ngay_xuat,
            "ma_tai_khoan": row.ma_tai_khoan,
            "ly_do": row.ly_do
        }
        for row in rows
    ]


# =========================================================
# BÁO CÁO TỒN KHO
# =========================================================

@router.get("/ton-kho")
def bao_cao_ton_kho(
    db: Session = Depends(get_db)
):
    rows = (
        db.query(TonKho, HangHoa)
        .join(
            HangHoa,
            TonKho.ma_hang == HangHoa.id
        )
        .order_by(HangHoa.id)
        .all()
    )

    return [
        {
            "ma_hang": hang_hoa.id,
            "ten_hang": hang_hoa.ten_hang,
            "so_luong_ton": ton_kho.so_luong,
            "ton_toi_thieu": hang_hoa.ton_toi_thieu,
            "canh_bao": (
                ton_kho.so_luong < hang_hoa.ton_toi_thieu
            )
        }
        for ton_kho, hang_hoa in rows
    ]