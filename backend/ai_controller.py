from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from database import SessionLocal
from models import TonKho, HangHoa
from gemini_service import phan_tich_ton_kho


router = APIRouter(
    prefix="/ai",
    tags=["AI"]
)


def get_db():
    db = SessionLocal()

    try:
        yield db
    finally:
        db.close()


@router.get("/phan-tich-ton-kho")
def ai_phan_tich_ton_kho(
    db: Session = Depends(get_db)
):
    ton_kho_list = (
        db.query(TonKho)
        .order_by(TonKho.ma_hang)
        .all()
    )

    du_lieu = []

    for ton_kho in ton_kho_list:

        hang_hoa = (
            db.query(HangHoa)
            .filter(HangHoa.id == ton_kho.ma_hang)
            .first()
        )

        if hang_hoa is None:
            continue

        du_lieu.append({
            "ma_hang": hang_hoa.id,
            "ten_hang": hang_hoa.ten_hang,
            "so_luong_ton": ton_kho.so_luong,
            "ton_toi_thieu": hang_hoa.ton_toi_thieu
        })

    if not du_lieu:
        return {
            "success": True,
            "message": "Chưa có dữ liệu tồn kho để phân tích",
            "data": []
        }

    ket_qua = phan_tich_ton_kho(
        du_lieu
    )

    return {
        "success": True,
        "data": du_lieu,
        "analysis": ket_qua
    }