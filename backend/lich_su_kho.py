from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from database import SessionLocal
from models import LichSuKho, HangHoa, User


router = APIRouter(
    prefix="/lich-su-kho",
    tags=["Lịch sử kho"]
)


def get_db():
    db = SessionLocal()

    try:
        yield db
    finally:
        db.close()


@router.get("")
def get_lich_su_kho(
    db: Session = Depends(get_db)
):
    lich_su_list = (
        db.query(LichSuKho)
        .order_by(LichSuKho.id.desc())
        .all()
    )

    result = []

    for item in lich_su_list:

        hang_hoa = (
            db.query(HangHoa)
            .filter(HangHoa.id == item.ma_hang)
            .first()
        )

        user = (
            db.query(User)
            .filter(User.id == item.ma_tai_khoan)
            .first()
        )

        result.append({
            "id": item.id,
            "ma_hang": item.ma_hang,
            "ten_hang": (
                hang_hoa.ten_hang
                if hang_hoa
                else None
            ),
            "ma_tai_khoan": item.ma_tai_khoan,
            "nguoi_thuc_hien": (
                user.full_name
                if user
                else None
            ),
            "loai_giao_dich": item.loai_giao_dich,
            "so_luong": item.so_luong,
            "thoi_gian": item.thoi_gian,
            "ghi_chu": item.ghi_chu
        })

    return result