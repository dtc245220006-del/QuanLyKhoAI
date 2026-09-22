from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session

from database import SessionLocal
from models import (
    PhieuNhap,
    ChiTietPhieuNhap,
    NhaCungCap,
    HangHoa,
    User,
    TonKho,
    LichSuKho
)

router = APIRouter(
    prefix="/phieu-nhap",
    tags=["Phiếu nhập"]
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
# SCHEMA CHI TIẾT PHIẾU NHẬP
# =========================================================

class ChiTietPhieuNhapCreate(BaseModel):
    ma_hang: int
    so_luong: int
    don_gia: int


class ChiTietPhieuNhapResponse(BaseModel):
    id: int
    ma_phieu_nhap: int
    ma_hang: int
    so_luong: int
    don_gia: int
    thanh_tien: int


# =========================================================
# SCHEMA PHIẾU NHẬP
# =========================================================

class PhieuNhapCreate(BaseModel):
    ma_ncc: int
    ma_tai_khoan: int
    chi_tiet: list[ChiTietPhieuNhapCreate]


class PhieuNhapResponse(BaseModel):
    id: int
    ma_ncc: int
    ma_tai_khoan: int
    ngay_nhap: str
    tong_tien: int
    trang_thai: str
    chi_tiet: list[ChiTietPhieuNhapResponse]


# =========================================================
# LẤY CHI TIẾT CỦA PHIẾU
# =========================================================

def get_chi_tiet(
    db: Session,
    ma_phieu_nhap: int
):
    return (
        db.query(ChiTietPhieuNhap)
        .filter(
            ChiTietPhieuNhap.ma_phieu_nhap == ma_phieu_nhap
        )
        .all()
    )


# =========================================================
# GET DANH SÁCH PHIẾU NHẬP
# =========================================================

@router.get("")
def get_phieu_nhap(
    db: Session = Depends(get_db)
):
    phieu_nhap_list = (
        db.query(PhieuNhap)
        .order_by(PhieuNhap.id.desc())
        .all()
    )

    result = []

    for phieu in phieu_nhap_list:

        chi_tiet = get_chi_tiet(
            db,
            phieu.id
        )

        result.append({
            "id": phieu.id,
            "ma_ncc": phieu.ma_ncc,
            "ma_tai_khoan": phieu.ma_tai_khoan,
            "ngay_nhap": phieu.ngay_nhap,
            "tong_tien": phieu.tong_tien,
            "trang_thai": phieu.trang_thai,
            "chi_tiet": [
                {
                    "id": item.id,
                    "ma_phieu_nhap": item.ma_phieu_nhap,
                    "ma_hang": item.ma_hang,
                    "so_luong": item.so_luong,
                    "don_gia": item.don_gia,
                    "thanh_tien": item.thanh_tien
                }
                for item in chi_tiet
            ]
        })

    return result


# =========================================================
# GET PHIẾU NHẬP THEO ID
# =========================================================

@router.get("/{phieu_nhap_id}")
def get_phieu_nhap_by_id(
    phieu_nhap_id: int,
    db: Session = Depends(get_db)
):
    phieu = (
        db.query(PhieuNhap)
        .filter(PhieuNhap.id == phieu_nhap_id)
        .first()
    )

    if phieu is None:
        raise HTTPException(
            status_code=404,
            detail="Không tìm thấy phiếu nhập"
        )

    chi_tiet = get_chi_tiet(
        db,
        phieu.id
    )

    return {
        "id": phieu.id,
        "ma_ncc": phieu.ma_ncc,
        "ma_tai_khoan": phieu.ma_tai_khoan,
        "ngay_nhap": phieu.ngay_nhap,
        "tong_tien": phieu.tong_tien,
        "trang_thai": phieu.trang_thai,
        "chi_tiet": [
            {
                "id": item.id,
                "ma_phieu_nhap": item.ma_phieu_nhap,
                "ma_hang": item.ma_hang,
                "so_luong": item.so_luong,
                "don_gia": item.don_gia,
                "thanh_tien": item.thanh_tien
            }
            for item in chi_tiet
        ]
    }


# =========================================================
# TẠO PHIẾU NHẬP
# =========================================================

@router.post("")
def create_phieu_nhap(
    data: PhieuNhapCreate,
    db: Session = Depends(get_db)
):

    # -----------------------------------------------------
    # Kiểm tra nhà cung cấp
    # -----------------------------------------------------

    nha_cung_cap = (
        db.query(NhaCungCap)
        .filter(NhaCungCap.id == data.ma_ncc)
        .first()
    )

    if nha_cung_cap is None:
        raise HTTPException(
            status_code=400,
            detail="Nhà cung cấp không tồn tại"
        )

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
            detail="Phiếu nhập phải có ít nhất một mặt hàng"
        )

    # -----------------------------------------------------
    # Kiểm tra chi tiết + tính tổng tiền
    # -----------------------------------------------------

    tong_tien = 0
    chi_tiet_temp = []

    for item in data.chi_tiet:

        if item.so_luong <= 0:
            raise HTTPException(
                status_code=400,
                detail="Số lượng phải lớn hơn 0"
            )

        if item.don_gia < 0:
            raise HTTPException(
                status_code=400,
                detail="Đơn giá không được âm"
            )

        hang_hoa = (
            db.query(HangHoa)
            .filter(HangHoa.id == item.ma_hang)
            .first()
        )

        if hang_hoa is None:
            raise HTTPException(
                status_code=400,
                detail=f"Hàng hóa có ID {item.ma_hang} không tồn tại"
            )

        thanh_tien = (
            item.so_luong * item.don_gia
        )

        tong_tien += thanh_tien

        chi_tiet_temp.append({
            "ma_hang": item.ma_hang,
            "so_luong": item.so_luong,
            "don_gia": item.don_gia,
            "thanh_tien": thanh_tien
        })

    # -----------------------------------------------------
    # Tạo phiếu nhập
    # -----------------------------------------------------

    phieu = PhieuNhap(
        ma_ncc=data.ma_ncc,
        ma_tai_khoan=data.ma_tai_khoan,
        ngay_nhap=datetime.now().strftime(
            "%Y-%m-%d %H:%M:%S"
        ),
        tong_tien=tong_tien,
        trang_thai="Nhap"
    )

    db.add(phieu)
    db.flush()

    # -----------------------------------------------------
    # Tạo chi tiết
    # -----------------------------------------------------

    for item in chi_tiet_temp:

        chi_tiet = ChiTietPhieuNhap(
            ma_phieu_nhap=phieu.id,
            ma_hang=item["ma_hang"],
            so_luong=item["so_luong"],
            don_gia=item["don_gia"],
            thanh_tien=item["thanh_tien"]
        )

        db.add(chi_tiet)

    db.commit()
    db.refresh(phieu)

    return {
        "success": True,
        "message": "Tạo phiếu nhập thành công",
        "phieu_nhap": {
            "id": phieu.id,
            "ma_ncc": phieu.ma_ncc,
            "ma_tai_khoan": phieu.ma_tai_khoan,
            "ngay_nhap": phieu.ngay_nhap,
            "tong_tien": phieu.tong_tien,
            "trang_thai": phieu.trang_thai
        }
    }


# =========================================================
# XÓA PHIẾU NHẬP
# =========================================================

@router.delete("/{phieu_nhap_id}")
def delete_phieu_nhap(
    phieu_nhap_id: int,
    db: Session = Depends(get_db)
):

    phieu = (
        db.query(PhieuNhap)
        .filter(PhieuNhap.id == phieu_nhap_id)
        .first()
    )

    if phieu is None:
        raise HTTPException(
            status_code=404,
            detail="Không tìm thấy phiếu nhập"
        )

    # Xóa chi tiết trước
    db.query(ChiTietPhieuNhap).filter(
        ChiTietPhieuNhap.ma_phieu_nhap == phieu.id
    ).delete()

    db.delete(phieu)
    db.commit()

    return {
        "success": True,
        "message": "Xóa phiếu nhập thành công"
    }
# =========================================================
# XÁC NHẬN PHIẾU NHẬP
# =========================================================

@router.put("/{phieu_nhap_id}/xac-nhan")
def xac_nhan_phieu_nhap(
    phieu_nhap_id: int,
    db: Session = Depends(get_db)
):
    # -----------------------------------------------------
    # Tìm phiếu nhập
    # -----------------------------------------------------

    phieu = (
        db.query(PhieuNhap)
        .filter(PhieuNhap.id == phieu_nhap_id)
        .first()
    )

    if phieu is None:
        raise HTTPException(
            status_code=404,
            detail="Không tìm thấy phiếu nhập"
        )

    # -----------------------------------------------------
    # Không cho xác nhận lần 2
    # -----------------------------------------------------

    if phieu.trang_thai != "Nhap":
        raise HTTPException(
            status_code=400,
            detail="Phiếu nhập đã được xác nhận hoặc không ở trạng thái hợp lệ"
        )

    # -----------------------------------------------------
    # Lấy chi tiết phiếu nhập
    # -----------------------------------------------------

    chi_tiet_list = (
        db.query(ChiTietPhieuNhap)
        .filter(
            ChiTietPhieuNhap.ma_phieu_nhap == phieu.id
        )
        .all()
    )

    if not chi_tiet_list:
        raise HTTPException(
            status_code=400,
            detail="Phiếu nhập không có chi tiết"
        )

    # -----------------------------------------------------
    # Cập nhật tồn kho + lịch sử
    # -----------------------------------------------------

    for chi_tiet in chi_tiet_list:

        # Kiểm tra hàng hóa
        hang_hoa = (
            db.query(HangHoa)
            .filter(
                HangHoa.id == chi_tiet.ma_hang
            )
            .first()
        )

        if hang_hoa is None:
            raise HTTPException(
                status_code=400,
                detail=f"Hàng hóa ID {chi_tiet.ma_hang} không tồn tại"
            )

        # Tìm tồn kho hiện tại
        ton_kho = (
            db.query(TonKho)
            .filter(
                TonKho.ma_hang == chi_tiet.ma_hang
            )
            .first()
        )

        # Nếu chưa có tồn kho thì tạo mới
        if ton_kho is None:

            ton_kho = TonKho(
                ma_hang=chi_tiet.ma_hang,
                so_luong=chi_tiet.so_luong,
                ngay_cap_nhat=datetime.now().strftime(
                    "%Y-%m-%d %H:%M:%S"
                )
            )

            db.add(ton_kho)

        else:

            ton_kho.so_luong += chi_tiet.so_luong

            ton_kho.ngay_cap_nhat = (
                datetime.now().strftime(
                    "%Y-%m-%d %H:%M:%S"
                )
            )

        # Ghi lịch sử kho
        lich_su = LichSuKho(
            ma_hang=chi_tiet.ma_hang,
            ma_tai_khoan=phieu.ma_tai_khoan,
            loai_giao_dich="Nhap",
            so_luong=chi_tiet.so_luong,
            thoi_gian=datetime.now().strftime(
                "%Y-%m-%d %H:%M:%S"
            ),
            ghi_chu=f"Nhập kho từ phiếu nhập #{phieu.id}"
        )

        db.add(lich_su)

    # -----------------------------------------------------
    # Cập nhật trạng thái phiếu
    # -----------------------------------------------------

    phieu.trang_thai = "DaNhap"

    db.commit()
    db.refresh(phieu)

    return {
        "success": True,
        "message": "Xác nhận phiếu nhập thành công",
        "phieu_nhap_id": phieu.id,
        "trang_thai": phieu.trang_thai
    }