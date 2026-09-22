from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session

from database import SessionLocal
from models import (
    PhieuXuat,
    ChiTietPhieuXuat,
    HangHoa,
    User,
    TonKho,
    LichSuKho
)


router = APIRouter(
    prefix="/phieu-xuat",
    tags=["Phiếu xuất"]
)


# =========================================================
# DATABASE
# =========================================================

def get_db():
    db = SessionLocal()

    try:
        yield db
    finally:
        db.close()


# =========================================================
# SCHEMA
# =========================================================

class ChiTietPhieuXuatCreate(BaseModel):
    ma_hang: int
    so_luong: int


class PhieuXuatCreate(BaseModel):
    ma_tai_khoan: int
    ly_do: str | None = None
    chi_tiet: list[ChiTietPhieuXuatCreate]


# =========================================================
# GET DANH SÁCH PHIẾU XUẤT
# =========================================================

@router.get("")
def get_phieu_xuat(
    db: Session = Depends(get_db)
):
    phieu_list = (
        db.query(PhieuXuat)
        .order_by(PhieuXuat.id.desc())
        .all()
    )

    result = []

    for phieu in phieu_list:

        chi_tiet = (
            db.query(ChiTietPhieuXuat)
            .filter(
                ChiTietPhieuXuat.ma_phieu_xuat == phieu.id
            )
            .all()
        )

        result.append({
            "id": phieu.id,
            "ma_tai_khoan": phieu.ma_tai_khoan,
            "ngay_xuat": phieu.ngay_xuat,
            "ly_do": phieu.ly_do,
            "trang_thai": phieu.trang_thai,
            "chi_tiet": [
                {
                    "id": item.id,
                    "ma_phieu_xuat": item.ma_phieu_xuat,
                    "ma_hang": item.ma_hang,
                    "so_luong": item.so_luong
                }
                for item in chi_tiet
            ]
        })

    return result


# =========================================================
# GET PHIẾU XUẤT THEO ID
# =========================================================

@router.get("/{phieu_xuat_id}")
def get_phieu_xuat_by_id(
    phieu_xuat_id: int,
    db: Session = Depends(get_db)
):
    phieu = (
        db.query(PhieuXuat)
        .filter(PhieuXuat.id == phieu_xuat_id)
        .first()
    )

    if phieu is None:
        raise HTTPException(
            status_code=404,
            detail="Không tìm thấy phiếu xuất"
        )

    chi_tiet = (
        db.query(ChiTietPhieuXuat)
        .filter(
            ChiTietPhieuXuat.ma_phieu_xuat == phieu.id
        )
        .all()
    )

    return {
        "id": phieu.id,
        "ma_tai_khoan": phieu.ma_tai_khoan,
        "ngay_xuat": phieu.ngay_xuat,
        "ly_do": phieu.ly_do,
        "trang_thai": phieu.trang_thai,
        "chi_tiet": [
            {
                "id": item.id,
                "ma_phieu_xuat": item.ma_phieu_xuat,
                "ma_hang": item.ma_hang,
                "so_luong": item.so_luong
            }
            for item in chi_tiet
        ]
    }


# =========================================================
# TẠO PHIẾU XUẤT
# =========================================================

@router.post("")
def create_phieu_xuat(
    data: PhieuXuatCreate,
    db: Session = Depends(get_db)
):
    # -----------------------------------------------------
    # Kiểm tra tài khoản
    # -----------------------------------------------------

    tai_khoan = (
        db.query(User)
        .filter(User.id == data.ma_tai_khoan)
        .first()
    )

    if tai_khoan is None:
        raise HTTPException(
            status_code=400,
            detail="Tài khoản không tồn tại"
        )

    # -----------------------------------------------------
    # Phải có ít nhất 1 sản phẩm
    # -----------------------------------------------------

    if not data.chi_tiet:
        raise HTTPException(
            status_code=400,
            detail="Phiếu xuất phải có ít nhất một mặt hàng"
        )

    # -----------------------------------------------------
    # Kiểm tra từng hàng hóa
    # -----------------------------------------------------

    chi_tiet_temp = []

    for item in data.chi_tiet:

        if item.so_luong <= 0:
            raise HTTPException(
                status_code=400,
                detail="Số lượng xuất phải lớn hơn 0"
            )

        hang_hoa = (
            db.query(HangHoa)
            .filter(HangHoa.id == item.ma_hang)
            .first()
        )

        if hang_hoa is None:
            raise HTTPException(
                status_code=400,
                detail=f"Hàng hóa ID {item.ma_hang} không tồn tại"
            )

        chi_tiet_temp.append({
            "ma_hang": item.ma_hang,
            "so_luong": item.so_luong
        })

    # -----------------------------------------------------
    # Tạo phiếu xuất
    # -----------------------------------------------------

    phieu = PhieuXuat(
        ma_tai_khoan=data.ma_tai_khoan,
        ngay_xuat=datetime.now().strftime(
            "%Y-%m-%d %H:%M:%S"
        ),
        ly_do=data.ly_do,
        trang_thai="Nhap"
    )

    db.add(phieu)
    db.flush()

    # -----------------------------------------------------
    # Tạo chi tiết
    # -----------------------------------------------------

    for item in chi_tiet_temp:

        chi_tiet = ChiTietPhieuXuat(
            ma_phieu_xuat=phieu.id,
            ma_hang=item["ma_hang"],
            so_luong=item["so_luong"]
        )

        db.add(chi_tiet)

    db.commit()
    db.refresh(phieu)

    return {
        "success": True,
        "message": "Tạo phiếu xuất thành công",
        "phieu_xuat": {
            "id": phieu.id,
            "ma_tai_khoan": phieu.ma_tai_khoan,
            "ngay_xuat": phieu.ngay_xuat,
            "ly_do": phieu.ly_do,
            "trang_thai": phieu.trang_thai
        }
    }


# =========================================================
# XÁC NHẬN PHIẾU XUẤT
# =========================================================

@router.put("/{phieu_xuat_id}/xac-nhan")
def xac_nhan_phieu_xuat(
    phieu_xuat_id: int,
    db: Session = Depends(get_db)
):
    # -----------------------------------------------------
    # Tìm phiếu
    # -----------------------------------------------------

    phieu = (
        db.query(PhieuXuat)
        .filter(PhieuXuat.id == phieu_xuat_id)
        .first()
    )

    if phieu is None:
        raise HTTPException(
            status_code=404,
            detail="Không tìm thấy phiếu xuất"
        )

    # -----------------------------------------------------
    # Kiểm tra trạng thái
    # -----------------------------------------------------

    if phieu.trang_thai != "Nhap":
        raise HTTPException(
            status_code=400,
            detail="Phiếu xuất đã được xác nhận hoặc không ở trạng thái hợp lệ"
        )

    # -----------------------------------------------------
    # Lấy chi tiết
    # -----------------------------------------------------

    chi_tiet_list = (
        db.query(ChiTietPhieuXuat)
        .filter(
            ChiTietPhieuXuat.ma_phieu_xuat == phieu.id
        )
        .all()
    )

    if not chi_tiet_list:
        raise HTTPException(
            status_code=400,
            detail="Phiếu xuất không có chi tiết"
        )

    # -----------------------------------------------------
    # BƯỚC 1:
    # Kiểm tra toàn bộ tồn kho trước khi trừ
    # -----------------------------------------------------

    ton_kho_data = []

    for chi_tiet in chi_tiet_list:

        ton_kho = (
            db.query(TonKho)
            .filter(
                TonKho.ma_hang == chi_tiet.ma_hang
            )
            .first()
        )

        if ton_kho is None:
            raise HTTPException(
                status_code=400,
                detail=f"Hàng hóa ID {chi_tiet.ma_hang} chưa có tồn kho"
            )

        if ton_kho.so_luong < chi_tiet.so_luong:
            raise HTTPException(
                status_code=400,
                detail=(
                    f"Hàng hóa ID {chi_tiet.ma_hang} "
                    f"chỉ còn {ton_kho.so_luong}, "
                    f"không đủ để xuất {chi_tiet.so_luong}"
                )
            )

        ton_kho_data.append(
            (chi_tiet, ton_kho)
        )

    # -----------------------------------------------------
    # BƯỚC 2:
    # Trừ tồn kho + ghi lịch sử
    # -----------------------------------------------------

    for chi_tiet, ton_kho in ton_kho_data:

        ton_kho.so_luong -= chi_tiet.so_luong

        ton_kho.ngay_cap_nhat = (
            datetime.now().strftime(
                "%Y-%m-%d %H:%M:%S"
            )
        )

        lich_su = LichSuKho(
            ma_hang=chi_tiet.ma_hang,
            ma_tai_khoan=phieu.ma_tai_khoan,
            loai_giao_dich="Xuat",
            so_luong=chi_tiet.so_luong,
            thoi_gian=datetime.now().strftime(
                "%Y-%m-%d %H:%M:%S"
            ),
            ghi_chu=f"Xuất kho từ phiếu xuất #{phieu.id}"
        )

        db.add(lich_su)

    # -----------------------------------------------------
    # BƯỚC 3:
    # Cập nhật trạng thái
    # -----------------------------------------------------

    phieu.trang_thai = "DaXuat"

    db.commit()
    db.refresh(phieu)

    return {
        "success": True,
        "message": "Xác nhận phiếu xuất thành công",
        "phieu_xuat_id": phieu.id,
        "trang_thai": phieu.trang_thai
    }


# =========================================================
# XÓA PHIẾU XUẤT
# =========================================================

@router.delete("/{phieu_xuat_id}")
def delete_phieu_xuat(
    phieu_xuat_id: int,
    db: Session = Depends(get_db)
):
    phieu = (
        db.query(PhieuXuat)
        .filter(PhieuXuat.id == phieu_xuat_id)
        .first()
    )

    if phieu is None:
        raise HTTPException(
            status_code=404,
            detail="Không tìm thấy phiếu xuất"
        )

    # Không cho xóa phiếu đã xuất
    if phieu.trang_thai == "DaXuat":
        raise HTTPException(
            status_code=400,
            detail="Không thể xóa phiếu xuất đã xác nhận"
        )

    db.query(ChiTietPhieuXuat).filter(
        ChiTietPhieuXuat.ma_phieu_xuat == phieu.id
    ).delete()

    db.delete(phieu)
    db.commit()

    return {
        "success": True,
        "message": "Xóa phiếu xuất thành công"
    }