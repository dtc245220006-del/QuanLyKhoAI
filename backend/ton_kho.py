from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from database import SessionLocal
from models import TonKho, HangHoa


router = APIRouter(
    prefix="/ton-kho",
    tags=["Tồn kho"]
)


def get_db():
    db = SessionLocal()

    try:
        yield db
    finally:
        db.close()


# =========================================================
# XEM TOÀN BỘ TỒN KHO
# =========================================================

@router.get("")
def get_ton_kho(
    db: Session = Depends(get_db)
):
    ton_kho_list = (
        db.query(TonKho)
        .order_by(TonKho.id)
        .all()
    )

    result = []

    for ton in ton_kho_list:

        hang_hoa = (
            db.query(HangHoa)
            .filter(HangHoa.id == ton.ma_hang)
            .first()
        )

        result.append({
            "id": ton.id,
            "ma_hang": ton.ma_hang,
            "ten_hang": (
                hang_hoa.ten_hang
                if hang_hoa
                else None
            ),
            "so_luong": ton.so_luong,
            "ton_toi_thieu": (
                hang_hoa.ton_toi_thieu
                if hang_hoa
                else None
            ),
            "ngay_cap_nhat": ton.ngay_cap_nhat
        })

    return result


# =========================================================
# XEM TỒN KHO THEO HÀNG
# =========================================================

@router.get("/{ma_hang}")
def get_ton_kho_by_hang(
    ma_hang: int,
    db: Session = Depends(get_db)
):
    ton_kho = (
        db.query(TonKho)
        .filter(TonKho.ma_hang == ma_hang)
        .first()
    )

    if ton_kho is None:
        raise HTTPException(
            status_code=404,
            detail="Chưa có dữ liệu tồn kho cho hàng hóa này"
        )

    hang_hoa = (
        db.query(HangHoa)
        .filter(HangHoa.id == ma_hang)
        .first()
    )

    return {
        "ma_hang": ma_hang,
        "ten_hang": (
            hang_hoa.ten_hang
            if hang_hoa
            else None
        ),
        "so_luong": ton_kho.so_luong,
        "ton_toi_thieu": (
            hang_hoa.ton_toi_thieu
            if hang_hoa
            else None
        ),
        "ngay_cap_nhat": ton_kho.ngay_cap_nhat
    }


# =========================================================
# CẢNH BÁO TỒN THẤP
# =========================================================

@router.get("/canh-bao/thap")
def get_canh_bao_ton_thap(
    db: Session = Depends(get_db)
):
    ton_kho_list = (
        db.query(TonKho)
        .all()
    )

    result = []

    for ton in ton_kho_list:

        hang_hoa = (
            db.query(HangHoa)
            .filter(HangHoa.id == ton.ma_hang)
            .first()
        )

        if (
            hang_hoa is not None
            and ton.so_luong < hang_hoa.ton_toi_thieu
        ):
            result.append({
                "ma_hang": ton.ma_hang,
                "ten_hang": hang_hoa.ten_hang,
                "so_luong": ton.so_luong,
                "ton_toi_thieu": hang_hoa.ton_toi_thieu
            })

    return result